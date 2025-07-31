import osascript
from . import constants

def clamp(value, min_value, max_value):
    """Clamp the value between min_value and max_value."""
    return max(min_value, min(value, max_value))

def get_true_volume():
    """Get the current output volume of the system."""
    return int(osascript.osascript("output volume of (get volume settings)")[1])

def set_volume(volume, min = constants.min_volume, max = constants.max_volume):
    """Set the output volume of the system, clamping it between min and max."""
    osascript.osascript(f"set volume output volume {clamp(volume, min, max)}")

def change_volume(current: float, delta: float, min = constants.min_volume, max = constants.max_volume):
    """Change the current volume by delta, clamping it between min and max."""
    current_volume = clamp(current + delta, min, max)
    set_volume(current_volume)
    return current_volume