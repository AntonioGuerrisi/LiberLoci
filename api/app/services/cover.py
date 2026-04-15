import hashlib
import io
import logging

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


def process_cover(image_bytes: bytes) -> tuple[bytes, int, int, str]:
    """Resize image to max 900px longest side, convert to JPEG.

    Returns (jpeg_bytes, width, height, sha256_checksum).
    """
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    w, h = img.size
    max_size = settings.cover_max_size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=settings.cover_jpeg_quality)
    data = buf.getvalue()

    checksum = hashlib.sha256(data).hexdigest()
    final_w, final_h = img.size
    return data, final_w, final_h, checksum


def download_cover(url: str) -> bytes | None:
    """Download an image from a URL. Returns raw bytes or None on failure."""
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            logger.info("cover_download", extra={"url": url, "size_bytes": len(resp.content)})
            return resp.content
    except Exception as exc:
        logger.warning("cover_download_error", extra={"url": url, "error": str(exc)})
        return None
