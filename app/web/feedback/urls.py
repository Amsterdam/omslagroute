from .views import *
from django.urls import path
from django.conf.urls import include


urlpatterns = [
    path('', FeedbackFormView.as_view(), name='feedback'),
    path('captcha/', include('captcha.urls')),
]
