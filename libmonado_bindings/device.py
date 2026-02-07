"""
Device class for managing VR devices in Monado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .types import MndProperty, DeviceRole as _DeviceRole
from .errors import MonadoError

if TYPE_CHECKING:
    from .libmonado import LibMonado


@dataclass
class BatteryStatus:
    """
    Battery status information for a device.
    
    Attributes:
        present: Whether a battery is present
        charging: Whether the battery is currently charging
        charge: Battery charge level (0.0 to 1.0)
    """
    present: bool
    charging: bool
    charge: float
    
    def __repr__(self) -> str:
        if not self.present:
            return "BatteryStatus(present=False)"
        status = "charging" if self.charging else "discharging"
        return f"BatteryStatus({status}, {self.charge:.0%})"


class DeviceRole:
    """
    Convenience class for device role constants.
    
    These match the role strings used by Monado internally.
    """
    HEAD = _DeviceRole.HEAD
    EYES = _DeviceRole.EYES
    LEFT = _DeviceRole.LEFT
    RIGHT = _DeviceRole.RIGHT
    GAMEPAD = _DeviceRole.GAMEPAD
    HAND_TRACKING_LEFT = _DeviceRole.HAND_TRACKING_LEFT
    HAND_TRACKING_RIGHT = _DeviceRole.HAND_TRACKING_RIGHT


class Device:
    """
    Represents a VR device managed by Monado.
    
    This could be a headset, controller, tracker, or other VR hardware.
    """
    
    def __init__(
        self,
        libmonado: "LibMonado",
        index: int,
        name_id: int,
        name: str,
    ):
        """
        Initialize a Device instance.
        
        Args:
            libmonado: The LibMonado instance
            index: The device index
            name_id: The device name ID (xrt_device_name enum value)
            name: The human-readable device name
        """
        self._lib = libmonado
        self._index = index
        self._name_id = name_id
        self._name = name
    
    @property
    def index(self) -> int:
        """The device index."""
        return self._index
    
    @property
    def name_id(self) -> int:
        """The device name ID (xrt_device_name enum value)."""
        return self._name_id
    
    @property
    def name(self) -> str:
        """The human-readable device name."""
        return self._name
    
    def battery_status(self) -> BatteryStatus:
        """
        Get the battery status for this device.
        
        Returns:
            BatteryStatus with present, charging, and charge level
        """
        return self._lib.get_device_battery_status(self._index)
    
    def brightness(self) -> float:
        """
        Get the brightness level for this device.
        
        Returns:
            Brightness level (0.0 to 1.0)
        """
        return self._lib.get_device_brightness(self._index)
    
    def set_brightness(self, brightness: float, relative: bool = False) -> None:
        """
        Set the brightness level for this device.
        
        Args:
            brightness: Brightness level (0.0 to 1.0, or delta if relative)
            relative: If True, brightness is interpreted as a relative change
        """
        self._lib.set_device_brightness(self._index, brightness, relative)
    
    def serial(self) -> str:
        """
        Get the serial number of this device.
        
        Returns:
            Device serial number string
        """
        return self.get_info_string(MndProperty.PropertySerialString)
    
    def model(self) -> str:
        """
        Get the model name of this device.
        
        Returns:
            Device model string
        """
        return self.get_info_string(MndProperty.PropertyModelString)
    
    def manufacturer(self) -> str:
        """
        Get the manufacturer of this device.
        
        Returns:
            Device manufacturer string
        """
        return self.get_info_string(MndProperty.PropertyManufacturerString)
    
    def get_info_bool(self, property: MndProperty) -> bool:
        """
        Get a boolean property for this device.
        
        Args:
            property: The property to query (must be a boolean property)
            
        Returns:
            The property value
        """
        return self._lib.get_device_info_bool(self._index, property)
    
    def get_info_u32(self, property: MndProperty) -> int:
        """
        Get a u32 property for this device.
        
        Args:
            property: The property to query (must be a u32 property)
            
        Returns:
            The property value
        """
        return self._lib.get_device_info_u32(self._index, property)
    
    def get_info_i32(self, property: MndProperty) -> int:
        """
        Get an i32 property for this device.
        
        Args:
            property: The property to query (must be an i32 property)
            
        Returns:
            The property value
        """
        return self._lib.get_device_info_i32(self._index, property)
    
    def get_info_float(self, property: MndProperty) -> float:
        """
        Get a float property for this device.
        
        Args:
            property: The property to query (must be a float property)
            
        Returns:
            The property value
        """
        return self._lib.get_device_info_float(self._index, property)
    
    def get_info_string(self, property: MndProperty) -> str:
        """
        Get a string property for this device.
        
        Args:
            property: The property to query (must be a string property)
            
        Returns:
            The property value
        """
        return self._lib.get_device_info_string(self._index, property)
    
    # Convenience properties
    @property
    def is_head_mounted_display(self) -> bool:
        """Check if this device is a head-mounted display."""
        return self.get_info_bool(MndProperty.PropertyHeadMountedDisplayBool)
    
    @property
    def is_controller(self) -> bool:
        """Check if this device is a controller."""
        return self.get_info_bool(MndProperty.PropertyControllerBool)
    
    @property
    def supports_hand_tracking(self) -> bool:
        """Check if this device supports hand tracking."""
        return self.get_info_bool(MndProperty.PropertyHandTrackingBool)
    
    @property
    def supports_eye_tracking(self) -> bool:
        """Check if this device supports eye tracking."""
        return self.get_info_bool(MndProperty.PropertyEyeTrackingBool)
    
    @property
    def supports_battery(self) -> bool:
        """Check if this device has battery support."""
        return self.get_info_bool(MndProperty.PropertyBatterySupportedBool)
    
    @property
    def supports_brightness(self) -> bool:
        """Check if this device has brightness control."""
        return self.get_info_bool(MndProperty.PropertyBrightnessSupportedBool)
    
    @property
    def vendor_id(self) -> int:
        """Get the USB vendor ID of this device."""
        return self.get_info_u32(MndProperty.PropertyVendorIdU32)
    
    @property
    def product_id(self) -> int:
        """Get the USB product ID of this device."""
        return self.get_info_u32(MndProperty.PropertyProductIdU32)
    
    @property
    def display_refresh_rate(self) -> float:
        """Get the display refresh rate (for HMDs)."""
        return self.get_info_float(MndProperty.PropertyDisplayRefreshRateFloat)
    
    def __repr__(self) -> str:
        """String representation of the device."""
        return f"Device(index={self._index}, name_id={self._name_id}, name='{self._name}')"
    
    def __eq__(self, other: object) -> bool:
        """Check if two devices are the same."""
        if not isinstance(other, Device):
            return NotImplemented
        return self._index == other._index
    
    def __hash__(self) -> int:
        """Hash based on device index."""
        return hash(self._index)
