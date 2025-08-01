"""Django database base model for SatNOGS Network"""
import codecs
import re
from datetime import timedelta
from operator import truth

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinLengthValidator, \
    MinValueValidator
from django.db import models
from django.db.models import Count, Q
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import now
from shortuuidfield import ShortUUIDField
from storages.backends.s3boto3 import S3Boto3Storage

from network.base.db_api import DBConnectionError, get_artifact_metadata_by_observation_id
from network.base.managers import ObservationManager
from network.base.utils import bands_from_range
from network.users.models import User

OBSERVATION_STATUSES = (
    ('unknown', 'Unknown'),
    ('good', 'Good'),
    ('bad', 'Bad'),
    ('failed', 'Failed'),
)
STATION_STATUSES = (
    (2, 'Online'),
    (1, 'Testing'),
    (0, 'Offline'),
)
STATION_VIOLATOR_SCHEDULING_CHOICES = (
    (0, 'No one'),
    (1, 'Only Operators'),
    (2, 'Everyone'),
)
SATELLITE_STATUS = ['alive', 'dead', 'future', 're-entered']
TRANSMITTER_STATUS = ['active', 'inactive', 'invalid']
TRANSMITTER_TYPE = ['Transmitter', 'Transceiver', 'Transponder', "Range transmitter"]


def _decode_pretty_hex(binary_data):
    """Return the binary data as hex dump of the following form: `DE AD C0 DE`"""

    data = codecs.encode(binary_data, 'hex').decode('ascii').upper()
    return ' '.join(data[i:i + 2] for i in range(0, len(data), 2))


def _name_obs_files(instance, filename):
    """Return a filepath formatted by Observation ID"""
    return 'data_obs/{0}/{1}'.format(instance.id, filename)


def _name_obs_demoddata(instance, filename):
    """Return a filepath for DemodData formatted by Observation ID"""
    # On change of the string bellow, change it also at api/views.py
    return 'data_obs/{0}/{1}'.format(instance.observation.id, filename)


def _name_observation_data(instance, filename):
    """Return a filepath formatted by Observation ID"""
    return 'data_obs/{0}/{1}/{2}/{3}/{4}/{5}'.format(
        instance.start.year, instance.start.month, instance.start.day, instance.start.hour,
        instance.id, filename
    )


def _name_observation_demoddata(instance, filename):
    """Return a filepath for DemodData formatted by Observation ID"""
    # On change of the string bellow, change it also at api/views.py
    return 'data_obs/{0}/{1}/{2}/{3}/{4}/{5}'.format(
        instance.observation.start.year, instance.observation.start.month,
        instance.observation.start.day, instance.observation.start.hour, instance.observation.id,
        filename
    )


def _select_audio_storage():
    return S3Boto3Storage() if settings.USE_S3_STORAGE_FOR_AUDIO else DefaultStorage()


def _select_waterfall_storage():
    return S3Boto3Storage() if settings.USE_S3_STORAGE_FOR_WATERFALL else DefaultStorage()


def _select_data_storage():
    return S3Boto3Storage() if settings.USE_S3_STORAGE_FOR_DATA else DefaultStorage()


def validate_image(fieldfile_obj):
    """Validates image size"""
    filesize = fieldfile_obj.file.size
    megabyte_limit = 2.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def get_default_station_configuration_schema():
    """Generate default value for schema field of StationConfigurationSchema model"""
    return {}


def get_default_station_configuration():
    """Generate default value for schema field of StationConfiguration model"""
    return {}


class StationType(models.Model):
    """Model for SatNOGS station types"""
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class StationConfigurationSchema(models.Model):
    """Model for SatNOGS station configuration schemas"""
    name = models.CharField(max_length=100)
    station_type = models.ForeignKey('StationType', on_delete=models.CASCADE)
    schema = models.JSONField(default=get_default_station_configuration_schema)

    def __str__(self):
        return self.station_type.name + ' - ' + self.name

    class Meta:
        unique_together = ['name', 'station_type']


class StationConfiguration(models.Model):
    """Model for SatNOGS station configuration schemas"""
    name = models.CharField(max_length=100)
    station = models.ForeignKey('Station', on_delete=models.CASCADE)
    schema = models.ForeignKey('StationConfigurationSchema', on_delete=models.CASCADE)
    configuration = models.JSONField(default=get_default_station_configuration)
    active = models.BooleanField(default=True)
    applied = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ActiveStationConfigurationManager(models.Manager):  # pylint: disable=R0903
    """Django Manager for ActiveStationConfiguration objects"""

    def get_queryset(self):
        """Returns query of StationConfigurations

        :returns: the active configurations for stations
        """
        return super().get_queryset().filter(active=True)


