from unittest.mock import Mock, patch

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import RequestFactory, TestCase

from web.feedback.views import FeedbackFormView


class FeedbackMailTestCase(TestCase):
    @patch('web.feedback.views.config')
    def test_feedback_is_escaped_in_html_only(self, config):
        config.FEEDBACK_RECIPIENT_LIST = 'feedback@example.com'
        view = FeedbackFormView()
        view.request = RequestFactory().get('/')
        view.request.user = AnonymousUser()
        view.success_url = '/'

        view.form_valid(Mock(cleaned_data={'name': "O'Brien", 'feedback': '<b>Mooi</b>'}))

        message = mail.outbox[-1]
        self.assertEqual(message.subject, 'Omslagroute - feedback')
        self.assertIn("O'Brien", message.body)
        self.assertIn('<b>Mooi</b>', message.body)
        self.assertIn('&lt;b&gt;Mooi&lt;/b&gt;', message.alternatives[0][0])
