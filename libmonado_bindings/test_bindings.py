#!/usr/bin/env python3
"""
Test script for libmonado Python bindings.

Usage:
    # Priority 1: Set the library path via environment (user override)
    export LIBMONADO_PATH=/path/to/libmonado.so.25.1.0
    
    # Priority 2: Script provides default, user can override with env var
    # (The script below uses this approach)
    
    # Priority 3: Auto-detect from XR_RUNTIME_JSON or XDG config
    
    # Run this test
    python3 test_bindings.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default path - script provides this, but user can override with LIBMONADO_PATH env var
DEFAULT_LIBMONADO_PATH = "/usr/lib/libmonado.so.25.1.0"  # Adjust to your system

from libmonado_bindings import (
    Monado,
    Client,
    Device,
    DeviceRole,
    ClientState,
    BatteryStatus,
    MndProperty,
    MonadoError,
)


def test_imports():
    """Test that all imports work."""
    print("✓ Imports successful")
    print(f"  - Monado: {Monado}")
    print(f"  - Client: {Client}")
    print(f"  - Device: {Device}")
    print(f"  - DeviceRole: {DeviceRole}")
    print(f"  - ClientState: {ClientState}")
    print(f"  - BatteryStatus: {BatteryStatus}")
    print(f"  - MndProperty: {MndProperty}")
    print()


def test_connect():
    """Test connecting to Monado with priority: Env Var > Script Path > Auto-detect."""
    try:
        if "LIBMONADO_PATH" in os.environ:
            print(f"Priority 1: Using LIBMONADO_PATH={os.environ['LIBMONADO_PATH']}")
            monado = Monado.auto_connect()  # Will use env var
        elif Path(DEFAULT_LIBMONADO_PATH).exists():
            print(f"Priority 2: Using script default: {DEFAULT_LIBMONADO_PATH}")
            monado = Monado.auto_connect(DEFAULT_LIBMONADO_PATH)
        else:
            print("Priority 3: Auto-detecting Monado...")
            monado = Monado.auto_connect()
        
        version = monado.get_api_version()
        print(f"✓ Connected to Monado API {version[0]}.{version[1]}.{version[2]}")
        return monado
    except MonadoError as e:
        print(f"✗ Connection failed: {e}")
        print("  (Is Monado running?)")
        return None


def test_clients(monado: Monado):
    """Test client enumeration."""
    try:
        clients = monado.clients()
        print(f"✓ Found {len(clients)} client(s)")
        
        for client in clients:
            print(f"  - Client {client.id}: '{client.name()}'")
            state = client.state()
            print(f"    State: primary={client.is_primary()}, focused={client.is_focused()}, io_active={client.is_io_active()}, visible={client.is_visible()}")
    except MonadoError as e:
        print(f"✗ Client enumeration failed: {e}")


def test_devices(monado: Monado):
    """Test device enumeration."""
    try:
        devices = monado.devices()
        print(f"✓ Found {len(devices)} device(s)")
        
        for device in devices:
            print(f"  - Device {device.index}: '{device.name}' (id={device.name_id})")
            
            # Try to get battery status
            if device.supports_battery:
                try:
                    battery = device.battery_status()
                    print(f"    Battery: {battery}")
                except MonadoError:
                    pass
            
            # Check for HMD
            if device.is_head_mounted_display:
                print(f"    Type: Head-Mounted Display")
                print(f"    Refresh Rate: {device.display_refresh_rate} Hz")
    except MonadoError as e:
        print(f"✗ Device enumeration failed: {e}")


def test_device_roles(monado: Monado):
    """Test getting devices by role."""
    roles_to_try = [
        DeviceRole.HEAD,
        DeviceRole.LEFT,
        DeviceRole.RIGHT,
    ]
    
    for role in roles_to_try:
        try:
            device = monado.device_from_role(role)
            print(f"✓ Role '{role}': '{device.name}'")
        except MonadoError:
            print(f"  Role '{role}': not available")


def test_context_manager():
    """Test context manager usage."""
    try:
        if "LIBMONADO_PATH" in os.environ:
            with Monado.connect(os.environ["LIBMONADO_PATH"]) as monado:
                print("✓ Context manager works")
                version = monado.get_api_version()
                print(f"  API version: {version}")
        else:
            print("  (Skipping context manager test - no LIBMONADO_PATH)")
    except MonadoError as e:
        print(f"✗ Context manager test failed: {e}")


def main():
    """Run all tests."""
    print("=" * 50)
    print("libmonado Python Bindings Test")
    print("=" * 50)
    print()
    
    test_imports()
    
    monado = test_connect()
    if monado is None:
        print("\nCould not connect to Monado. Tests aborted.")
        print("Make sure Monado is running and the library path is correct.")
        sys.exit(1)
    
    print()
    test_clients(monado)
    print()
    test_devices(monado)
    print()
    test_device_roles(monado)
    print()
    
    monado.close()
    print("✓ Connection closed cleanly")
    print()
    test_context_manager()
    
    print()
    print("=" * 50)
    print("Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
