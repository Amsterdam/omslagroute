from django.views.generic import FormView
from .forms import *
from constance import config
from django.http.response import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def validate_email_wrapper(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class FeedbackFormView(FormView):
    form_class = FeedbackForm
    template_name = 'feedback/feedback.html'
    success_url = '.?send=1'

    def form_valid(self, form):
        addresses = [x.strip() for x in config.FEEDBACK_RECIPIENT_LIST.split(',') if validate_email_wrapper(x.strip())]
        if addresses:
            current_site = get_current_site(self.request)
            data = form.cleaned_data
            data.update({
                'site': current_site.domain,
            })
            user = self.request.user
            if user.is_authenticated:
                data.update({
                    'rol': user.user_type_names,
                    'email': '%s%s%s' % (
                        data.get('email', ''),
                        ', ' if data.get('email') else '',
                        user.username,
                    )
                })
                if user.first_name or user.last_name:
                    data.update({
                        'name': user.get_full_name()
                    })
            subject = 'Omslagroute - feedback'
            message = render_to_string('feedback/mail/feedback.txt', data)
            from_email = settings.FROM_EMAIL
            to_emails = addresses
            send_mail(subject, message, from_email, to_emails, fail_silently=False)
        else:
            return HttpResponseRedirect('./?error=1')
        return super().form_valid(form)
