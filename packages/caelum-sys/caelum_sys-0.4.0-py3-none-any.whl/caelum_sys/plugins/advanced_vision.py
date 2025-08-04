"""
Advanced Screen Capture Plugin for CaelumSys
High-performance vision with MSS, OpenCV, and Tesseract as core dependencies (v0.4.1+)
All backends are guaranteed to be available - no optional imports needed
"""

import base64
import io
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2

# High-performance libraries are now core dependencies (v0.4.0+)
import mss
import numpy as np
import pyautogui
import pytesseract
from PIL import Image, ImageDraw

from caelum_sys.registry import register_command

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False


@register_command("ultra fast screenshot", safe=True)
def ultra_fast_screenshot() -> str:
    """Take a screenshot using MSS (3x faster than PyAutoGUI)."""
    try:
        timestamp = int(time.time())

        with mss.mss() as sct:
            # Grab the entire screen
            monitor = sct.monitors[1]  # Monitor 1 (primary)
            screenshot = sct.grab(monitor)

            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            filename = f"ultra_screenshot_{timestamp}.png"
            img.save(filename)

            return f"⚡ Ultra-fast screenshot saved as: {filename} (MSS backend - 3x faster)"

    except Exception as e:
        return f"❌ Failed to take ultra-fast screenshot: {str(e)}"


@register_command("lightning region capture {x1} {y1} {x2} {y2}", safe=True)
def lightning_region_capture(x1: int, y1: int, x2: int, y2: int) -> str:
    """Capture screen region with maximum speed using MSS (10x faster than PyAutoGUI for regions)."""
    try:
        # Calculate region
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        left = min(x1, x2)
        top = min(y1, y2)

        with mss.mss() as sct:
            # Define the region to capture
            region = {"top": top, "left": left, "width": width, "height": height}

            start_time = time.time()
            screenshot = sct.grab(region)
            capture_time = (time.time() - start_time) * 1000  # Convert to ms

            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            timestamp = int(time.time())
            filename = f"lightning_region_{timestamp}.png"
            img.save(filename)

            return (
                f"⚡ Lightning region capture: {filename}\n"
                f"   Region: ({left},{top},{width},{height})\n"
                f"   Capture time: {capture_time:.2f}ms (MSS backend - 10x faster)"
            )

    except Exception as e:
        return f"❌ Failed lightning region capture: {str(e)}"


@register_command("gaming pixel monitor {x} {y} fps {target_fps}", safe=True)
def gaming_pixel_monitor(x: int, y: int, target_fps: int) -> str:
    """Ultra-high-speed pixel monitoring for gaming (up to 1000+ FPS with MSS)."""
    try:
        if target_fps > 1000:
            return "❌ Maximum target FPS is 1000 for safety"

        frame_time = 1.0 / target_fps

        with mss.mss() as sct:
            # Define 1x1 pixel region
            region = {"top": y, "left": x, "width": 1, "height": 1}

            # Get initial pixel
            initial_pixel = sct.grab(region)
            initial_color = initial_pixel.pixel(0, 0)  # Get RGB tuple

            print(
                f"🎮 Gaming pixel monitor active at ({x}, {y}) - Target: {target_fps} FPS"
            )
            start_time = time.time()
            frames = 0

            while frames < target_fps * 5:  # Run for 5 seconds max
                current_pixel = sct.grab(region)
                current_color = current_pixel.pixel(0, 0)
                frames += 1

                if current_color != initial_color:
                    elapsed = time.time() - start_time
                    actual_fps = frames / elapsed if elapsed > 0 else 0

                    return (
                        f"🎯 PIXEL CHANGE DETECTED at ({x}, {y})!\n"
                        f"   From: RGB{initial_color} → To: RGB{current_color}\n"
                        f"   Performance: {actual_fps:.0f} FPS (Target: {target_fps} FPS)\n"
                        f"   Detection time: {elapsed:.3f}s after {frames} frames"
                    )

                # Precise timing
                time.sleep(max(0, frame_time - 0.0001))  # Account for processing time

            elapsed = time.time() - start_time
            actual_fps = frames / elapsed if elapsed > 0 else 0
            return (
                f"🎮 Gaming monitor complete: No changes detected\n"
                f"   Performance: {actual_fps:.0f} FPS (Target: {target_fps} FPS)"
            )

    except Exception as e:
        return f"❌ Failed gaming pixel monitor: {str(e)}"


