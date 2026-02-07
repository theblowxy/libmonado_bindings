"""
Type definitions, constants, and enums for libmonado.

Based on the Rust bindings and C API from libmonado.
"""
from enum import IntEnum, IntFlag
from typing import Final


class MndResult(IntEnum):
    """Result codes from Monado API calls."""
    Success = 0
    ErrorInvalidVersion = -1
    ErrorInvalidValue = -2
    ErrorConnectingFailed = -3
    ErrorOperationFailed = -4
    ErrorRecenteringNotSupported = -5
    ErrorInvalidProperty = -6
    ErrorInvalidOperation = -7
    ErrorUnsupportedOperation = -8


class ClientState(IntFlag):
    """Client state flags."""
    ClientPrimaryApp = 1 << 0
    ClientSessionActive = 1 << 1
    ClientSessionVisible = 1 << 2
    ClientSessionFocused = 1 << 3
    ClientSessionOverlay = 1 << 4
    ClientIoActive = 1 << 5
    ClientPosesBlocked = 1 << 6
    ClientHtBlocked = 1 << 7
    ClientInputsBlocked = 1 << 8
    ClientOutputsBlocked = 1 << 9


class BlockFlags(IntFlag):
    """IO block flags for clients."""
    BlockNone = 0
    BlockPoses = 1 << 0
    BlockHt = 1 << 1
    BlockInputs = 1 << 2
    BlockOutputs = 1 << 3


class MndProperty(IntEnum):
    """Device property types for get_info_* functions."""
    # String properties
    PropertyNameString = 0
    PropertySerialString = 1

    # u32 properties
    PropertyTrackingOriginU32 = 2

    # Boolean properties
    PropertySupportsPositionBool = 3
    PropertySupportsOrientationBool = 4
    PropertySupportsBrightnessBool = 5


class DeviceRole:
    """Device role names as used by Monado."""
    HEAD: Final[str] = "head"
    EYES: Final[str] = "eyes"
    LEFT: Final[str] = "left"
    RIGHT: Final[str] = "right"
    GAMEPAD: Final[str] = "gamepad"
    HAND_TRACKING_LEFT: Final[str] = "hand-tracking-left"
    HAND_TRACKING_RIGHT: Final[str] = "hand-tracking-right"


# API version requirements
MIN_API_VERSION_MAJOR: Final[int] = 1
MIN_API_VERSION_MINOR: Final[int] = 5
MIN_API_VERSION_PATCH: Final[int] = 0
