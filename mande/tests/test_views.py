from django.test import TestCase
from django.test import Client
from mande.models import *
from datetime import date

class UserLoginTestCase(TestCase):
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
class IndexViewTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json',
                'exitsurveys.json','intakeinternals.json','notificationlogs.json',
                'classrooms.json','attendances.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='admin')
        #generate a student who is at grade level no matter what grade they're in
        glstudent = IntakeSurvey.objects.create(
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
        IntakeInternal.objects.create(
            student_id=glstudent,
            enrollment_date=date.today(),
            starting_grade='6'
        )
    def test_context(self):
        resp = self.client.get('/')
        self.assertEqual(len(resp.context['schools']),3)
        self.assertEqual(len(resp.context['surveys']),9) #one student has no internal intake
        self.assertEqual(resp.context['females'],2)

        #check breakdown of genders by site
        self.assertEqual(resp.context['breakdown']['VDP-1']['M'],3) #one student in English (50)
        self.assertEqual(resp.context['breakdown']['VDP-1']['F'],2)

        self.assertEqual(resp.context['breakdown']['VDP-2']['M'],2)
        self.assertEqual(resp.context['breakdown']['VDP-2']['F'],0)

        self.assertEqual(resp.context['breakdown']['VDP-3']['M'],2)
        self.assertEqual(resp.context['breakdown']['VDP-3']['F'],0)

        #check breakdown of programs by site
        self.assertEqual(resp.context['program_breakdown']['VDP-1']['Skills'],1) #one student in English (50)
        self.assertEqual(resp.context['program_breakdown']['VDP-1']['Grades'],4)

        self.assertEqual(resp.context['program_breakdown']['VDP-2']['Skills'],1)
        self.assertEqual(resp.context['program_breakdown']['VDP-2']['Grades'],1)

        self.assertEqual(resp.context['program_breakdown']['VDP-3']['Skills'],0)
        self.assertEqual(resp.context['program_breakdown']['VDP-3']['Grades'],2)

        self.assertEqual(resp.context['total_skills'],2) #sum of skills students above

        #check numbers in grades
        self.assertEqual(resp.context['students_by_grade'][1],1)
        self.assertEqual(resp.context['students_by_grade'][2],1)
        self.assertEqual(resp.context['students_by_grade'][3],1)
        self.assertEqual(resp.context['students_by_grade'][4],1)
        self.assertEqual(resp.context['students_by_grade'][5],1)
        self.assertEqual(resp.context['students_by_grade'][6],2)
        self.assertEqual(resp.context['students_by_grade'][50],2)

        #check students at grade level
        self.assertEqual(resp.context['students_at_gl_by_grade'][6],1) #the student we added above only

        #check students in grades by site
        self.assertEqual(resp.context['students_by_grade_by_site'][1]['VDP-1'],1)
        self.assertEqual(resp.context['students_by_grade_by_site'][1]['VDP-2'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][1]['VDP-3'],0)

        self.assertEqual(resp.context['students_by_grade_by_site'][2]['VDP-1'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][2]['VDP-2'],1)
        self.assertEqual(resp.context['students_by_grade_by_site'][2]['VDP-3'],0)

        self.assertEqual(resp.context['students_by_grade_by_site'][3]['VDP-1'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][3]['VDP-2'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][3]['VDP-3'],1)

        self.assertEqual(resp.context['students_by_grade_by_site'][4]['VDP-1'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][4]['VDP-2'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][4]['VDP-3'],1)

        self.assertEqual(resp.context['students_by_grade_by_site'][5]['VDP-1'],1)
        self.assertEqual(resp.context['students_by_grade_by_site'][5]['VDP-2'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][5]['VDP-3'],0)

        self.assertEqual(resp.context['students_by_grade_by_site'][6]['VDP-1'],2)
        self.assertEqual(resp.context['students_by_grade_by_site'][6]['VDP-2'],0)
        self.assertEqual(resp.context['students_by_grade_by_site'][6]['VDP-3'],0)

        self.assertEqual(resp.context['students_by_grade_by_site'][50]['VDP-1'],1)
        self.assertEqual(resp.context['students_by_grade_by_site'][50]['VDP-2'],1)
        self.assertEqual(resp.context['students_by_grade_by_site'][50]['VDP-3'],0)

        #check that our student is there. might want to check that all others are zero?
        self.assertEqual(resp.context['students_at_gl_by_grade_by_site'][6]['VDP-1'],1)

        #check notifications should display
        self.assertEqual(len(resp.context['notifications']),1)

        #check we have one student who isn't enrlled (no intake internal)
        self.assertEqual(len(resp.context['unenrolled_students']),1)

        #check that we just have one attendance with no comment
        self.assertEqual(len(resp.context['unapproved_absence_no_comment']),1)

    #this tests to make sure that additional sites will be shown in the dashboard
    def test_addding_school(self):
        School.objects.create(school_name="test school",school_location="the moon")
        resp = self.client.get('/')
        self.assertEqual(len(resp.context['schools']),4)

    def test_adding_student(self):
        #check breakdown of genders by site
        female = IntakeSurvey.objects.create(
            minors_training= "NA",
            grade_current= -1,
            minors= 0,
            reasons= "123",
            minors_in_public_school= 0,
            site= School.objects.get(pk=2),
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
            gender= "F",
            minors_profession= "",
            guardian1_name= "123",
            minors_training_type= "",
            guardian1_employment= "1",
            notes= ""
        )
        IntakeInternal.objects.create(
            student_id=female,
            enrollment_date=date.today(),
            starting_grade='6'
        )
        resp = self.client.get('/')
        #things that should change
        self.assertEqual(resp.context['females'],3)
        self.assertEqual(resp.context['students_by_grade_by_site'][6]['VDP-2'],1)
        self.assertEqual(resp.context['breakdown']['VDP-2']['F'],1)
        self.assertEqual(resp.context['students_by_grade'][6],3)
        self.assertEqual(resp.context['program_breakdown']['VDP-2']['Grades'],2)


        #sanity check, these should not change
        self.assertEqual(resp.context['breakdown']['VDP-1']['M'],3) #one student in English (50)
        self.assertEqual(resp.context['breakdown']['VDP-1']['F'],2)

        self.assertEqual(resp.context['breakdown']['VDP-2']['M'],2)
        self.assertEqual(resp.context['breakdown']['VDP-2']['F'],1)

        self.assertEqual(resp.context['breakdown']['VDP-3']['M'],2)
        self.assertEqual(resp.context['breakdown']['VDP-3']['F'],0)

    def test_promoting_student(self):
        Academic.objects.create(
            student_id=IntakeSurvey.objects.get(pk=2),
            test_level=6,
            test_grade_math=99,
            test_grade_khmer=99,
            promote=True)
        resp = self.client.get('/')

        #promoted a 1st grade student to English, these should change
        self.assertEqual(resp.context['students_by_grade'][1],0)
        self.assertEqual(resp.context['students_by_grade'][50],3)

        #sanity check
        self.assertEqual(resp.context['students_by_grade'][2],1)
        self.assertEqual(resp.context['students_by_grade'][3],1)
        self.assertEqual(resp.context['students_by_grade'][4],1)
        self.assertEqual(resp.context['students_by_grade'][5],1)
        self.assertEqual(resp.context['students_by_grade'][6],2)



class StudentListTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json','exitsurveys.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='admin')
        # generate a student who is at grade level
        glstudent = IntakeSurvey.objects.create(
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

        IntakeInternal.objects.create(
            student_id=glstudent,
            enrollment_date=date.today(),
            starting_grade='6'
        )

    def test_verifyknownlistlength(self):
        resp = self.client.get('/students/')
        #expecting list length to be9: intake surveys have 10 students
        #2 exit surveys, generating one student above
        self.assertEqual(len(resp.context['surveys']),10)
        self.assertEqual(len(resp.context['at_grade_level']),10)

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
