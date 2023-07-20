from django.conf import settings
from django.urls import path, include as path_include
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from web.core.views import *
from web.health.views import health_default, health_db
from web.users.views import generic_logout, generic_login
from django.views.generic import TemplateView
from django.conf import settings
from web.users.views import OIDCAuthenticationRequestView
from .routers import router
from django.views.generic import RedirectView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('data/', DataView.as_view(), name='data'),
    path('admin/settings', VariablesView.as_view(), name='variables'),
    path('admin/dumpdata', dumpdata, name='dumpdata'),
    path('admin/objectstore', ObjectStoreView.as_view(), name='objectstore'),
    path('admin/sendmail', SendMailView.as_view(), name='sendmail'),
    path('admin/login/', RedirectView.as_view(url='/oidc/authenticate/'), name='disabled_login'),

    path('health', health_default),
    path('omslagroute/health', health_default),
    path('omslagroute/health-db', health_db),

    path('document/', path_include('web.documents.urls')),
    path('timeline/', path_include('web.timeline.urls')),
    path('organisaties/', path_include('web.organizations.urls')),
    path('gebruikers/', path_include('web.users.urls')),

    path('clienten/', path_include('web.cases.urls')),
    path('feedback/', path_include('web.feedback.urls')),

    path('inloggen/', generic_login, name='inloggen'),
    path('uitloggen/', generic_logout, name='uitloggen'),

    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('404', TemplateView.as_view(**{
            'template_name': '404.html',
        }), name='sendmail'),
    ]

if settings.IAM_URL:
    urlpatterns += [
        url(r'^oidc/', include('keycloak_oidc.urls')),
        path('inloggen/', OIDCAuthenticationRequestView.as_view(), name='inloggen'),
    ]
if settings.BRANCH_NAME != 'production':
    urlpatterns += [
        path('user-meta/', TemplateView.as_view(
            template_name="user_meta.html",
        ), name='user_meta'),
    ]