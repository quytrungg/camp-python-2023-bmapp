from celery.schedules import crontab

CELERY_TASK_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ["pickle", "json"]

# if this option is True - celery task will run like default functions,
# not asynchronous
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = False
# Raise error for eager task
CELERY_TASK_EAGER_PROPAGATES = True

# specify connection options for task producer, so it won’t retry forever if
# the broker isn’t available at the first task execution
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "max_retries": 3,
    "socket_timeout": 5,
    "global_keyprefix": "camp-python-2023-bmapp:",
}

# specify the timezone
CELERY_TIMEZONE = "Asia/Ho_Chi_Minh"

CELERY_IMPORTS = [
    "apps.transactions.tasks",
]

CELERY_BEAT_SCHEDULE = {
    "admin_weekly_report": {
        "task": (
            "apps.transactions.tasks.generate_admin_weekly_report"
            ".generate_admin_weekly_report"
        ),
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    "generate_transaction_report": {
        "task": (
            "apps.transactions.tasks.generate_transaction_report."
            "generate_transaction_report"
        ),
        "schedule": crontab(hour=23, minute=59, day_of_week=0),
    },
}
