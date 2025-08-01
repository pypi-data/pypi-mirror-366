"""Django base views for SatNOGS Network"""
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import make_aware, now
from django.views.decorators.http import require_POST

from network.base.cache import get_satellites
from network.base.db_api import DBConnectionError, get_tle_set_by_sat_id, get_tle_sets, \
    get_transmitter_by_uuid, get_transmitters, get_transmitters_by_sat_id
from network.base.decorators import ajax_required
from network.base.forms import ObservationFormSet, SatelliteFilterForm
from network.base.models import Observation, Station
from network.base.perms import schedule_perms, schedule_station_violators_perms
from network.base.scheduling import create_new_observation, get_available_stations, \
    over_min_duration, predict_available_observation_windows
from network.base.serializers import StationSerializer
from network.base.stats import get_satellite_stats_by_transmitter_list, get_transmitters_with_stats
from network.base.tasks import fetch_satellites
from network.base.validators import NegativeElevationError, NoTleSetError, \
    ObservationOverlapError, OutOfRangeError, SchedulingLimitError, SinglePassError, \
    check_violators_scheduling_limit, is_frequency_in_transmitter_range, \
    is_transmitter_in_station_range


def create_new_observations(formset, user):
    """Creates new observations from formset. Error handling is performed by upper layers."""
    new_observations = []
    observations_per_sat_id = defaultdict(list)
    for observation_data in formset.cleaned_data:
        transmitter_uuid = observation_data['transmitter_uuid']
        transmitter = formset.transmitters[transmitter_uuid]
        center_frequency = observation_data.get('center_frequency', None)
        if (transmitter["type"] == "Transponder"
                or transmitter["type"] == "Range transmitter") and center_frequency is None:
            center_frequency = (transmitter['downlink_high'] + transmitter['downlink_low']) // 2
        tle_set = formset.tle_sets[transmitter['sat_id']]
        observations_per_sat_id[transmitter['sat_id']].append(observation_data['start'])

        observation = create_new_observation(
            station=observation_data['ground_station'],
            transmitter=transmitter,
            start=observation_data['start'],
            end=observation_data['end'],
            author=user,
            tle_set=tle_set,
            center_frequency=center_frequency
        )
        new_observations.append(observation)

    if formset.violators and not user.groups.filter(name='Operators').exists():
        check_violators_scheduling_limit(formset.violators, observations_per_sat_id)

    for observation in new_observations:
        observation.save()

    return new_observations


def observation_new_post(request):
    """Handles POST requests for creating one or more new observations."""
    formset = ObservationFormSet(request.user, request.POST, prefix='obs')
    try:
        if not formset.is_valid():
            errors_list = [error for error in formset.errors if error]
            if errors_list:
                for field in errors_list[0]:
                    messages.error(request, str(errors_list[0][field][0]))
            else:
                messages.error(request, str(formset.non_form_errors()[0]))
            return redirect(reverse('base:observation_new'))

        new_observations = create_new_observations(formset, request.user)
        if not request.user.is_observer:
            request.user.is_observer = True
            request.user.save(update_fields=['is_observer'])

        if 'scheduled' in request.session:
            del request.session['scheduled']
        request.session['scheduled'] = list(obs.id for obs in new_observations)

        # If it's a single observation redirect to that one
        total = formset.total_form_count()
        if total == 1:
            messages.success(request, 'Observation was scheduled successfully.')
            response = redirect(
                reverse(
                    'base:observation_view', kwargs={'observation_id': new_observations[0].id}
                )
            )
        else:
            messages.success(request, str(total) + ' Observations were scheduled successfully.')
            response = redirect(reverse('base:observations_list'))
            observer = request.user.id
            start = request.POST.get('start')
            end = request.POST.get('end')
            satellite = request.POST.get('satellite')
            transmitter_uuid = request.POST.get('transmitter')
            response['Location'] += (
                f'?observer={observer}&start={start}&end={end}'
                f'&sat_id={satellite}&transmitter_uuid={transmitter_uuid}'
            )
    except (ObservationOverlapError, NegativeElevationError, NoTleSetError, SinglePassError,
            ValidationError, ValueError, SchedulingLimitError) as error:
        messages.error(request, str(error))
        response = redirect(reverse('base:observation_new'))
    return response


