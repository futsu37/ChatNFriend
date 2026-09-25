from datetime import datetime, UTC
def get_datetime_UTC() -> datetime:
    return datetime.now(UTC)