class ActiveStationConfiguration(StationConfiguration):
    """Proxy model for StationConfiguration that contains only active ones"""
    objects = ActiveStationConfigurationManager()

    class Meta:
        proxy = True


class Station(models.Model):
    """Model for SatNOGS ground stations."""
    owner = models.ForeignKey(
        User, related_name="ground_stations", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=45)
    image = models.ImageField(upload_to='ground_stations', blank=True, validators=[validate_image])
    alt = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-500)],
        help_text='In meters above sea level'
    )
    lat = models.FloatField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(90), MinValueValidator(-90)],
        help_text='eg. 38.01697'
    )
    lng = models.FloatField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(180), MinValueValidator(-180)],
        help_text='eg. 23.7314'
    )
    # https://en.wikipedia.org/wiki/Maidenhead_Locator_System
    qthlocator = models.CharField(max_length=8, blank=True)
    featured_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    testing = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=STATION_STATUSES, default=0)
    violator_scheduling = models.IntegerField(
        choices=STATION_VIOLATOR_SCHEDULING_CHOICES, default=0
    )
    horizon = models.PositiveIntegerField(help_text='In degrees above 0', default=10)
    description = models.TextField(max_length=500, blank=True, help_text='Max 500 characters')
    client_version = models.CharField(max_length=45, blank=True)
    target_utilization = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        help_text='Target utilization factor for '
        'your station',
        null=True,
        blank=True
    )
    client_id = models.CharField(max_length=128, blank=True)
    active_configuration_changed = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-status', 'id']
        indexes = [models.Index(fields=['-status', 'id'])]

    @property
    def active_configuration(self):
        """Returns the currently used configuration of the station"""
        try:
            conf = ActiveStationConfiguration.objects.get(station=self)
        except ActiveStationConfiguration.DoesNotExist:
            conf = None
        return conf

    def get_image(self):
        """Return the image of the station or the default image if there is a defined one"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return settings.STATION_DEFAULT_IMAGE

    @property
    def is_online(self):
        """Return true if station is online"""
        try:
            heartbeat = self.last_seen + timedelta(minutes=int(settings.STATION_HEARTBEAT_TIME))
            return heartbeat > now()
        except TypeError:
            return False

    @property
    def is_offline(self):
        """Return true if station is offline"""
        return not self.is_online

    @property
    def has_location(self):
        """Return true if station location is defined"""
        if self.alt is None or self.lat is None or self.lng is None:
            return False
        return True

    @property
    def is_testing(self):
        """Return true if station is online and in testing mode"""
        if self.is_online:
            if self.status == 1:
                return True
        return False

    def state(self):
        """Return the station status in html format"""
        if not self.status:
            return format_html('<span style="color:red;">Offline</span>')
        if self.status == 1:
            return format_html('<span style="color:orange;">Testing</span>')
        return format_html('<span style="color:green">Online</span>')

    @property
    def success_rate(self):
        """Return the success rate of the station - successful observation over failed ones"""
        rate = cache.get('station-{0}-rate'.format(self.id))
        if not rate:
            observations = self.observations.exclude(experimental=True
                                                     ).exclude(status__range=(0, 99))
            stats = observations.aggregate(
                bad=Count('pk', filter=Q(status__range=(-100, -1))),
                good=Count('pk', filter=Q(status__gte=100)),
                failed=Count('pk', filter=Q(status__lt=100))
            )
            good_count = 0 if stats['good'] is None else stats['good']
            bad_count = 0 if stats['bad'] is None else stats['bad']
            failed_count = 0 if stats['failed'] is None else stats['failed']
            total = good_count + bad_count + failed_count
            if total:
                rate = int(100 * ((bad_count + good_count) / total))
                cache.set('station-{0}-rate'.format(self.id), rate, 60 * 60 * 6)
            else:
                rate = False
        return rate

    def __str__(self):
        if self.pk:
            return "%d - %s" % (self.pk, self.name)
        return "%s" % (self.name)

    @property
    def observations_stats(self):
        """ Return and objects with total and future observations of the station.
           For the total we cache the results for 6 hours and for future observations for 1 hour.
       """
        total_counter = cache.get('station-{0}-obs-total-stats'.format(self.id))
        if total_counter is None:
            total_counter = self.observations.count()
            cache.set('station-{0}-obs-total-stats'.format(self.id), total_counter, 60 * 60 * 6)

        future_counter = cache.get('station-{0}-obs-future-stats'.format(self.id))
        if future_counter is None:
            future_counter = self.observations.filter(end__gt=now()).count()
            cache.set('station-{0}-obs-future-stats'.format(self.id), future_counter, 60 * 60)

        return {'total': total_counter, 'future': future_counter}

    def clean(self):
        if re.search('[^\x20-\x7E\xA0-\xFF]', self.name, re.IGNORECASE):
            raise ValidationError(
                {
                    'name': (
                        'Please use characters that belong to ISO-8859-1'
                        ' (https://en.wikipedia.org/wiki/ISO/IEC_8859-1).'
                    )
                }
            )
        if re.search('[^\n\r\t\x20-\x7E\xA0-\xFF]', self.description, re.IGNORECASE):
            raise ValidationError(
                {
                    'description': (
                        'Please use characters that belong to ISO-8859-1'
                        ' (https://en.wikipedia.org/wiki/ISO/IEC_8859-1).'
                    )
                }
            )

    def update_status(self, created: bool = False):
        """
        Update the status of the station

        :param created: Whether the model is being created
        """
        if not created:
            current_status = self.status
            if self.is_offline:
                self.status = 0
            elif self.testing:
                self.status = 1
            else:
                self.status = 2
            self.save()
            if self.status != current_status:
                StationStatusLog.objects.create(station=self, status=self.status)
        else:
            StationStatusLog.objects.create(station=self, status=self.status)


class AntennaType(models.Model):
    """Model for antenna types."""
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name


class Antenna(models.Model):
    """Model for antennas of SatNOGS ground stations."""
    antenna_type = models.ForeignKey(
        AntennaType, on_delete=models.PROTECT, related_name='antennas'
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='antennas')

    @property
    def bands(self):
        """Return comma separated string of the bands that the antenna works on"""
        bands = []
        for frequency_range in self.frequency_ranges.all():
            for band in bands_from_range(frequency_range.min_frequency,
                                         frequency_range.max_frequency):
                if band not in bands:
                    bands.append(band)
        return ', '.join(bands)

    def __str__(self):
        if self.pk:
            return "%d - %s (#%s)" % (self.pk, self.antenna_type.name, self.station.id)
        if self.station.id:
            return "%s (#%s)" % (self.antenna_type.name, self.station.id)
        return "%s" % (self.antenna_type.name)


class FrequencyRange(models.Model):
    """Model for frequency ranges of antennas."""
    antenna = models.ForeignKey(Antenna, on_delete=models.CASCADE, related_name='frequency_ranges')
    min_frequency = models.BigIntegerField()
    max_frequency = models.BigIntegerField()

    @property
    def bands(self):
        """Return comma separated string of the bands that of the frequeny range"""
        bands = bands_from_range(self.min_frequency, self.max_frequency)
        return ', '.join(bands)

    class Meta:
        ordering = ['min_frequency']

    def clean(self):
        if self.max_frequency < self.min_frequency:
            raise ValidationError(
                {
                    'min_frequency': (
                        'Minimum frequency is greater than the maximum one ({0} > {1}).'.format(
                            self.min_frequency, self.max_frequency
                        )
                    ),
                    'max_frequency': (
                        'Maximum frequency is less than the minimum one ({0} < {1}).'.format(
                            self.max_frequency, self.min_frequency
                        )
                    ),
                }
            )
        if self.min_frequency < settings.MIN_FREQUENCY_FOR_RANGE:
            raise ValidationError(
                {
                    'min_frequency': ('Minimum frequency should be more than {0}.').format(
                        settings.MIN_FREQUENCY_FOR_RANGE
                    )
                }
            )
        if self.max_frequency > settings.MAX_FREQUENCY_FOR_RANGE:
            raise ValidationError(
                {
                    'max_frequency': ('Maximum frequency should be less than {0}.').format(
                        settings.MAX_FREQUENCY_FOR_RANGE
                    )
                }
            )


class StationStatusLog(models.Model):
    """Model for keeping Status log for Station."""
    station = models.ForeignKey(
        Station, related_name='station_logs', on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.IntegerField(choices=STATION_STATUSES, default=0)
    changed = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed']
        indexes = [models.Index(fields=['-changed'])]

    def __str__(self):
        return '{0} - {1}'.format(self.station, self.status)


class Observation(models.Model):
    """Model for SatNOGS observations."""
    sat_id = models.CharField(db_index=True, max_length=24)
    tle_line_0 = models.CharField(
        max_length=69, blank=True, validators=[MinLengthValidator(1),
                                               MaxLengthValidator(69)]
    )
    tle_line_1 = models.CharField(
        max_length=69, blank=True, validators=[MinLengthValidator(69),
                                               MaxLengthValidator(69)]
    )
    tle_line_2 = models.CharField(
        max_length=69, blank=True, validators=[MinLengthValidator(69),
                                               MaxLengthValidator(69)]
    )
    tle_source = models.CharField(max_length=300, blank=True)
    tle_updated = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(
        User, related_name='observations', on_delete=models.SET_NULL, null=True, blank=True
    )
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)
    ground_station = models.ForeignKey(
        Station, related_name='observations', on_delete=models.SET_NULL, null=True, blank=True
    )
    client_version = models.CharField(max_length=255, blank=True)
    client_metadata = models.TextField(blank=True)
    payload = models.FileField(
        upload_to=_name_observation_data, storage=_select_audio_storage, blank=True
    )
    waterfall = models.ImageField(
        upload_to=_name_observation_data, storage=_select_waterfall_storage, blank=True
    )
    """
    Meaning of values:
    True -> Waterfall has signal of the observed satellite (with-signal)
    False -> Waterfall has not signal of the observed satellite (without-signal)
    None -> Uknown whether waterfall has or hasn't signal of the observed satellite (unknown)
    """
    waterfall_status = models.BooleanField(blank=True, null=True, default=None)
    waterfall_status_datetime = models.DateTimeField(null=True, blank=True)
    waterfall_status_user = models.ForeignKey(
        User, related_name='waterfalls_vetted', on_delete=models.SET_NULL, null=True, blank=True
    )
    vetted_status = models.CharField(
        choices=OBSERVATION_STATUSES, max_length=20, default='unknown'
    )
    """
    Meaning of values:
    x < -100      -> Failed
    -100 =< x < 0 -> Bad
    0 =< x < 100  -> Unknown (Future if observation not completed)
    100 =< x      -> Good
    """
    status = models.SmallIntegerField(default=0)
    experimental = models.BooleanField(default=False)
    rise_azimuth = models.FloatField(blank=True, null=True)
    max_altitude = models.FloatField(blank=True, null=True)
    set_azimuth = models.FloatField(blank=True, null=True)
    audio_zipped = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    archive_identifier = models.CharField(max_length=255, blank=True)
    archive_url = models.URLField(blank=True, null=True)
    transmitter_uuid = ShortUUIDField(auto=False, db_index=True)
    transmitter_description = models.TextField(default='')
    transmitter_type = models.CharField(
        choices=list(zip(TRANSMITTER_TYPE, TRANSMITTER_TYPE)),
        max_length=17,
        default='Transmitter'
    )
    transmitter_uplink_low = models.BigIntegerField(blank=True, null=True)
    transmitter_uplink_high = models.BigIntegerField(blank=True, null=True)
    transmitter_uplink_drift = models.IntegerField(blank=True, null=True)
    transmitter_downlink_low = models.BigIntegerField(blank=True, null=True)
    transmitter_downlink_high = models.BigIntegerField(blank=True, null=True)
    transmitter_downlink_drift = models.IntegerField(blank=True, null=True)
    transmitter_mode = models.CharField(max_length=25, blank=True, null=True)
    transmitter_invert = models.BooleanField(default=False)
    transmitter_baud = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    transmitter_created = models.DateTimeField(default=now)
    transmitter_status = models.BooleanField(null=True, blank=True)
    transmitter_unconfirmed = models.BooleanField(blank=True, null=True)
    station_alt = models.PositiveIntegerField(null=True, blank=True)
    station_lat = models.FloatField(
        validators=[MaxValueValidator(90), MinValueValidator(-90)], null=True, blank=True
    )
    station_lng = models.FloatField(
        validators=[MaxValueValidator(180), MinValueValidator(-180)], null=True, blank=True
    )
    station_antennas = models.TextField(null=True, blank=True)
    center_frequency = models.BigIntegerField(blank=True, null=True)

    objects = ObservationManager.as_manager()

    @property
    def is_past(self):
        """Return true if observation is in the past (end time is in the past)"""
        return self.end < now()

    @property
    def is_future(self):
        """Return true if observation is in the future (end time is in the future)"""
        return self.end > now()

    @property
    def is_started(self):
        """Return true if observation has started (start time is in the past)"""
        return self.start < now()

    # The values bellow are used as returned values in the API and for css rules in templates
    @property
    def status_badge(self):
        """Return badge for status field"""
        if self.is_future:
            return "future"
        if self.status < -100:
            return "failed"
        if -100 <= self.status < 0:
            return "bad"
        if 0 <= self.status < 100:
            return "unknown"
        return "good"

    # The values bellow are used as displayed values in templates
    @property
    def status_display(self):
        """Return display name for status field"""
        if self.is_future:
            return "Future"
        if self.status < -100:
            return "Failed"
        if -100 <= self.status < 0:
            return "Bad"
        if 0 <= self.status < 100:
            return "Unknown"
        return "Good"

    # The values bellow are used as returned values in the API and for css rules in templates
    @property
    def waterfall_status_badge(self):
        """Return badge for waterfall_status field"""
        if self.waterfall_status is None:
            return 'unknown'
        if self.waterfall_status:
            return 'with-signal'
        return 'without-signal'

    # The values bellow are used as displayed values in templates
    @property
    def waterfall_status_display(self):
        """Return display name for waterfall_status field"""
        if self.waterfall_status is None:
            return 'Unknown'
        if self.waterfall_status:
            return 'With Signal'
        return 'Without Signal'

    @property
    def has_waterfall(self):
        """Run some checks on the waterfall for existence of data."""
        if self.waterfall:
            return True
        return False

    @property
    def has_audio(self):
        """Run some checks on the payload for existence of data."""
        if self.archive_url:
            return True
        if self.payload:
            return True
        return False

    @property
    def has_demoddata(self):
        """Check if the observation has Demod Data."""
        if self.demoddata.exists():
            return True
        return False

    @property
    def has_artifact(self):
        """Check if the observation has an associated artifact in satnogs-db."""
        try:
            artifact_metadata = get_artifact_metadata_by_observation_id(self.id)
        except DBConnectionError:
            return False

        return truth(artifact_metadata)

    @property
    def artifact_url(self):
        """Return url for the oberations artifact file (if it exists)"""
        try:
            artifact_metadata = get_artifact_metadata_by_observation_id(self.id)
        except DBConnectionError:
            return ''

        if not artifact_metadata:
            return ''
        return artifact_metadata[0]['artifact_file']

    @property
    def audio_url(self):
        """Return url for observation's audio file"""
        if self.has_audio:
            if self.archive_url:
                return self.archive_url
            return self.payload.url
        return ''

    @property
    def observation_frequency(self):
        """
        Return the observation frequency
        """
        frequency = self.center_frequency or self.transmitter_downlink_low
        frequency_drift = self.transmitter_downlink_drift
        if self.center_frequency or frequency_drift is None:
            return frequency
        return int(round(frequency + ((frequency * frequency_drift) / 1e9)))

    class Meta:
        ordering = ['-start', '-end']
        indexes = [models.Index(fields=['-start', '-end'])]
        permissions = (('can_vet', 'Can vet observations'), )

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        """Return absolute url of the model object"""
        return reverse('base:observation_view', kwargs={'observation_id': self.id})


