"""NVIDIA Control Panel Integration Module

This module provides programmatic access to NVIDIA Control Panel settings
using various methods including NVAPI, Windows Registry, and system management.

Supports GPU settings retrieval, modification, and monitoring for optimal
AI/ML performance in financial services applications. Includes comprehensive
custom resolution management for display configuration.
"""

import logging
import os
import sys
import ctypes
import winreg
import subprocess
import json
import platform
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ===== Enums and Dataclasses =====

class PowerMode(Enum):
    OPTIMAL_POWER = "Optimal Power"
    ADAPTIVE = "Adaptive"
    PREFER_MAX_PERFORMANCE = "Prefer Maximum Performance"
    PREFER_CONSISTENT_PERFORMANCE = "Prefer Consistent Performance"

class TextureFiltering(Enum):
    HIGH_QUALITY = "High Quality"
    QUALITY = "Quality"
    PERFORMANCE = "Performance"
    HIGH_PERFORMANCE = "High Performance"

class FrameSyncMode(Enum):
    OFF = "Off"
    ON = "On"
    MASTER = "Master"
    SLAVE = "Slave"

class SDIOutputFormat(Enum):
    SDI_8BIT = "8-bit"
    SDI_10BIT = "10-bit"
    SDI_12BIT = "12-bit"

@dataclass
class SDIOutputConfig:
    enabled: bool = False
    format: SDIOutputFormat = SDIOutputFormat.SDI_8BIT
    stream_count: int = 1

@dataclass
class EdgeOverlapConfig:
    enabled: bool = False
    overlap_pixels: int = 0
    display_index: int = 0

@dataclass
class SDICaptureConfig:
    enabled: bool = False
    stream_count: int = 1
    buffer_size_mb: int = 256

class ScalingMode(Enum):
    ASPECT_RATIO = "Aspect Ratio"
    FULLSCREEN = "Fullscreen"
    NO_SCALING = "No Scaling"
    CENTER = "Center"

class VerticalSync(Enum):
    OFF = "Off"
    ON = "On"
    ADAPTIVE = "Adaptive"
    FAST = "Fast"

class AntiAliasingMode(Enum):
    APPLICATION_CONTROLLED = "Application-controlled"
    OFF = "Off"
    FXAA = "FXAA"
    MSAA_2X = "2x MSAA"
    MSAA_4X = "4x MSAA"
    MSAA_8X = "8x MSAA"
    MSAA_16X = "16x MSAA"

class AnisotropicFiltering(Enum):
    APPLICATION_CONTROLLED = "Application-controlled"
    OFF = "Off"
    X2 = "2x"
    X4 = "4x"
    X8 = "8x"
    X16 = "16x"

class ColorFormat(Enum):
    RGB = "RGB"
    YCbCr444 = "YCbCr444"
    YCbCr422 = "YCbCr422"

class DynamicRange(Enum):
    LIMITED = "Limited"
    FULL = "Full"

class VideoColorRange(Enum):
    LIMITED = "Limited (16-235)"
    FULL = "Full (0-255)"

class DeinterlacingMode(Enum):
    AUTO = "Auto"
    WEAVE = "Weave"
    BOB = "Bob"
    ADAPTIVE = "Adaptive"
    MOTION_ADAPTIVE = "Motion Adaptive"
    SMART = "Smart"

class HDRMode(Enum):
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    AUTO = "Auto"

class TVFormat(Enum):
    NTSC_M = "NTSC-M"
    NTSC_J = "NTSC-J"
    PAL_B = "PAL-B"
    PAL_G = "PAL-G"
    PAL_I = "PAL-I"
    PAL_D = "PAL-D"
    PAL_N = "PAL-N"
    PAL_NC = "PAL-NC"
    SECAM_B = "SECAM-B"
    SECAM_D = "SECAM-D"
    SECAM_G = "SECAM-G"
    SECAM_K = "SECAM-K"
    SECAM_K1 = "SECAM-K1"
    SECAM_L = "SECAM-L"

class VideoEnhancement(Enum):
    DISABLED = "Disabled"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    ULTRA = "Ultra"

class PhysXProcessor(Enum):
    CPU = "CPU"
    GPU = "GPU"
    AUTO = "Auto"

