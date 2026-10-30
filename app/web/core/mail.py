import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template, render_to_string


def render_text(template_name, context):
    # Plain text, so the escaping of the html templates shouldn't be applied.
    template = get_template(template_name).template
    return template.render(Context(context, autoescape=False)).strip()


def send_template_mail(
    subject,
    template_name,
    context,
    to_emails,
    button_text=None,
    button_url=None,
    login_required=True,
):
    """
    Sends the text template as plain text and html. Paragraphs in the template are separated
    by a blank line, the button is added by the mail layout in mail/base.html and mail/base.txt.
    """
    body = render_text(template_name, context)
    layout_context = {
        "subject": subject,
        "body": body,
        "paragraphs": re.split(r"\n\s*\n", body),
        "button_text": button_text,
        "button_url": button_url,
        "login_required": login_required,
    }
    message = EmailMultiAlternatives(
        subject,
        render_text("mail/base.txt", layout_context),
        settings.FROM_EMAIL,
        to_emails,
    )
    message.attach_alternative(
        render_to_string("mail/base.html", layout_context), "text/html"
    )
    return message.send(fail_silently=False)
