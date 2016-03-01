from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import Client

class IntakeSurveyTestCase(TestCase):
    fixtures = ['users.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='admin')

    def test_bad_data(self):
        #incomplete data
        resp = self.client.post(reverse('intake_survey', kwargs={}),{'name':'test'})
        self.assertEqual(resp.status_code,200)
        self.assertFormError(resp, 'form','date', 'This field is required.')
