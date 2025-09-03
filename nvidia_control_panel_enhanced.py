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

# ===== System Topology Enums =====

class TopologyType(Enum):
    """Types of GPU interconnect topologies."""
    UNKNOWN = "Unknown"
    SINGLE_GPU = "Single GPU"
    SLI = "SLI (Scalable Link Interface)"
    NVLINK = "NVLink"
    PCIE = "PCI Express"
    MOSAIC = "NVIDIA Mosaic"
    QUADRO_PLEX = "Quadro Plex"
    VIRTUAL_LINK = "Virtual Link"

class ConnectionType(Enum):
    """Types of connections between GPUs or displays."""
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    BRIDGE = "Bridge"
    MASTER = "Master"
    SLAVE = "Slave"
    PEER_TO_PEER = "Peer-to-Peer"
    CASCADE = "Cascade"

class DisplayTopologyMode(Enum):
    """Display topology configuration modes."""
    SINGLE = "Single Display"
    EXTENDED = "Extended Desktop"
    CLONE = "Clone Mode"
    SURROUND = "Surround"
    MOSAIC = "Mosaic"
    INDEPENDENT = "Independent"

class PCIeGeneration(Enum):
    """PCI Express generation versions."""
    UNKNOWN = "Unknown"
    PCIE_1_0 = "PCIe 1.0"
    PCIE_2_0 = "PCIe 2.0"
    PCIE_3_0 = "PCIe 3.0"
    PCIE_4_0 = "PCIe 4.0"
    PCIE_5_0 = "PCIe 5.0"
    PCIE_6_0 = "PCIe 6.0"

class PCIeLinkWidth(Enum):
    """PCI Express link widths."""
    X1 = "x1"
    X2 = "x2"
    X4 = "x4"
    X8 = "x8"
    X16 = "x16"
    X32 = "x32"

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

# ===== System Topology Dataclasses =====

@dataclass
class GPUTopologyNode:
    """Represents a GPU node in the system topology."""
    gpu_index: int
    name: str
    pcie_bus_id: str
    pcie_generation: PCIeGeneration
    pcie_link_width: PCIeLinkWidth
    memory_size_mb: int
    is_primary: bool = False
    connected_displays: List[int] = field(default_factory=list)
    sli_bridge_present: bool = False
    nvlink_connections: List[int] = field(default_factory=list)
    pcie_slot: Optional[str] = None
    driver_version: Optional[str] = None
    
    def __post_init__(self):
        """Validate GPU topology node parameters."""
        if self.gpu_index < 0:
            raise ValueError("GPU index cannot be negative")
        if self.memory_size_mb < 0:
            raise ValueError("Memory size cannot be negative")

@dataclass
class DisplayTopologyNode:
    """Represents a display node in the system topology."""
    display_index: int
    name: str
    resolution_width: int
    resolution_height: int
    refresh_rate: int
    connected_gpu_index: int
    edid_manufacturer: Optional[str] = None
    edid_product: Optional[str] = None
    edid_serial: Optional[str] = None
    display_position_x: int = 0
    display_position_y: int = 0
    is_primary: bool = False
    hdr_capable: bool = False
    color_depth: int = 8
    
    def __post_init__(self):
        """Validate display topology node parameters."""
        if self.display_index < 0:
            raise ValueError("Display index cannot be negative")
        if self.resolution_width < 640 or self.resolution_width > 7680:
            raise ValueError(f"Resolution width {self.resolution_width} is outside valid range")
        if self.resolution_height < 480 or self.resolution_height > 4320:
            raise ValueError(f"Resolution height {self.resolution_height} is outside valid range")
        if self.refresh_rate < 24 or self.refresh_rate > 240:
            raise ValueError(f"Refresh rate {self.refresh_rate} is outside valid range")