@register_command("read text from screen region {x1} {y1} {x2} {y2}", safe=True)
def read_text_from_region(x1: int, y1: int, x2: int, y2: int) -> str:
    """Extract text from screen region using Tesseract OCR."""
    try:
        # Calculate region
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        left = min(x1, x2)
        top = min(y1, y2)

        # Capture region using MSS (fastest method)
        with mss.mss() as sct:
            region = {"top": top, "left": left, "width": width, "height": height}
            screenshot = sct.grab(region)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        # OCR text extraction with Tesseract
        text = pytesseract.image_to_string(img).strip()

        if text:
            return (
                f"📖 Text extracted from region ({left},{top},{width},{height}):\n"
                f"   '{text}'"
            )
        else:
            return (
                f"📖 No readable text found in region ({left},{top},{width},{height})"
            )

    except Exception as e:
        return f"❌ Failed to read text from screen: {str(e)}"


@register_command(
    "opencv template match {template_path} confidence {confidence}", safe=True
)
def opencv_template_match(template_path: str, confidence: float) -> str:
    """Find template image on screen using OpenCV (much faster than PyAutoGUI)."""
    try:
        if confidence < 0.1 or confidence > 1.0:
            return "❌ Confidence must be between 0.1 and 1.0"

        # Take screenshot using MSS
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            # Convert to OpenCV format
            screen_img = np.array(screenshot)[:, :, :3]  # Remove alpha channel
            screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGB2BGR)

        # Load template
        template = cv2.imread(template_path)
        if template is None:
            return f"❌ Could not load template image: {template_path}"

        # Template matching
        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)

        if len(locations[0]) > 0:
            matches = []
            for i in range(len(locations[0])):
                x, y = locations[1][i], locations[0][i]
                h, w = template.shape[:2]
                center_x, center_y = x + w // 2, y + h // 2
                match_confidence = result[y, x]
                matches.append((center_x, center_y, match_confidence))

            # Sort by confidence
            matches.sort(key=lambda x: x[2], reverse=True)

            result_text = f"🎯 Found {len(matches)} matches for {template_path}:\n"
            for i, (cx, cy, conf) in enumerate(matches[:5]):  # Show top 5
                result_text += f"   {i+1}. ({cx}, {cy}) - Confidence: {conf:.3f}\n"

            if len(matches) > 5:
                result_text += f"   ... and {len(matches)-5} more matches"

            return result_text
        else:
            return f"❌ Template not found on screen: {template_path} (confidence: {confidence})"

    except Exception as e:
        return f"❌ Failed OpenCV template matching: {str(e)}"


@register_command("performance benchmark screen capture", safe=True)
def benchmark_screen_capture() -> str:
    """Benchmark different screen capture methods to find the fastest."""
    try:
        results = []
        iterations = 10

        # Test PyAutoGUI
        start_time = time.time()
        for _ in range(iterations):
            pyautogui.screenshot()
        pyautogui_time = (time.time() - start_time) / iterations * 1000
        results.append(f"PyAutoGUI: {pyautogui_time:.2f}ms per screenshot")

        # Test MSS
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            start_time = time.time()
            for _ in range(iterations):
                sct.grab(monitor)
            mss_time = (time.time() - start_time) / iterations * 1000
            results.append(
                f"MSS: {mss_time:.2f}ms per screenshot ({pyautogui_time/mss_time:.1f}x faster)"
            )

        # Test region capture
        with mss.mss() as sct:
            region = {"top": 100, "left": 100, "width": 200, "height": 200}
            start_time = time.time()
            for _ in range(iterations):
                sct.grab(region)
            region_time = (time.time() - start_time) / iterations * 1000
            results.append(f"MSS Region (200x200): {region_time:.2f}ms per capture")

        benchmark_result = "📊 Screen Capture Performance Benchmark:\n" + "\n".join(
            f"   • {r}" for r in results
        )

        # Add recommendations
        benchmark_result += f"\n\n💡 Recommendations:\n"
        benchmark_result += f"   • MSS provides maximum speed\n"
        benchmark_result += f"   • Small regions can achieve 1000+ FPS\n"
        benchmark_result += f"   • Full screen: ~{1000/mss_time:.0f} FPS possible"

        return benchmark_result

    except Exception as e:
        return f"❌ Failed performance benchmark: {str(e)}"


