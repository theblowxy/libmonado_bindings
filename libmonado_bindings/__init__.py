"""
Python bindings for libmonado - Monado VR runtime control library.

This package provides a Python interface to the Monado VR compositor,
allowing you to monitor and control VR clients and devices.

Example usage:
    >>> from libmonado_bindings import Monado
    >>> monado = Monado.auto_connect()
    >>> for client in monado.clients():
    ...     print(f"Client: {client.name()}")
    >>> for device in monado.devices():
    ...     print(f"Device: {device.name}")
"""

from .libmonado import LibMonado
from .client import Client
from .device import Device, DeviceRole, BatteryStatus
from .errors import MonadoError, MonadoConnectionError, MonadoVersionError
from .types import ClientState, MndProperty, MndResult

__version__ = "0.1.0"
__all__ = [
    "Monado",
    "Client",
    "Device",
    "DeviceRole",
    "BatteryStatus",
    "ClientState",
    "MndProperty",
    "MndResult",
    "MonadoError",
    "MonadoConnectionError",
    "MonadoVersionError",
]


class Monado:
    """
    Main entry point for the libmonado Python bindings.
    
    This class provides a high-level interface to the Monado VR runtime,
    allowing you to enumerate clients and devices, control focus, and
    query device state.
    """
    
    def __init__(self, lib: LibMonado):
        """Initialize with a LibMonado instance."""
        self._lib = lib
    
    @classmethod
    def auto_connect(cls, library_path: str | None = None) -> "Monado":
        """
        Automatically connect to the Monado runtime.
        
        Tries to find and connect to libmonado.so using the following priority:
        1. LIBMONADO_PATH environment variable (highest priority - user override)
        2. Script-provided path (if passed to this function)
        3. XR_RUNTIME_JSON environment variable
        4. XDG config directories (openxr/1/active_runtime.json)
        
        Args:
            library_path: Optional path to libmonado.so. Used if LIBMONADO_PATH 
                         env var is not set. Allows scripts to provide a default
                         while still allowing user override via environment.
        
        Returns:
            Monado: Connected Monado instance
            
        Raises:
            MonadoConnectionError: If connection fails
            
        Example:
            # Script provides default, user can override with env var
            monado = Monado.auto_connect("/usr/lib/libmonado.so.25.1.0")
            
            # Or just auto-detect everything
            monado = Monado.auto_connect()
        """
        import os
        
        # Priority 1: Environment variable (user override)
        if "LIBMONADO_PATH" in os.environ:
            lib = LibMonado(os.environ["LIBMONADO_PATH"])
            return cls(lib)
        
        # Priority 2: Script-provided path
        if library_path is not None:
            lib = LibMonado(library_path)
            return cls(lib)
        
        # Priority 3 & 4: Auto-detect
        lib = LibMonado.auto_connect()
        return cls(lib)
    
    @classmethod
    def connect(cls, library_path: str) -> "Monado":
        """
        Connect to Monado using a specific library path.
        
        Args:
            library_path: Path to libmonado.so
            
        Returns:
            Monado: Connected Monado instance
            
        Raises:
            MonadoConnectionError: If connection fails
        """
        lib = LibMonado(library_path)
        return cls(lib)
    
    def clients(self) -> list[Client]:
        """
        Get a list of all connected OpenXR clients.
        
        Returns:
            List of Client objects
        """
        return self._lib.get_clients()
    
    def devices(self) -> list[Device]:
        """
        Get a list of all VR devices.
        
        Returns:
            List of Device objects
        """
        return self._lib.get_devices()
    
    def device_from_role(self, role: DeviceRole) -> Device:
        """
        Get a device by its role.
        
        Args:
            role: The device role (e.g., DeviceRole.Head, DeviceRole.Left)
            
        Returns:
            Device object
            
        Raises:
            MonadoError: If device not found
        """
        return self._lib.get_device_from_role(role)
    
    def recenter_local_spaces(self) -> None:
        """
        Recenter the local tracking spaces.
        
        This is equivalent to pressing the recenter button on the headset.
        """
        self._lib.recenter_local_spaces()
    
    def get_api_version(self) -> tuple[int, int, int]:
        """
        Get the libmonado API version.
        
        Returns:
            Tuple of (major, minor, patch)
        """
        return self._lib.get_api_version()
    
    def close(self) -> None:
        """Close the connection to Monado."""
        self._lib.close()
    
    def __enter__(self) -> "Monado":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    def __del__(self) -> None:
        """Destructor - ensures cleanup."""
        try:
            self.close()
        except:
            pass
