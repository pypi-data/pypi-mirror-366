"""SatNOGS Network API serializers, django rest framework"""
from collections import defaultdict

from django.core.validators import MaxValueValidator, MinValueValidator
from drf_spectacular.utils import extend_schema_field, inline_serializer
from PIL import Image
from rest_framework import serializers

from network.base.cache import get_satellites
from network.base.db_api import DBConnectionError, get_tle_sets_by_sat_id_set, \
    get_transmitters_by_uuid_set
from network.base.models import ActiveStationConfiguration, Antenna, DemodData, FrequencyRange, \
    Observation, Station
from network.base.perms import UserNoPermissionError, \
    check_schedule_perms_of_violators_per_station, check_schedule_perms_per_station
from network.base.scheduling import create_new_observation
from network.base.validators import ObservationOverlapError, OutOfRangeError, check_end_datetime, \
    check_overlaps, check_start_datetime, check_start_end_datetimes, \
    check_transmitter_station_pairs, check_violators_scheduling_limit


class CreateDemodDataSerializer(serializers.ModelSerializer):
    """SatNOGS Network DemodData API Serializer for creating demoddata."""

    class Meta:
        model = DemodData
        fields = (
            'observation',
            'demodulated_data',
        )

    def create(self, validated_data):
        """Creates demoddata from a list of validated data after checking if demodulated_data is an
        image and add the result in is_image field
        """
        try:
            image = Image.open(validated_data['demodulated_data'])
            image.verify()
            validated_data['is_image'] = True
        except Exception:  # pylint: disable=W0703
            validated_data['is_image'] = False
        return DemodData.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Updates demoddata from a list of validated data
        currently disabled and returns None
        """
        return None


class DemodDataSerializer(serializers.ModelSerializer):
    """SatNOGS Network DemodData API Serializer"""
    payload_demod = serializers.SerializerMethodField()

    class Meta:
        model = DemodData
        fields = ('payload_demod', )

    @extend_schema_field(serializers.URLField())
    def get_payload_demod(self, obj):
        """Returns DemodData Link"""
        request = self.context.get("request")
        if obj.demodulated_data:
            return request.build_absolute_uri(obj.demodulated_data.url)
        return None


class UpdateObservationSerializer(serializers.ModelSerializer):
    """SatNOGS Network Observation API Serializer for uploading audio and waterfall.
    This is Serializer is used temporarily until waterfall_old and payload_old fields are removed.
    """

    class Meta:
        model = Observation
        fields = ('id', 'payload', 'waterfall', 'client_metadata', 'client_version')


class ObservationSerializer(serializers.ModelSerializer):  # pylint: disable=R0904
    """SatNOGS Network Observation API Serializer"""
    transmitter = serializers.SerializerMethodField()
    transmitter_updated = serializers.SerializerMethodField()
    norad_cat_id = serializers.SerializerMethodField()
    payload = serializers.SerializerMethodField()
    waterfall = serializers.SerializerMethodField()
    station_name = serializers.SerializerMethodField()
    station_lat = serializers.SerializerMethodField()
    station_lng = serializers.SerializerMethodField()
    station_alt = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    waterfall_status = serializers.SerializerMethodField()
    vetted_status = serializers.SerializerMethodField()  # Deprecated
    vetted_user = serializers.SerializerMethodField()  # Deprecated
    vetted_datetime = serializers.SerializerMethodField()  # Deprecated
    demoddata = DemodDataSerializer(required=False, many=True)
    tle0 = serializers.SerializerMethodField()
    tle1 = serializers.SerializerMethodField()
    tle2 = serializers.SerializerMethodField()
    observer = serializers.SerializerMethodField()
    center_frequency = serializers.SerializerMethodField()
    observation_frequency = serializers.SerializerMethodField()
    transmitter_status = serializers.SerializerMethodField()
    transmitter_unconfirmed = serializers.SerializerMethodField()

    class Meta:
        model = Observation
        fields = (
            'id', 'start', 'end', 'ground_station', 'transmitter', 'norad_cat_id', 'payload',
            'waterfall', 'demoddata', 'station_name', 'station_lat', 'station_lng', 'station_alt',
            'vetted_status', 'vetted_user', 'vetted_datetime', 'archived', 'archive_url',
            'client_version', 'client_metadata', 'status', 'waterfall_status',
            'waterfall_status_user', 'waterfall_status_datetime', 'rise_azimuth', 'set_azimuth',
            'max_altitude', 'transmitter_uuid', 'transmitter_description', 'transmitter_type',
            'transmitter_uplink_low', 'transmitter_uplink_high', 'transmitter_uplink_drift',
            'transmitter_downlink_low', 'transmitter_downlink_high', 'transmitter_downlink_drift',
            'transmitter_mode', 'transmitter_invert', 'transmitter_baud', 'transmitter_updated',
            'transmitter_status', 'tle0', 'tle1', 'tle2', 'tle_source', 'center_frequency',
            'observer', 'observation_frequency', 'transmitter_unconfirmed', 'sat_id'
        )
        read_only_fields = [
            'id', 'start', 'end', 'observation', 'ground_station', 'transmitter', 'norad_cat_id',
            'archived', 'archive_url', 'station_name', 'station_lat', 'station_lng',
            'waterfall_status_user', 'status', 'waterfall_status', 'station_alt', 'vetted_status',
            'vetted_user', 'vetted_datetime', 'waterfall_status_datetime', 'rise_azimuth',
            'set_azimuth', 'max_altitude', 'transmitter_uuid', 'transmitter_description',
            'transmitter_type', 'transmitter_uplink_low', 'transmitter_uplink_high',
            'transmitter_uplink_drift', 'transmitter_downlink_low', 'transmitter_downlink_high',
            'transmitter_downlink_drift', 'transmitter_mode', 'transmitter_invert',
            'transmitter_baud', 'transmitter_created', 'transmitter_updated', 'transmitter_status',
            'tle0', 'tle1', 'tle2', 'tle_source', 'observer', 'center_frequency',
            'observation_frequency', 'transmitter_unconfirmed', 'sat_id'
        ]

    def update(self, instance, validated_data):
        """Updates observation object with validated data"""
        super().update(instance, validated_data)
        return instance

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_observation_frequency(self, obj):
        """Returns observation center frequency"""
        return obj.observation_frequency

    @extend_schema_field(serializers.BooleanField(allow_null=True))
    def get_transmitter_unconfirmed(self, obj):
        """Returns whether the transmitter was unconfirmed at the time of observation"""
        return obj.transmitter_unconfirmed

    @extend_schema_field(serializers.ChoiceField(choices=["active", "inactive", "unknown"]))
    def get_transmitter_status(self, obj):
        """Returns the status of the transmitter at the time of observation"""
        if obj.transmitter_status:
            return "active"
        if obj.transmitter_status is not None:
            return "inactive"
        return "unknown"

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_center_frequency(self, obj):
        """Returns observation center frequency"""
        return obj.center_frequency

    @extend_schema_field(str)
    def get_transmitter(self, obj):
        """Returns Transmitter UUID"""
        try:
            return obj.transmitter_uuid
        except AttributeError:
            return ''

    @extend_schema_field(serializers.DateTimeField(allow_null=True))
    def get_transmitter_updated(self, obj):
        """Returns Transmitter last update date"""
        try:
            return obj.transmitter_created
        except AttributeError:
            return None

    @extend_schema_field(int)
    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        sat = get_satellites()[obj.sat_id]
        return sat['norad_cat_id']

    @extend_schema_field(serializers.URLField())
    def get_payload(self, obj):
        """Returns Audio Link"""
        request = self.context.get("request")
        if obj.payload:
            return request.build_absolute_uri(obj.payload.url)
        return None

    @extend_schema_field(serializers.URLField())
    def get_waterfall(self, obj):
        """Returns Watefall Link"""
        request = self.context.get("request")
        if obj.waterfall:
            return request.build_absolute_uri(obj.waterfall.url)
        return None

    @extend_schema_field(str)
    def get_station_name(self, obj):
        """Returns Station name"""
        try:
            return obj.ground_station.name
        except AttributeError:
            return None

    @extend_schema_field(
        serializers.FloatField(
            validators=[MaxValueValidator(90), MinValueValidator(-90)]
        )
    )
    def get_station_lat(self, obj):
        """Returns Station latitude"""
        try:
            return obj.ground_station.lat
        except AttributeError:
            return None

    @extend_schema_field(
        serializers.FloatField(
            validators=[MaxValueValidator(180), MinValueValidator(-180)]
        )
    )
    def get_station_lng(self, obj):
        """Returns Station longitude"""
        try:
            return obj.ground_station.lng
        except AttributeError:
            return None

    @extend_schema_field(serializers.IntegerField(validators=[MinValueValidator(1)]))
    def get_station_alt(self, obj):
        """Returns Station elevation"""
        try:
            return obj.ground_station.alt
        except AttributeError:
            return None

    @extend_schema_field(
        serializers.ChoiceField(choices=["future", "failed", "bad", "unknown", "good"])
    )
    def get_status(self, obj):
        """Returns Observation status"""
        return obj.status_badge

    @extend_schema_field(
        serializers.ChoiceField(choices=["unknown", "with-signal", "without-signal"])
    )
    def get_waterfall_status(self, obj):
        """Returns Observation status"""
        return obj.waterfall_status_badge

    @extend_schema_field(str)
    def get_vetted_status(self, obj):
        """DEPRECATED: Returns vetted status"""
        if obj.status_badge == 'future':
            return 'unknown'
        return obj.status_badge

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_vetted_user(self, obj):
        """DEPRECATED: Returns vetted user"""
        if obj.waterfall_status_user:
            return obj.waterfall_status_user.pk
        return None

    @extend_schema_field(serializers.DateTimeField())
    def get_vetted_datetime(self, obj):
        """DEPRECATED: Returns vetted datetime"""
        return obj.waterfall_status_datetime

    @extend_schema_field(str)
    def get_tle0(self, obj):
        """Returns tle0"""
        return obj.tle_line_0

    @extend_schema_field(str)
    def get_tle1(self, obj):
        """Returns tle1"""
        return obj.tle_line_1

    @extend_schema_field(str)
    def get_tle2(self, obj):
        """Returns tle2"""
        return obj.tle_line_2

    @extend_schema_field(str)
    def get_observer(self, obj):
        """Returns the author of the observation"""
        if obj.author:
            return obj.author.username
        return ""


class NewObservationListSerializer(serializers.ListSerializer):
    """SatNOGS Network New Observation API List Serializer"""
    transmitters = {}
    tle_sets = set()
    violators = []

    def validate(self, attrs):
        """Validates data from a list of new observations"""

        (
            station_set, transmitter_uuid_set, transmitter_uuid_station_set, sat_id_set,
            transm_uuid_station_center_freq_set
        ) = (set() for _ in range(5))
        uuid_to_sat_id = {}
        start_end_per_station = defaultdict(list)

        for observation in attrs:
            station = observation.get('ground_station')
            transmitter_uuid = observation.get('transmitter_uuid')
            station_set.add(station)
            transmitter_uuid_set.add(transmitter_uuid)
            transmitter_uuid_station_set.add((transmitter_uuid, station))
            start_end_per_station[int(station.id)].append(
                (observation.get('start'), observation.get('end'))
            )
        try:
            check_overlaps(start_end_per_station)
        except ObservationOverlapError as error:
            raise serializers.ValidationError(error, code='invalid')

        try:
            check_schedule_perms_per_station(self.context['request'].user, station_set)
        except UserNoPermissionError as error:
            raise serializers.ValidationError(error, code='forbidden')

        try:
            self.transmitters = get_transmitters_by_uuid_set(transmitter_uuid_set)
            for uuid in transmitter_uuid_set:
                sat_id_set.add(self.transmitters[uuid]['sat_id'])
                uuid_to_sat_id[uuid] = self.transmitters[uuid]['sat_id']
            self.tle_sets = get_tle_sets_by_sat_id_set(sat_id_set)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        except DBConnectionError as error:
            raise serializers.ValidationError(error)

        self.violators = []
        sats = get_satellites()
        for sat_id in sat_id_set:
            if sats[sat_id]['is_frequency_violator']:
                self.violators.append(sats[sat_id])
        violators_sat_ids = [satellite['sat_id'] for satellite in self.violators]
        station_with_violators_set = {
            station
            for transmitter_uuid, station in transmitter_uuid_station_set
            if uuid_to_sat_id[transmitter_uuid] in violators_sat_ids
        }
        try:
            check_schedule_perms_of_violators_per_station(
                self.context['request'].user, station_with_violators_set
            )
        except UserNoPermissionError as error:
            raise serializers.ValidationError(error, code='forbidden')

        for observation in attrs:
            transmitter_uuid = observation.get('transmitter_uuid')
            station = observation.get('ground_station')
            center_frequency = observation.get('center_frequency', None)
            transmitter = self.transmitters[transmitter_uuid]
            if (transmitter["type"] == "Transponder"
                    or transmitter["type"] == "Range transmitter") and center_frequency is None:
                observation["center_frequency"
                            ] = (transmitter['downlink_high'] + transmitter['downlink_low']) // 2
            transm_uuid_station_center_freq_set.add((transmitter_uuid, station, center_frequency))

        transmitter_station_list = [
            (self.transmitters[transmitter_uuid], station, center_freq)
            for transmitter_uuid, station, center_freq in transm_uuid_station_center_freq_set
        ]
        try:
            check_transmitter_station_pairs(transmitter_station_list)
        except OutOfRangeError as error:
            raise serializers.ValidationError(error, code='invalid')
        return attrs

    def create(self, validated_data):
        """Creates new observations from a list of new observations validated data"""
        new_observations = []
        observations_per_sat_id = defaultdict(list)
        for observation_data in validated_data:
            transmitter_uuid = observation_data['transmitter_uuid']
            transmitter = self.transmitters[transmitter_uuid]
            tle_set = self.tle_sets[transmitter['sat_id']]

            observations_per_sat_id[transmitter['sat_id']].append(observation_data['start'])

            observation = create_new_observation(
                station=observation_data['ground_station'],
                transmitter=transmitter,
                start=observation_data['start'],
                end=observation_data['end'],
                author=self.context['request'].user,
                tle_set=tle_set,
                center_frequency=observation_data.get('center_frequency', None)
            )
            new_observations.append(observation)

        if self.violators and not self.context['request'].user.groups.filter(name='Operators'
                                                                             ).exists():
            check_violators_scheduling_limit(self.violators, observations_per_sat_id)

        for observation in new_observations:
            observation.save()

        if not self.context['request'].user.is_observer:
            self.context['request'].user.is_observer = True
            self.context['request'].user.save(update_fields=['is_observer'])

        return new_observations

    def update(self, instance, validated_data):
        """Updates observations from a list of validated data

        currently disabled and returns None
        """
        return None


class NewObservationSerializer(serializers.Serializer):
    """SatNOGS Network New Observation API Serializer"""
    start = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'],
        error_messages={
            'invalid': 'Start datetime should have either \'%Y-%m-%d %H:%M:%S.%f\' or '
            '\'%Y-%m-%d %H:%M:%S\' '
            'format.',
            'required': 'Start(\'start\' key) datetime is required.'
        }
    )
    end = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'],
        error_messages={
            'invalid': 'End datetime should have either \'%Y-%m-%d %H:%M:%S.%f\' or '
            '\'%Y-%m-%d %H:%M:%S\' '
            'format.',
            'required': 'End datetime(\'end\' key) is required.'
        }
    )
    ground_station = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.filter(
            status__gt=0, alt__isnull=False, lat__isnull=False, lng__isnull=False
        ),
        allow_null=False,
        error_messages={
            'does_not_exist': 'Station should exist, be online and have a defined location.',
            'required': 'Station(\'ground_station\' key) is required.'
        }
    )
    transmitter_uuid = serializers.CharField(
        max_length=22,
        min_length=22,
        error_messages={
            'invalid': 'Transmitter UUID should be valid.',
            'required': 'Transmitter UUID(\'transmitter_uuid\' key) is required.'
        }
    )

    center_frequency = serializers.IntegerField(
        error_messages={'negative': 'Frequency cannot be a negative value.'}, required=False
    )

    def validate_start(self, value):
        """Validates start datetime of a new observation"""
        try:
            check_start_datetime(value)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        return value

    def validate_end(self, value):
        """Validates end datetime of a new observation"""
        try:
            check_end_datetime(value)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        return value

    def validate(self, attrs):
        """Validates combination of start and end datetimes of a new observation"""
        start = attrs['start']
        end = attrs['end']
        try:
            check_start_end_datetimes(start, end)
        except ValueError as error:
            raise serializers.ValidationError(error, code='invalid')
        return attrs

    def create(self, validated_data):
        """Creates a new observation

        Currently not implemented and raises exception. If in the future we want to implement this
        serializer accepting and creating observation from single object instead from a list of
        objects, we should remove raising the exception below and implement the validations that
        exist now only on NewObservationListSerializer
        """
        raise serializers.ValidationError(
            "Serializer is implemented for accepting and schedule\
                                           only lists of observations"
        )

    def update(self, instance, validated_data):
        """Updates an observation from validated data, currently disabled and returns None"""
        return None

    class Meta:
        list_serializer_class = NewObservationListSerializer


class FrequencyRangeSerializer(serializers.ModelSerializer):
    """SatNOGS Network FrequencyRange API Serializer"""

    class Meta:
        model = FrequencyRange
        fields = ('min_frequency', 'max_frequency', 'bands')


class AntennaSerializer(serializers.ModelSerializer):
    """SatNOGS Network Antenna API Serializer"""
    antenna_type = serializers.StringRelatedField()
    frequency_ranges = FrequencyRangeSerializer(many=True)

    class Meta:
        model = Antenna
        fields = ('antenna_type', 'frequency_ranges')


class StationSerializer(serializers.ModelSerializer):
    """SatNOGS Network Station API Serializer"""
    # Using SerializerMethodField instead of directly the reverse relation (antennas) with the
    # AntennaSerializer for not breaking the API, it should change in next API version
    antenna = serializers.SerializerMethodField()
    min_horizon = serializers.SerializerMethodField()
    observations = serializers.SerializerMethodField()
    future_observations = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    altitude = serializers.IntegerField(min_value=0, source='alt')
    image = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = (
            'id', 'name', 'altitude', 'min_horizon', 'lat', 'lng', 'qthlocator', 'antenna',
            'created', 'last_seen', 'status', 'observations', 'future_observations', 'description',
            'client_version', 'target_utilization', 'image', 'success_rate', 'owner'
        )

    @extend_schema_field(str)
    def get_owner(self, obj):
        """Returns the username of the station's owner"""
        if obj.owner:
            return obj.owner.username
        return ""

    @extend_schema_field(serializers.IntegerField(validators=[MinValueValidator(1)]))
    def get_success_rate(self, obj):
        """Returns the success rate of the station"""
        return obj.success_rate

    @extend_schema_field(str)
    def get_image(self, obj):
        """Returns the url of the station image"""
        return obj.get_image()

    @extend_schema_field(serializers.IntegerField(validators=[MinValueValidator(1)]))
    def get_min_horizon(self, obj):
        """Returns Station minimum horizon"""
        return obj.horizon

    @extend_schema_field(
        {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'frequency': {
                        'type': 'number'
                    },
                    'frequency_max': {
                        'type': 'number'
                    },
                    'band': {
                        'type': 'string'
                    },
                    'antenna_type': {
                        'type': 'string'
                    },
                    'antenna_type_name': {
                        'type': 'string'
                    },
                },
            },
        }
    )
    def get_antenna(self, obj):
        """Returns Station antenna list"""

        antenna_types = {
            'Dipole': 'dipole',
            'V-Dipole': 'v-dipole',
            'Discone': 'discone',
            'Ground Plane': 'ground',
            'Yagi': 'yagi',
            'Cross Yagi': 'cross-yagi',
            'Helical': 'helical',
            'Parabolic': 'parabolic',
            'Vertical': 'vertical',
            'Turnstile': 'turnstile',
            'Quadrafilar': 'quadrafilar',
            'Eggbeater': 'eggbeater',
            'Lindenblad': 'lindenblad',
            'Parasitic Lindenblad': 'paralindy',
            'Patch': 'patch',
            'Other Directional': 'other direct',
            'Other Omni-Directional': 'other omni',
        }
        serializer = AntennaSerializer(obj.antennas, many=True)
        antennas = []
        for antenna in serializer.data:
            for frequency_range in antenna['frequency_ranges']:
                antennas.append(
                    {
                        'frequency': frequency_range['min_frequency'],
                        'frequency_max': frequency_range['max_frequency'],
                        'band': frequency_range['bands'],
                        'antenna_type': antenna_types[antenna['antenna_type']],
                        'antenna_type_name': antenna['antenna_type'],
                    }
                )
        return antennas

    @extend_schema_field(serializers.IntegerField(validators=[MinValueValidator(1)]))
    def get_observations(self, obj):
        """Returns Station observations number"""
        return obj.observations_stats['total']

    @extend_schema_field(serializers.IntegerField(validators=[MinValueValidator(1)]))
    def get_future_observations(self, obj):
        """Returns Station future observations number"""
        return obj.observations_stats['future']

    @extend_schema_field(str)
    def get_status(self, obj):
        """Returns Station status"""
        try:
            return obj.get_status_display()
        except AttributeError:
            return None


