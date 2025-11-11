import os
from django.conf import settings
from django.forms import ValidationError
import magic
from django.utils.translation import gettext_lazy as _


def validate_email_wrapper(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def validate_uploaded_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    file.seek(0)
    file_chunk = file.read(2048)
    file.seek(0)
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(file_chunk)
    if file_mime_type not in settings.ALLOWED_FILE_TYPES or ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(_("Dit bestandstype is niet toegestaan."))
