import io
from PIL import Image
import pytest
from core import prepare_image, valid_email, revision_export


@pytest.mark.parametrize("address", ["student@example.com", "name+study@college.ac.in"])
def test_email_valid(address):
    assert valid_email(address)


@pytest.mark.parametrize("address", ["", "x", "a@b", "a@b.com\r\nBcc:x@y.com", "a@b.com,c@d.com", "a@b.com\n", "a b@c.com"])
def test_rejects_invalid_or_multiple_email(address):
    assert not valid_email(address)


def test_image_normalization():
    source = io.BytesIO()
    Image.new("RGBA", (2400, 1200), (0, 0, 0, 0)).save(source, "PNG")
    image = Image.open(io.BytesIO(prepare_image(source.getvalue())))
    assert image.format == "JPEG"
    assert image.size == (1600, 800)
    assert image.getpixel((0, 0)) == (255, 255, 255)
    assert not image.getexif()


@pytest.mark.parametrize("data", [b"not a photo", b"", b"x" * (8 * 1024 * 1024 + 1)])
def test_bad_images(data):
    with pytest.raises(ValueError):
        prepare_image(data)


def test_wrong_format():
    source = io.BytesIO()
    Image.new("RGB", (10, 10)).save(source, "GIF")
    with pytest.raises(ValueError, match="genuine"):
        prepare_image(source.getvalue())


def test_demo_export_label():
    assert "DEMO - prewritten" in revision_export("Mahesh", "Hello", demo=True)
