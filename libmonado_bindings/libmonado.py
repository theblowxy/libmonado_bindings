"""
Low-level ctypes bindings for libmonado.

This module provides direct access to the Monado C API through ctypes.
For most use cases, use the high-level Monado class instead.
"""

import ctypes
import json
import os
from pathlib import Path
from typing import Optional

from .errors import MonadoConnectionError, MonadoVersionError, MonadoError
from .types import (
    MndResult,
    ClientState,
    MndProperty,
    DeviceRole,
    MIN_API_VERSION_MAJOR,
    MIN_API_VERSION_MINOR,
)
from .client import Client
from .device import Device, BatteryStatus


class LibMonado:
    """
    Low-level wrapper around libmonado.so using ctypes.
    
    This class handles library loading, function signatures, and
    provides a Pythonic interface to the C API.
    """
    
    def __init__(self, library_path: str):
        """
        Load and initialize libmonado.
        
        Args:
            library_path: Path to libmonado.so
            
        Raises:
            MonadoConnectionError: If library loading or connection fails
        """
        self._lib = None
        self._root = ctypes.c_void_p(0)
        self._closed = False
        
        try:
            self._lib = ctypes.CDLL(library_path)
        except OSError as e:
            raise MonadoConnectionError(f"Failed to load library: {e}")
        
        self._setup_function_signatures()
        self._check_version()
        self._connect()
    
    def _setup_function_signatures(self) -> None:
        """Setup ctypes function signatures for all Monado API functions."""
        lib = self._lib
        
        # API version
        lib.mnd_api_get_version.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.mnd_api_get_version.restype = ctypes.c_int
        
        # Root management
        lib.mnd_root_create.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        lib.mnd_root_create.restype = ctypes.c_int
        
        lib.mnd_root_destroy.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        lib.mnd_root_destroy.restype = None
        
        # Client management
        lib.mnd_root_update_client_list.argtypes = [ctypes.c_void_p]
        lib.mnd_root_update_client_list.restype = ctypes.c_int
        
        lib.mnd_root_get_number_clients.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.mnd_root_get_number_clients.restype = ctypes.c_int
        
        lib.mnd_root_get_client_id_at_index.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.mnd_root_get_client_id_at_index.restype = ctypes.c_int
        
        lib.mnd_root_get_client_name.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.mnd_root_get_client_name.restype = ctypes.c_int
        
        lib.mnd_root_get_client_state.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.mnd_root_get_client_state.restype = ctypes.c_int
        
        lib.mnd_root_set_client_primary.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        lib.mnd_root_set_client_primary.restype = ctypes.c_int
        
        lib.mnd_root_set_client_focused.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        lib.mnd_root_set_client_focused.restype = ctypes.c_int
        
        lib.mnd_root_toggle_client_io_active.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        lib.mnd_root_toggle_client_io_active.restype = ctypes.c_int
        
        # Device management
        lib.mnd_root_get_device_count.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.mnd_root_get_device_count.restype = ctypes.c_int
        
        lib.mnd_root_get_device_info.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.mnd_root_get_device_info.restype = ctypes.c_int
        
        lib.mnd_root_get_device_from_role.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.mnd_root_get_device_from_role.restype = ctypes.c_int
        
        # Device info getters
        lib.mnd_root_get_device_info_bool.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,  # MndProperty
            ctypes.POINTER(ctypes.c_bool),
        ]
        lib.mnd_root_get_device_info_bool.restype = ctypes.c_int
        
        lib.mnd_root_get_device_info_u32.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.mnd_root_get_device_info_u32.restype = ctypes.c_int
        
        lib.mnd_root_get_device_info_i32.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_int32),
        ]
        lib.mnd_root_get_device_info_i32.restype = ctypes.c_int
        
        lib.mnd_root_get_device_info_float.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_float),
        ]
        lib.mnd_root_get_device_info_float.restype = ctypes.c_int
        
        lib.mnd_root_get_device_info_string.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.mnd_root_get_device_info_string.restype = ctypes.c_int
        
        # Battery and brightness
        lib.mnd_root_get_device_battery_status.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_bool),
            ctypes.POINTER(ctypes.c_bool),
            ctypes.POINTER(ctypes.c_float),
        ]
        lib.mnd_root_get_device_battery_status.restype = ctypes.c_int
        
        lib.mnd_root_get_device_brightness.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_float),
        ]
        lib.mnd_root_get_device_brightness.restype = ctypes.c_int
        
        lib.mnd_root_set_device_brightness.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_float,
            ctypes.c_bool,
        ]
        lib.mnd_root_set_device_brightness.restype = ctypes.c_int
        
        # Space management
        lib.mnd_root_recenter_local_spaces.argtypes = [ctypes.c_void_p]
        lib.mnd_root_recenter_local_spaces.restype = ctypes.c_int
        
        lib.mnd_root_get_tracking_origin_count.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        lib.mnd_root_get_tracking_origin_count.restype = ctypes.c_int
        
        lib.mnd_root_get_tracking_origin_name.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        lib.mnd_root_get_tracking_origin_name.restype = ctypes.c_int
    
    def _check_version(self) -> None:
        """Check if the library version is compatible."""
        major = ctypes.c_int(0)
        minor = ctypes.c_int(0)
        patch = ctypes.c_int(0)
        
        result = self._lib.mnd_api_get_version(
            ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)
        )
        
        if result != MndResult.Success:
            raise MonadoVersionError("Failed to get API version")
        
        if major.value < MIN_API_VERSION_MAJOR or (
            major.value == MIN_API_VERSION_MAJOR
            and minor.value < MIN_API_VERSION_MINOR
        ):
            raise MonadoVersionError(
                f"Incompatible API version: {major.value}.{minor.value}.{patch.value} "
                f"(requires >= {MIN_API_VERSION_MAJOR}.{MIN_API_VERSION_MINOR}.0)"
            )
        
        self._version = (major.value, minor.value, patch.value)
    
    def _connect(self) -> None:
        """Create the root connection to Monado."""
        result = self._lib.mnd_root_create(ctypes.byref(self._root))
        
        if result != MndResult.Success or not self._root:
            raise MonadoConnectionError(
                f"Failed to connect to Monado (error {result}). Is Monado running?"
            )
    
    @classmethod
    def auto_connect(cls) -> "LibMonado":
        """
        Automatically find and connect to Monado.
        
        Tries the following in order:
        1. LIBMONADO_PATH environment variable
        2. XR_RUNTIME_JSON environment variable
        3. XDG config directories
        4. Envision build directory (~/.local/share/envision/monado/build/src/xrt/targets/libmonado/libmonado.so)
        
        If a version error occurs with one path, it will try other available paths.
        
        Returns:
            Connected LibMonado instance
            
        Raises:
            MonadoConnectionError: If connection fails or no library found
            MonadoVersionError: If all found libraries have version mismatches
        """
        # Check LIBMONADO_PATH first (requires validation)
        if "LIBMONADO_PATH" in os.environ:
            path = os.environ["LIBMONADO_PATH"]
            if os.path.isfile(path):
                try:
                    return cls(path)
                except MonadoVersionError:
                    pass  # Will try other paths below
            else:
                raise MonadoConnectionError(
                    f"LIBMONADO_PATH points to non-existent file: {path}"
                )
        
        # Get all candidate paths and try them
        candidate_paths = cls._find_all_library_paths()
        
        if not candidate_paths:
            raise MonadoConnectionError(
                "Could not find Monado runtime. "
                "Set LIBMONADO_PATH or XR_RUNTIME_JSON environment variable."
            )
        
        version_errors = []
        connection_errors = []
        
        for lib_path in candidate_paths:
            try:
                return cls(lib_path)
            except MonadoVersionError as e:
                version_errors.append(f"  - {lib_path}: {e}")
            except MonadoConnectionError as e:
                connection_errors.append(f"  - {lib_path}: {e}")
        
        # All paths failed - raise comprehensive error
        error_msg = "Failed to connect to Monado.\n"
        if version_errors:
            error_msg += "\nVersion mismatches:\n" + "\n".join(version_errors)
        if connection_errors:
            error_msg += "\nConnection failures:\n" + "\n".join(connection_errors)
        
        raise MonadoConnectionError(error_msg)
    
    @classmethod
    def find_library_path(cls) -> Optional[str]:
        """
        Find the first available path to libmonado.so without loading it.
        
        Tries the same search order as auto_connect():
        1. LIBMONADO_PATH environment variable
        2. XR_RUNTIME_JSON environment variable
        3. XDG config directories
        4. Envision build directory
        
        Returns:
            Path to libmonado.so if found, None otherwise
        """
        paths = cls._find_all_library_paths()
        return paths[0] if paths else None
    
    @classmethod
    def _find_all_library_paths(cls) -> list[str]:
        """
        Find all candidate paths to libmonado.so without loading.
        
        Returns:
            List of paths to libmonado.so candidates (may be empty)
        """
        candidates = []
        
        # Try LIBMONADO_PATH first
        if "LIBMONADO_PATH" in os.environ:
            path = os.environ["LIBMONADO_PATH"]
            if os.path.isfile(path):
                candidates.append(path)
        
        # Try XR_RUNTIME_JSON
        if "XR_RUNTIME_JSON" in os.environ:
            runtime_path = Path(os.environ["XR_RUNTIME_JSON"])
            lib_path = cls._resolve_runtime_library(runtime_path)
            if lib_path:
                candidates.append(str(lib_path))
        
        # Try XDG config directories
        xdg_config_home = os.environ.get(
            "XDG_CONFIG_HOME", Path.home() / ".config"
        )
        
        search_paths = [
            Path(xdg_config_home) / "openxr" / "1" / "active_runtime.json",
        ]
        
        for config_dir in ["/etc/xdg", "/usr/local/share", "/usr/share"]:
            search_paths.append(
                Path(config_dir) / "openxr" / "1" / "active_runtime.json"
            )
        
        for runtime_path in search_paths:
            if runtime_path.exists():
                lib_path = cls._resolve_runtime_library(runtime_path)
                if lib_path:
                    candidates.append(str(lib_path))
        
        # Try common system library paths
        system_lib_paths = [
            "/usr/lib/libmonado.so",
            "/usr/local/lib/libmonado.so",
            "/usr/lib64/libmonado.so",
        ]
        for lib_path in system_lib_paths:
            if os.path.isfile(lib_path):
                candidates.append(lib_path)
        
        # Try Envision directories with glob patterns
        envision_base = Path.home() / ".local" / "share" / "envision"
        
        if envision_base.exists():
            # Pattern: */xrservice/build/src/xrt/targets/libmonado/libmonado.so
            for pattern in envision_base.glob("*/xrservice/build/src/xrt/targets/libmonado/libmonado.so"):
                if pattern.is_file():
                    candidates.append(str(pattern))
            
            # Pattern: prefixes/*/lib/libmonado.so
            prefixes_dir = envision_base / "prefixes"
            if prefixes_dir.exists():
                for pattern in prefixes_dir.glob("*/lib/libmonado.so"):
                    if pattern.is_file():
                        candidates.append(str(pattern))
        
        # Try legacy Envision build directory (fallback)
        envision_path = envision_base / "monado" / "build" / "src" / "xrt" / "targets" / "libmonado" / "libmonado.so"
        if envision_path.exists():
            candidates.append(str(envision_path))
        
        return candidates
    
    @staticmethod
    def _resolve_runtime_library(runtime_json_path: Path) -> Optional[Path]:
        """Resolve the library path from a runtime JSON file."""
        try:
            with open(runtime_json_path) as f:
                runtime_info = json.load(f)
            
            # Get the library path from the runtime info
            lib_path_str = runtime_info.get("runtime", {}).get(
                "MND_libmonado_path"
            )
            if not lib_path_str:
                return None
            
            # Resolve relative to the runtime.json directory
            runtime_dir = runtime_json_path.parent.resolve()
            lib_path = runtime_dir / lib_path_str
            
            if lib_path.exists():
                return lib_path
            
            # Try as absolute path
            lib_path = Path(lib_path_str)
            if lib_path.exists():
                return lib_path
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
        
        return None
    
    def _check_result(self, result: int) -> None:
        """Check a result code and raise appropriate exception if error."""
        if result == MndResult.Success:
            return

        error_messages = {
            MndResult.ErrorInvalidVersion: "Invalid API version",
            MndResult.ErrorInvalidValue: "Invalid value provided",
            MndResult.ErrorConnectingFailed: "Failed to connect",
            MndResult.ErrorOperationFailed: "Operation failed",
            MndResult.ErrorRecenteringNotSupported: "Recentering not supported",
            MndResult.ErrorInvalidProperty: "Invalid property",
            MndResult.ErrorInvalidOperation: "Invalid operation",
            MndResult.ErrorUnsupportedOperation: "Operation not supported",
        }

        message = error_messages.get(
            result, f"Unknown error (code {result})"
        )
        raise MonadoError(message)
    
    def get_api_version(self) -> tuple[int, int, int]:
        """Get the library API version."""
        return self._version
    
    def update_client_list(self) -> None:
        """Update the internal client list. Call before getting clients."""
        result = self._lib.mnd_root_update_client_list(self._root)
        self._check_result(result)
    
    def get_number_clients(self) -> int:
        """Get the number of connected clients."""
        count = ctypes.c_uint32(0)
        result = self._lib.mnd_root_get_number_clients(
            self._root, ctypes.byref(count)
        )
        self._check_result(result)
        return count.value
    
    def get_clients(self) -> list[Client]:
        """Get a list of all connected clients."""
        self.update_client_list()
        count = self.get_number_clients()
        
        clients = []
        for i in range(count):
            client_id = ctypes.c_uint32(0)
            result = self._lib.mnd_root_get_client_id_at_index(
                self._root, i, ctypes.byref(client_id)
            )
            self._check_result(result)
            clients.append(Client(self, client_id.value))
        
        return clients
    
    def get_client_name(self, client_id: int) -> str:
        """Get the name of a client."""
        name_ptr = ctypes.c_char_p()
        result = self._lib.mnd_root_get_client_name(
            self._root, client_id, ctypes.byref(name_ptr)
        )
        self._check_result(result)
        return name_ptr.value.decode("utf-8") if name_ptr.value else ""
    
    def get_client_state(self, client_id: int) -> ClientState:
        """Get the state flags of a client."""
        state = ctypes.c_uint32(0)
        result = self._lib.mnd_root_get_client_state(
            self._root, client_id, ctypes.byref(state)
        )
        self._check_result(result)
        return ClientState(state.value)
    
    def set_client_primary(self, client_id: int) -> None:
        """Set a client as the primary client."""
        result = self._lib.mnd_root_set_client_primary(self._root, client_id)
        self._check_result(result)
    
    def set_client_focused(self, client_id: int) -> None:
        """Set a client as the focused client."""
        result = self._lib.mnd_root_set_client_focused(self._root, client_id)
        self._check_result(result)
    
    def toggle_client_io_active(self, client_id: int) -> None:
        """Toggle IO active state for a client."""
        result = self._lib.mnd_root_toggle_client_io_active(
            self._root, client_id
        )
        self._check_result(result)
    
    def get_device_count(self) -> int:
        """Get the number of devices."""
        count = ctypes.c_uint32(0)
        result = self._lib.mnd_root_get_device_count(
            self._root, ctypes.byref(count)
        )
        self._check_result(result)
        return count.value
    
    def get_device_info(self, index: int) -> tuple[int, str]:
        """Get device info (name_id, name)."""
        name_id = ctypes.c_uint32(0)
        name_ptr = ctypes.c_char_p()
        result = self._lib.mnd_root_get_device_info(
            self._root, index, ctypes.byref(name_id), ctypes.byref(name_ptr)
        )
        self._check_result(result)
        name = name_ptr.value.decode("utf-8") if name_ptr.value else ""
        return name_id.value, name
    
    def get_devices(self) -> list[Device]:
        """Get a list of all devices."""
        count = self.get_device_count()
        devices = []
        
        for i in range(count):
            name_id, name = self.get_device_info(i)
            devices.append(Device(self, i, name_id, name))
        
        return devices
    
    def get_device_from_role(self, role: str) -> Device:
        """Get a device by its role name."""
        index = ctypes.c_int(-1)
        c_name = role.encode("utf-8")
        result = self._lib.mnd_root_get_device_from_role(
            self._root, c_name, ctypes.byref(index)
        )
        self._check_result(result)
        
        if index.value == -1:
            raise MonadoError(f"No device found for role: {role}")
        
        name_id, name = self.get_device_info(index.value)
        return Device(self, index.value, name_id, name)
    
    def get_device_battery_status(self, index: int) -> BatteryStatus:
        """Get battery status for a device."""
        present = ctypes.c_bool()
        charging = ctypes.c_bool()
        charge = ctypes.c_float()
        
        result = self._lib.mnd_root_get_device_battery_status(
            self._root,
            index,
            ctypes.byref(present),
            ctypes.byref(charging),
            ctypes.byref(charge),
        )
        self._check_result(result)
        
        return BatteryStatus(
            present=present.value,
            charging=charging.value,
            charge=charge.value,
        )
    
    def get_device_brightness(self, index: int) -> float:
        """Get brightness for a device."""
        brightness = ctypes.c_float()
        result = self._lib.mnd_root_get_device_brightness(
            self._root, index, ctypes.byref(brightness)
        )
        self._check_result(result)
        return brightness.value
    
    def set_device_brightness(self, index: int, brightness: float, relative: bool = False) -> None:
        """Set brightness for a device."""
        result = self._lib.mnd_root_set_device_brightness(
            self._root, index, brightness, relative
        )
        self._check_result(result)
    
    def get_device_info_bool(self, index: int, prop: MndProperty) -> bool:
        """Get a boolean property for a device."""
        value = ctypes.c_bool()
        result = self._lib.mnd_root_get_device_info_bool(
            self._root, index, prop.value, ctypes.byref(value)
        )
        self._check_result(result)
        return value.value
    
    def get_device_info_u32(self, index: int, prop: MndProperty) -> int:
        """Get a u32 property for a device."""
        value = ctypes.c_uint32()
        result = self._lib.mnd_root_get_device_info_u32(
            self._root, index, prop.value, ctypes.byref(value)
        )
        self._check_result(result)
        return value.value
    
    def get_device_info_i32(self, index: int, prop: MndProperty) -> int:
        """Get an i32 property for a device."""
        value = ctypes.c_int32()
        result = self._lib.mnd_root_get_device_info_i32(
            self._root, index, prop.value, ctypes.byref(value)
        )
        self._check_result(result)
        return value.value
    
    def get_device_info_float(self, index: int, prop: MndProperty) -> float:
        """Get a float property for a device."""
        value = ctypes.c_float()
        result = self._lib.mnd_root_get_device_info_float(
            self._root, index, prop.value, ctypes.byref(value)
        )
        self._check_result(result)
        return value.value
    
    def get_device_info_string(self, index: int, prop: MndProperty) -> str:
        """Get a string property for a device."""
        value = ctypes.c_char_p()
        result = self._lib.mnd_root_get_device_info_string(
            self._root, index, prop.value, ctypes.byref(value)
        )
        self._check_result(result)
        if value.value:
            return value.value.decode("utf-8")
        return ""
    
    def recenter_local_spaces(self) -> None:
        """Recenter the local tracking spaces."""
        result = self._lib.mnd_root_recenter_local_spaces(self._root)
        self._check_result(result)
    
    def close(self) -> None:
        """Close the connection and cleanup resources."""
        if not self._closed and self._lib and self._root:
            self._lib.mnd_root_destroy(ctypes.byref(self._root))
            self._closed = True
    
    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        try:
            self.close()
        except:
            pass
