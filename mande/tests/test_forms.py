from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import Client

class IntakeSurveyTestCase(TestCase):
    fixtures = ['mande_initial.json']
    def setup(self):
        self.client = Client()

    def test_bad_data(self):
        #login
        self.client.post('/login/',{'username':'admin','password':'admin'})

        #incomplete data
        resp = self.client.post(reverse('intake_survey', kwargs={}),{'name':'test'})
        self.assertEqual(resp.status_code,200)
        self.assertFormError(resp, 'form','date', 'This field is required.')

