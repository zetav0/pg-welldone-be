from pathlib import Path

from core.envs import settings

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = settings.DEBUG

INSTALLED_APPS = [
    "models.apps.DatabaseConfig",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
]

TIME_ZONE = "America/Lima"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_DB_TIMEZONE = "Etc/GMT+5"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "TIME_ZONE": _DB_TIMEZONE,
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]
