"""
Audio Devices Library

Cross-platform library for listing audio devices.
"""

import sys

# setuptools-scmによるバージョン管理
try:
    from ._version import version as __version__
except ImportError:
    # フォールバック: setuptools-scmが利用できない場合
    try:
        from importlib.metadata import version
        __version__ = version("audio_devices")
    except ImportError:
        __version__ = "unknown"

__all__ = ["list_device_uids", "list_device_details", "list_devices_by_type"]

if sys.platform == "darwin":
    # macOS用
    try:
        from ._audio_devices import list_device_uids
        from ._audio_devices import list_device_details
        from ._audio_devices import list_devices_by_type
    except ImportError as e:
        def list_device_uids():
            raise ImportError(f"Failed to import macOS audio extension: {e}")
        
        def list_device_details():
            raise ImportError(f"Failed to import macOS audio extension: {e}")
            
        def list_devices_by_type(device_type="all"):
            raise ImportError(f"Failed to import macOS audio extension: {e}")

elif sys.platform == "win32":
    # Windows用
    try:
        from ._audio_devices import list_device_uids
        from ._audio_devices import list_device_details
        from ._audio_devices import list_devices_by_type
    except ImportError as e:
        def list_device_uids():
            raise ImportError(f"Failed to import Windows audio extension: {e}")
        
        def list_device_details():
            raise ImportError(f"Failed to import Windows audio extension: {e}")
            
        def list_devices_by_type(device_type="all"):
            raise ImportError(f"Failed to import Windows audio extension: {e}")

else:
    # その他のOS（Linux等）
    def list_device_uids():
        """List audio devices (not supported on this platform)"""
        raise NotImplementedError(f"Audio device listing not supported on {sys.platform}")
    
    def list_device_details():
        """Detailed device information (not supported on this platform)"""
        raise NotImplementedError(f"Detailed audio device information not supported on {sys.platform}")
        
    def list_devices_by_type(device_type="all"):
        """List devices by type (not supported on this platform)"""
        raise NotImplementedError(f"Device type filtering not supported on {sys.platform}")


# 後方互換性のためのエイリアス
list_audio_devices = list_device_uids

# 便利な関数を追加
def get_input_devices():
    """Get input devices only"""
    return list_devices_by_type("input")

def get_output_devices():
    """Get output devices only"""  
    return list_devices_by_type("output")

def get_all_devices():
    """Get all devices"""
    return list_devices_by_type("all")


def get_platform_info():
    """Get information about the current platform and available features"""
    platform_info = {
        "platform": sys.platform,
        "list_device_uids": "list_device_uids" in globals(),
        "list_device_details": "list_device_details" in globals(),
        "list_devices_by_type": "list_devices_by_type" in globals(),
    }
    
    if sys.platform == "darwin":
        platform_info["backend"] = "CoreAudio"
    elif sys.platform == "win32":
        platform_info["backend"] = "Windows Audio"
    else:
        platform_info["backend"] = "Not supported"
    
    return platform_info


# モジュールレベルでの使用例を提供
def print_devices_by_type(device_type="all"):
    """Print devices filtered by type in a user-friendly format"""
    try:
        devices = list_devices_by_type(device_type)
        print(f"Found {len(devices)} {device_type} audio device(s):")
        
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device.get('name', 'Unknown')} (UID: {device.get('uid', 'unknown')})")
            print(f"     Type: {device.get('device_type', 'unknown')}")
            print(f"     Input channels: {device.get('input_channels', 0)}")
            print(f"     Output channels: {device.get('output_channels', 0)}")
            print(f"     Manufacturer: {device.get('manufacturer', 'Unknown')}")
            print()
                
    except Exception as e:
        print(f"Error listing {device_type} devices: {e}")


def print_devices():
    """Print all available audio devices in a user-friendly format"""
    print_devices_by_type("all")