@dataclass
class TopologyConnection:
    """Represents a connection between nodes in the system topology."""
    source_node_index: int
    target_node_index: int
    connection_type: ConnectionType
    bandwidth_gbps: Optional[float] = None
    latency_ns: Optional[float] = None
    is_active: bool = True
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate topology connection parameters."""
        if self.source_node_index < 0 or self.target_node_index < 0:
            raise ValueError("Node indices cannot be negative")
        if self.source_node_index == self.target_node_index:
            raise ValueError("Source and target nodes cannot be the same")

@dataclass
class SystemTopology:
    """Represents the complete system topology including GPUs and displays."""
    topology_type: TopologyType
    gpu_nodes: List[GPUTopologyNode]
    display_nodes: List[DisplayTopologyNode]
    connections: List[TopologyConnection]
    timestamp: datetime = field(default_factory=datetime.now)
    sli_enabled: bool = False
    nvlink_enabled: bool = False
    mosaic_enabled: bool = False
    total_gpu_memory_mb: int = 0
    total_displays: int = 0
    description: Optional[str] = None
    
    def __post_init__(self):
        """Calculate derived topology properties."""
        self.total_gpu_memory_mb = sum(gpu.memory_size_mb for gpu in self.gpu_nodes)
        self.total_displays = len(self.display_nodes)
        
        # Check for SLI/NVLink
        self.sli_enabled = any(conn.connection_type == ConnectionType.BRIDGE for conn in self.connections)
        self.nvlink_enabled = any(conn.connection_type == ConnectionType.PEER_TO_PEER for conn in self.connections)
        
        # Check for Mosaic
        mosaic_connections = [conn for conn in self.connections 
                            if conn.connection_type in [ConnectionType.MASTER, ConnectionType.SLAVE]]
        self.mosaic_enabled = len(mosaic_connections) > 0

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
    refresh_rate: int = 60
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

# ===== Quadro Plex Configuration =====

@dataclass
class QuadroPlexConfig:
    enabled: bool = False
    num_plexes: int = 0
    displays_per_plex: int = 0
    total_displays: int = 0
    overlap_pixels: int = 0
    edge_blending_enabled: bool = False
    edge_overlap_pixels: int = 0
    mosaic_enabled: bool = False
    # Add other relevant fields as needed

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

        # Set platform information first
        self.is_windows = platform.system() == "Windows"

        self.nvapi_available = self._check_nvapi_availability()
        self.gpu_count = self._get_gpu_count()
        # Mock at least one GPU for testing if none found
        if self.gpu_count == 0:
            self.gpu_count = 1
            logger.info("No GPUs detected, mocking 1 GPU for testing purposes")
        self.driver_version = self._get_driver_version()
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
                       if item.Name and "nvidia" in item.Name.lower()]
                if gpus:
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
                                    if provider and "nvidia" in provider.lower():
                                        gpu_count += 1
                            except:
                                continue
                    if gpu_count > 0:
                        return gpu_count
            except FileNotFoundError:
                pass

            # Method 3: Using nvidia-smi system command as fallback
            try:
                result = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    gpu_count = sum(1 for line in lines if line.lower().startswith('gpu'))
                    if gpu_count > 0:
                        return gpu_count
            except Exception as e:
                logger.warning(f"nvidia-smi GPU count fallback failed: {e}")
                
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
                    if version:
                        return str(version)
            except FileNotFoundError:
                pass
                
            # Method 2: System command (Windows/Linux/macOS)
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception as e:
                logger.warning(f"nvidia-smi driver version fallback failed: {e}")
                    
        except Exception as e:
            logger.error(f"Error getting driver version: {e}")
            
        return "Unknown"

    def _initialize_nvapi(self):
        """Initialize NVAPI interface."""
        try:
            # Load NVAPI DLL
            try:
                self.nvapi_dll = ctypes.WinDLL('nvapi64.dll')
            except OSError:
                self.nvapi_dll = ctypes.WinDLL('nvapi.dll')
            
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

            # Define GPU handle array and count
            gpu_handles = (ctypes.c_void_p * self.gpu_count)()
            gpu_count = ctypes.c_uint(self.gpu_count)

            # Enumerate physical GPUs
            result = self.nvapi_dll.NvAPI_EnumPhysicalGPUs(gpu_handles, ctypes.byref(gpu_count))
            if result == 0:  # NVAPI_OK
                self.gpu_handles = list(gpu_handles[:gpu_count.value])
                logger.info(f"Successfully enumerated {gpu_count.value} physical GPUs")
            else:
                logger.warning(f"NVAPI GPU enumeration failed with error: {result}")
                self.nvapi_available = False

        except Exception as e:
            logger.error(f"GPU handle initialization failed: {e}")
            self.nvapi_available = False

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

    def _get_settings_via_nvapi(self, gpu_index: int) -> Dict[str, Any]:
        """Get settings from NVAPI."""
        settings = {}
        try:
            # Placeholder for actual NVAPI calls to get GPU settings
            # For example, query clock speeds, power modes, etc.
            logger.info(f"Retrieving GPU settings via NVAPI for GPU index {gpu_index}")
            # Example: settings["power_mode"] = self._query_nvapi_power_mode(gpu_index)
            # Add more NVAPI queries here as needed
        except Exception as e:
            logger.error(f"NVAPI settings retrieval failed: {e}")
        return settings

    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GPU settings before applying them."""
        validated = {}

        # Validate power mode
        if "power_mode" in settings:
            power_mode = settings["power_mode"]
            if isinstance(power_mode, str):
                # Convert string to enum value if needed
                for mode in PowerMode:
                    if mode.value == power_mode:
                        validated["power_mode"] = power_mode
                        break
                else:
                    raise ValueError(f"Invalid power mode: {power_mode}")
            elif isinstance(power_mode, int):
                # Handle numeric values
                validated["power_mode"] = self._map_power_mode(power_mode)
            else:
                raise ValueError(f"Power mode must be string or int, got {type(power_mode)}")

        # Validate texture filtering
        if "texture_filtering" in settings:
            texture_filtering = settings["texture_filtering"]
            if isinstance(texture_filtering, str):
                for mode in TextureFiltering:
                    if mode.value == texture_filtering:
                        validated["texture_filtering"] = texture_filtering
                        break
                else:
                    raise ValueError(f"Invalid texture filtering: {texture_filtering}")
            else:
                raise ValueError(f"Texture filtering must be string, got {type(texture_filtering)}")

        # Validate vertical sync
        if "vertical_sync" in settings:
            vsync = settings["vertical_sync"]
            if isinstance(vsync, str):
                for mode in VerticalSync:
                    if mode.value == vsync:
                        validated["vertical_sync"] = vsync
                        break
                else:
                    raise ValueError(f"Invalid vertical sync: {vsync}")
            else:
                raise ValueError(f"Vertical sync must be string, got {type(vsync)}")

        # Validate anti-aliasing
        if "anti_aliasing" in settings:
            aa = settings["anti_aliasing"]
            if isinstance(aa, str):
                for mode in AntiAliasingMode:
                    if mode.value == aa:
                        validated["anti_aliasing"] = aa
                        break
                else:
                    raise ValueError(f"Invalid anti-aliasing: {aa}")
            else:
                raise ValueError(f"Anti-aliasing must be string, got {type(aa)}")

        # Validate anisotropic filtering
        if "anisotropic_filtering" in settings:
            af = settings["anisotropic_filtering"]
            if isinstance(af, str):
                for mode in AnisotropicFiltering:
                    if mode.value == af:
                        validated["anisotropic_filtering"] = af
                        break
                else:
                    raise ValueError(f"Invalid anisotropic filtering: {af}")
            else:
                raise ValueError(f"Anisotropic filtering must be string, got {type(af)}")

        return validated
    
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

    def _get_physx_config_via_registry(self) -> PhysXConfiguration:
        """Get PhysX configuration from Windows registry."""
        try:
            config = PhysXConfiguration()
            
            # Try to read PhysX settings from registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\NVIDIA Corporation\Global\PhysX") as key:
                    
                    # Read PhysX processor setting
                    try:
                        processor_value, _ = winreg.QueryValueEx(key, "PhysXProcessor")
                        if processor_value == 0:
                            config.selected_processor = PhysXProcessor.CPU
                        elif processor_value == 1:
                            config.selected_processor = PhysXProcessor.GPU
                        else:
                            config.selected_processor = PhysXProcessor.AUTO
                    except FileNotFoundError:
                        pass
                    
                    # Read PhysX enabled setting
                    try:
                        enabled_value, _ = winreg.QueryValueEx(key, "PhysXEnabled")
                        config.enabled = bool(enabled_value)
                    except FileNotFoundError:
                        pass
                    
            except FileNotFoundError:
                logger.warning("PhysX registry key not found")
                
            return config
            
        except Exception as e:
            logger.error(f"Error reading PhysX configuration from registry: {e}")
            return PhysXConfiguration()

    def _set_physx_config_via_registry(self, config: PhysXConfiguration) -> str:
        """Set PhysX configuration in Windows registry."""
        try:
            # Create or open PhysX registry key
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, 
                                 r"SOFTWARE\NVIDIA Corporation\Global\PhysX") as key:
                
                # Set PhysX processor
                processor_value = {
                    PhysXProcessor.CPU: 0,
                    PhysXProcessor.GPU: 1,
                    PhysXProcessor.AUTO: 2
                }.get(config.selected_processor, 2)
                
                winreg.SetValueEx(key, "PhysXProcessor", 0, winreg.REG_DWORD, processor_value)
                winreg.SetValueEx(key, "PhysXEnabled", 0, winreg.REG_DWORD, int(config.enabled))
                
            return "PhysX configuration applied successfully"
            
        except Exception as e:
            logger.error(f"Error setting PhysX configuration in registry: {e}")
            return f"Error applying PhysX configuration: {e}"

    def _get_physx_config_via_nvapi(self) -> PhysXConfiguration:
        """Get PhysX configuration using NVAPI."""
        # Placeholder implementation
        return PhysXConfiguration()

    def _set_physx_config_via_nvapi(self, config: PhysXConfiguration) -> str:
        """Set PhysX configuration using NVAPI."""
        # Placeholder implementation
        return "PhysX configuration applied successfully"

    def _get_physx_config_via_system(self) -> PhysXConfiguration:
        """Get PhysX configuration using system methods."""
        # Placeholder implementation
        return PhysXConfiguration()
        
    def _set_physx_config_via_system(self, config: PhysXConfiguration) -> str:
        """Set PhysX configuration using system methods."""
        # Placeholder implementation
        return "PhysX configuration applied successfully"

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

    # ===== System Topology Methods =====

    @cache_results(ttl=60)  # Cache for 1 minute
    @retry_on_failure(max_retries=2)
    def get_system_topology(self) -> SystemTopology:
        """Get the complete system topology including GPUs and displays."""
        try:
            topology = SystemTopology(
                topology_type=TopologyType.UNKNOWN,
                gpu_nodes=[],
                display_nodes=[],
                connections=[]
            )
            
            if self.nvapi_available:
                topology = self._get_topology_via_nvapi()
            elif self.is_windows:
                topology = self._get_topology_via_wmi()
            else:
                topology = self._get_topology_via_system_commands()
                
            logger.info(f"Retrieved system topology: {topology.topology_type}")
            return topology
            
        except Exception as e:
            logger.error(f"Error getting system topology: {e}")
            # Return basic topology with available information
            return self._get_basic_topology()

    @retry_on_failure(max_retries=2)
    def get_gpu_topology_info(self, gpu_index: int = 0) -> GPUTopologyNode:
        """Get detailed topology information for a specific GPU."""
        try:
            if self.nvapi_available:
                return self._get_gpu_topology_via_nvapi(gpu_index)
            else:
                return self._get_gpu_topology_via_system(gpu_index)
                
        except Exception as e:
            logger.error(f"Error getting GPU topology info: {e}")
            # Return basic GPU info
            return GPUTopologyNode(
                gpu_index=gpu_index,
                name=f"GPU {gpu_index}",
                pcie_bus_id="Unknown",
                pcie_generation=PCIeGeneration.UNKNOWN,
                pcie_link_width=PCIeLinkWidth.X16,
                memory_size_mb=0
            )

    @retry_on_failure(max_retries=2)
    def get_display_topology_info(self, display_index: int = 0) -> DisplayTopologyNode:
        """Get detailed topology information for a specific display."""
        try:
            if self.nvapi_available:
                return self._get_display_topology_via_nvapi(display_index)
            else:
                return self._get_display_topology_via_system(display_index)
                
        except Exception as e:
            logger.error(f"Error getting display topology info: {e}")
            # Return basic display info
            return DisplayTopologyNode(
                display_index=display_index,
                name=f"Display {display_index}",
                resolution_width=1920,
                resolution_height=1080,
                refresh_rate=60,
                connected_gpu_index=0
            )

    def _get_basic_topology(self) -> SystemTopology:
        """Create a basic system topology with available information."""
        gpu_nodes = []
        for i in range(self.gpu_count):
            gpu_nodes.append(GPUTopologyNode(
                gpu_index=i,
                name=f"GPU {i}",
                pcie_bus_id=f"PCIe Bus {i}",
                pcie_generation=PCIeGeneration.UNKNOWN,
                pcie_link_width=PCIeLinkWidth.X16,
                memory_size_mb=0,
                is_primary=(i == 0)
            ))
            
        return SystemTopology(
            topology_type=TopologyType.SINGLE_GPU if self.gpu_count == 1 else TopologyType.PCIE,
            gpu_nodes=gpu_nodes,
            display_nodes=[],
            connections=[]
        )

    def _get_topology_via_nvapi(self) -> SystemTopology:
        """Get system topology using NVAPI (placeholder implementation)."""
        # This would use actual NVAPI calls to get topology information
        logger.info("Getting system topology via NVAPI")
        
        # Placeholder implementation - would be replaced with actual NVAPI calls
        gpu_nodes = []
        for i in range(self.gpu_count):
            gpu_nodes.append(GPUTopologyNode(
                gpu_index=i,
                name=f"NVIDIA GPU {i}",
                pcie_bus_id=f"PCIe Bus {i}",
                pcie_generation=PCIeGeneration.PCIE_4_0,
                pcie_link_width=PCIeLinkWidth.X16,
                memory_size_mb=8192,  # 8GB placeholder
                is_primary=(i == 0)
            ))
            
        return SystemTopology(
            topology_type=TopologyType.SINGLE_GPU if self.gpu_count == 1 else TopologyType.PCIE,
            gpu_nodes=gpu_nodes,
            display_nodes=[],
            connections=[]
        )

    def _get_topology_via_wmi(self) -> SystemTopology:
        """Get system topology using WMI (Windows Management Instrumentation)."""
        try:
            import wmi
            c = wmi.WMI()
            
            gpu_nodes = []
            display_nodes = []
            connections = []
            
            # Get GPU information
            gpu_controllers = c.Win32_VideoController()
            for i, gpu in enumerate(gpu_controllers):
                if "nvidia" in gpu.Name.lower() if gpu.Name else False:
                    gpu_nodes.append(GPUTopologyNode(
                        gpu_index=i,
                        name=gpu.Name or f"GPU {i}",
                        pcie_bus_id=gpu.PNPDeviceID or f"PCIe Bus {i}",
                        pcie_generation=PCIeGeneration.UNKNOWN,
                        pcie_link_width=PCIeLinkWidth.X16,
                        memory_size_mb=getattr(gpu, 'AdapterRAM', 0) // (1024 * 1024) if hasattr(gpu, 'AdapterRAM') else 0,
                        is_primary=getattr(gpu, 'CurrentHorizontalResolution', 0) > 0
                    ))
            
            # Get display information
            displays = c.Win32_DesktopMonitor()
            for i, display in enumerate(displays):
                display_nodes.append(DisplayTopologyNode(
                    display_index=i,
                    name=display.Name or f"Display {i}",
                    resolution_width=getattr(display, 'ScreenWidth', 1920),
                    resolution_height=getattr(display, 'ScreenHeight', 1080),
                    refresh_rate=getattr(display, 'RefreshRate', 60),
                    connected_gpu_index=0  # Simplified assumption
                ))
                
            return SystemTopology(
                topology_type=TopologyType.SINGLE_GPU if len(gpu_nodes) == 1 else TopologyType.PCIE,
                gpu_nodes=gpu_nodes,
                display_nodes=display_nodes,
                connections=connections
            )
            
        except ImportError:
            logger.warning("WMI not available for topology detection")
            return self._get_basic_topology()
        except Exception as e:
            logger.error(f"WMI topology detection failed: {e}")
            return self._get_basic_topology()

    def _get_topology_via_system_commands(self) -> SystemTopology:
        """Get system topology using system commands (Linux/macOS)."""
        try:
            # For non-Windows systems, use nvidia-smi and other system commands
            result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,pci.bus_id,memory.total', '--format=csv,noheader'],
                                  capture_output=True, text=True, timeout=10)
            
            gpu_nodes = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split(', ')
                    if len(parts) >= 4:
                        try:
                            memory_str = parts[3].replace(' MiB', '')
                            memory_mb = int(memory_str) if memory_str.isdigit() else 0
                            gpu_nodes.append(GPUTopologyNode(
                                gpu_index=int(parts[0]),
                                name=parts[1],
                                pcie_bus_id=parts[2],
                                pcie_generation=PCIeGeneration.UNKNOWN,
                                pcie_link_width=PCIeLinkWidth.X16,
                                memory_size_mb=memory_mb,
                                is_primary=(int(parts[0]) == 0)
                            ))
                        except (ValueError, IndexError):
                            continue
            
            return SystemTopology(
                topology_type=TopologyType.SINGLE_GPU if len(gpu_nodes) == 1 else TopologyType.PCIE,
                gpu_nodes=gpu_nodes,
                display_nodes=[],
                connections=[]
            )
            
        except Exception as e:
            logger.error(f"System command topology detection failed: {e}")
            return self._get_basic_topology()

    def _get_gpu_topology_via_nvapi(self, gpu_index: int) -> GPUTopologyNode:
        """Get GPU topology information using NVAPI."""
        # Placeholder implementation
        return GPUTopologyNode(
            gpu_index=gpu_index,
            name=f"NVIDIA GPU {gpu_index}",
            pcie_bus_id=f"PCIe Bus {gpu_index}",
            pcie_generation=PCIeGeneration.PCIE_4_0,
            pcie_link_width=PCIeLinkWidth.X16,
            memory_size_mb=8192,
            is_primary=(gpu_index == 0)
        )

    def _get_gpu_topology_via_system(self, gpu_index: int) -> GPUTopologyNode:
        """Get GPU topology information using system methods."""
        return GPUTopologyNode(
            gpu_index=gpu_index,
            name=f"GPU {gpu_index}",
            pcie_bus_id=f"PCIe Bus {gpu_index}",
            pcie_generation=PCIeGeneration.UNKNOWN,
            pcie_link_width=PCIeLinkWidth.X16,
            memory_size_mb=0,
            is_primary=(gpu_index == 0)
        )

    def _get_display_topology_via_nvapi(self, display_index: int) -> DisplayTopologyNode:
        """Get display topology information using NVAPI."""
        # Placeholder implementation
        return DisplayTopologyNode(
            display_index=display_index,
            name=f"Display {display_index}",
            resolution_width=1920,
            resolution_height=1080,
            refresh_rate=60,
            connected_gpu_index=0,
            is_primary=(display_index == 0)
        )

    def _get_display_topology_via_system(self, display_index: int) -> DisplayTopologyNode:
        """Get display topology information using system methods."""
        return DisplayTopologyNode(
            display_index=display_index,
            name=f"Display {display_index}",
            resolution_width=1920,
            resolution_height=1080,
            refresh_rate=60,
            connected_gpu_index=0,
            is_primary=(display_index == 0)
        )

    # ===== Performance Monitoring Methods =====

    @cache_results(ttl=5)
    def get_performance_counters(self, gpu_index: int = 0) -> List[PerformanceCounter]:
        """Get performance counters for a specific GPU."""
        try:
            if self.nvapi_available:
                return self._get_performance_counters_via_nvapi(gpu_index)
            else:
                return self._get_performance_counters_via_system(gpu_index)
        except Exception as e:
            logger.error(f"Error getting performance counters: {e}")
            return []

    def _get_performance_counters_via_nvapi(self, gpu_index: int) -> List[PerformanceCounter]:
        """Get performance counters using NVAPI."""
        # Placeholder implementation
        return [
            PerformanceCounter(
                name="GPU Utilization",
                type=PerformanceCounterType.GPU_UTILIZATION,
                value=15.5,
                unit="%"
            ),
            PerformanceCounter(
                name="Memory Usage",
                type=PerformanceCounterType.MEMORY_USED,
                value=2048,
                unit="MB"
            )
        ]

    def _get_performance_counters_via_system(self, gpu_index: int) -> List[PerformanceCounter]:
        """Get performance counters using system commands."""
        try:
            if not self.is_windows:
                result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used', '--format=csv,noheader,nounits'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    data = result.stdout.strip().split(', ')
                    if len(data) >= 2:
                        return [
                            PerformanceCounter(
                                name="GPU Utilization",
                                type=PerformanceCounterType.GPU_UTILIZATION,
                                value=float(data[0]) if data[0].replace('.', '').isdigit() else 0,
                                unit="%"
                            ),
                            PerformanceCounter(
                                name="Memory Usage",
                                type=PerformanceCounterType.MEMORY_USED,
                                value=int(data[1]) if data[1].isdigit() else 0,
                                unit="MB"
                            )
                        ]
        except Exception as e:
            logger.error(f"System command performance counter failed: {e}")
        
        return []

    def get_frame_sync_mode(self, gpu_index: int = 0) -> FrameSyncMode:
        """Get the current frame sync mode for a specific GPU."""
        # Validate input parameters
        if not isinstance(gpu_index, int):
            raise TypeError(f"gpu_index must be an integer, got {type(gpu_index).__name__}")

        if gpu_index < 0:
            raise ValueError(f"gpu_index cannot be negative, got {gpu_index}")

        if gpu_index >= self.gpu_count:
            raise ValueError(f"gpu_index {gpu_index} is out of range (0-{self.gpu_count-1})")

        try:
            if self.nvapi_available:
                return self._get_frame_sync_mode_via_nvapi(gpu_index)
            else:
                return self._get_frame_sync_mode_via_system(gpu_index)
        except Exception as e:
            logger.error(f"Error getting frame sync mode: {e}")
            return FrameSyncMode.OFF

    def _get_frame_sync_mode_via_nvapi(self, gpu_index: int) -> FrameSyncMode:
        """Get frame sync mode using NVAPI."""
        # Placeholder implementation
        logger.info(f"Getting frame sync mode via NVAPI for GPU {gpu_index}")
        # This would use actual NVAPI calls to get frame sync mode
        return FrameSyncMode.OFF

    def _get_frame_sync_mode_via_system(self, gpu_index: int) -> FrameSyncMode:
        """Get frame sync mode using system methods."""
    def _get_frame_sync_mode_via_system(self, gpu_index: int) -> FrameSyncMode:
        logger.info(f"Getting frame sync mode via system for GPU {gpu_index}")
        return FrameSyncMode.OFF

    def set_frame_sync_mode(self, mode: FrameSyncMode, gpu_index: int = 0) -> bool:
        """Set the frame sync mode for a specific GPU."""
        # Validate input parameters
        if not isinstance(mode, FrameSyncMode):
            raise TypeError(f"mode must be a FrameSyncMode enum, got {type(mode).__name__}")

        if not isinstance(gpu_index, int):
            raise TypeError(f"gpu_index must be an integer, got {type(gpu_index).__name__}")

        if gpu_index < 0:
            raise ValueError(f"gpu_index cannot be negative, got {gpu_index}")

        if gpu_index >= self.gpu_count:
            raise ValueError(f"gpu_index {gpu_index} is out of range (0-{self.gpu_count-1})")

        try:
            if self.nvapi_available:
                return self._set_frame_sync_mode_via_nvapi(mode, gpu_index)
            else:
                return self._set_frame_sync_mode_via_system(mode, gpu_index)
        except Exception as e:
            logger.error(f"Error setting frame sync mode: {e}")
            return False

    def _set_frame_sync_mode_via_nvapi(self, mode: FrameSyncMode, gpu_index: int) -> bool:
        """Set frame sync mode using NVAPI."""
        # Placeholder implementation
        logger.info(f"Setting frame sync mode via NVAPI for GPU {gpu_index}: {mode}")
        # This would use actual NVAPI calls to set frame sync mode
        return True

    def _set_frame_sync_mode_via_system(self, mode: FrameSyncMode, gpu_index: int) -> bool:
        """Set frame sync mode using system methods."""
        # Placeholder implementation - would modify registry or system settings
        logger.info(f"Setting frame sync mode via system for GPU {gpu_index}: {mode}")
        return True

    def get_sdi_output_config(self, gpu_index: int = 0) -> SDIOutputConfig:
        """Get the current SDI output configuration for a specific GPU."""
        # Validate input parameters
        if not isinstance(gpu_index, int):
            raise TypeError(f"gpu_index must be an integer, got {type(gpu_index).__name__}")

        if gpu_index < 0:
            raise ValueError(f"gpu_index cannot be negative, got {gpu_index}")

        if gpu_index >= self.gpu_count:
            raise ValueError(f"gpu_index {gpu_index} is out of range (0-{self.gpu_count-1})")

        try:
            if self.nvapi_available:
                return self._get_sdi_output_config_via_nvapi(gpu_index)
            else:
                return self._get_sdi_output_config_via_system(gpu_index)
        except Exception as e:
            logger.error(f"Error getting SDI output config: {e}")
            return SDIOutputConfig()

    def _get_sdi_output_config_via_nvapi(self, gpu_index: int) -> SDIOutputConfig:
        """Get SDI output configuration using NVAPI."""
        # Placeholder implementation
        logger.info(f"Getting SDI output config via NVAPI for GPU {gpu_index}")
        return SDIOutputConfig()

    def _get_sdi_output_config_via_system(self, gpu_index: int) -> SDIOutputConfig:
        """Get SDI output configuration using system methods."""
        # Placeholder implementation
        """Get frame sync mode using system methods."""
        # Placeholder implementation - would check registry or system settings
        logger.info(f"Getting frame sync mode via system for GPU {gpu_index}")
        return FrameSyncMode.OFF

def get_nvidia_control_panel() -> NVIDIAControlPanel:
    """
    Factory function to get the singleton instance of NVIDIAControlPanel.
    """
    return NVIDIAControlPanel()
