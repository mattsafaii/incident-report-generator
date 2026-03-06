import base64
from io import BytesIO
from pathlib import Path

from PIL import Image

from app.config import FRAME_MAX_WIDTH


def resize_frame(image_path: Path, max_width: int = FRAME_MAX_WIDTH) -> Image.Image:
    """Resize image to max_width maintaining aspect ratio."""
    img = Image.open(image_path)
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    return img


def frame_to_base64(image_path: Path, max_width: int = FRAME_MAX_WIDTH) -> str:
    """Resize and encode frame as base64 JPEG string."""
    img = resize_frame(image_path, max_width)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
