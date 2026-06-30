import base64
import io
import os
from PIL import Image
import qrcode

from hte.settings import IMAGE_PATH

def generate_qrcode(url: str) -> str:
    qr = qrcode.QRCode(
        version=3,
        border=1,
        box_size=10,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(url)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # 中心加水印 logo
    image_path = os.path.join(IMAGE_PATH, f"logo.jpg")
    logo = Image.open(image_path)
    logo_size = 80
    logo = logo.resize((logo_size, logo_size))
    pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
    img.paste(logo, pos)

    buffered = io.BytesIO()
    img.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode('utf-8')