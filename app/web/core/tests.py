from django.core import mail
from django.template.loader import get_template
from django.test import SimpleTestCase

from web.core.mail import send_template_mail


class SendTemplateMailTestCase(SimpleTestCase):
    def send(self, context=None, **kwargs):
        send_template_mail(
            'Omslagroute - test',
            'cases/mail/case_delete_request_revoke.txt',
            context or {'user': {'username': 'a@example.com'}},
            ['b@example.com'],
            **kwargs
        )
        message = mail.outbox[-1]
        return message, message.body, message.alternatives[0][0]

    def test_sends_plain_text_and_html(self):
        message, text, html = self.send()

        self.assertEqual(message.subject, 'Omslagroute - test')
        self.assertEqual(message.to, ['b@example.com'])
        self.assertIn('ongedaan gemaakt door a@example.com.', text)
        self.assertIn('ongedaan gemaakt door a@example.com.', html)
        self.assertEqual(message.alternatives[0][1], 'text/html')

    def test_signature_follows_the_style_guide(self):
        _, text, html = self.send()

        self.assertRegex(html, r'<strong style="color:\s*#ec0000;?">Gemeente Amsterdam</strong')
        self.assertIn('Gemeente Amsterdam\nOmslagroute', text)

    def test_html_loads_nothing_external(self):
        _, _, html = self.send(button_text='Bekijken', button_url='https://example.com/')

        self.assertNotIn('<img', html)
        self.assertNotIn('<link', html)
        self.assertNotIn('<script', html)
        self.assertNotIn('url(', html)

    def test_free_text_is_escaped_in_html_only(self):
        _, text, html = self.send({
            'user': {'username': 'a@example.com'},
            'delete_request_revoke_message': "<b>O'Brien</b>\ntweede regel",
        })

        self.assertIn("<b>O'Brien</b>\ntweede regel", text)
        self.assertNotIn('<b>O', html)
        self.assertIn('&lt;b&gt;O&#x27;Brien&lt;/b&gt;<br>tweede regel', html)

    def test_button_with_fallback_url_and_login_note(self):
        _, text, html = self.send(button_text='Bekijken', button_url='https://example.com/1/')

        self.assertIn('Bekijken:\nhttps://example.com/1/', text)
        self.assertIn('<strong>Bekijken</strong>', html)
        self.assertIn('Werkt de knop niet?', html)
        self.assertIn('Je moet ingelogd zijn', html)
        self.assertIn('Je moet ingelogd zijn', text)

    def test_login_note_is_optional(self):
        _, text, html = self.send(
            button_text='Bekijken', button_url='https://example.com/', login_required=False
        )

        self.assertNotIn('Je moet ingelogd zijn', text)
        self.assertNotIn('Je moet ingelogd zijn', html)

    def test_without_button(self):
        _, text, html = self.send()

        self.assertNotIn('Je moet ingelogd zijn', text)
        self.assertNotIn('Werkt de knop niet?', html)
        self.assertNotIn('bgcolor="#004699"', html)

    def test_all_mail_templates_exist(self):
        for name in (
            'cases/mail/case_address_changed.txt',
            'cases/mail/case_deleted.txt',
            'cases/mail/case_delete_request.txt',
            'cases/mail/case_delete_request_revoke.txt',
            'cases/mail/case_link.txt',
            'cases/mail/case_status_to_pb.txt',
            'cases/mail/invated_removed.txt',
            'cases/mail/invite.txt',
            'cases/mail/validate_case.txt',
            'feedback/mail/feedback.txt',
            'mail/test.txt',
            'users/mail/gebruikers_beheerders_new_user.txt',
            'users/mail/to_new_user.txt',
        ):
            get_template(name)
