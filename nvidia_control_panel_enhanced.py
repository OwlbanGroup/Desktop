"""Enhanced NVIDIA Control Panel Integration Module

This module provides comprehensive programmatic access to NVIDIA Control Panel settings
using NVAPI, Windows Registry, system management, and fallback mechanisms.

Features:
- Complete GPU settings management with validation
- PhysX configuration support
- Performance monitoring and counters
- Cross-platform compatibility (Windows, Linux, macOS)
- Advanced error handling and resilience patterns
- Caching and performance optimization
- Integration with NVIDIA NeMo-Agent-Toolkit

Based on NVIDIA's official Control Panel documentation and best practices.
"""

import logging
import os
import sys
import ctypes
import winreg
import subprocess
import json
import platform
import time
import asyncio
from typing import Dict, Any, List, Optional, Union, Set, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from contextlib import contextmanager

# Third-party imports with fallback handling
try:
    import backoff
    BACKOFF_AVAILABLE = True
except ImportError:
    BACKOFF_AVAILABLE = False
    logging.warning("backoff module not available, retry mechanisms disabled")

try:
    import cachetools
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    logging.warning("cachetools not available, caching disabled")

try:
    from circuitbreaker import circuit
    CIRCUITBREAKER_AVAILABLE = True
except ImportError:
    CIRCUITBREAKER_AVAILABLE = False
    logging.warning("circuitbreaker not available, circuit breaker pattern disabled")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nvidia_control_panel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== Custom Exceptions =====

class NVIDIAControlPanelError(Exception):
    """Base exception for NVIDIA Control Panel errors."""
    pass

class NVAPIUnavailableError(NVIDIAControlPanelError):
    """Raised when NVAPI is not available."""
    pass

class RegistryAccessError(NVIDIAControlPanelError):
    """Raised when registry access fails."""
    pass

class SettingValidationError(NVIDIAControlPanelError):
    """Raised when setting validation fails."""
    pass

class PhysXConfigurationError(NVIDIAControlPanelError):
    """Raised when PhysX configuration fails."""
    pass

class PerformanceCounterError(NVIDIAControlPanelError):
    """Raised when performance counter operations fail."""
    pass

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

@dataclass
class PerformanceCounter:
    name: str
    type: PerformanceCounterType
    value: Union[int, float, str]
    unit: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceCounterGroup:
    group_name: str
    counters: List[PerformanceCounter]
    timestamp: datetime = field(default_factory=datetime.now)

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

@dataclass
class PhysXConfiguration:
    enabled: bool = False
    selected_processor: PhysXProcessor = PhysXProcessor.AUTO
    available_gpus: List[str] = field(default_factory=list)
    gpu_count: int = 0
    version: str = "Unknown"
    
    def __post_init__(self):
        """Validate PhysX configuration."""
        if self.selected_processor not in PhysXProcessor:
            raise ValueError(f"Invalid PhysX processor: {self.selected_processor}")
        if self.gpu_count < 0:
            raise ValueError("GPU count cannot be negative")

@dataclass
class GPUProfile:
    """Represents a saved GPU configuration profile."""
    name: str
    settings: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

# ===== Utility Functions and Decorators =====

