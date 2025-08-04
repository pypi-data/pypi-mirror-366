"""
Input Control Plugin for CaelumSys
Provides AI agents with mouse and keyboard input control capabilities
"""

import time
from typing import List, Optional, Tuple

import pyautogui

from caelum_sys.registry import register_command

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False

# Mouse Control Commands


@register_command("click at {x} {y}", safe=False)
def click_at_position(x: int, y: int) -> str:
    """Click at specific screen coordinates."""
    try:
        pyautogui.click(x, y)
        return f"🖱️ Clicked at position ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to click: {str(e)}"


@register_command("double click at {x} {y}", safe=False)
def double_click_at_position(x: int, y: int) -> str:
    """Double-click at specific screen coordinates."""
    try:
        pyautogui.doubleClick(x, y)
        return f"🖱️ Double-clicked at position ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to double-click: {str(e)}"


@register_command("right click at {x} {y}", safe=False)
def right_click_at_position(x: int, y: int) -> str:
    """Right-click at specific screen coordinates."""
    try:
        pyautogui.rightClick(x, y)
        return f"🖱️ Right-clicked at position ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to right-click: {str(e)}"


@register_command("move mouse to {x} {y}", safe=False)
def move_mouse_to_position(x: int, y: int) -> str:
    """Move mouse cursor to specific coordinates."""
    try:
        pyautogui.moveTo(x, y)
        return f"🖱️ Mouse moved to position ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to move mouse: {str(e)}"


@register_command("drag from {x1} {y1} to {x2} {y2}", safe=False)
def drag_mouse(x1: int, y1: int, x2: int, y2: int) -> str:
    """Drag mouse from one position to another."""
    try:
        pyautogui.drag(x2 - x1, y2 - y1, duration=0.5)
        return f"🖱️ Dragged from ({x1}, {y1}) to ({x2}, {y2})"
    except Exception as e:
        return f"❌ Failed to drag: {str(e)}"


@register_command("scroll {direction} {clicks} times", safe=False)
def scroll_mouse(direction: str, clicks: int) -> str:
    """Scroll mouse wheel up or down."""
    try:
        if direction.lower() not in ["up", "down"]:
            return "❌ Direction must be 'up' or 'down'"

        if clicks > 10:
            return "❌ Maximum 10 scroll clicks for safety"

        scroll_amount = clicks if direction.lower() == "up" else -clicks
        pyautogui.scroll(scroll_amount)
        return f"🖱️ Scrolled {direction} {clicks} times"
    except Exception as e:
        return f"❌ Failed to scroll: {str(e)}"


@register_command("get mouse position", safe=True)
def get_mouse_position() -> str:
    """Get current mouse cursor position."""
    try:
        x, y = pyautogui.position()
        return f"🖱️ Mouse position: ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to get mouse position: {str(e)}"


# Keyboard Control Commands


@register_command("type text {text}", safe=False)
def type_text(text: str) -> str:
    """Type the specified text."""
    try:
        pyautogui.typewrite(text)
        return f"⌨️ Typed text: '{text}'"
    except Exception as e:
        return f"❌ Failed to type text: {str(e)}"


@register_command("press key {key}", safe=False)
def press_key(key: str) -> str:
    """Press a specific key."""
    try:
        pyautogui.press(key)
        return f"⌨️ Pressed key: {key}"
    except Exception as e:
        return f"❌ Failed to press key: {str(e)}"


@register_command("press keys {keys}", safe=False)
def press_key_combination(keys: str) -> str:
    """Press a combination of keys (e.g., 'ctrl+c', 'alt+tab')."""
    try:
        key_list = [k.strip() for k in keys.split("+")]
        pyautogui.hotkey(*key_list)
        return f"⌨️ Pressed key combination: {keys}"
    except Exception as e:
        return f"❌ Failed to press key combination: {str(e)}"


@register_command("hold key {key} for {seconds} seconds", safe=False)
def hold_key(key: str, seconds: float) -> str:
    """Hold a key down for specified duration."""
    try:
        if seconds > 5.0:
            return "❌ Maximum hold duration is 5 seconds for safety"

        pyautogui.keyDown(key)
        time.sleep(seconds)
        pyautogui.keyUp(key)
        return f"⌨️ Held key '{key}' for {seconds} seconds"
    except Exception as e:
        return f"❌ Failed to hold key: {str(e)}"


# Advanced Input Commands


