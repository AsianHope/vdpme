from django.test import TestCase
from django.test import Client
from mande.models import *
from datetime import date

class IndexViewTestCase(TestCase):
    fixtures = ['users.json']
    def setUp(self):
        self.client = Client()

    def test_middleware_redirect(self):
        #attempt to get the page root
        resp = self.client.get('/')

        #we should be redirected by the middleware since we haven't logged in
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'http://testserver/login/')

    def test_bad_login(self):
        #attempt to log in with bad credentials
        resp = self.client.login(username='admin',password='badpass')
        self.assertEqual(resp,False)

        #we should still be on the login page if we try to get root
        resp = self.client.get('/')
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'http://testserver/login/')

    def test_good_login(self):
        #attempt to log in with good credentials
        self.client.login(username='admin',password='admin')
        resp = self.client.get('/')
        #redirect to root now that we're logged in
        self.assertEqual(resp.status_code,200)
        self.assertEqual(str(resp.context['user']),'admin')

    def test_index(self):
        #log in
        self.client.login(username='admin',password='admin')

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

    #LOGOUT TESTING
    def test_logged_out(self):

        #log in and verify
        self.client.login(username='admin',password='admin')
        resp = self.client.get('/')
        self.assertEqual(str(resp.context['user']),'admin')

        self.client.logout()
        #try to retrieve another page
        resp = self.client.get('/')
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'http://testserver/login/')
        #If we're really logged out, this key won't exist
        try:
            user = resp['user']
        except KeyError:
            user = None
        self.assertEqual(user,None)

class StudentListTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json','exitsurveys.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='admin')
        #generate a student who is at grade level
        IntakeSurvey.objects.create(
            minors_training= "NA",
            grade_current= -1,
            minors= 0,
            reasons= "123",
            minors_in_public_school= 0,
            site= School.objects.get(pk=1),
            grade_appropriate= 1,
            guardian2_relationship= "MOTHER",
            minors_in_other_school= 0,
            guardian1_phone= "123",
            guardian2_phone= "",
            guardian1_relationship= "FATHER",
            guardian1_profession= "123",
            minors_working= 0,
            enrolled= "N",
            guardian2_profession= "NA",
            address= "123",
            date="2005-07-01",
            guardian2_name= "",
            minors_encouraged= "NA",
            grade_last= -1,
            name= "GeneratedStudent",
            guardian2_employment= "1",
            dob=str(date.today().year)+"-07-01",
            gender= "M",
            minors_profession= "",
            guardian1_name= "123",
            minors_training_type= "",
            guardian1_employment= "1",
            notes= ""
        )

    def test_verifyknownlistlength(self):
        resp = self.client.get('/students/')
        #expecting list length to be9: intake surveys have 10 students
        #2 exit surveys, generating one student above
        self.assertEqual(len(resp.context['surveys']),9)
        self.assertEqual(len(resp.context['at_grade_level']),9)

    def test_verifyunknownlistlength(self):
        resp = self.client.get('/students/')
        self.assertEqual(len(resp.context['surveys']),len(resp.context['at_grade_level']))

    def test_verifyatgradelevel(self):
        resp = self.client.get('/students/')
        atgl_count = 0
        for sid,status in resp.context['at_grade_level'].iteritems():
            if status:
                atgl_count += 1
        self.assertEqual(atgl_count,1)

class StudentDetailTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json','exitsurveys.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='admin')

#should be a new class
    #TESTING SUCCESSFUL REDIRECTION TO REPORTS
    # def test_go_to_classroom_attendance(self):
    #     #attempt to go to classroom_attendance
    #     resp = self.client.get('/attendance/report/')
    #
    #     #check you're in the classroom_attendance page
    #     self.assertEqual(resp.status_code,11894)
    #     self.assertEqual(resp['Location'],'http://testserver/attendance/report/')
    #
    # def test_go_to_daily_attendance(self):
    #     #attempt to go to daily absences
    #     resp = self.client.get('/attendance/report/absences/')
    #
    #     #check you're in the daily absences page
    #     self.assertEqual(resp.status_code,11952)
    #     self.assertEqual(resp['Location'],'http://testserver/attendance/report/absences/')
    #
    # def test_go_to_daily_audit(self):
    #     #attempt to go to daily audit
    #     resp = self.client.get('/reports/data_audit/')
    #
    #     #check you're in the daily audit page
    #     self.assertEqual(resp.status_code,12865)
    #     self.assertEqual(resp['Location'],'http://testserver/reports/data_audit/')
    #
    # def test_go_to_daily_audit(self):
    #     #attempt to go to class list
    #     resp = self.client.get('/reports/class_list/')
    #
    #     #check you're in the class list page
    #     self.assertEqual(resp.status_code,12100)
    #     self.assertEqual(resp['Location'],'http://testserver/reports/class_list/')
