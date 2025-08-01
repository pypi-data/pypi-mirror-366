import enum

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE


class Unit(enum.IntEnum):
    KIB = 1024
    MIB = KIB * 1024
    GIB = MIB * 1024
