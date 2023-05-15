import base64
import mimetypes
import os
from django.core.files.storage import default_storage
from django.template import Library

register = Library()


@register.filter
def image_to_base64(image):
    if not image:
        return None

    with default_storage.open(image.path, 'rb') as img_file:
        img_data = img_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        content_type, _ = mimetypes.guess_type(image.path)

    return f'data:{content_type};base64,{img_base64}'



@register.filter
def basename(url):
    return os.path.basename(url)