@register_command("get available vision backends", safe=True)
def get_vision_backends() -> str:
    """List all available computer vision backends and their capabilities."""
    backends = [
        "✅ PyAutoGUI - Basic screen capture and input control",
        "✅ MSS - Ultra-fast screen capture (3-10x faster)",
        "✅ OpenCV - Advanced computer vision and template matching",
        "✅ Tesseract - OCR text extraction from screen",
        "",
        "🚀 PERFORMANCE TIERS:",
        "   • Gaming/Real-time: MSS + OpenCV",
        "   • OCR Applications: Tesseract + MSS",
        "   • Basic Automation: PyAutoGUI",
        "",
        "✅ ALL BACKENDS INCLUDED:",
        "   High-performance vision is built into CaelumSys v0.4.1+",
    ]

    return "\n".join(backends)


@register_command(
    "extreme gaming monitor {x1} {y1} {x2} {y2} threshold {threshold} max_fps {fps}",
    safe=True,
)
def extreme_gaming_monitor(
    x1: int, y1: int, x2: int, y2: int, threshold: float, fps: int
) -> str:
    """Extreme performance gaming monitor using MSS + OpenCV for maximum speed."""
    try:
        if fps > 500:
            return "❌ Maximum FPS is 500 for extreme gaming monitor"

        if threshold < 0.01 or threshold > 1.0:
            return "❌ Threshold must be between 0.01 and 1.0"

        # Calculate region
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        left = min(x1, x2)
        top = min(y1, y2)

        frame_time = 1.0 / fps

        with mss.mss() as sct:
            region = {"top": top, "left": left, "width": width, "height": height}

            # Get baseline
            baseline_capture = sct.grab(region)
            baseline_array = np.array(baseline_capture)[:, :, :3]  # Remove alpha

            print(f"🔥 EXTREME gaming monitor active - {fps} FPS target")
            start_time = time.time()
            frames = 0
            max_frames = fps * 10  # 10 seconds max

            while frames < max_frames:
                current_capture = sct.grab(region)
                current_array = np.array(current_capture)[:, :, :3]
                frames += 1

                # Ultra-fast difference calculation using OpenCV
                diff = cv2.absdiff(baseline_array, current_array)
                change_percentage = np.mean(diff) / 255.0

                if change_percentage >= threshold:
                    elapsed = time.time() - start_time
                    actual_fps = frames / elapsed if elapsed > 0 else 0

                    # Save detection
                    timestamp = int(time.time())
                    filename = f"extreme_gaming_detection_{timestamp}.png"
                    cv2.imwrite(
                        filename, cv2.cvtColor(current_array, cv2.COLOR_RGB2BGR)
                    )

                    return (
                        f"🔥 EXTREME CHANGE DETECTED!\n"
                        f"   Change: {change_percentage:.3f} (threshold: {threshold})\n"
                        f"   Performance: {actual_fps:.0f} FPS (target: {fps} FPS)\n"
                        f"   Detection: {elapsed:.3f}s after {frames} frames\n"
                        f"   Screenshot: {filename}"
                    )

                # Precise timing for extreme performance
                time.sleep(max(0, frame_time - 0.0005))

            elapsed = time.time() - start_time
            actual_fps = frames / elapsed if elapsed > 0 else 0
            return (
                f"🔥 Extreme gaming monitor complete: No changes above threshold\n"
                f"   Performance: {actual_fps:.0f} FPS (target: {fps} FPS)\n"
                f"   Frames processed: {frames} in {elapsed:.2f}s"
            )

    except Exception as e:
        return f"❌ Failed extreme gaming monitor: {str(e)}"