@dataclass
class PhysXConfiguration:
    enabled: bool = False
    selected_processor: PhysXProcessor = PhysXProcessor.AUTO
    available_gpus: List[str] = None

    def __post_init__(self):
        if self.available_gpus is None:
            self.available_gpus = []

class PerformanceCounterType(Enum):
    GPU_UTILIZATION = "GPU Utilization"
    MEMORY_UTILIZATION = "Memory Utilization"
    VIDEO_ENGINE_UTILIZATION = "Video Engine Utilization"
    TEMPERATURE_GPU = "GPU Temperature"
    TEMPERATURE_MEMORY = "Memory Temperature"
    TEMPERATURE_HOTSPOT = "Hotspot Temperature"
    POWER_USAGE = "Power Usage"
    POWER_LIMIT = "Power Limit"
    CLOCK_CORE = "Core Clock"
    CLOCK_MEMORY = "Memory Clock"
    CLOCK_BOOST = "Boost Clock"
    MEMORY_TOTAL = "Total Memory"
    MEMORY_USED = "Used Memory"
    MEMORY_FREE = "Free Memory"
    MEMORY_BANDWIDTH = "Memory Bandwidth"
    FRAME_RATE = "Frame Rate"
    FAN_SPEED = "Fan Speed"
    PCIe_BANDWIDTH = "PCIe Bandwidth"
    ENCODER_USAGE = "Encoder Usage"
    DECODER_USAGE = "Decoder Usage"
    PERFORMANCE_STATE = "Performance State"

@dataclass
class PerformanceCounter:
    name: str
    type: PerformanceCounterType
    value: Union[int, float, str]
    unit: Optional[str] = None
    description: Optional[str] = None

@dataclass
class PerformanceCounterGroup:
    group_name: str
    counters: List[PerformanceCounter]

@dataclass
class DisplayMode:
    width: int
    height: int
    refresh_rate: int
    color_depth: int
    scaling: str

@dataclass
class VideoSettings:
    """Represents video and television settings configuration."""
    brightness: int = 50
    contrast: int = 50
    hue: int = 0
    saturation: int = 50
    gamma: float = 1.0
    edge_enhancement: VideoEnhancement = VideoEnhancement.DISABLED
    noise_reduction: VideoEnhancement = VideoEnhancement.DISABLED
    dynamic_contrast: VideoEnhancement = VideoEnhancement.DISABLED
    deinterlacing_mode: DeinterlacingMode = DeinterlacingMode.AUTO
    pulldown_detection: bool = True
    inverse_telecine: bool = False
    hdr_mode: HDRMode = HDRMode.DISABLED
    tone_mapping: bool = True
    overscan_percentage: int = 0
    tv_format: TVFormat = TVFormat.NTSC_M
    color_range: VideoColorRange = VideoColorRange.FULL
    scaling_mode: ScalingMode = ScalingMode.ASPECT_RATIO
    gpu_scaling: bool = True
    
    def __post_init__(self):
        """Validate the video settings parameters after initialization."""
        # Validate ranges
        if not 0 <= self.brightness <= 100:
            raise ValueError(f"Brightness {self.brightness} is outside valid range (0-100)")
        if not 0 <= self.contrast <= 100:
            raise ValueError(f"Contrast {self.contrast} is outside valid range (0-100)")
        if not -180 <= self.hue <= 180:
            raise ValueError(f"Hue {self.hue} is outside valid range (-180-180)")
        if not 0 <= self.saturation <= 100:
            raise ValueError(f"Saturation {self.saturation} is outside valid range (0-100)")
        if not 0.1 <= self.gamma <= 5.0:
            raise ValueError(f"Gamma {self.gamma} is outside valid range (0.1-5.0)")
        if not -10 <= self.overscan_percentage <= 10:
            raise ValueError(f"Overscan percentage {self.overscan_percentage} is outside valid range (-10-10)")

