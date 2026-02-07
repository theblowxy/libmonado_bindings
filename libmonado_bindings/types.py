"""
Type definitions, constants, and enums for libmonado.

Based on the Rust bindings and C API from libmonado.
"""
from enum import IntEnum, IntFlag
from typing import Final


class MndResult(IntEnum):
    """Result codes from Monado API calls."""
    Success = 0
    ErrorConnectingFailed = -1
    ErrorInvalidVersion = -2
    ErrorInvalidValue = -3
    ErrorInvalidClientId = -4
    ErrorInvalidDeviceId = -5
    ErrorInvalidTrackingOriginId = -6
    ErrorInvalidSpaceId = -7
    ErrorInvalidSwapchainId = -8
    ErrorInvalidSemaphoreId = -9
    ErrorInvalidReferenceSpaceType = -10
    ErrorInvalidFormFactor = -11
    ErrorInvalidViewConfigurationType = -12
    ErrorInvalidEnvironmentBlendMode = -13
    ErrorInvalidInteractionProfile = -14
    ErrorInvalidActionSet = -15
    ErrorInvalidAction = -16
    ErrorInvalidPose = -17
    ErrorInvalidIndex = -18
    ErrorUnsupportedOperation = -19
    ErrorAllocationFailure = -20
    ErrorFeatureNotSupported = -21
    ErrorExtensionNotEnabled = -22
    ErrorNameInvalid = -23
    ErrorNameDuplicate = -24


class ClientState(IntFlag):
    """Client state flags."""
    ClientPrimary = 1 << 0
    ClientFocused = 1 << 1
    ClientIoActive = 1 << 2
    ClientVisible = 1 << 3


class BlockFlags(IntFlag):
    """IO block flags for clients."""
    BlockNone = 0
    BlockInput = 1 << 0
    BlockOutput = 1 << 1


class MndProperty(IntEnum):
    """Device property types for get_info_* functions."""
    # Boolean properties
    PropertyHeadMountedDisplayBool = 0
    PropertyControllerBool = 1
    PropertyHandTrackingBool = 2
    PropertyEyeTrackingBool = 3
    PropertyFaceTrackingBool = 4
    PropertyBodyTrackingBool = 5
    PropertyForceFeedbackBool = 6
    PropertyVibrationBool = 7
    PropertyBatterySupportedBool = 8
    PropertyBrightnessSupportedBool = 9
    PropertyCanOrientBool = 10
    PropertyCanPositionBool = 11
    PropertyCanPoseBool = 12
    PropertyCanDetectHandBool = 13
    
    # u32 properties
    PropertyVendorIdU32 = 100
    PropertyProductIdU32 = 101
    PropertyDeviceTypeU32 = 102
    
    # i32 properties
    PropertyControllerRoleI32 = 200
    
    # Float properties
    PropertyDisplayRefreshRateFloat = 300
    PropertyRecommendedRenderWidthFloat = 301
    PropertyRecommendedRenderHeightFloat = 302
    PropertyFieldOfViewLeftFloat = 303
    PropertyFieldOfViewRightFloat = 304
    PropertyFieldOfViewUpFloat = 305
    PropertyFieldOfViewDownFloat = 306
    PropertyInterpupillaryDistanceFloat = 307
    
    # String properties
    PropertySerialString = 400
    PropertyModelString = 401
    PropertyManufacturerString = 402


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
