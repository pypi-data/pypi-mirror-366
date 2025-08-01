"""Define functions and settings for the django admin base interface"""
from django.contrib import admin

from network.base.models import ActiveStationConfiguration, Antenna, AntennaType, DemodData, \
    FrequencyRange, Observation, Station, StationConfiguration, StationConfigurationSchema, \
    StationStatusLog, StationType
from network.base.utils import export_as_csv, export_station_status


@admin.register(FrequencyRange)
class FrequenyRangeAdmin(admin.ModelAdmin):
    """Define Frequency Range view in django admin UI"""
    list_display = ('id', 'min_frequency', 'max_frequency', 'antenna', 'antenna_type', 'station')

    def antenna_type(self, obj):
        """Return the antenna type that use this frequency range"""
        return obj.antenna.antenna_type

    def station(self, obj):
        """Return the antenna station that use this frequency range"""
        return str(obj.antenna.station.id) + ' - ' + obj.antenna.station.name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "antenna":
            kwargs["queryset"] = Antenna.objects.order_by('station_id')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AntennaType)
class AntennaTypeAdmin(admin.ModelAdmin):
    """Define Antenna Type view in django admin UI"""
    list_display = ('id', '__str__', 'antenna_count', 'antenna_list', 'station_list')

    def antenna_count(self, obj):
        """Return the number of antennas use this antenna type"""
        return obj.antennas.all().count()

    def antenna_list(self, obj):
        """Return antennas that use the antenna type"""
        return ",\n".join([str(s.id) for s in obj.antennas.all().order_by('id')])

    def station_list(self, obj):
        """Return antennas that use the antenna type"""
        return ",\n".join([str(s.station.id) for s in obj.antennas.all().order_by('id')])


@admin.register(Antenna)
class AntennaAdmin(admin.ModelAdmin):
    """Define Antenna Type view in django admin UI"""
    list_display = ('id', 'antenna_type', 'station', 'ranges_list')

    list_filter = ('antenna_type', 'station')

    def ranges_list(self, obj):
        """Return frequeny ranges for this antenna"""
        return ",\n".join(
            [
                str(s.min_frequency) + ' - ' + str(s.max_frequency)
                for s in obj.frequency_ranges.all()
            ]
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "station":
            kwargs["queryset"] = Station.objects.order_by('id')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StationType)
class StationTypeAdmin(admin.ModelAdmin):
    """Define StationType view in django admin UI"""
    list_display = ('id', 'name')


@admin.register(StationConfigurationSchema)
class StationConfigurationSchemaAdmin(admin.ModelAdmin):
    """Define StationConfigurationSchema view in django admin UI"""
    list_display = ('id', 'name', 'station_type', 'schema')


@admin.register(StationConfiguration)
class StationConfigurationAdmin(admin.ModelAdmin):
    """Define StationConfiguration view in django admin UI"""
    list_display = ('id', 'name', 'station', 'schema', 'active', 'created', 'configuration')
    list_filter = ('station', 'active', 'schema', 'schema__station_type')
    search_fields = ('id', 'name', 'station')


@admin.register(ActiveStationConfiguration)
class ActiveStationConfigurationAdmin(admin.ModelAdmin):
    """Define StationConfiguration view in django admin UI"""
    list_display = ('id', 'name', 'station', 'schema', 'created', 'configuration')
    list_filter = ('station', 'schema', 'schema__station_type')
    search_fields = ('id', 'name', 'station')


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    """Define Station view in django admin UI"""
    list_display = (
        'id', 'name', 'owner', 'get_email', 'lat', 'lng', 'qthlocator', 'client_version',
        'created_date', 'state', 'target_utilization', 'violator_scheduling', 'client_id'
    )
    list_filter = ('status', 'created', 'client_version', 'violator_scheduling')
    search_fields = ('id', 'name', 'owner__username')

    actions = [export_as_csv, export_station_status]
    export_as_csv.short_description = "Export selected as CSV"
    export_station_status.short_description = "Export selected status"

    def created_date(self, obj):
        """Return when the station was created"""
        return obj.created.strftime('%d.%m.%Y, %H:%M')

    def get_email(self, obj):
        """Return station owner email address"""
        if obj.owner:
            return obj.owner.email
        return None

    get_email.admin_order_field = 'email'
    get_email.short_description = 'Owner Email'

    def get_actions(self, request):
        """Return the list of actions for station admin view"""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(StationStatusLog)
class StationStatusLogAdmin(admin.ModelAdmin):
    """Define StationStatusLog view in django admin UI"""
    list_display = ('id', 'station', 'status', 'changed')
    list_filter = ('station', 'status')
    search_fields = ('id', 'station__id')


class DemodDataInline(admin.TabularInline):
    """Define DemodData inline template for use in Observation view in django admin UI"""
    model = DemodData


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    """Define Observation view in django admin UI"""
    list_display = (
        'id', 'author', 'sat_id', 'transmitter_uuid', 'start', 'end', 'archived', 'audio_zipped',
        'status', 'payload', 'waterfall'
    )
    list_filter = ('start', 'end', 'archived', 'audio_zipped', 'status', 'sat_id', 'author')
    search_fields = ('id', 'sat_id', 'author__username')
    inlines = [
        DemodDataInline,
    ]


@admin.register(DemodData)
class DemodDataAdmin(admin.ModelAdmin):
    """Define DemodData view in django admin UI"""
    list_display = ('id', 'observation', 'demodulated_data', 'copied_to_db', 'is_image')
    list_filter = ('copied_to_db', 'is_image')
    search_fields = ('id', 'observation__id')
