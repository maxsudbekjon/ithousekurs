from django.core.exceptions import ValidationError
from PIL import Image

MAX_IMAGE_SIZE_MB = 100  # umumiy limit (ixtiyoriy)


def validate_desktop_banner(image):
    _validate_image(
        image=image,
        required_width=1200,
        required_height=400,
        aspect_ratio=(16, 9),
        field_name="Desktop banner"
    )


def validate_mobile_banner(image):
    _validate_image(
        image=image,
        required_width=360,
        required_height=120,
        aspect_ratio=(3, 1),
        field_name="Mobile banner"
    )


def _validate_image(image, required_width, required_height, aspect_ratio, field_name):
    # 1️⃣ Fayl hajmi (MB)
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"{field_name}: rasm hajmi {MAX_IMAGE_SIZE_MB}MB dan oshmasligi kerak."
        )

    # 2️⃣ Rasmni ochish
    try:
        img = Image.open(image)
        img.verify()
        image.seek(0)
        img = Image.open(image)
    except Exception:
        raise ValidationError(f"{field_name}: yaroqsiz rasm fayli.")

    # 3️⃣ Format
    if img.format not in ['JPEG', 'PNG', 'WEBP']:
        raise ValidationError(
            f"{field_name}: faqat JPEG, PNG yoki WEBP format ruxsat etiladi."
        )

    # 4️⃣ Aniq o‘lcham tekshiruvi
    if img.width != required_width or img.height != required_height:
        raise ValidationError(
            f"{field_name}: rasm aniq {required_width}x{required_height} bo‘lishi kerak."
        )

    # 5️⃣ Nisbat (ratio) tekshiruvi (extra himoya)
    expected_ratio = aspect_ratio[0] / aspect_ratio[1]
    actual_ratio = img.width / img.height

    if abs(actual_ratio - expected_ratio) > 0.01:
        raise ValidationError(
            f"{field_name}: rasm nisbatı {aspect_ratio[0]}:{aspect_ratio[1]} bo‘lishi kerak."
        )
