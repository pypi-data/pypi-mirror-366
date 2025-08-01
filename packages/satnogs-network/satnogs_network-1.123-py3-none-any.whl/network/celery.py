# pylint: disable=C0415
"""SatNOGS Network celery task workers"""
import os

from celery import Celery
from django.conf import settings  # noqa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'network.settings')

RUN_DAILY = 60 * 60 * 24
RUN_EVERY_TWO_HOURS = 2 * 60 * 60
RUN_HOURLY = 60 * 60
RUN_EVERY_15_MINUTES = 60 * 15
RUN_TWICE_HOURLY = 60 * 30
RUN_EVERY_FOUR_HOURS = 60 * 60 * 4

APP = Celery('network')

APP.config_from_object('django.conf:settings', namespace='CELERY')
APP.autodiscover_tasks()


# Wrapper tasks as workaround for registering shared tasks to beat scheduler
# See https://github.com/celery/celery/issues/5059
# and https://github.com/celery/celery/issues/3797#issuecomment-422656038
@APP.task
def refresh_transmitters_with_stats_cache():
    """Wrapper task for 'refresh_transmitters_with_stats_cache' shared task"""
    from network.base.tasks import get_and_refresh_transmitters_with_stats_cache as periodic_task
    periodic_task()


@APP.task
def update_future_observations_with_new_tle_sets():
    """Wrapper task for 'update_future_observations_with_new_tle_sets' shared task"""
    from network.base.tasks import update_future_observations_with_new_tle_sets as periodic_task
    periodic_task()


@APP.task
def update_future_observations_with_new_transmitter_details():
    """Wrapper task for 'update_future_observations_with_new_transmitter_details' shared task"""
    from network.base.tasks import (  # isort:skip
        update_future_observations_with_new_transmitter_details as periodic_task)
    periodic_task()


@APP.task
def fetch_satellites():
    """Wrapper task for 'fetch_satellites' shared task"""
    from network.base.tasks import fetch_satellites as periodic_task
    periodic_task()


@APP.task
def clean_observations():
    """Wrapper task for 'clean_observations' shared task"""
    from network.base.tasks import clean_observations as periodic_task
    periodic_task()


@APP.task
def station_status_update():
    """Wrapper task for 'station_status_update' shared task"""
    from network.base.tasks import station_status_update as periodic_task
    periodic_task()


@APP.task
def notify_for_stations_without_results():
    """Wrapper task for 'notify_for_stations_without_results' shared task"""
    from network.base.tasks import notify_for_stations_without_results as periodic_task
    periodic_task()


@APP.task
def zip_audio_files():
    """Wrapper task for 'zip_audio_files' shared task"""
    from network.base.tasks import zip_audio_files as periodic_task
    periodic_task()


@APP.task
def archive_audio_zip_files():
    """Wrapper task for 'archive_audio_zip_files' shared task"""
    from network.base.tasks import archive_audio_zip_files as periodic_task
    periodic_task()


@APP.task
def find_and_rate_failed_observations():
    """Wrapper task for 'find_and_rate_failed_observations' shared task"""
    from network.base.rating_tasks import find_and_rate_failed_observations as periodic_task
    periodic_task()


@APP.task
def sync_to_db():
    """Wrapper task for 'sync_to_db' shared task"""
    from network.base.tasks import sync_to_db as periodic_task
    periodic_task()


@APP.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):  # pylint: disable=W0613
    """Initializes celery tasks that need to run on a scheduled basis"""
    sender.add_periodic_task(
        RUN_TWICE_HOURLY,
        update_future_observations_with_new_tle_sets.s(),
        name='update_future_observations_with_new_tle_sets'
    )

    sender.add_periodic_task(
        RUN_TWICE_HOURLY,
        update_future_observations_with_new_transmitter_details.s(),
        name='update_future_observations_with_new_transmitter_details'
    )

    sender.add_periodic_task(
        RUN_EVERY_FOUR_HOURS,
        refresh_transmitters_with_stats_cache.s(),
        name='refresh_transmitters_with_stats_cache'
    )

    sender.add_periodic_task(RUN_HOURLY, fetch_satellites.s(), name='fetch_satellites')

    sender.add_periodic_task(RUN_HOURLY, sync_to_db.s(), name='sync_to_db')

    sender.add_periodic_task(RUN_HOURLY, station_status_update.s(), name='station_status_update')

    sender.add_periodic_task(
        settings.OBS_NO_RESULTS_CHECK_PERIOD,
        notify_for_stations_without_results.s(),
        name='notify_for_stations_without_results'
    )

    if settings.ARCHIVE_ZIP_FILES and not settings.USE_S3_STORAGE_FOR_AUDIO:
        sender.add_periodic_task(
            RUN_HOURLY, archive_audio_zip_files.s(), name='archive_audio_zip_files'
        )

    if settings.ZIP_AUDIO_FILES and not settings.USE_S3_STORAGE_FOR_AUDIO:
        sender.add_periodic_task(RUN_EVERY_15_MINUTES, zip_audio_files.s(), name='zip_audio_files')

    sender.add_periodic_task(
        RUN_EVERY_15_MINUTES,
        find_and_rate_failed_observations.s(),
        name='find_and_rate_failed_observations'
    )