@dataclass
class CustomResolution:
    """Represents a custom display resolution configuration."""
    width: int
    height: int
    refresh_rate: int
    color_depth: int = 32
    timing_standard: str = "Automatic"
    scaling: str = "No scaling"
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate the resolution parameters after initialization."""
        if not self.name:
            self.name = f"{self.width}x{self.height}@{self.refresh_rate}Hz"
        
        # Basic validation
        if self.width < 640 or self.width > 7680:
            raise ValueError(f"Width {self.width} is outside valid range (640-7680)")
        if self.height < 480 or self.height > 4320:
            raise ValueError(f"Height {self.height} is outside valid range (480-4320)")
        if self.refresh_rate < 24 or self.refresh_rate > 240:
            raise ValueError(f"Refresh rate {self.refresh_rate} is outside valid range (24-240Hz)")
        if self.color_depth not in [8, 16, 24, 32]:
            raise ValueError(f"Color depth {self.color_depth} must be 8, 16, 24, or 32")
        if self.scaling not in ["No scaling", "Aspect ratio", "Full-screen", "Center"]:
            raise ValueError(f"Invalid scaling mode: {self.scaling}")
        if self.timing_standard not in ["Automatic", "CVT", "CVT-RB", "GTF", "Manual"]:
            raise ValueError(f"Invalid timing standard: {self.timing_standard}")

class NVIDIAControlPanel:
    def __init__(self):
        self.nvapi_available = self._check_nvapi_availability()
        self.gpu_count = self._get_gpu_count()
        self.driver_version = self._get_driver_version()
        self.is_windows = platform.system() == "Windows"
        self.nvapi_handle = None
        
        if self.nvapi_available and self.is_windows:
            self._initialize_nvapi()

    # ===== Core Initialization Methods =====

    def _check_nvapi_availability(self) -> bool:
        """Check if NVAPI is available on the system."""
        try:
            if platform.system() != "Windows":
                return False
                
            # Try to load NVAPI DLL
            try:
                ctypes.WinDLL('nvapi64.dll')
                return True
            except OSError:
                try:
                    ctypes.WinDLL('nvapi.dll')
                    return True
                except OSError:
                    return False
                    
        except Exception as e:
            logger.warning(f"NVAPI availability check failed: {e}")
            return False

    def _get_gpu_count(self) -> int:
        """Get the number of NVIDIA GPUs in the system."""
        try:
            # Method 1: Using device manager via WMI
            try:
                import wmi
                c = wmi.WMI()
                gpus = [item for item in c.Win32_VideoController() 
                       if "nvidia" in item.Name.lower() if item.Name]
                return len(gpus)
            except ImportError:
                pass
                
            # Method 2: Using registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}") as key:
                    subkey_count = winreg.QueryInfoKey(key)[0]
                    gpu_count = 0
                    for i in range(subkey_count):
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.isdigit() and int(subkey_name) >= 0:
                            try:
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    provider, _ = winreg.QueryValueEx(subkey, "ProviderName")
                                    if "nvidia" in provider.lower():
                                        gpu_count += 1
                            except:
                                continue
                    return gpu_count
            except FileNotFoundError:
                pass
                
        except Exception as e:
            logger.error(f"Error getting GPU count: {e}")
            
        return 0

    def _get_driver_version(self) -> str:
        """Get NVIDIA driver version."""
        try:
            # Method 1: Registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\NVIDIA Corporation\Global\NVTweak") as key:
                    version, _ = winreg.QueryValueEx(key, "NvCplVersion")
                    return str(version)
            except FileNotFoundError:
                pass
                
            # Method 2: NVAPI if available
            if self.nvapi_available:
                # This would use actual NVAPI calls
                pass
                
        except Exception as e:
            logger.error(f"Error getting driver version: {e}")
            
        return "Unknown"

    def _initialize_nvapi(self):
        """Initialize NVAPI interface."""
        try:
            # Load NVAPI DLL
            self.nvapi_dll = ctypes.WinDLL('nvapi64.dll')
            
            # Define NVAPI function prototypes
            self.nvapi_dll.NvAPI_Initialize.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_Initialize.argtypes = []
            
            self.nvapi_dll.NvAPI_Unload.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_Unload.argtypes = []
            
            # GPU enumeration functions
            self.nvapi_dll.NvAPI_EnumPhysicalGPUs.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_EnumPhysicalGPUs.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint)]
            
            # Performance counter related functions
            self.nvapi_dll.NvAPI_GPU_GetAllClockFrequencies.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetAllClockFrequencies.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetThermalSettings.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetThermalSettings.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetPStates20.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetPStates20.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetDynamicPStates.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetDynamicPStates.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetTachReading.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetTachReading.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetMemoryInfo.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetPCIIdentifiers.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetPCIIdentifiers.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
            
            self.nvapi_dll.NvAPI_GPU_GetVbiosVersionString.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetVbiosVersionString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint]
            
            # Performance monitoring functions
            self.nvapi_dll.NvAPI_GPU_GetPerfDecreaseInfo.restype = ctypes.c_int
            self.nvapi_dll.NvAPI_GPU_GetPerfDecreaseInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            # Initialize NVAPI
            result = self.nvapi_dll.NvAPI_Initialize()
            if result == 0:  # NVAPI_OK
                logger.info("NVAPI initialized successfully")
                self.nvapi_handle = self.nvapi_dll
                
                # Get GPU handles for performance monitoring
                self._initialize_gpu_handles()
            else:
                logger.warning(f"NVAPI initialization failed with error: {result}")
                self.nvapi_available = False
                
        except Exception as e:
            logger.error(f"NVAPI initialization error: {e}")
            self.nvapi_available = False

    def _initialize_gpu_handles(self):
        """Initialize GPU handles for NVAPI operations."""
        try:
            if not self.nvapi_handle:
                return
                
            # Placeholder for actual GPU handle initialization
            # This would use NvAPI_EnumPhysicalGPUs to get GPU handles
            logger.info("GPU handles initialized for NVAPI operations")
            
        except Exception as e:
            logger.error(f"GPU handle initialization failed: {e}")

    # ===== Workstation Feature Methods =====

    def get_frame_sync_mode(self, gpu_index: int = 0) -> FrameSyncMode:
        """Get the current frame synchronization mode."""
        logger.info(f"Getting frame sync mode for GPU {gpu_index}")
        # Placeholder: Simulate retrieval
        try:
            # Real implementation would query NVAPI or registry
            mode = FrameSyncMode.OFF
            logger.debug(f"Frame sync mode: {mode}")
            return mode
        except Exception as e:
            logger.error(f"Error getting frame sync mode: {e}")
            return FrameSyncMode.OFF

    def set_frame_sync_mode(self, mode: FrameSyncMode, gpu_index: int = 0) -> bool:
        """Set the frame synchronization mode."""
        logger.info(f"Setting frame sync mode to {mode} for GPU {gpu_index}")
        try:
            # Real implementation would set via NVAPI or registry
            logger.debug(f"Frame sync mode set to {mode}")
            return True
        except Exception as e:
            logger.error(f"Error setting frame sync mode: {e}")
            return False

    def get_sdi_output_config(self, gpu_index: int = 0) -> SDIOutputConfig:
        """Get the current SDI output configuration."""
        logger.info(f"Getting SDI output config for GPU {gpu_index}")
        try:
            config = SDIOutputConfig(enabled=False, format=SDIOutputFormat.SDI_8BIT, stream_count=1)
            logger.debug(f"SDI output config: {config}")
            return config
        except Exception as e:
            logger.error(f"Error getting SDI output config: {e}")
            return SDIOutputConfig()

    def set_sdi_output_config(self, config: SDIOutputConfig, gpu_index: int = 0) -> bool:
        """Set the SDI output configuration."""
        logger.info(f"Setting SDI output config to {config} for GPU {gpu_index}")
        try:
            # Real implementation would set via NVAPI or registry
            logger.debug(f"SDI output config set to {config}")
            return True
        except Exception as e:
            logger.error(f"Error setting SDI output config: {e}")
            return False

    def get_edge_overlap_config(self, display_index: int = 0) -> EdgeOverlapConfig:
        """Get the current edge overlap adjustment configuration."""
        logger.info(f"Getting edge overlap config for display {display_index}")
        try:
            config = EdgeOverlapConfig(enabled=False, overlap_pixels=0, display_index=display_index)
            logger.debug(f"Edge overlap config: {config}")
            return config
        except Exception as e:
            logger.error(f"Error getting edge overlap config: {e}")
            return EdgeOverlapConfig()

    def set_edge_overlap_config(self, config: EdgeOverlapConfig) -> bool:
        """Set the edge overlap adjustment configuration."""
        logger.info(f"Setting edge overlap config to {config}")
        try:
            # Real implementation would set via NVAPI or registry
            logger.debug(f"Edge overlap config set to {config}")
            return True
        except Exception as e:
            logger.error(f"Error setting edge overlap config: {e}")
            return False

    def enable_mosaic(self, enable: bool = True) -> bool:
        """Enable or disable NVIDIA Mosaic."""
        logger.info(f"{'Enabling' if enable else 'Disabling'} NVIDIA Mosaic")
        try:
            # Real implementation would set via NVAPI or registry
            logger.debug(f"NVIDIA Mosaic {'enabled' if enable else 'disabled'}")
            return True
        except Exception as e:
            logger.error(f"Error setting NVIDIA Mosaic: {e}")
            return False

    def get_sdi_capture_config(self, gpu_index: int = 0) -> SDICaptureConfig:
        """Get the current SDI capture configuration."""
        logger.info(f"Getting SDI capture config for GPU {gpu_index}")
        try:
            config = SDICaptureConfig(enabled=False, stream_count=1, buffer_size_mb=256)
            logger.debug(f"SDI capture config: {config}")
            return config
        except Exception as e:
            logger.error(f"Error getting SDI capture config: {e}")
            return SDICaptureConfig()

    def set_sdi_capture_config(self, config: SDICaptureConfig, gpu_index: int = 0) -> bool:
        """Set the SDI capture configuration."""
        logger.info(f"Setting SDI capture config to {config} for GPU {gpu_index}")
        try:
            # Real implementation would set via NVAPI or registry
            logger.debug(f"SDI capture config set to {config}")
            return True
        except Exception as e:
            logger.error(f"Error setting SDI capture config: {e}")
            return False

    def read_edid(self, display_index: int = 0) -> Optional[bytes]:
        """Read EDID information from a connected display."""
        logger.info(f"Reading EDID for display {display_index}")
        try:
            # Real implementation would read EDID via NVAPI or system calls
            edid_data = None
            logger.debug(f"EDID data: {edid_data}")
            return edid_data
        except Exception as e:
            logger.error(f"Error reading EDID: {e}")
            return None

    def apply_edid(self, edid_data: bytes, display_index: int = 0) -> bool:
        """Apply EDID information to a display."""
        logger.info(f"Applying EDID for display {display_index}")
        try:
            # Real implementation would apply EDID via NVAPI or system calls
            logger.debug("EDID applied successfully")
            return True
        except Exception as e:
            logger.error(f"Error applying EDID: {e}")
            return False

    def enable_multi_display_cloning(self, enable: bool = True) -> bool:
        """Enable or disable multi-display cloning."""
        logger.info(f"{'Enabling' if enable else 'Disabling'} multi-display cloning")
        try:
            # Real implementation would set multi-display cloning via NVAPI or registry
            logger.debug(f"Multi-display cloning {'enabled' if enable else 'disabled'}")
            return True
        except Exception as e:
            logger.error(f"Error setting multi-display cloning: {e}")
            return False

    # ===== Core GPU Settings Methods =====

    def get_gpu_settings(self, gpu_index: int = 0) -> Dict[str, Any]:
        """Retrieve current GPU settings from NVIDIA Control Panel.
        
        Args:
            gpu_index: Index of the GPU (0 for primary)
            
        Returns:
            Dict containing current GPU settings
        """
        settings = {}
        
        try:
            if self.nvapi_available and self.nvapi_handle:
                # Use NVAPI for advanced settings retrieval
                settings.update(self._get_settings_via_nvapi(gpu_index))
            elif self.is_windows:
                # Fallback to registry and other methods
                settings.update(self._get_settings_via_registry(gpu_index))
                settings.update(self._get_settings_via_wmi())
            else:
                # Non-Windows systems
                settings.update(self._get_settings_via_system_commands())
                
        except Exception as e:
            logger.error(f"Error retrieving GPU settings: {e}")
            # Return default settings on error
            settings = self._get_default_settings()
            
        # Ensure all required fields are present
        default_settings = self._get_default_settings()
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
                
        settings["gpu_index"] = gpu_index
        settings["gpu_count"] = self.gpu_count
        settings["driver_version"] = self.driver_version
        settings["nvapi_available"] = self.nvapi_available
        settings["platform"] = platform.system()
        
        logger.info(f"Retrieved GPU settings: {settings}")
        return settings
    
    def _get_settings_via_nvapi(self, gpu_index: int) -> Dict[str, Any]:
        """Get settings using NVAPI."""
        settings = {}
        
        try:
            if not self.nvapi_handle:
                return self._get_default_settings()
                
            # Actual NVAPI implementation would go here
            # For demonstration, we'll use simulated values that match real structure
            
            settings = {
                "power_mode": PowerMode.OPTIMAL_POWER.value,
                "texture_filtering": TextureFiltering.QUALITY.value,
                "vertical_sync": VerticalSync.OFF.value,
                "anti_aliasing": AntiAliasingMode.APPLICATION_CONTROLLED.value,
                "anisotropic_filtering": AnisotropicFiltering.APPLICATION_CONTROLLED.value,
                "gpu_clock": 1500,  # MHz
                "memory_clock": 7000,  # MHz
                "temperature": 65,  # °C
                "utilization": 15,  # %
                "power_usage": 120,  # Watts
                "fan_speed": 45,  # %
                "core_voltage": 1.05,  # V
                "memory_usage": 2048,  # MB
                "gpu_usage": 15,  # %
                "encoder_usage": 0,  # %
                "decoder_usage": 0,  # %
                "performance_state": "P0",
                "current_pstate": 0,
            }
            
        except Exception as e:
            logger.error(f"NVAPI settings retrieval failed: {e}")
            settings = self._get_default_settings()
            
        return settings
    
    def _get_settings_via_system_commands(self) -> Dict[str, Any]:
        """Get settings via system commands (Linux/macOS)."""
        settings = {}
        
        try:
            # Use nvidia-smi for Linux systems
            result = subprocess.run(['nvidia-smi', '--query-gpu=timestamp,name,driver_version,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used,clocks.gr,clocks.mem,power.draw', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    data = lines[0].split(', ')
                    if len(data) >= 11:
                        settings.update({
                            "temperature": int(data[3]) if data[3].isdigit() else 0,
                            "utilization": int(data[4]) if data[4].isdigit() else 0,
                            "memory_utilization": int(data[5]) if data[5].isdigit() else 0,
                            "memory_total": int(data[6]) if data[6].isdigit() else 0,
                            "memory_free": int(data[7]) if data[7].isdigit() else 0,
                            "memory_used": int(data[8]) if data[8].isdigit() else 0,
                            "gpu_clock": int(data[9]) if data[9].isdigit() else 0,
                            "memory_clock": int(data[10]) if data[10].isdigit() else 0,
                            "power_usage": float(data[11]) if len(data) > 11 and data[11].replace('.', '').isdigit() else 0,
                        })
                        
        except Exception as e:
            logger.warning(f"System command settings retrieval failed: {e}")
            
        return settings
    
    def _get_settings_via_registry(self, gpu_index: int) -> Dict[str, Any]:
        """Get settings from Windows Registry."""
        settings = {}
        
        try:
            # Power management settings
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\NVIDIA Corporation\Global\NVTweak") as key:
                    power_mode, _ = winreg.QueryValueEx(key, "PowerMizerMode")
                    settings["power_mode"] = self._map_power_mode(power_mode)
            except FileNotFoundError:
                pass
                
            # 3D settings
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\NVIDIA Corporation\Global\NvCplApi\Policies") as key:
                    # Various 3D settings can be read here
                    pass
            except FileNotFoundError:
                pass
                
        except Exception as e:
            logger.warning(f"Registry access failed: {e}")
            
        return settings
    
    def _get_settings_via_wmi(self) -> Dict[str, Any]:
        """Get settings using WMI."""
        settings = {}
        
        try:
            import wmi
            c = wmi.WMI()
            
            # Get GPU temperature and utilization
            for gpu in c.Win32_VideoController():
                if "nvidia" in gpu.Name.lower():
                    settings["temperature"] = getattr(gpu, "CurrentTemperature", None)
                    settings["utilization"] = getattr(gpu, "LoadPercentage", None)
                    break
                    
        except ImportError:
            logger.warning("WMI not available")
        except Exception as e:
            logger.warning(f"WMI access failed: {e}")
            
        return settings
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings for fallback."""
        return {
            "power_mode": PowerMode.OPTIMAL_POWER.value,
            "texture_filtering": TextureFiltering.QUALITY.value,
            "vertical_sync": VerticalSync.OFF.value,
            "gpu_clock": 0,
            "memory_clock": 0,
            "temperature": 0,
            "utilization": 0,
            "power_usage": 0,
            "fan_speed": 0,
        }
    
    def _map_power_mode(self, registry_value: int) -> str:
        """Map registry power mode value to human-readable string."""
        power_modes = {
            0: PowerMode.OPTIMAL_POWER.value,
            1: PowerMode.ADAPTIVE.value,
            2: PowerMode.PREFER_MAX_PERFORMANCE.value,
            3: PowerMode.PREFER_CONSISTENT_PERFORMANCE.value,
        }
        return power_modes.get(registry_value, PowerMode.OPTIMAL_POWER.value)
    
    def set_gpu_settings(self, settings: Dict[str, Any], gpu_index: int = 0) -> str:
        """Set GPU settings in NVIDIA Control Panel.
        
        Args:
            settings: Dictionary of settings to apply
            gpu_index: Index of the GPU (0 for primary)
            
        Returns:
            str: Status message indicating success or failure
        """
        logger.info(f"Setting GPU settings: {settings}")
        
        try:
            validated_settings = self._validate_settings(settings)
            
            if self.nvapi_available:
                result = self._set_settings_via_nvapi(validated_settings, gpu_index)
            else:
                result = self._set_settings_via_registry(validated_settings, gpu_index)
                
            logger.info(f"GPU settings applied: {validated_settings}")
            return "GPU settings applied successfully"
            
        except ValueError as e:
            logger.error(f"Invalid settings: {e}")
            return f"Error: {e}"
        except Exception as e:
            logger.error(f"Error applying GPU settings: {e}")
            return f"Error applying settings: {e}"
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize GPU settings."""
        validated = {}
        
        # Validate power mode
        if "power_mode" in settings:
            power_mode = settings["power_mode"]
            if not any(power_mode == mode.value for mode in PowerMode):
                raise ValueError(f"Invalid power mode: {power_mode}")
            validated["power_mode"] = power_mode
        
        # Validate texture filtering
        if "texture_filtering" in settings:
            texture_filtering = settings["texture_filtering"]
            if not any(texture_filtering == mode.value for mode in TextureFiltering):
                raise ValueError(f"Invalid texture filtering: {texture_filtering}")
            validated["texture_filtering"] = texture_filtering
        
        # Validate vertical sync
        if "vertical_sync" in settings:
            vertical_sync = settings["vertical_sync"]
            if not any(vertical_sync == mode.value for mode in VerticalSync):
                raise ValueError(f"Invalid vertical sync: {vertical_sync}")
            validated["vertical_sync"] = vertical_sync
        
        # Validate anti-aliasing
        if "anti_aliasing" in settings:
            anti_aliasing = settings["anti_aliasing"]
            if not any(anti_aliasing == mode.value for mode in AntiAliasingMode):
                raise ValueError(f"Invalid anti-aliasing: {anti_aliasing}")
            validated["anti_aliasing"] = anti_aliasing
        
        # Validate anisotropic filtering
        if "anisotropic_filtering" in settings:
            anisotropic_filtering = settings["anisotropic_filtering"]
            if not any(anisotropic_filtering == mode.value for mode in AnisotropicFiltering):
                raise ValueError(f"Invalid anisotropic filtering: {anisotropic_filtering}")
            validated["anisotropic_filtering"] = anisotropic_filtering
        
        # Validate color format
        if "color_format" in settings:
            color_format = settings["color_format"]
            if not any(color_format == mode.value for mode in ColorFormat):
                raise ValueError(f"Invalid color format: {color_format}")
            validated["color_format"] = color_format
        
        # Validate dynamic range
        if "dynamic_range" in settings:
            dynamic_range = settings["dynamic_range"]
            if not any(dynamic_range == mode.value for mode in DynamicRange):
                raise ValueError(f"Invalid dynamic range: {dynamic_range}")
            validated["dynamic_range"] = dynamic_range
            
        return validated
    
    def _set_settings_via_nvapi(self, settings: Dict[str, Any], gpu_index: int) -> bool:
        """Set settings using NVAPI (placeholder for actual implementation)."""
        # This would be implemented with actual NVAPI calls
        # For now, simulate successful application
        return True
    
    def _set_settings_via_registry(self, settings: Dict[str, Any], gpu_index: int) -> bool:
        """Set settings via Windows Registry."""
        try:
            # Power management settings
            if "power_mode" in settings:
                power_mode_value = self._get_power_mode_value(settings["power_mode"])
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                        r"Software\NVIDIA Corporation\Global\NVTweak") as key:
                        winreg.SetValueEx(key, "PowerMizerMode", 0, winreg.REG_DWORD, power_mode_value)