@login_required
def observation_new(request):
    """View for new observation"""
    can_schedule = schedule_perms(request.user)
    if not can_schedule:
        messages.error(request, 'You don\'t have permissions to schedule observations')
        return redirect(reverse('base:observations_list'))

    if request.method == 'POST':
        return observation_new_post(request)

    try:
        satellites = {k: v for k, v in fetch_satellites().items() if v['status'] == 'alive'}
    except DBConnectionError:
        try:
            satellites = get_satellites()
            messages.warning(request, ('Warning: Using cached list of satellites.'))
        except DBConnectionError:
            satellites = {}
            messages.error(
                request, (
                    'Error: Could not load satellite list. Please try again later. '
                    'If the error persists, contact an administrator.'
                )
            )
    obs_filter = {}
    if request.method == 'GET':
        filter_form = SatelliteFilterForm(request.GET)
        if filter_form.is_valid():
            start = filter_form.cleaned_data['start']
            end = filter_form.cleaned_data['end']
            ground_station = filter_form.cleaned_data['ground_station']
            transmitter = filter_form.cleaned_data['transmitter']
            sat_id = filter_form.cleaned_data['sat_id']

            obs_filter['dates'] = False
            if start and end:  # Either give both dates or ignore if only one is given
                start = datetime.strptime(start, '%Y/%m/%d %H:%M').strftime('%Y-%m-%d %H:%M')
                end = (datetime.strptime(end, '%Y/%m/%d %H:%M') +
                       timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
                obs_filter['start'] = start
                obs_filter['end'] = end
                obs_filter['dates'] = True

            obs_filter['exists'] = True
            if sat_id:
                obs_filter['sat_id'] = sat_id
                obs_filter['transmitter'] = transmitter  # Add transmitter only if sat_id exists
            if ground_station:
                obs_filter['ground_station'] = ground_station
        else:
            obs_filter['exists'] = False

    return render(
        request, 'base/observation_new.html', {
            'satellites': satellites.values(),
            'obs_filter': obs_filter,
            'date_min_start': settings.OBSERVATION_DATE_MIN_START,
            'date_min_end': settings.OBSERVATION_DATE_MIN_END,
            'date_max_range': settings.OBSERVATION_DATE_MAX_RANGE,
            'warn_min_obs': settings.OBSERVATION_WARN_MIN_OBS,
            'obs_min_duration': settings.OBSERVATION_DURATION_MIN,
            'split': {
                'duration': settings.OBSERVATION_SPLIT_DURATION,
                'break': settings.OBSERVATION_SPLIT_BREAK_DURATION
            }
        }
    )


def prediction_windows_parse_parameters(request):
    """ Parse HTTP parameters with defaults"""
    params = {
        'sat_id': request.POST['satellite'],
        'transmitter': request.POST['transmitter'],
        'start': make_aware(
            datetime.strptime(request.POST['start'], '%Y-%m-%d %H:%M'), timezone.utc
        ),
        'end': make_aware(datetime.strptime(request.POST['end'], '%Y-%m-%d %H:%M'), timezone.utc),
        'station_ids': request.POST.getlist('stations[]', []),
        'min_horizon': request.POST.get('min_horizon', None),
        'split_duration': int(
            request.POST.get('split_duration', settings.OBSERVATION_SPLIT_DURATION)
        ),
        'break_duration': int(
            request.POST.get('break_duration', settings.OBSERVATION_SPLIT_BREAK_DURATION)
        ),
        'overlapped': int(request.POST.get('overlapped', 0)),
        'center_frequency': int(request.POST.get('center_frequency', 0)) or None
    }

    if params['split_duration'] < 0 or params['break_duration'] < 0:
        raise ValueError('Please re-check your request parameters.')
    if not over_min_duration(params['split_duration']):
        raise ValueError(
            'Split duration should be over minimum observation duration({} seconds)'.format(
                settings.OBSERVATION_DURATION_MIN
            )
        )

    return params


def get_tle_set_if_available(sat_id):
    """ Returns TLE set for Satellite ID if exists or raises an exception"""
    tle_set = get_tle_set_by_sat_id(sat_id)
    if tle_set:
        return tle_set[0]
    raise ValueError('No TLEs for this satellite yet.')


@ajax_required
def prediction_windows(request):
    """Calculates and returns passes of satellites over stations"""

    try:
        # Parse and validate parameters
        params = prediction_windows_parse_parameters(request)
        sat_id = params['sat_id']
        # Check the selected satellite exists and is alive
        satellite = get_satellites()[sat_id]
        if not satellite or satellite['status'] != 'alive':
            raise ValueError('You should select a Satellite first.')
        # Get TLE set if there is one available for this satellite
        tle = get_tle_set_if_available(satellite['sat_id'])

        # Check the selected transmitter exists, and if yes,
        # store this transmitter in the downlink variable
        transmitter = get_transmitter_by_uuid(params['transmitter'])
        if not transmitter:
            raise ValueError('You should select a valid Transmitter.')
        if params['center_frequency']:
            if not is_frequency_in_transmitter_range(params['center_frequency'], transmitter[0]):
                raise OutOfRangeError('The center frequency is out of the transmitter\'s range.')
            downlink = params['center_frequency']
        if (transmitter[0]["type"] == "Transponder" or transmitter[0]["type"]
                == "Range transmitter") and not params['center_frequency']:
            downlink = (transmitter[0]['downlink_high'] + transmitter[0]['downlink_low']) // 2
        else:
            downlink = transmitter[0]['downlink_low']
    except (ValueError, DBConnectionError, OutOfRangeError) as error:
        return JsonResponse([{'error': str(error)}], safe=False)

    # Fetch all available ground stations
    stations = Station.objects.filter(
        status__gt=0, alt__isnull=False, lat__isnull=False, lng__isnull=False
    ).prefetch_related(
        Prefetch(
            'observations',
            queryset=Observation.objects.filter(end__gt=now()),
            to_attr='scheduled_obs'
        ), 'antennas', 'antennas__frequency_ranges'
    )

    data = []
    if params['station_ids'] and params['station_ids'] != ['']:
        # Filter ground stations based on the given selection
        stations = stations.filter(id__in=params['station_ids'])
        if not stations:
            if len(params['station_ids']) == 1:
                data = [
                    {
                        'error': (
                            'Station is offline, it doesn\'t exist or'
                            ' it hasn\'t defined location.'
                        )
                    }
                ]
            else:
                data = [
                    {
                        'error': (
                            'Stations are offline, they don\'t exist or'
                            ' they haven\'t defined location.'
                        )
                    }
                ]
            return JsonResponse(data, safe=False)

    available_stations = get_available_stations(stations, downlink, request.user, satellite)

    passes_found = defaultdict(list)
    for station in available_stations:
        station_passes, station_windows = predict_available_observation_windows(
            station, params['min_horizon'], params['overlapped'], tle, params['start'],
            params['end'], {
                'split': params['split_duration'],
                'break': params['break_duration']
            }
        )
        passes_found[station.id] = station_passes
        if station_windows:
            data.append(
                {
                    'id': station.id,
                    'name': station.name,
                    'status': station.status,
                    'lng': station.lng,
                    'lat': station.lat,
                    'alt': station.alt,
                    'window': station_windows
                }
            )

    if not data:
        error_message = 'Satellite is always below horizon or ' \
                        'no free observation time available on visible stations.'
        error_details = {}
        for station in available_stations:
            if station.id not in passes_found:
                error_details[station.id] = 'Satellite is always above or below horizon.\n'
            else:
                error_details[station.id] = 'No free observation time during passes available.\n'

        data = [
            {
                'error': error_message,
                'error_details': error_details,
                'passes_found': passes_found
            }
        ]

    return JsonResponse(data, safe=False)


@ajax_required
def pass_predictions(request, station_id):
    """Endpoint for pass predictions"""
    station = get_object_or_404(
        Station.objects.prefetch_related(
            Prefetch(
                'observations',
                queryset=Observation.objects.filter(end__gt=now()),
                to_attr='scheduled_obs'
            ), 'antennas', 'antennas__frequency_ranges'
        ),
        id=station_id,
        alt__isnull=False,
        lat__isnull=False,
        lng__isnull=False
    )

    satellites = [
        sat for sat in get_satellites().values()
        if sat['status'] == 'alive' and 'merged_into' not in sat
    ]
    if not schedule_station_violators_perms(request.user, station):
        satellites = [sat for sat in satellites if not sat['is_frequency_violator']]

    nextpasses = []
    start = make_aware(datetime.now(), timezone.utc)
    end = make_aware(datetime.now() + timedelta(hours=settings.STATION_UPCOMING_END), timezone.utc)
    observation_min_start = (
        datetime.now() + timedelta(minutes=settings.OBSERVATION_DATE_MIN_START)
    ).strftime("%Y-%m-%d %H:%M:%S.%f")
    observation_min_end = (
        datetime.now() + timedelta(minutes=settings.OBSERVATION_DATE_MIN_START) +
        timedelta(seconds=settings.OBSERVATION_DURATION_MIN)
    ).strftime("%Y-%m-%d %H:%M:%S.%f")

    available_transmitter_and_tle_sets = True
    try:
        all_transmitters = get_transmitters()
        all_tle_sets = get_tle_sets()
    except DBConnectionError:
        available_transmitter_and_tle_sets = False

    if available_transmitter_and_tle_sets:
        for satellite in satellites:
            # look for a match between transmitters from the satellite and
            # ground station antenna frequency capabilities
            sat_id = satellite['sat_id']
            transmitters = [
                t for t in all_transmitters
                if t['sat_id'] == sat_id and t["status"] in ("active", "inactive")
                and is_transmitter_in_station_range(t, station)  # noqa: W503
            ]
            tle = next((tle_set for tle_set in all_tle_sets if tle_set["sat_id"] == sat_id), None)

            if not transmitters or not tle:
                continue

            _, station_windows = predict_available_observation_windows(
                station, None, 2, tle, start, end, {
                    'split': settings.OBSERVATION_SPLIT_DURATION,
                    'break': settings.OBSERVATION_SPLIT_BREAK_DURATION
                }
            )

            if station_windows:
                satellite_stats = get_satellite_stats_by_transmitter_list(transmitters)
                for window in station_windows:
                    valid = window['start'] > observation_min_start and window['valid_duration']
                    if not valid:
                        valid = window['end'] > observation_min_end and window['valid_duration']
                    window_start = datetime.strptime(window['start'], '%Y-%m-%d %H:%M:%S.%f')
                    window_end = datetime.strptime(window['end'], '%Y-%m-%d %H:%M:%S.%f')
                    sat_pass = {
                        'name': str(satellite['name']),
                        'success_rate': str(satellite_stats['success_rate']),
                        'bad_rate': str(satellite_stats['bad_rate']),
                        'unknown_rate': str(satellite_stats['unknown_rate']),
                        'future_rate': str(satellite_stats['future_rate']),
                        'total_count': str(satellite_stats['total_count']),
                        'good_count': str(satellite_stats['good_count']),
                        'bad_count': str(satellite_stats['bad_count']),
                        'unknown_count': str(satellite_stats['unknown_count']),
                        'future_count': str(satellite_stats['future_count']),
                        'norad_cat_id': str(satellite['norad_cat_id']),
                        'sat_id': str(satellite['sat_id']),
                        'tle1': window['tle1'],
                        'tle2': window['tle2'],
                        'tr': window_start,  # Rise time
                        'azr': window['az_start'],  # Rise Azimuth
                        'altt': window['elev_max'],  # Max altitude
                        'ts': window_end,  # Set time
                        'azs': window['az_end'],  # Set azimuth
                        'valid': valid,
                        'overlapped': window['overlapped'],
                        'overlap_ratio': window['overlap_ratio']
                    }
                    nextpasses.append(sat_pass)

    data = {
        'id': station_id,
        'nextpasses': sorted(nextpasses, key=itemgetter('tr')),
        'ground_station': {
            'lng': str(station.lng),
            'lat': str(station.lat),
            'alt': station.alt
        }
    }

    return JsonResponse(data, safe=False)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance based on the given coordinates"""
    earth_radius_km = 6371  # Mean radius of the Earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius_km * c

    return distance


@ajax_required
def scheduling_stations(request):  # pylint: disable=too-many-return-statements
    """Returns json with stations on which user has permissions to schedule"""
    uuid = request.POST.get('transmitter', None)
    lat = request.POST.get('latitude', None)
    lng = request.POST.get('longitude', None)
    radius = request.POST.get('radius', None)
    if uuid is None:
        data = [{'error': 'You should select a Transmitter.'}]
        return JsonResponse(data, safe=False)
    try:
        transmitter = get_transmitter_by_uuid(uuid)
        if not transmitter:
            data = [{'error': 'You should select a valid Transmitter.'}]
            return JsonResponse(data, safe=False)
        downlink = transmitter[0]['downlink_low']
        if downlink is None:
            data = [{'error': 'You should select a valid Transmitter.'}]
            return JsonResponse(data, safe=False)
        satellite = get_satellites()[transmitter[0]['sat_id']]
        if not satellite:
            raise ValueError('Unable to find satellite for the selected transmitter.')
    except (DBConnectionError, ValueError) as error:
        data = [{'error': str(error)}]
        return JsonResponse(data, safe=False)

    stations = Station.objects.filter(
        status__gt=0, alt__isnull=False, lat__isnull=False, lng__isnull=False
    ).prefetch_related('antennas', 'antennas__frequency_ranges')

    center_frequency = request.POST.get('center_frequency', downlink)
    try:
        center_frequency = int(float(center_frequency))
    except ValueError:
        data = {'error': 'Center frequency value is invalid'}
        return JsonResponse(data, safe=False)
    if lat is not None and lng is not None and radius is not None:
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
        except ValueError:
            data = {'error': 'Latitude, longitude, or radius value is invalid'}
            return JsonResponse(data, safe=False)

        available_stations = get_available_stations(
            stations, center_frequency, request.user, satellite
        )

        filtered_stations = []
        for station in available_stations:
            station_lat = round(station.lat, 3)
            station_lng = round(station.lng, 3)
            distance = calculate_distance(lat, lng, station_lat, station_lng)
            if distance <= radius:
                filtered_stations.append(station)

        available_stations = filtered_stations
    else:
        available_stations = get_available_stations(
            stations, center_frequency, request.user, satellite
        )
    data = {
        'stations': StationSerializer(available_stations, many=True).data,
    }

    return JsonResponse(data, safe=False)


@require_POST
def transmitters_view(request):
    """Returns a transmitter JSON object with information and statistics"""
    sat_id = request.POST.get('satellite', None)
    station_id = request.POST.get('station_id', None)
    try:
        if sat_id:
            satellite = get_satellites()[sat_id]
        else:
            data = {'error': 'Satellite not provided.'}
            return JsonResponse(data, safe=False)
    except KeyError:
        data = {'error': 'Unable to find that satellite.'}
        return JsonResponse(data, safe=False)

    try:
        transmitters = get_transmitters_by_sat_id(sat_id)
    except DBConnectionError:
        data = [
            {
                'error': 'Could\'t reach the SatNOGS DB service, which is needed to provide the '
                'latest list of transmitters. Please try again in a few moments.'
            }
        ]
        return JsonResponse(data, safe=False)

    transmitters = [
        t for t in transmitters if t["status"] != "invalid" and t['downlink_low'] is not None
    ]
    if station_id:
        supported_transmitters = []
        station = Station.objects.prefetch_related('antennas', 'antennas__frequency_ranges').get(
            id=station_id
        )
        if satellite['is_frequency_violator'] and not schedule_station_violators_perms(
                request.user, station):
            data = [{'error': 'No permission to schedule this satellite on this station.'}]
            return JsonResponse(data, safe=False)
        for transmitter in transmitters:
            transmitter_supported = is_transmitter_in_station_range(transmitter, station)
            if transmitter_supported:
                supported_transmitters.append(transmitter)
        transmitters = supported_transmitters

    data = {
        "transmitters_active": get_transmitters_with_stats(
            [t for t in transmitters if t["status"] == "active" and not t["unconfirmed"]]
        ),
        "transmitters_inactive": get_transmitters_with_stats(
            [t for t in transmitters if t["status"] == "inactive" and not t["unconfirmed"]]
        ),
        "transmitters_unconfirmed": get_transmitters_with_stats(
            [t for t in transmitters if t["unconfirmed"]]
        ),
    }

    if not any((data['transmitters_active'], data['transmitters_inactive'],
                data['transmitters_unconfirmed'])):
        data = []
        return JsonResponse(data, safe=False)

    return JsonResponse(data, safe=False)
