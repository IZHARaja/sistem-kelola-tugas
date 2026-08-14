from datetime import UTC, datetime


def utc_now():
    """Return a naive UTC timestamp sourced from a timezone-aware clock."""
    return datetime.now(UTC).replace(tzinfo=None)