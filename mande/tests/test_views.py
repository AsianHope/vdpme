from django.test import TestCase
from django.test import Client

from mande.models import *

from datetime import date,datetime

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import activate

from mande.utils import studentAtAgeAppropriateGradeLevel
from mande.utils import getStudentAgeAppropriateGradeLevel


activate('en')
class UserLoginTestCase(TestCase):
    fixtures = ['users.json']
    def setUp(self):
        self.client = Client()

    def test_middleware_redirect(self):
        #attempt to get the page root
        resp = self.client.get('/')

        #we should be redirected by the middleware since we haven't logged in
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'/login/')

    def test_bad_login(self):
        #attempt to log in with bad credentials
        resp = self.client.login(username='admin',password='badpass')
        self.assertEqual(resp,False)

        # #we should still be on the login page if we try to get root
        resp = self.client.get('/')
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'/login/')

    def test_good_login(self):
        #attempt to log in with good credentials
        self.client.login(username='admin',password='test')
        resp = self.client.get('/')
        #should redirect to /en/ (default english) now that we're logged in
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'/en/')
        #load the context, expect user is admin
        resp = self.client.get('/en/')
        self.assertEqual(str(resp.context['user']),'admin')

    def test_index(self):
        #log in
        self.client.login(username='admin',password='test')
        #get the index
        resp = self.client.get('/en/')
        self.assertEqual(resp.status_code,200)
        #make sure all the stuff from context is around
        self.assertTrue('surveys' in resp.context)
        self.assertTrue('females' in resp.context)
        self.assertTrue('breakdown' in resp.context)
        self.assertTrue('program_breakdown' in resp.context)
        self.assertTrue('total_skills' in resp.context)
        self.assertTrue('students_by_grade' in resp.context)
        self.assertTrue('students_at_gl_by_grade' in resp.context)
        self.assertTrue('students_by_grade_by_site' in resp.context)
        # self.assertTrue('students_at_gl_by_grade_by_site' in resp.context)
        self.assertTrue('schools' in resp.context)
        self.assertTrue('notifications' in resp.context)
        self.assertTrue('unenrolled_students' in resp.context)
        self.assertTrue('unapproved_absence_no_comment' in resp.context)
    #LOGOUT TESTING
    def test_logged_out(self):

        #log in and verify
        self.client.login(username='admin',password='test')
        resp = self.client.get('/',follow=True)
        self.assertEqual(str(resp.context['user']),'admin')

        self.client.logout()
        #try to retrieve another page
        resp = self.client.get('/')
        self.assertEqual(resp.status_code,302)
        self.assertEqual(resp['Location'],'/login/')
        #If we're really logged out, this key won't exist
        try:
            user = resp['user']
        except KeyError:
            user = None
        self.assertEqual(user,None)

class IndexViewTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json',
                'exitsurveys.json','intakeinternals.json','notificationlogs.json',
                'classrooms.json','attendances.json','currentstudentInfos.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
        #generate a student who is at grade level no matter what grade they're in
        glstudent = IntakeSurvey.objects.create(
            minors_training= "NA",
            minors= 0,
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
            guardian2_profession= "NA",
            address= "123",
            date="2005-07-01",
            guardian2_name= "",
            minors_encouraged= "NA",
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
        recent_survey = glstudent.getRecentFields()
        intake = IntakeSurvey.objects.get(student_id=glstudent.student_id)
        CurrentStudentInfo.objects.create(
            student_id=recent_survey['student_id'],
            name = recent_survey['name'],
            site = recent_survey['site'],
            date = recent_survey['date'],
            dob = recent_survey['dob'],
            gender = recent_survey['gender'],
            age_appropriate_grade = intake.age_appropriate_grade(),
            in_public_school = True if intake.get_pschool().status=='Y' else False,
            at_grade_level = studentAtAgeAppropriateGradeLevel(recent_survey['student_id']),
            vdp_grade = intake.current_vdp_grade()
        )
        # unapproved_absence_no_comment
        today = date.today()
        if (today < datetime.strptime(str(today.year)+"-08-01", "%Y-%m-%d").date()):
             school_year = today.year - 1
        else:
             school_year = today.year
        school_year_start_date = str(school_year)+"-08-01"
        school_year_end_date = str(school_year+1)+"-07-31"
        Attendance.objects.create(
             student_id=IntakeSurvey.objects.get(pk=1),
             classroom = Classroom.objects.get(pk=1),
             date=str(school_year)+"-08-01",
             attendance="UA",
        )

    def test_context(self):
        resp = self.client.get('/',follow=True)
        self.assertTemplateUsed(resp,'mande/index.html')

        self.assertEqual(len(resp.context['schools']),3)
        self.assertEqual(len(resp.context['surveys']),9) #one student has no internal intake
        self.assertEqual(resp.context['females'],2)

        #check breakdown of genders by site
        self.assertEqual(resp.context['breakdown']['VDP-1']['M'],3) #one student in English (50)
        self.assertEqual(resp.context['breakdown']['VDP-1']['F'],1)

        self.assertEqual(resp.context['breakdown']['VDP-2']['M'],1)
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

        # check numbers in grades
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

        #check notifications should display
        self.assertEqual(len(resp.context['notifications']),1)

        #check we have one student who isn't enrlled (no intake internal)
        self.assertEqual(len(resp.context['unenrolled_students']),1)

        #check that we just have one attendance with no comment
        self.assertEqual(len(resp.context['unapproved_absence_no_comment']),1)

class NotificationLogViewTestCase(TestCase):
    fixtures = ['users.json','notificationlogs.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
        NotificationLog.objects.create(
            date="2017-01-01",
            user=User.objects.get(pk=1),
            user_generated=True,
            text="test",
            font_awesome_icon="fa-user-plus"
        )

    def test_context(self):
        url = reverse('notification_log')
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/notificationlog.html')
        self.assertEqual(len(resp.context['notifications']),2)