class StationConfigurationSerializer(serializers.ModelSerializer):
    """SatNOGS Network Station Configuration API Serializer"""

    class Meta:
        model = ActiveStationConfiguration
        fields = ['configuration']


class JobSerializer(serializers.ModelSerializer):
    """SatNOGS Network Job API Serializer"""
    frequency = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    transmitter = serializers.SerializerMethodField()
    baud = serializers.SerializerMethodField()
    tle0 = serializers.SerializerMethodField()
    tle1 = serializers.SerializerMethodField()
    tle2 = serializers.SerializerMethodField()
    norad_cat_id = serializers.SerializerMethodField()

    class Meta:
        model = Observation
        fields = (
            'id', 'start', 'end', 'ground_station', 'tle0', 'tle1', 'tle2', 'frequency', 'mode',
            'transmitter', 'baud', 'max_altitude', 'norad_cat_id'
        )

    @extend_schema_field(str)
    def get_tle0(self, obj):
        """Returns tle0"""
        return obj.tle_line_0

    @extend_schema_field(str)
    def get_tle1(self, obj):
        """Returns tle1"""
        return obj.tle_line_1

    @extend_schema_field(str)
    def get_tle2(self, obj):
        """Returns tle2"""
        return obj.tle_line_2

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_frequency(self, obj):
        """Returns Observation frequency"""
        frequency = obj.center_frequency or obj.transmitter_downlink_low
        frequency_drift = obj.transmitter_downlink_drift
        if obj.center_frequency or frequency_drift is None:
            return frequency
        return int(round(frequency + ((frequency * frequency_drift) / 1e9)))

    @extend_schema_field(str)
    def get_transmitter(self, obj):
        """Returns Transmitter UUID"""
        return obj.transmitter_uuid

    @extend_schema_field(str)
    def get_mode(self, obj):
        """Returns Transmitter mode"""
        try:
            return obj.transmitter_mode
        except AttributeError:
            return ''

    @extend_schema_field(serializers.FloatField())
    def get_baud(self, obj):
        """Returns Transmitter baudrate"""
        return obj.transmitter_baud

    @extend_schema_field(int)
    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        satellite = get_satellites()[obj.sat_id]
        return satellite['norad_cat_id']


class TransmitterSerializer(serializers.Serializer):
    """SatNOGS Network Transmitter API Serializer"""
    uuid = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    @extend_schema_field(serializers.UUIDField())
    def get_uuid(self, obj):
        """Returns Transmitter UUID"""
        return obj['transmitter_uuid']

    @extend_schema_field(
        inline_serializer(
            name='TransmitterStats',
            fields={
                'total_count': serializers.IntegerField(),
                'unknown_count': serializers.IntegerField(),
                'future_count': serializers.IntegerField(),
                'good_count': serializers.IntegerField(),
                'bad_count': serializers.IntegerField(),
                'unknown_rate': serializers.FloatField(),
                'future_rate': serializers.FloatField(),
                'success_rate': serializers.FloatField(),
                'bad_rate': serializers.FloatField()
            }
        )
    )
    def get_stats(self, obj):
        """Returns Transmitter statistics"""
        return obj['stats']

    def create(self, validated_data):
        """Creates an object instance of transmitter, currently disabled and returns None"""
        return None

    def update(self, instance, validated_data):
        """Updates an object instance of transmitter, currently disabled and returns None"""
        return None
