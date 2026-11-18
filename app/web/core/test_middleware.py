from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from web.core.middleware import NoStoreMiddleware


def _call(path):
    middleware = NoStoreMiddleware(lambda request: HttpResponse("ok"))
    return middleware(RequestFactory().get(path))


class NoStoreMiddlewareTest(SimpleTestCase):
    def test_registered_in_settings(self):
        self.assertIn("web.core.middleware.NoStoreMiddleware", settings.MIDDLEWARE)

    def test_page_and_api_responses_are_not_cached(self):
        for path in ("/clienten/", "/api/"):
            with self.subTest(path=path):
                cache_control = _call(path).headers["Cache-Control"]
                self.assertIn("no-store", cache_control)
                self.assertIn("private", cache_control)