@receiver(models.signals.post_delete, sender=Observation)
def observation_remove_files(sender, instance, **kwargs):  # pylint: disable=W0613
    """Remove audio and waterfall files of an observation if the observation is deleted"""
    if instance.payload:
        instance.payload.delete(save=False)
    if instance.waterfall:
        instance.waterfall.delete(save=False)


class DemodData(models.Model):
    """Model for DemodData."""
    observation = models.ForeignKey(
        Observation, related_name='demoddata', on_delete=models.CASCADE
    )
    demodulated_data = models.FileField(
        upload_to=_name_observation_demoddata, storage=_select_data_storage, blank=True
    )
    copied_to_db = models.BooleanField(default=False)
    is_image = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["copied_to_db", "is_image"])]

    def display_payload_hex(self):
        """
        Return the content of the data file as hex dump of the following form: `DE AD C0 DE`.
        """
        if self.demodulated_data:
            with self.demodulated_data.storage.open(self.demodulated_data.name,
                                                    mode='rb') as data_file:
                payload = data_file.read()

        return _decode_pretty_hex(payload)

    def display_payload_utf8(self):
        """
        Return the content of the data file decoded as UTF-8. If this fails,
        show as hex dump.
        """
        if self.demodulated_data:
            with self.demodulated_data.storage.open(self.demodulated_data.name,
                                                    mode='rb') as data_file:
                payload = data_file.read()

        try:
            return payload.decode('utf-8')
        except UnicodeDecodeError:
            return _decode_pretty_hex(payload)

    def __str__(self):
        return '{} - {}'.format(self.id, self.demodulated_data)


@receiver(models.signals.post_delete, sender=DemodData)
def demoddata_remove_files(sender, instance, **kwargs):  # pylint: disable=W0613
    """Remove data file of an observation if the observation is deleted"""
    if instance.demodulated_data:
        instance.demodulated_data.delete(save=False)
