"""Pure validation, image processing and export helpers."""

import io
import re
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MAX_TURNS = 20
MAX_IMAGES = 3
MAX_TEXT = 6000


def valid_email(value: str) -> bool:
    """Intentionally accept one ordinary ASCII mailbox, never a header/list."""
    return bool(value and len(value) <= 254 and re.fullmatch(
        r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+", value
    ))


def prepare_image(data: bytes) -> bytes:
    """Validate actual pixels; orient, resize and re-encode without EXIF."""
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Choose a JPG or PNG image smaller than 8 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in {"JPEG", "PNG"}:
                    raise ValueError("Only genuine JPG and PNG images are supported.")
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image is too large. Crop or resize it below 20 megapixels.")
                source.load()
                oriented = ImageOps.exif_transpose(source)
                rgba = oriented.convert("RGBA")
                image = Image.new("RGB", rgba.size, "white")
                image.paste(rgba, mask=rgba.getchannel("A"))
                image.thumbnail((1600, 1600))
                output = io.BytesIO()
                image.save(output, "JPEG", quality=88, optimize=True)
                return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError("This image cannot be read. Try a clear JPG or PNG.") from exc


def revision_export(name: str, summary: str, demo: bool = False) -> str:
    label = "DEMO - prewritten BFS example\n\n" if demo else ""
    safe_name = " ".join(name.split())[:60]
    return (f"# Snap & Study | Revision pack\n\nPrepared for {safe_name}\n\n"
            f"{label}{summary.strip()}\n\n---\n"
            "Check important results against your course material.\n")


def transcript_export(messages: list[dict]) -> str:
    lines = ["# Snap & Study | Conversation", ""]
    for message in messages:
        lines.extend([f"## {'You' if message['role'] == 'user' else 'Tutor'}", ""])
        if message.get("image"):
            lines.extend(["[Image attached; pixels are not included in this export.]", ""])
        lines.extend([message["text"], ""])
    return "\n".join(lines)
