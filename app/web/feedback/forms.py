from django import forms
from captcha.fields import CaptchaField


class FeedbackForm(forms.Form):
    name = forms.CharField(
        required=False,
    )
    email = forms.EmailField(
        required=False,
    )
    feedback = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
            }
        ),
    )
    captcha = CaptchaField(
        required=True,
    )
