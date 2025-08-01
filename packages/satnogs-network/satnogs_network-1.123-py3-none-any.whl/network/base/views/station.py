"""Django base views for SatNOGS Network"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import ListView
from jsonschema import Draft202012Validator, ValidationError

from network.base.decorators import ajax_required
from network.base.forms import AntennaInlineFormSet, FrequencyRangeInlineFormSet, StationForm, \
    StationRegistrationForm
from network.base.models import AntennaType, Station, StationConfiguration, \
    StationConfigurationSchema, StationStatusLog, StationType
from network.base.perms import modify_delete_station_perms, schedule_station_perms
from network.base.serializers import StationSerializer
from network.base.utils import populate_formset_error_messages


@ajax_required
def station_all_view(request):
    """Return JSON with all stations"""
    stations = Station.objects.all()
    data = StationSerializer(stations, many=True).data
    return JsonResponse(data, safe=False)


class StationListView(ListView):
    """Displays a list of stations with pagination"""
    model = Station
    context_object_name = "stations"
    paginate_by = settings.ITEMS_PER_PAGE
    template_name = "base/stations.html"
    flag_filters = ['online', 'testing', 'offline', 'future']
    freq_filters = ['freq']
    is_filtered = False
    freq_filter_errors = []

    def get_filter_params(self):
        """
        Get the parsed filter parameters from the HTTP GET parameters
        """

        filter_params = {}
        for param_name in self.flag_filters:
            param_val = self.request.GET.get(param_name, 1)
            if param_val != '0':
                filter_params[param_name] = True
            else:
                filter_params[param_name] = False
                self.is_filtered = True
        self.freq_filter_errors = []
        filter_freq = self.request.GET.get('freq', None)
        if filter_freq:
            self.is_filtered = True
            try:
                filter_freq = int(float(filter_freq))
            except ValueError:
                self.freq_filter_errors.append("Frequency: Invalid value")
                return filter_params
            if filter_freq < 0:
                self.freq_filter_errors.append('Frequency: Value cannot be less than 0')
            filter_params['freq'] = filter_freq
        return filter_params

    def get_queryset(self):
        stations = Station.objects.select_related('owner').prefetch_related(
            'antennas', 'antennas__antenna_type', 'antennas__frequency_ranges'
        )

        filter_params = self.get_filter_params()

        if not filter_params["online"]:
            stations = stations.exclude(status=2)
        if not filter_params["testing"]:
            stations = stations.exclude(status=1)
        if not filter_params["offline"]:
            stations = stations.exclude(Q(status=0) & Q(last_seen__isnull=False))
        if not filter_params["future"]:
            stations = stations.exclude(last_seen__isnull=True)

        freq = filter_params.get("freq", None)
        if freq:
            freq_filter = Q(antennas__frequency_ranges__min_frequency__lte=freq)
            freq_filter &= Q(antennas__frequency_ranges__max_frequency__gte=freq)
            stations = stations.filter(freq_filter)
        return stations

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_filtered"] = self.is_filtered
        context.update(self.get_filter_params())
        context["mapbox_id"] = settings.MAPBOX_MAP_ID
        context["mapbox_token"] = settings.MAPBOX_TOKEN
        context["freq_filter_errors"] = self.freq_filter_errors

        return context


def station_view(request, station_id):
    """View for single station page."""
    station = get_object_or_404(
        Station.objects.prefetch_related(
            'owner', 'antennas', 'antennas__antenna_type', 'antennas__frequency_ranges'
        ),
        id=station_id
    )
    station_log = StationStatusLog.objects.filter(station=station)

    can_schedule = schedule_station_perms(request.user, station)
    can_modify_delete_station = modify_delete_station_perms(request.user, station)

    # Calculate uptime
    uptime_since = None
    if station_log:
        latest_entry = station_log[0]
        if latest_entry.status > 0:
            for entry in station_log:
                if entry.status == 0:
                    break
                uptime_since = entry.changed

    if request.user.is_authenticated:
        if request.user == station.owner:
            wiki_help = (
                '<a href="{0}" target="_blank" class="wiki-help"><span class="bi '
                'bi-question-circle" aria-hidden="true"></span>'
                '</a>'.format(settings.WIKI_STATION_URL)
            )
            if station.is_offline:
                messages.error(
                    request, (
                        'Your Station is offline. You should make '
                        'sure it can successfully connect to the Network API. '
                        '{0}'.format(wiki_help)
                    )
                )
            if station.is_testing:
                messages.warning(
                    request, (
                        'Your Station is in Testing mode. Once you are sure '
                        'it returns good observations you can put it online. '
                        '{0}'.format(wiki_help)
                    )
                )

    return render(
        request, 'base/station_view.html', {
            'station': station,
            'mapbox_id': settings.MAPBOX_MAP_ID,
            'mapbox_token': settings.MAPBOX_TOKEN,
            'can_schedule': can_schedule,
            'can_modify_delete_station': can_modify_delete_station,
            'uptime_since': uptime_since,
            'station_log': station_log
        }
    )


@login_required
def station_delete(request, station_id):
    """View for deleting a station."""
    username = request.user
    station = get_object_or_404(Station, id=station_id, owner=request.user)
    station.delete()
    messages.success(request, 'Ground Station deleted successfully.')
    return redirect(reverse('users:view_user', kwargs={'username': username}))


@login_required
def station_delete_future_observations(request, station_id):
    """View for deleting all future observations of a given station."""
    return redirect(reverse('base:station_view', kwargs={'station_id': station_id}))
    # station = get_object_or_404(Station, id=station_id)

    # if not modify_delete_station_perms(request.user, station):
    #     messages.error(
    #         request,
    #         'You are not allowed to bulk-delete future observations on ground station {}!'.
    #         format(station_id)
    #     )
    #     return redirect(reverse('base:station_view', kwargs={'station_id': station_id}))

    # count, _ = station.observations.filter(start__gte=now()).delete()
    # if count:
    #     messages.success(
    #         request,
    #         'Deleted {} future observations on ground station {}.'.format(count, station_id)
    #     )
    # else:
    #     messages.success(
    #         request, 'No future observations on ground station {}.'.format(station_id)
    #     )
    # return redirect(reverse('base:station_view', kwargs={'station_id': station_id}))


@login_required
def station_register(request, step=None, station_id=None):
    """ Station register view """
    client_hash = request.GET.get('hash', None)
    if client_hash:
        client_id = cache.get(client_hash)
        if client_id is None:
            messages.error(
                request,
                'Invalid or expired hash, please restart the "Station Registration" process.'
            )
            return redirect(reverse('base:home'))
    else:
        messages.error(request, 'Missing hash parameter.')
        return redirect(reverse('base:home'))
    if step == '1':
        stations = Station.objects.filter(owner=request.user)
        return render(request, 'base/station_register_step1.html', {'stations': stations})
    if step == '2':
        station = None
        if station_id:
            station = get_object_or_404(Station, id=station_id, owner=request.user)

        if request.method == 'POST':
            if station:
                station_form = StationRegistrationForm(request.POST, instance=station)
            else:
                station_form = StationRegistrationForm(request.POST)
            if station_form.is_valid():
                station = station_form.save(commit=False)
                station.owner = request.user
                station.save()
                cache.delete(client_hash)
                messages.success(
                    request, (
                        'Ground Station {0} is registered successfully.'
                        ' Continue now with its configuration.'
                    ).format(station.id)
                )
                return redirect(reverse('base:station_edit', kwargs={'station_id': station.id}))
            messages.error(request, str(station_form.errors))
        else:
            if station:
                station_form = StationRegistrationForm(instance=station)
            else:
                station_form = StationRegistrationForm()

        return render(
            request, 'base/station_register_step2.html', {
                'station_form': station_form,
                'client_id': client_id
            }
        )

    return redirect(reverse('base:home'))


def initialize_station_and_registration_status(request, station_id):
    """Return Station model and its registration status if station exists"""
    if station_id:
        station = get_object_or_404(
            Station.objects.prefetch_related(
                'antennas', 'antennas__antenna_type', 'antennas__frequency_ranges'
            ),
            id=station_id,
            owner=request.user
        )
        registered = bool(station.client_id)
        return (station, registered)
    return (None, False)


@login_required
def station_edit(request, station_id=None):
    """Edit or add a single station."""
    (station, registered) = initialize_station_and_registration_status(request, station_id)
    if request.method == 'POST':
        return handle_station_edit_post(request, station, registered)
    return handle_station_edit_get(request, station, registered)


def handle_station_edit_get(request, station, registered):
    """Returns the form for creating or editing a station."""
    antenna_formset = None
    frequency_range_formsets = {}
    if station:
        station_form = StationForm(instance=station)
        antenna_formset = AntennaInlineFormSet(instance=station, prefix='ant')
        for antenna_form in antenna_formset.forms:
            antenna_prefix = antenna_form.prefix
            frequency_range_formsets[antenna_prefix] = FrequencyRangeInlineFormSet(
                instance=antenna_form.instance, prefix=antenna_prefix + '-fr'
            )

    else:
        station_form = StationForm()
        antenna_formset = AntennaInlineFormSet(prefix='ant')

    return render_station_edit_form(
        request, station_form, registered, antenna_formset, frequency_range_formsets
    )


def handle_station_edit_post(request, station, registered):
    """Handles the form submission for creating or editing a station"""
    frequency_range_formsets = {}
    station_form = StationForm(request.POST, request.FILES, instance=station)
    antenna_formset = AntennaInlineFormSet(
        request.POST, instance=station_form.instance, prefix='ant'
    )
    for antenna_form in antenna_formset:
        if not antenna_form['DELETE'].value():
            prefix = antenna_form.prefix
            frequency_range_formsets[prefix] = FrequencyRangeInlineFormSet(
                request.POST, instance=antenna_form.instance, prefix=prefix + '-fr'
            )

    if not station_form.is_valid():
        messages.error(request, str(station_form.errors))
        return render_station_edit_form(
            request, station_form, registered, antenna_formset, frequency_range_formsets
        )

    station_configuration = station_form.cleaned_data.get('station_configuration')
    schema_id = station_form.cleaned_data.get('schema')

    station = station_form.save(commit=False)
    station.owner = request.user
    station.qthlocator = calculate_qth_locator(station.lat, station.lng)
    if not antenna_formset.is_valid():
        populate_formset_error_messages(messages, request, antenna_formset)
        return render_station_edit_form(
            request, station_form, registered, antenna_formset, frequency_range_formsets
        )

    for frequency_range_formset_value in frequency_range_formsets.values():
        if not frequency_range_formset_value.is_valid():
            populate_formset_error_messages(messages, request, frequency_range_formset_value)
            return render_station_edit_form(
                request, station_form, registered, antenna_formset, frequency_range_formsets
            )

    try:
        schema_instance = StationConfigurationSchema.objects.select_related('station_type').get(
            id=schema_id
        )
        current_active_conf = station.active_configuration
        if (current_active_conf and schema_id == current_active_conf.schema_id
                and station_configuration == current_active_conf.configuration):
            conf_changed = False
        else:
            conf_changed = True

        if conf_changed:
            Draft202012Validator(schema_instance.schema).validate(station_configuration)
        with transaction.atomic():
            is_station_new = not bool(station.pk)
            if conf_changed:
                station.active_configuration_changed = now()
            station.save()
            antenna_formset.save()
            for frequency_range_formset_value in frequency_range_formsets.values():
                frequency_range_formset_value.save()
            if conf_changed:
                if not is_station_new:
                    StationConfiguration.objects.filter(
                        station=station, active=True
                    ).update(active=False)
                StationConfiguration.objects.create(
                    name=f"{schema_instance.station_type.name} - {schema_instance.name}",
                    station=station,
                    schema=schema_instance,
                    configuration=station_configuration
                )
        success_message = f'Ground Station {station.id} saved successfully.'
        if conf_changed:
            success_message += ' Configuration changes will be applied soon.'
        messages.success(request, success_message)
        return redirect(reverse('base:station_view', kwargs={'station_id': station.id}))
    except StationConfigurationSchema.DoesNotExist:
        messages.error(request, 'Cannot find schema')
    except ValidationError:
        messages.error(request, 'Configuration is not valid')
    except DatabaseError:
        messages.error(
            request, 'Something went wrong, if the problem persists'
            ' please contact an administrator'
        )

    return render_station_edit_form(
        request, station_form, registered, antenna_formset, frequency_range_formsets
    )


def calculate_qth_locator(latitude, longitude):
    """Calculates the qth locator given latitude and longitude"""
    field_identifiers = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
    ]

    working_lon = (longitude + 180) % 20
    lon_field = field_identifiers[int((longitude + 180) / 20)]
    lon_square = int(working_lon / 2)
    working_lon = int((working_lon % 2) * 12)
    lon_subsquare = field_identifiers[working_lon]

    working_lat = (latitude + 90) % 10
    lat_field = field_identifiers[int((latitude + 90) / 10)]
    lat_square = int(working_lat)
    working_lat = int((working_lat - lat_square) * 24)
    lat_subsquare = field_identifiers[working_lat]

    # Combine all parts to form the QTH locator
    qthlocator = (
        f"{lon_field}{lat_field}{lon_square}{lat_square}"
        f"{lon_subsquare.lower()}{lat_subsquare.lower()}"
    )

    return qthlocator


def render_station_edit_form(
    request, station_form, registered, antenna_formset, frequency_range_formsets
):
    """Creates the context and renders template for the station_edit page"""
    return render(
        request, 'base/station_edit.html', {
            'station_types': StationType.objects.all(),
            'conf_schemas': StationConfigurationSchema.objects.all(),
            'registered': registered,
            'station_form': station_form,
            'antenna_formset': antenna_formset,
            'frequency_range_formsets': frequency_range_formsets,
            'antenna_types': AntennaType.objects.all(),
            'max_antennas_per_station': settings.MAX_ANTENNAS_PER_STATION,
            'max_frequency_ranges_per_antenna': settings.MAX_FREQUENCY_RANGES_PER_ANTENNA,
            'max_frequency_for_range': settings.MAX_FREQUENCY_FOR_RANGE,
            'min_frequency_for_range': settings.MIN_FREQUENCY_FOR_RANGE,
            'vhf_min_frequency': settings.VHF_MIN_FREQUENCY,
            'vhf_max_frequency': settings.VHF_MAX_FREQUENCY,
            'uhf_min_frequency': settings.UHF_MIN_FREQUENCY,
            'uhf_max_frequency': settings.UHF_MAX_FREQUENCY,
            'l_min_frequency': settings.L_MIN_FREQUENCY,
            'l_max_frequency': settings.L_MAX_FREQUENCY,
            's_min_frequency': settings.S_MIN_FREQUENCY,
            's_max_frequency': settings.S_MAX_FREQUENCY,
            'image_changed': 'image' in station_form.changed_data,
        }
    )
