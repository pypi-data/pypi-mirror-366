"""
Nedo Vision Core Library

A library for running AI vision processing and detection in the Nedo Vision platform.
"""

from .core_service import CoreService

__version__ = "0.2.0"
__all__ = ["CoreService"]

# Convenience functions for callback management
def register_ppe_detection_callback(callback):
    """Register a callback for PPE detection events."""
    return CoreService.register_detection_callback('ppe_detection', callback)

def register_area_violation_callback(callback):
    """Register a callback for restricted area violation events."""
    return CoreService.register_detection_callback('area_violation', callback)

def register_general_detection_callback(callback):
    """Register a callback for all detection events."""
    return CoreService.register_detection_callback('general_detection', callback) 