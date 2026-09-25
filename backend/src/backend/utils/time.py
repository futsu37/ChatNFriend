from datetime import UTC, datetime


def get_datetime_UTC() -> datetime:
    return datetime.now(UTC)