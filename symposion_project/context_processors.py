import datetime


def current_utc_datetime(request):
    return {
        "current_utc_datetime":
        datetime.datetime.utcnow().isoformat(),
    }