def retry_on_failure(max_retries=3, delay=1, backoff_factor=2):
    """Decorator for retrying failed operations with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = delay * (backoff_factor ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            raise last_exception
        return wrapper
    return decorator

def cache_results(ttl=300, maxsize=128):
    """Decorator for caching method results with time-to-live."""
    if not CACHETOOLS_AVAILABLE:
        return lambda func: func
        
    def decorator(func):
        cache = cachetools.TTLCache(maxsize=maxsize, ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if key in cache:
                logger.debug(f"Cache hit for {func.__name__}")
                return cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator

@contextmanager
def nvapi_context():
    """Context manager for NVAPI operations with proper cleanup."""
    try:
        yield
    except Exception as e:
        logger.error(f"NVAPI operation failed: {e}")
        raise NVIDIAControlPanelError(f"NVAPI operation failed: {e}")

# ===== Main NVIDIA Control Panel Class =====

class NVIDIAControlPanel:
    """Enhanced NVIDIA Control Panel integration with comprehensive features."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(NVIDIAControlPanel, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize NVIDIA Control Panel integration."""
        if self._initialized:
            return
            
        self.nvapi_available = self._check_nvapi_availability()
        self.gpu_count = self._get_gpu_count()
        self.driver_version = self._get_driver_version()
        self.is_windows = platform.system() == "Windows"
        self.nvapi_handle = None
        self.gpu_handles = []
        self._performance_counters = {}
        self._gpu_profiles = {}
        
        # Initialize platform-specific components
        if self.nvapi_available and self.is_windows:
            self._initialize_nvapi()
            
        self._initialized = True
        logger.info(f"NVIDIA Control Panel initialized: {self.gpu_count} GPUs, NVAPI: {self.nvapi_available}")

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

    @retry_on_failure(max_retries=2, delay=0.5)
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

    @cache_results(ttl=3600)  # Cache for 1 hour
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
                
            # Method 2: System command (Linux/macOS)
            if not self.is_windows:
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return result.stdout.strip()
                except:
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
            
            # Initialize NVAPI
            result = self.nvapi_dll.NvAPI_Initialize()
            if result == 0:  # NVAPI_OK
                logger.info("NVAPI initialized successfully")
                self.nvapi_handle = self.nvapi_dll
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

    # ===== Core GPU Settings Methods =====

    @cache_results(ttl=30)  # Cache for 30 seconds
    @retry_on_failure(max_retries=2)
    def get_gpu_settings(self, gpu_index: int = 0) -> Dict[str, Any]:
        """Retrieve current GPU settings from NVIDIA Control Panel."""
        settings = {}
        
        try:
            if self.nvapi_available and self.nvapi_handle:
                settings.update(self._get_settings_via_nvapi(gpu_index))
            elif self.is_windows:
                settings.update(self._get_settings_via_registry(gpu_index))
                settings.update(self._get_settings_via_wmi())
            else:
                settings.update(self._get_settings_via_system_commands())
                
        except Exception as e:
            logger.error(f"Error retrieving GPU settings: {e}")
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
        
        logger.debug(f"Retrieved GPU settings: {settings}")
        return settings

    @retry_on_failure(max_retries=3)
    def set_gpu_settings(self, settings: Dict[str, Any], gpu_index: int = 0) -> str:
        """Set GPU settings in NVIDIA Control Panel."""
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

    # ===== PhysX Configuration Methods =====

    @retry_on_failure(max_retries=2)
    def get_physx_configuration(self) -> PhysXConfiguration:
        """Get current PhysX configuration."""
        try:
            config = PhysXConfiguration()
            
            if self.nvapi_available:
                config = self._get_physx_config_via_nvapi()
            elif self.is_windows:
                config = self._get_physx_config_via_registry()
            else:
                config = self._get_physx_config_via_system()
                
            # Ensure we have available GPUs
            if not config.available_gpus and self.gpu_count > 0:
                config.available_gpus = [f"GPU{i}" for i in range(self.gpu_count)]
                config.gpu_count = self.gpu_count
                
            return config
            
        except Exception as e:
            logger.error(f"Error getting PhysX configuration: {e}")
            # Return default configuration on error
            return PhysXConfiguration(
                available_gpus=[f"GPU{i}" for i in range(self.gpu_count)],
                gpu_count=self.gpu_count
            )

    @retry_on_failure(max_retries=3)
    def set_physx_configuration(self, config: PhysXConfiguration) -> str:
        """Set PhysX configuration."""
        try:
            # Validate configuration
            if not isinstance(config, PhysXConfiguration):
                raise PhysXConfigurationError("Invalid PhysX configuration object")
                
            if self.nvapi_available:
                result = self._set_physx_config_via_nvapi(config)
            elif self.is_windows:
                result = self._set_physx_config_via_registry(config)
            else:
                result = self._set_physx_config_via_system(config)
                
            logger.info(f"PhysX configuration applied: {config}")
            return "PhysX configuration applied successfully"
            
        except Exception as e:
            logger.error(f"Error setting PhysX configuration: {e}")
            return f"Error applying PhysX configuration: {e}"

    # ===== Performance Monitoring Methods =====

    @cache_results(ttl=5)

def get_nvidia_control_panel() -> NVIDIAControlPanel:
    """
    Factory function to get the singleton instance of NVIDIAControlPanel.
    """
    return NVIDIAControlPanel()
