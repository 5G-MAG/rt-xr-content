import os

from mpegi_sd_validator import schemas


def pytest_configure(config):
    """The MPEG schemas are a dependency: MPEGI_SD_SCHEMAS names a clone; without it the pinned commit is fetched into the cache."""
    try:
        schemas.source()
    except schemas.SchemasUnavailable as e:
        raise SystemExit(f"the tests need the MPEG schemas: {e}")
