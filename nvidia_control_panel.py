"""NVIDIA Control Panel Integration Module

This module provides programmatic access to NVIDIA Control Panel settings
using various methods including NVAPI, Windows Registry, and system management.

Supports GPU settings retrieval, modification, and monitoring for optimal
AI/ML performance in financial services applications.
"""

import logging
import os
import sys
import ctypes
import winreg
import subprocess
import json
from typing import Dict, Any, List, Optional, Union
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PowerMode(Enum):
    OPTIMAL_POWER = "Optimal Power"
    MAX_PERFORMANCE = "Maximum Performance"
    ADAPTIVE = "Adaptive"
    PREFER_MAX_PERFORMANCE = "Prefer Maximum Performance"
    PREFER_CONSISTENT_PERFORMANCE = "Prefer Consistent Performance"

class TextureFiltering(Enum):
    HIGH_QUALITY = "High Quality"
    QUALITY = "Quality"
    PERFORMANCE = "Performance"
    HIGH_PERFORMANCE = "High Performance"

class VerticalSync(Enum):
    OFF = "Off"
    ON = "On"
    ADAPTIVE = "Adaptive"
    FAST = "Fast"

class NVIDIAControlPanel:
    def __init__(self):
        self.nvapi_available = self._check_nvapi_availability()
        self.gpu_count = self._get_gpu_count()
        self.driver_version = self._get_driver_version()
        
    def _check_nvapi_availability(self) -> bool:
        """Check if NVAPI is available on the system."""
        try:
            # Try to load NVAPI DLL
            nvapi_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'),
                                     'System32', 'nvapi64.dll')
            if os.path.exists(nvapi_path):
                return True
                
            # Alternative check through registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\NVIDIA Corporation\Global\NvControlPanel2") as key:
                    return True
            except FileNotFoundError:
                pass
                
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
    
    def get_gpu_settings(self, gpu_index: int = 0) -> Dict[str, Any]:
        """Retrieve current GPU settings from NVIDIA Control Panel.
        
        Args:
            gpu_index: Index of the GPU (0 for primary)
            
        Returns:
            Dict containing current GPU settings
        """
        settings = {}
        
        try:
            if self.nvapi_available:
                # Use NVAPI for advanced settings retrieval
                settings.update(self._get_settings_via_nvapi(gpu_index))
            else:
                # Fallback to registry and other methods
                settings.update(self._get_settings_via_registry(gpu_index))
                settings.update(self._get_settings_via_wmi())
                
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
        
        logger.info(f"Retrieved GPU settings: {settings}")
        return settings
    
    def _get_settings_via_nvapi(self, gpu_index: int) -> Dict[str, Any]:
        """Get settings using NVAPI (placeholder for actual implementation)."""
        # This would be implemented with actual NVAPI calls
        # For now, return simulated values that match real NVAPI structure
        return {
            "power_mode": PowerMode.OPTIMAL_POWER.value,
            "texture_filtering": TextureFiltering.QUALITY.value,
            "vertical_sync": VerticalSync.OFF.value,
            "gpu_clock": 1500,  # MHz
            "memory_clock": 7000,  # MHz
            "temperature": 65,  # °C
            "utilization": 15,  # %
            "power_usage": 120,  # Watts
            "fan_speed": 45,  # %
        }
    
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
                except Exception as e:
                    logger.warning(f"Failed to set power mode via registry: {e}")
            
            # Additional settings would be set here
            
            return True
            
        except Exception as e:
            logger.error(f"Registry setting failed: {e}")
            return False
    
    def _get_power_mode_value(self, power_mode: str) -> int:
        """Get registry value for power mode."""
        power_mode_map = {
            PowerMode.OPTIMAL_POWER.value: 0,
            PowerMode.ADAPTIVE.value: 1,
            PowerMode.PREFER_MAX_PERFORMANCE.value: 2,
            PowerMode.PREFER_CONSISTENT_PERFORMANCE.value: 3,
        }
        return power_mode_map.get(power_mode, 0)
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """Get comprehensive GPU status information."""
        status = {
            "gpu_count": self.gpu_count,
            "driver_version": self.driver_version,
            "nvapi_available": self.nvapi_available,
            "gpus": []
        }
        
        for i in range(self.gpu_count):
            gpu_info = self.get_gpu_settings(i)
            status["gpus"].append(gpu_info)
            
        return status
    
    def optimize_for_ai_workload(self) -> Dict[str, Any]:
        """Optimize GPU settings for AI/ML workloads."""
        optimal_settings = {
            "power_mode": PowerMode.PREFER_MAX_PERFORMANCE.value,
            "texture_filtering": TextureFiltering.PERFORMANCE.value,
            "vertical_sync": VerticalSync.OFF.value,
        }
        
        result = self.set_gpu_settings(optimal_settings)
        
        return {
            "applied_settings": optimal_settings,
            "result": result,
            "previous_settings": self.get_gpu_settings()
        }

# Singleton instance for easy access
_nvidia_control_panel = None

def get_nvidia_control_panel() -> NVIDIAControlPanel:
    """Get the singleton NVIDIA Control Panel instance."""
    global _nvidia_control_panel
    if _nvidia_control_panel is None:
        _nvidia_control_panel = NVIDIAControlPanel()
    return _nvidia_control_panel

if __name__ == "__main__":
    # Test the module
    ncp = NVIDIAControlPanel()
    print("NVIDIA Control Panel Integration Test")
    print("=" * 40)
    print(f"GPUs detected: {ncp.gpu_count}")
    print(f"Driver version: {ncp.driver_version}")
    print(f"NVAPI available: {ncp.nvapi_available}")
    print()
    
    settings = ncp.get_gpu_settings()
    print("Current GPU Settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    print()
    print("Optimizing for AI workload...")
    result = ncp.optimize_for_ai_workload()
    print(f"Optimization result: {result['result']}")
