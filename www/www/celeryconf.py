import os
import sys
from celery import Celery
from celery import signals
from celery.bin import Option
from pyramid.paster import bootstrap, get_appsettings
from pyramid.scripting import prepare
import transaction


#: The global pyramid registry.
_PYRAMID_REGISTRY = None

#: The Pyramid closer function.
_PYRAMID_CLOSER = None

#: Global celery app for this project.
app = Celery()

# Registry our extra command line option with celery
app.user_options['preload'].add(
    Option('--ini', dest='ini', default='development.ini',
           help='Specifies pyramid configuration file location.'))


# Default celery configuration
app.config_from_object({
    'task_time_limit': 300,
    'worker_max_tasks_per_child': 1000,
    'task_ignore_result': True,
})


#: Environment variables for celery config overrides.
CELERY_ENV_CONFIG = {
    'CELERY_BROKER_URL': 'broker_url',
}


def merge_env_settings(settings, env_config):
    for (env, key) in env_config.items():
        settings[key] = os.environ.get(env, settings.get(key))


def _update_config_from_ini_and_env(celery, settings):
    settings = {
        k[7:]: v
        for (k, v) in settings.items()
        if k.startswith('celery.')
    }
    merge_env_settings(settings, CELERY_ENV_CONFIG)
    celery.conf.update(settings)


def includeme(config):
    _update_config_from_ini_and_env(app, config.get_settings())


@signals.user_preload_options.connect
def on_preload_parsed(options, **kwargs):
    """Load configuration and configure celery.

    This event is triggered after Celery has parsed its command-line
    options.
    """
    pyramid_config = options['ini']
    if not pyramid_config or not os.path.exists(pyramid_config):
        print('You must provide the Pyramid configuration with --ini',
            file=sys.stderr)
        sys.exit(1)
    try:
        settings = get_appsettings(pyramid_config)
    except Exception:
        print('Error loading Pyramid configuration', file=sys.stderr)
        sys.exit(1)
    _update_config_from_ini_and_env(app, settings)


@signals.celeryd_init.connect
def on_celeryd_init(sender, instance, conf, options, **kwargs):
    """Configure Pyramid application.

    This event is triggered after a worker instance completes basic setup,
    but before it processes any tasks.
    """
    global _PYRAMID_REGISTRY, _PYRAMID_CLOSER
    if _PYRAMID_REGISTRY is not None:
        print('Can not initialise celery multiple times')
    try:
        env = bootstrap(options['ini'][0])
    except Exception:
        print('Error initialising Pyramid', file=sys.stderr)
        sys.exit(1)

    _PYRAMID_REGISTRY = env['registry']
    _PYRAMID_CLOSER = env['closer']


@signals.before_task_publish.connect
def on_before_task_publish(body, exchange, routing_key, headers, properties, declare, retry_policy, **kw):
    return


@signals.task_prerun.connect
def on_task_prerun(task_id, task, args, **kwargs):
    """Setup Pyramid environment for a task.

    This event is triggered before a task is executed by the Celery worker. A
    Pyramid context is setup to make it appear as if the task is run in a
    request context.
    """
    env = prepare(registry=_PYRAMID_REGISTRY)
    transaction.begin()


@signals.task_success.connect
def on_task_success(**kw):
    """Commit transaction on task success.

    This event is triggered when a task completes successfully.
    """
    transaction.commit()


@signals.task_retry.connect
@signals.task_failure.connect
@signals.task_revoked.connect
def on_task_failure(**kw):
    """Abort transaction on task errors.
    """
    transaction.abort()


@signals.task_postrun.connect
def on_task_postrun(**kw):
    """End the Pyramid request context.

    This event is triggered after a task finishes running.
    """
    _PYRAMID_CLOSER()
