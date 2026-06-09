import io
import qrcode

from django.core.files.base import ContentFile

from .models import ShortURL
from .utils import generate_short_code


def create_short_url(user, original_url, custom_alias=None, expires_at=None):
    """Create a new ShortURL with optional custom alias, expiration, and QR code.

    Args:
        user: The authenticated user who owns this URL.
        original_url: The long URL to shorten.
        custom_alias: Optional custom short code chosen by the user.
        expires_at: Optional expiration datetime.

    Returns:
        The created ShortURL instance.

    Raises:
        ValueError: If the custom_alias is already taken.
    """
    if custom_alias:
        if ShortURL.objects.filter(short_code=custom_alias).exists():
            raise ValueError(f'The alias "{custom_alias}" is already taken.')
        short_code = custom_alias
    else:
        short_code = generate_short_code()

    short_url = ShortURL.objects.create(
        user=user,
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
    )

    # Generate QR code pointing to the short URL
    _generate_qr_code(short_url)

    return short_url


def _generate_qr_code(short_url_obj):
    """Generate a QR code image for the given ShortURL and save it to the model.

    The QR code encodes the redirect URL: /r/<short_code>/
    """
    redirect_path = f'/r/{short_url_obj.short_code}/'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_path)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)

    filename = f'{short_url_obj.short_code}.png'
    short_url_obj.qr_code.save(filename, ContentFile(buffer.read()), save=True)
