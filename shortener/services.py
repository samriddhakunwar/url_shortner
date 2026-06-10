import base64
import io
import qrcode

from .models import ShortURL
from .utils import generate_short_code


def create_short_url(user, original_url, custom_alias=None, expires_at=None):
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

    _generate_qr_code(short_url)
    return short_url


def _generate_qr_code(short_url_obj):
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
    img.save(buffer, format='PNG')
    short_url_obj.qr_code = base64.b64encode(buffer.getvalue()).decode('utf-8')
    short_url_obj.save(update_fields=['qr_code'])
