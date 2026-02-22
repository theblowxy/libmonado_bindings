# libmonado Python Bindings

Python bindings for the Monado VR runtime control library.

> **Note:** This library was entirely written by AI. No human wrote the core implementation code.

## What is this?

These bindings allow you to control and monitor the [Monado](https://monado.freedesktop.org/) VR compositor from Python. You can:

- List and control OpenXR applications (clients)
- Manage VR devices (headsets, controllers, trackers)
- Query device information (battery, brightness, properties)
- Recenter tracking spaces

## How to install

you can easily install it using pip
```pip install git+https://github.com/theblowxy/pylibmonado_bindings.git```


## Quick Start

```python
from libmonado_bindings import Monado, DeviceRole

# Connect to Monado (auto-detects the library)
with Monado.auto_connect() as monado:
    print(f"Connected to Monado {monado.get_api_version()}")
    
    # List clients
    for client in monado.clients():
        print(f"Client: {client.name()} - Primary: {client.is_primary()}")
    
    # List devices
    for device in monado.devices():
        print(f"Device: {device.name}")
        print(f"  Position tracking: {device.supports_position}")
        print(f"  Orientation tracking: {device.supports_orientation}")
        
        # Battery (always available via direct API)
        batt = device.battery_status()
        if batt.present:
            print(f"  Battery: {batt.charge:.0%}")
    
    # Get specific device by role
    try:
        hmd = monado.device_from_role(DeviceRole.HEAD)
        print(f"HMD: {hmd.name}")
    except:
        print("No HMD found")
```

## Installation

### Prerequisites

- Python 3.7+
- Monado runtime installed and running
- `libmonado.so` available on your system

### Setup

No installation needed - just import the module. The bindings will auto-detect the library location, or you can specify it:

```bash
# Option 1: Environment variable (highest priority)
export LIBMONADO_PATH=/usr/lib/libmonado.so.25.1.0

# Option 2: XR runtime JSON
export XR_RUNTIME_JSON=$HOME/.config/openxr/1/active_runtime.json
```

## Connection Priority

The bindings use a priority system for finding the library:

1. **`LIBMONADO_PATH`** environment variable (user override)
2. **Script-provided path** - `Monado.auto_connect("/path/to/lib.so")`
3. **`XR_RUNTIME_JSON`** environment variable
4. **XDG auto-detection** - Searches standard locations

This allows scripts to provide defaults while users can override via environment variable.

## Examples

### List all clients and devices

```python
from libmonado_bindings import Monado

with Monado.auto_connect() as monado:
    print("Clients:")
    for client in monado.clients():
        print(f"  {client.name()}: focused={client.is_focused()}")
    
    print("\nDevices:")
    for device in monado.devices():
        print(f"  {device.name}")
        print(f"    Position: {device.supports_position}")
        print(f"    Orientation: {device.supports_orientation}")
```

### Control client focus

```python
# Set a specific client as focused
for client in monado.clients():
    if "MyApp" in client.name():
        client.set_focused()
        print(f"Focused: {client.name()}")
```

### Monitor battery levels

```python
for device in monado.devices():
    batt = device.battery_status()
    if batt.present:
        print(f"{device.name}: {batt.charge:.0%} ({'⚡' if batt.charging else '🔋'})")
```

### Recenter VR view

```python
monado.recenter_local_spaces()
```

## Documentation

Documentation at github ([link to doc](https://github.com/theblowxy/pylibmonado_bindings/wiki))

## Testing

Run the test script:

```bash
python3 test_bindings.py
```

## Key Classes

- **`Monado`** - Main entry point for connecting to the runtime
- **`Client`** - Represents an OpenXR application
- **`Device`** - Represents a VR device (HMD, controller, etc.)
- **`DeviceRole`** - Constants for device roles (HEAD, LEFT, RIGHT, etc.)
- **`BatteryStatus`** - Battery information dataclass
- **`MonadoError`** - Base exception class

## Requirements

- Python 3.7 or newer
- Monado runtime with libmonado.so (API >= 1.5.0)
- ctypes (included in Python standard library)

## License

Same as the main project. See LICENSE file in parent directory.

## Links

- [Monado Project](https://monado.freedesktop.org/)
- [OpenXR Specification](https://www.khronos.org/openxr/)
