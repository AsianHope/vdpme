from django.test import TestCase
from django.test import Client

class IndexViewTestCase(TestCase):
    fixtures = ['mande_initial.json']
    def setup(self):
        self.client = Client()

    def test_middleware_redirect(self):
        #attempt to get the page root
        resp = self.client.get('/')

        #we should be redirected by the middleware since we haven't logged in
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'http://testserver/login/')

    def test_bad_login(self):
        #attempt to log in with bad credentials
        resp = self.client.post('/login/',{'username':'admin','password':'badpass'})
        self.assertEqual(resp.status_code,200)

        #we should still be on the login page if we try to get root
        resp = self.client.get('/')
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'http://testserver/login/')

    def test_good_login(self):
        #attempt to log in with good credentials
        resp = self.client.post('/login/',{'username':'admin','password':'admin'})

        #redirect to root now that we're logged in
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'http://testserver/')

    def test_index(self):
        #log in
        resp = self.client.post('/login/',{'username':'admin','password':'admin'})

        #get the index
        resp = self.client.get('/')
        self.assertEqual(resp.status_code,200)
        
        #make sure all the stuff from context is around
        self.assertTrue('surveys' in resp.context)
        self.assertTrue('females' in resp.context)
        self.assertTrue('breakdown' in resp.context)
        self.assertTrue('students_by_grade' in resp.context)
        self.assertTrue('students_at_gl_by_grade' in resp.context)
        self.assertTrue('students_by_grade_by_site' in resp.context)
        self.assertTrue('students_at_gl_by_grade_by_site' in resp.context)
        self.assertTrue('schools' in resp.context)
        self.assertTrue('notifications' in resp.context)
        self.assertTrue('unenrolled_students' in resp.context)
