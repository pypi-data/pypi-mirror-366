"""Django base views for SatNOGS Network"""
from datetime import datetime
from urllib.parse import urlparse

import ephem
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now, timedelta
from django.views.generic import ListView

from network.base.cache import get_satellite_stats, get_satellites
from network.base.db_api import DBConnectionError, get_transmitters_by_sat_id
from network.base.decorators import ajax_required
from network.base.models import Observation, Station
from network.base.perms import delete_perms, schedule_perms, vet_perms
from network.base.rating_tasks import rate_observation
from network.base.stats import get_transmitters_with_stats
from network.base.tasks import get_and_refresh_transmitters_with_stats_cache
from network.base.utils import community_get_discussion_details
from network.users.models import User


def get_one_day_ago():
    """Helper function to get the datetime 24 hours before as formatted string"""
    return (now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")


class ObservationListBaseView(ListView):
    """
    Base class for displaying a list of observations
    """
    model = Observation
    context_object_name = "observations"
    paginate_by = settings.ITEMS_PER_PAGE
    template_name = 'base/observations.html'
    str_filters = [
        'sat_id', 'observer', 'station', 'start', 'end', 'transmitter_mode', 'transmitter_uuid',
        'experimental_observation'
    ]
    flag_filters = ['bad', 'good', 'unknown', 'future', 'failed']
    filtered = None
    more_filtered = None  # Filtered by filters hidden by default
    filter_params = {}
    filter_errors = []

    def parse_filter_params(self):
        """
        Get the parsed filter parameters from the HTTP GET parameters

        - str_filters vaues are str, default to ''
        - flag_filters values are Boolean, default to False

        Returns a dict, filter_name is the key, the parsed parameter is the value.
        """
        self.filter_params = {}
        self.filter_errors = []
        for parameter_name in self.str_filters:
            self.filter_params[parameter_name] = self.request.GET.get(parameter_name, '')
            if parameter_name in {'sat_id', 'observer', 'station'
                                  } and self.filter_params[parameter_name] != '':
                filter_param = self.filter_params[parameter_name]
                if parameter_name != 'sat_id':
                    try:
                        filter_param = int(filter_param)
                        if filter_param < 0:
                            self.filter_errors.append(
                                'Filter "' + parameter_name +
                                '" is ignored due to error: Value cannot be less than 0'
                            )
                            filter_param = ''
                    except ValueError:
                        self.filter_errors.append(
                            'Filter "' + parameter_name +
                            '" is ignored due to error: Invalid value'
                        )
                        filter_param = ''
                    self.filter_params[parameter_name] = filter_param

        for parameter_name in self.flag_filters:
            param = self.request.GET.get(parameter_name, 1)
            self.filter_params[parameter_name] = param != '0'

        if self.filter_errors:
            for error in self.filter_errors:
                messages.error(self.request, error)

    def get_queryset(self):
        """
        Optionally filter based on sat_id get argument
        Optionally filter based on future/good/bad/unknown/failed
        """
        self.parse_filter_params()

        results = self.request.GET.getlist('results')
        rated = self.request.GET.getlist('rated')

        observations = Observation.objects.prefetch_related(
            'demoddata', 'author', 'ground_station'
        )

        # Mapping between the HTTP POST parameters and the fiter keys
        parameter_filter_mapping = {
            'sat_id': 'sat_id',
            'observer': 'author',
            'station': 'ground_station_id',
            'start': 'start__gt',
            'end': 'end__lt',
            'transmitter_mode': 'transmitter_mode__icontains',
            'transmitter_uuid': 'transmitter_uuid__icontains',
            'experimental_observation': 'experimental'
        }

        # Create observations filter based on the received HTTP POST parameters
        filter_dict = {}
        for parameter_key, filter_key in parameter_filter_mapping.items():
            if self.filter_params[parameter_key] == '':
                continue

            filter_dict[filter_key] = self.filter_params[parameter_key]

        self.filtered = bool(
            (
                not all(
                    [
                        self.filter_params['bad'], self.filter_params['good'],
                        self.filter_params['unknown'], self.filter_params['future'],
                        self.filter_params['failed']
                    ]
                )
            ) or results or rated or filter_dict
        )

        # If user has not filtered the results, display the observations of the last 24 hours
        if not self.filtered:
            filter_dict["start__gt"] = get_one_day_ago()

        # If the user has used the extra filters, display the extra filter section expaned
        self.more_filtered = (
            results or rated or filter_dict.get('author') or filter_dict.get('ground_station_id')
            or filter_dict.get('transmitter_mode__icontains')
            or filter_dict.get('transmitter_uuid__icontains') or filter_dict.get('experimental')
        )

        observations = observations.filter(**filter_dict)

        if not self.filter_params['failed']:
            observations = observations.exclude(status__lt=-100)
        if not self.filter_params['bad']:
            observations = observations.exclude(status__range=(-100, -1))
        if not self.filter_params['unknown']:
            observations = observations.exclude(status__range=(0, 99), end__lte=now())
        if not self.filter_params['future']:
            observations = observations.exclude(end__gt=now())
        if not self.filter_params['good']:
            observations = observations.exclude(status__gte=100)

        if results:
            if 'w0' in results:
                observations = observations.filter(waterfall='')
            elif 'w1' in results:
                observations = observations.exclude(waterfall='')
            if 'a0' in results:
                observations = observations.filter(archived=False, payload='')
            elif 'a1' in results:
                observations = observations.exclude(archived=False, payload='')
            if 'd0' in results:
                observations = observations.filter(demoddata__demodulated_data__isnull=True)
            elif 'd1' in results:
                observations = observations.exclude(demoddata__demodulated_data__isnull=True)
            if 'i1' in results:
                observations = observations.filter(demoddata__is_image=True)

        if rated:
            if 'rwu' in rated:
                observations = observations.filter(waterfall_status__isnull=True
                                                   ).exclude(waterfall='')
            elif 'rw1' in rated:
                observations = observations.filter(waterfall_status=True)
            elif 'rw0' in rated:
                observations = observations.filter(waterfall_status=False)

        return observations

    def get_context_data(self, **kwargs):  # pylint: disable=W0221
        """
        Need to add a list of satellites to the context for the template
        """
        context = super().get_context_data(**kwargs)
        context.update(self.filter_params)
        context['satellites'] = get_satellites()
        context['authors'] = User.objects.filter(is_observer=True
                                                 ).order_by('first_name', 'last_name', 'username')
        context['stations'] = Station.objects.all().order_by('id')
        start = get_one_day_ago() if not self.filtered else self.request.GET.get('start')
        end = self.request.GET.get('end', None)
        transmitter_uuid = self.request.GET.get('transmitter_uuid', None)
        context['display_no_filter_warning'] = not self.filtered
        context['results'] = self.request.GET.getlist('results')
        context['rated'] = self.request.GET.getlist('rated')
        context['transmitter_mode'] = self.request.GET.get('transmitter_mode', None)
        cached_transmitters_with_stats = cache.get('transmitters-with-stats')
        context['transmitter_uuids_info'] = cached_transmitters_with_stats.values(
        ) if cached_transmitters_with_stats else get_and_refresh_transmitters_with_stats_cache(
            in_list_form=True
        )
        context['more_filtered'] = bool(self.more_filtered)
        if start is not None and start != '':
            context['start'] = start
        if end is not None and end != '':
            context['end'] = end
        if 'scheduled' in self.request.session:
            context['scheduled'] = self.request.session['scheduled']
            try:
                del self.request.session['scheduled']
            except KeyError:
                pass
        if transmitter_uuid:
            context['transmitters_uuid'] = transmitter_uuid
        context['can_schedule'] = schedule_perms(self.request.user)

        url_query = urlparse(self.request.build_absolute_uri()).query
        if not url_query:
            vet_url_query = 'results=w1&start=' + (now() -
                                                   timedelta(days=2)).strftime("%Y-%m-%d+%H:%M")
        else:
            vet_url_query = url_query.replace('results=w0', 'results=w1')
            if vet_url_query == url_query:  # no 'results' parameter was given
                vet_url_query += '&results=w1'
        if 'future=0' not in vet_url_query:
            vet_url_query += '&future=0'
        context['vet_url_query'] = vet_url_query
        return context


class ObservationListView(ObservationListBaseView):
    """
    Displays a list of observations with pagination
    """

    def get_queryset(self):
        observations = super().get_queryset()
        if (obs_count := observations.count()) > settings.OBSERVATION_MAX_QUERY_COUNT:
            observations = observations[:settings.OBSERVATION_MAX_QUERY_COUNT]
            messages.error(
                self.request, 'Search too wide, ignored ' +
                str(obs_count - settings.OBSERVATION_MAX_QUERY_COUNT) +
                ' observations. Please change the filters below to narrow down the search results.'
            )
        return observations


def get_observation_demoddata_details(observation, demoddata, demoddata_count):
    """Returns details about the Demoddata of the observation"""
    demoddata_details = []
    show_hex_to_ascii_button = False
    if demoddata_count:
        if observation.transmitter_mode == 'CW':
            content_type = 'text'
        else:
            content_type = 'binary'

        for datum in demoddata:
            if datum.is_image:
                if datum.demodulated_data:
                    demoddata_details.append(
                        {
                            'url': datum.demodulated_data.url,
                            'name': datum.demodulated_data.name,
                            'type': 'image'
                        }
                    )
            else:
                show_hex_to_ascii_button = True
                if datum.demodulated_data:
                    demoddata_details.append(
                        {
                            'url': datum.demodulated_data.url,
                            'name': datum.demodulated_data.name,
                            'type': content_type
                        }
                    )
        demoddata_details = sorted(demoddata_details, key=lambda d: d['name'])
    return demoddata_details, show_hex_to_ascii_button


class VetObservationsChunkListView(LoginRequiredMixin, ListView):
    """View for getting the observations to vet as HTML snippets"""

    def get_queryset(self):
        ids = [int(obs_id) for obs_id in self.request.GET.get('obs_ids').split(',')]
        return Observation.objects.filter(id__in=ids).annotate(demoddata_count=Count('demoddata')
                                                               ).order_by('-start', '-end')

    def get(self, request, *args, **kwargs):
        observations = self.get_queryset()
        obs_html = []
        satellites = get_satellites()
        for obs in observations:
            demoddata_details = get_observation_demoddata_details(
                obs, obs.demoddata.all(), obs.demoddata_count
            )

            if obs.is_future:
                can_vet = False
            else:
                can_vet = True

            context = {
                "tle_datetime": calculate_datetime_from_tle(obs.id),
                "observation": obs,
                'satellite': satellites[obs.sat_id],
                "from_vetting": True,
                "can_vet": can_vet,
                "demoddata_count": obs.demoddata_count,
                "demoddata_details": demoddata_details[0],
                "show_hex_to_ascii_button": demoddata_details[1],
            }
            context.update(csrf(request))

            rendered = render_to_string("includes/observation_detail.html", context)
            obs_html.append(rendered)

        return JsonResponse(obs_html, safe=False)


class VetObservationsView(LoginRequiredMixin, ObservationListBaseView):
    """View for vetting multiple observations"""
    template_name = 'base/vet_observation_container.html'
    object_list = []

    def get_queryset(self):
        """ Limits the queryset to those observations that the user can vet.
            works, similar to 'vet_perms' function.
        """
        queryset = super().get_queryset()
        if not (self.request.user.is_superuser
                or self.request.user.groups.filter(name='Moderators').exists()
                or self.request.user.has_perm('base.can_vet')
                or self.request.user.ground_stations.filter(status=2).exists()):
            queryset = queryset.filter(
                Q(author=self.request.user)
                | Q(ground_station__isnull=False, ground_station__owner=self.request.user)
            )

        if (obs_count := queryset.count()) > settings.OBSERVATION_MAX_QUERY_COUNT:
            queryset = queryset[:settings.OBSERVATION_MAX_QUERY_COUNT]
            parsed_url = urlparse(self.request.build_absolute_uri())
            observation_search_url = reverse('base:observations_list') + '?' + parsed_url.query
            messages.error(
                self.request, 'Search too wide, ignored ' +
                str(obs_count - settings.OBSERVATION_MAX_QUERY_COUNT) +
                ' observations. Please change the filters in the <a href="' +
                observation_search_url +
                '">observation page</a> to narrow down the search results.'
            )
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        ids = queryset.values_list('id', flat=True)
        context = {}
        parsed_url = urlparse(request.build_absolute_uri())
        context["query_url"] = reverse('base:vet_observations_chunks')
        context["obs_ids"] = list(ids)
        context["observation_search_url"
                ] = reverse('base:observations_list') + '?' + parsed_url.query
        context["page_size"] = settings.VET_ITEMS_PER_CHUNK
        context["chunks_buffer_headstart"] = settings.CHUNKS_BUFFER_HEADSTART
        context["fwd_buffer_chunks"] = settings.FWD_BUFFER_CHUNKS
        context["bwd_buffer_chunks"] = settings.BWD_BUFFER_CHUNKS
        return self.render_to_response(context)


def observation_view(request, observation_id):
    """View for single observation page."""
    observation = get_object_or_404(Observation, id=observation_id)

    if observation.is_future:
        can_vet = False
    else:
        can_vet = vet_perms(request.user, observation)

    can_delete = delete_perms(request.user, observation)

    if observation.has_audio and not observation.audio_url:
        messages.error(
            request, 'Audio file is not currently available,'
            ' if the problem persists please contact an administrator.'
        )

    has_comments = False
    discuss_url = ''
    discuss_slug = ''
    satellite = get_satellites()[observation.sat_id]
    if settings.ENVIRONMENT == 'production':
        discussion_details = community_get_discussion_details(
            observation.id, satellite['name'], satellite['norad_cat_id'],
            'https:%2F%2F{}{}'.format(request.get_host(), request.path)
        )
        has_comments = discussion_details['has_comments']
        discuss_url = discussion_details['url']
        discuss_slug = discussion_details['slug']

    demoddata_count = observation.demoddata.count()
    demoddata = observation.demoddata.all()
    demoddata_details, show_hex_to_ascii_button = get_observation_demoddata_details(
        observation, demoddata, demoddata_count
    )

    return render(
        request, 'base/observation_view.html', {
            'observation': observation,
            'satellite': satellite,
            'tle_datetime': calculate_datetime_from_tle(observation.id),
            'demoddata_count': demoddata_count,
            'demoddata_details': demoddata_details,
            'show_hex_to_ascii_button': show_hex_to_ascii_button,
            'can_vet': can_vet,
            'can_delete': can_delete,
            'has_comments': has_comments,
            'discuss_url': discuss_url,
            'discuss_slug': discuss_slug
        }
    )


def calculate_datetime_from_tle(observation_id):
    """
    Converts TLE epoch to datetime object.
    :returns: timezone-aware datetime or None: The epoch for the given TLE
    """
    observation = get_object_or_404(Observation, id=observation_id)

    try:
        # Parse the TLE data to create an ephem EarthSatellite object
        tle = ephem.readtle(observation.tle_line_0, observation.tle_line_1, observation.tle_line_2)

        # Get the TLE epoch time as an ephem.Date object
        epoch_date = tle.epoch

        # Convert the epoch time to a datetime object
        epoch_datetime = datetime.strptime(str(epoch_date), "%Y/%m/%d %H:%M:%S")

        # Make epoch_datetime timezone-aware
        tle_datetime = timezone.make_aware(epoch_datetime)
    except ValueError:
        tle_datetime = None
    return tle_datetime


@login_required
def observation_delete(request, observation_id):
    """View for deleting observation."""
    observation = get_object_or_404(Observation, id=observation_id)
    can_delete = delete_perms(request.user, observation)
    if can_delete:
        observation.delete()
        messages.success(request, 'Observation deleted successfully.')
    else:
        messages.error(request, 'Permission denied.')
    return redirect(reverse('base:observations_list'))


@login_required
@ajax_required
def waterfall_vet(request, observation_id):
    """Handles request for vetting a waterfall"""
    try:
        observation = Observation.objects.get(id=observation_id)
    except Observation.DoesNotExist:
        data = {'error': 'Observation does not exist.'}
        return JsonResponse(data, safe=False)

    status = request.POST.get('status', None)
    if observation.is_future:
        can_vet = False
    else:
        can_vet = vet_perms(request.user, observation)

    if not can_vet:
        data = {'error': 'Permission denied.'}
        return JsonResponse(data, safe=False)
    if not observation.has_waterfall:
        data = {'error': 'Observation without waterfall.'}
        return JsonResponse(data, safe=False)

    if status not in ['with-signal', 'without-signal', 'unknown']:
        data = {
            'error': 'Invalid status, select one of \'with-signal\', \'without-signal\' and '
            '\'unknown\'.'
        }
        return JsonResponse(data, safe=False)

    if status == 'with-signal':
        observation.waterfall_status = True
    elif status == 'without-signal':
        observation.waterfall_status = False
    elif status == 'unknown':
        observation.waterfall_status = None

    observation.waterfall_status_user = request.user
    observation.waterfall_status_datetime = now()
    observation.save(
        update_fields=['waterfall_status', 'waterfall_status_user', 'waterfall_status_datetime']
    )
    (observation_status, observation_status_badge, observation_status_display
     ) = rate_observation(observation.id, 'set_waterfall_status', observation.waterfall_status)
    data = {
        'waterfall_status_user': observation.waterfall_status_user.displayname,
        'waterfall_status_datetime': observation.waterfall_status_datetime.
        strftime('%Y-%m-%d %H:%M:%S'),
        'waterfall_status': observation.waterfall_status,
        'waterfall_status_badge': observation.waterfall_status_badge,
        'waterfall_status_display': observation.waterfall_status_display,
        'status': observation_status,
        'status_badge': observation_status_badge,
        'status_display': observation_status_display,
    }
    return JsonResponse(data, safe=False)


def satellite_view(request, sat_id):
    """Returns a satellite JSON object with information and statistics"""

    try:
        satellite = get_satellites()[sat_id]
    except KeyError:
        data = {'error': 'Unable to find that satellite.'}
        return JsonResponse(data, safe=False)

    try:
        transmitters = get_transmitters_by_sat_id(sat_id)
    except (DBConnectionError, ValueError) as error:
        data = [{'error': str(error)}]
        return JsonResponse(data, safe=False)
    satellite_stats = get_satellite_stats().get(satellite['sat_id']) or {
        'unknown_rate': 0,
        'future_rate': 0,
        'success_rate': 0,
        'bad_rate': 0,
        'total_count': 0,
        'unknown_count': 0,
        'future_count': 0,
        'good_count': 0,
        'bad_count': 0,
    }

    data = {
        'id': sat_id,
        'norad': satellite['norad_cat_id'],
        'name': satellite['name'],
        'names': satellite['names'],
        'image': satellite['image'],
        'success_rate': satellite_stats['success_rate'],
        'good_count': satellite_stats['good_count'],
        'bad_count': satellite_stats['bad_count'],
        'unknown_count': satellite_stats['unknown_count'],
        'future_count': satellite_stats['future_count'],
        'total_count': satellite_stats['total_count'],
        'transmitters': get_transmitters_with_stats(transmitters)
    }

    return JsonResponse(data, safe=False)