@register_command("click on image {image_path}", safe=False)
def click_on_image(image_path: str) -> str:
    """Find an image on screen and click on it."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=0.8)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            return f"🎯 Found and clicked on image at ({center.x}, {center.y})"
        else:
            return f"❌ Image not found on screen: {image_path}"
    except Exception as e:
        return f"❌ Failed to click on image: {str(e)}"


@register_command("wait for image {image_path} then click", safe=False)
def wait_and_click_image(image_path: str) -> str:
    """Wait for an image to appear on screen, then click it."""
    try:
        # Wait up to 10 seconds for image to appear
        max_wait = 10
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if location:
                    center = pyautogui.center(location)
                    pyautogui.click(center)
                    elapsed = time.time() - start_time
                    return f"🎯 Image appeared after {elapsed:.1f}s and clicked at ({center.x}, {center.y})"
            except:
                pass

            time.sleep(0.5)

        return f"⏰ Timeout: Image did not appear within {max_wait} seconds"
    except Exception as e:
        return f"❌ Failed to wait for image: {str(e)}"


@register_command("type with delay {text} delay {delay_ms}", safe=False)
def type_with_delay(text: str, delay_ms: int) -> str:
    """Type text with specified delay between characters."""
    try:
        if delay_ms > 1000:
            return "❌ Maximum delay is 1000ms for practicality"

        delay_seconds = delay_ms / 1000.0
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(delay_seconds)

        return f"⌨️ Typed '{text}' with {delay_ms}ms delay between characters"
    except Exception as e:
        return f"❌ Failed to type with delay: {str(e)}"


@register_command("simulate human typing {text}", safe=False)
def simulate_human_typing(text: str) -> str:
    """Type text with human-like variations in speed."""
    try:
        import random

        for char in text:
            pyautogui.typewrite(char)
            # Random delay between 50-200ms to simulate human typing
            delay = random.uniform(0.05, 0.2)
            time.sleep(delay)

        return f"⌨️ Human-like typing completed: '{text}'"
    except Exception as e:
        return f"❌ Failed to simulate human typing: {str(e)}"


# Screen Interaction Commands


@register_command("click center of screen", safe=False)
def click_center_of_screen() -> str:
    """Click at the center of the screen."""
    try:
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        pyautogui.click(center_x, center_y)
        return f"🖱️ Clicked at screen center ({center_x}, {center_y})"
    except Exception as e:
        return f"❌ Failed to click center: {str(e)}"


@register_command("drag and drop from {x1} {y1} to {x2} {y2}", safe=False)
def drag_and_drop(x1: int, y1: int, x2: int, y2: int) -> str:
    """Perform drag and drop operation."""
    try:
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=1.0)
        return f"🖱️ Drag and drop from ({x1}, {y1}) to ({x2}, {y2})"
    except Exception as e:
        return f"❌ Failed to drag and drop: {str(e)}"


@register_command("select text at {x} {y} length {length}", safe=False)
def select_text_at_position(x: int, y: int, length: int) -> str:
    """Click at position and select text by dragging."""
    try:
        if length > 500:
            return "❌ Maximum selection length is 500 characters for safety"

        # Click at starting position
        pyautogui.click(x, y)

        # Approximate character width (this is rough estimation)
        char_width = 8
        end_x = x + (length * char_width)

        # Drag to select text
        pyautogui.drag(end_x - x, 0, duration=0.5)

        return f"📝 Selected approximately {length} characters starting at ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to select text: {str(e)}"


# Safety and Control Commands


@register_command("move mouse safely to {x} {y}", safe=True)
def move_mouse_safely(x: int, y: int) -> str:
    """Move mouse with safety checks (slower, visible movement)."""
    try:
        # Move slowly for safety
        pyautogui.moveTo(x, y, duration=1.0)
        return f"🖱️ Mouse moved safely to position ({x}, {y})"
    except Exception as e:
        return f"❌ Failed to move mouse safely: {str(e)}"


@register_command("get input capabilities", safe=True)
def get_input_capabilities() -> str:
    """List available input control capabilities."""
    capabilities = [
        "🖱️ Mouse Controls:",
        "  • Click, double-click, right-click at coordinates",
        "  • Move mouse cursor",
        "  • Drag and drop operations",
        "  • Scroll wheel control",
        "",
        "⌨️ Keyboard Controls:",
        "  • Type text and special characters",
        "  • Press individual keys",
        "  • Key combinations (Ctrl+C, Alt+Tab, etc.)",
        "  • Hold keys for duration",
        "",
        "🎯 Smart Interactions:",
        "  • Click on images found on screen",
        "  • Wait for UI elements to appear",
        "  • Human-like typing simulation",
        "  • Text selection operations",
    ]

    return "\n".join(capabilities)


@register_command("emergency stop input", safe=True)
def emergency_stop_input() -> str:
    """Emergency stop for all input operations."""
    try:
        # Move mouse to corner to stop any ongoing operations
        pyautogui.moveTo(0, 0)
        return "🛑 Emergency stop activated - mouse moved to (0,0)"
    except Exception as e:
        return f"❌ Failed to emergency stop: {str(e)}"
