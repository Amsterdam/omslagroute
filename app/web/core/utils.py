from calendar import timegm
import hashlib
import hmac
import logging
import os
from django.conf import settings
from django.forms import ValidationError
import magic
import six
import time
from swiftclient.utils import EXPIRES_ISO8601_FORMAT, SHORT_EXPIRES_ISO8601_FORMAT, TIME_ERRMSG
from django.utils.translation import gettext_lazy as _


def validate_email_wrapper(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def generate_temp_url(path, seconds, key, method, absolute=False,
                      prefix=False, iso8601=False):
    """Generates a temporary URL that gives unauthenticated access to the
    Swift object.

    :param path: The full path to the Swift object or prefix if
         a prefix-based temporary URL should be generated. Example:
        /v1/AUTH_account/c/o or /v1/AUTH_account/c/prefix.
    :param seconds: time in seconds or ISO 8601 timestamp.
        If absolute is False and this is the string representation of an
        integer, then this specifies the amount of time in seconds for which
        the temporary URL will be valid.
        If absolute is True then this specifies an absolute time at which the
        temporary URL will expire.
    :param key: The secret temporary URL key set on the Swift
        cluster. To set a key, run 'swift post -m
        "Temp-URL-Key: <substitute tempurl key here>"'
    :param method: A HTTP method, typically either GET or PUT, to allow
        for this temporary URL.
    :param absolute: if True then the seconds parameter is interpreted as a
        Unix timestamp, if seconds represents an integer.
    :param prefix: if True then a prefix-based temporary URL will be generated.
    :param iso8601: if True, a URL containing an ISO 8601 UTC timestamp
        instead of a UNIX timestamp will be created.
    :raises ValueError: if timestamp or path is not in valid format.
    :return: the path portion of a temporary URL
    """
    try:
        try:
            timestamp = float(seconds)
        except ValueError:
            formats = (
                EXPIRES_ISO8601_FORMAT,
                EXPIRES_ISO8601_FORMAT[:-1],
                SHORT_EXPIRES_ISO8601_FORMAT)
            for f in formats:
                try:
                    t = time.strptime(seconds, f)
                except ValueError:
                    t = None
                else:
                    if f == EXPIRES_ISO8601_FORMAT:
                        timestamp = timegm(t)
                    else:
                        # Use local time if UTC designator is missing.
                        timestamp = int(time.mktime(t))

                    absolute = True
                    break

            if t is None:
                raise ValueError()
        else:
            if not timestamp.is_integer():
                raise ValueError()
            timestamp = int(timestamp)
            if timestamp < 0:
                raise ValueError()
    except ValueError:
        raise ValueError(TIME_ERRMSG)

    if isinstance(path, six.binary_type):
        try:
            path_for_body = path.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError('path must be representable as UTF-8')
    else:
        path_for_body = path

    parts = path_for_body.split('/', 4)
    # if len(parts) != 5 or parts[0] or not all(parts[1:(4 if prefix else 5)]):
    #     if prefix:
    #         raise ValueError('path must at least contain /v1/a/c/')
    #     else:
    #         raise ValueError('path must be full path to an object'
    #                          ' e.g. /v1/a/c/o')

    standard_methods = ['GET', 'PUT', 'HEAD', 'POST', 'DELETE']
    if method.upper() not in standard_methods:
        logger = logging.getLogger("swiftclient")
        logger.warning('Non default HTTP method %s for tempurl specified, '
                       'possibly an error', method.upper())

    if not absolute:
        expiration = int(time.time() + timestamp)
    else:
        expiration = timestamp
    hmac_body = u'\n'.join([method.upper(), str(expiration),
                            ('prefix:' if prefix else '') + path_for_body])

    # Encode to UTF-8 for py3 compatibility
    if not isinstance(key, six.binary_type):
        key = key.encode('utf-8')
    sig = hmac.new(key, hmac_body.encode('utf-8'), hashlib.sha1).hexdigest()

    if iso8601:
        expiration = time.strftime(
            EXPIRES_ISO8601_FORMAT, time.gmtime(expiration))

    temp_url = u'{path}?temp_url_sig={sig}&temp_url_expires={exp}'.format(
        path=path_for_body, sig=sig, exp=expiration)
    if prefix:
        temp_url += u'&temp_url_prefix={}'.format(parts[4])
    # Have return type match path from caller
    if isinstance(path, six.binary_type):
        return temp_url.encode('utf-8')
    else:
        return temp_url


def validate_uploaded_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    file.seek(0)
    file_chunk = file.read(2048)
    file.seek(0)
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(file_chunk)
    if file_mime_type not in settings.ALLOWED_FILE_TYPES or ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(_("Dit bestandstype is niet toegestaan."))
