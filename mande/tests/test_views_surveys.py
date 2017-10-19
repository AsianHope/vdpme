from django.test import TestCase
from django.test import Client

from mande.models import *
from mande.forms import *
from django.db.models import Q

from datetime import date,datetime
from django.core.urlresolvers import reverse
from django.utils.translation import activate
import json

from mande.utils import studentAtAgeAppropriateGradeLevel


activate('en')
class IntakeSurveyViewTestCase(TestCase):
    fixtures = [
        'users.json','intakesurveys.json',
        'intakeupdates.json','notificationlogs.json',
        'classrooms.json','schools.json',
        'intakeinternals.json','currentstudentInfos.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # no student_id
        url = reverse('intake_survey',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/intakesurvey.html')
        self.assertEqual(IntakeSurvey.objects.all().count(),11)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(IntakeInternal.objects.all().count(),8)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

        self.assertEqual(resp.context['student'],None)
        self.assertIsInstance(resp.context['form'],IntakeSurveyForm)
        self.assertEqual(resp.context['form'].data,{})
        self.assertEqual(resp.context['limit'],None)
        self.assertEqual(resp.context['next_url'],None)
        # expect data_guardian_profession is json format
        raised = True
        try:
            json.loads(resp.context['data_guardian_profession'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_guardian_profession'],'["123", "456", "NA"]')

        # with student_id
        student_id = 11
        url = reverse('intake_survey',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/intakesurvey.html')
        self.assertEqual(IntakeSurvey.objects.all().count(),11)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(IntakeInternal.objects.all().count(),8)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

        instance = IntakeSurvey.objects.get(pk=student_id)
        self.assertEqual(resp.context['student'],instance)
        self.assertIsInstance(resp.context['form'],IntakeSurveyForm)
        self.assertEqual(resp.context['form'].data,{})
        self.assertEqual(resp.context['form'].instance,instance)
        self.assertEqual(resp.context['limit'],None)
        self.assertEqual(resp.context['next_url'],None)
        # expect data_guardian_profession is json format
        raised = True
        try:
            json.loads(resp.context['data_guardian_profession'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_guardian_profession'],'["123", "456", "NA"]')

    def test_context_post_create(self):
        enrollment_date = "2017-01-01"
        starting_grade = 1
        today = date.today().isoformat()
        data = {
            "date":today,
            "site":1,
            "dob": "2000-01-01",
            "name":"abc",
            "gender":"F",
            "guardian1_name":"abc",
            "guardian1_relationship":"FATHER",
            "guardian1_phone":"00000",
            "guardian1_profession":"test",
            "guardian1_employment":1,
            "minors":0,
            "minors_in_public_school":0,
            "minors_in_other_school":0,
            "address": "test", "notes": "test",
            "enrollment_date":enrollment_date,
            "starting_grade":starting_grade
        }
        url = reverse('intake_survey',kwargs={})
        resp = self.client.post(url,data)
        instance = IntakeSurvey.objects.get(date=date.today().isoformat())
        self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':instance.student_id}), status_code=302, target_status_code=200)
        self.assertEqual(IntakeSurvey.objects.all().count(),12)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        self.assertEqual(IntakeInternal.objects.all().count(),9)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),10)
        self.assertTrue(
            IntakeInternal.objects.filter(student_id=instance, enrollment_date=enrollment_date,starting_grade=starting_grade).exists()
        )

        message = 'Performed intake survey and intake internal for '+unicode(instance.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-female',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=instance.student_id,
                name = instance.name,
                site = instance.site,
                date = instance.date,
                dob = instance.dob,
                gender = instance.gender,
                age_appropriate_grade = instance.age_appropriate_grade(),
                in_public_school = True if instance.get_pschool().status=='Y' else False,
                at_grade_level = studentAtAgeAppropriateGradeLevel(instance.student_id),
                vdp_grade = instance.current_vdp_grade(),
                refresh = date.today().isoformat(),
                ).exists()
        )

    def test_context_post_update(self):
        # update intakesurvey
        enrollment_date = "2017-01-01"
        starting_grade = 1
        today = date.today().isoformat()
        student_id=11
        data = {
            "date":today,
            "site":1,
            "dob": "2000-01-01",
            "name":"abc",
            "gender":"M",
            "guardian1_name":"abc",
            "guardian1_relationship":"FATHER",
            "guardian1_phone":"00000",
            "guardian1_profession":"test",
            "guardian1_employment":1,
            "minors":0,
            "minors_in_public_school":0,
            "minors_in_other_school":0,
            "address": "test", "notes": "test",
            "enrollment_date":enrollment_date,
            "starting_grade":starting_grade
        }
        url = reverse('intake_survey',kwargs={'student_id':student_id})
        resp = self.client.post(url,data)
        instance = IntakeSurvey.objects.get(pk=student_id)
        self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':instance.student_id}), status_code=302, target_status_code=200)
        self.assertEqual(IntakeSurvey.objects.all().count(),11)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        self.assertEqual(IntakeInternal.objects.all().count(),9)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),10)

        self.assertTrue(IntakeSurvey.objects.filter(pk=student_id,date=today).exists())
        self.assertTrue(
            IntakeInternal.objects.filter(student_id=instance, enrollment_date=enrollment_date,starting_grade=starting_grade).exists()
        )

        message = 'Updated intake survey and intake internal for '+unicode(instance.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-male',
                user=self.client.session['_auth_user_id'],
            ).exists()
        )
        self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=instance.student_id,
                name = instance.name,
                site = instance.site,
                date = instance.date,
                dob = instance.dob,
                gender = instance.gender,
                age_appropriate_grade = instance.age_appropriate_grade(),
                in_public_school = True if instance.get_pschool().status=='Y' else False,
                at_grade_level = studentAtAgeAppropriateGradeLevel(instance.student_id),
                vdp_grade = instance.current_vdp_grade(),
                refresh = date.today().isoformat(),
                ).exists()
        )

class IntakeInternalViewTestCase(TestCase):
    fixtures = ['users.json','intakesurveys.json',
                'classrooms.json','schools.json',
                'intakeinternals.json','notificationlogs.json',
                'currentstudentInfos.json'
               ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
        self.student = IntakeSurvey.objects.create(
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

    def test_context_with_student_id(self):
        # request with student_id
        student_id = 1
        url = reverse('intake_internal',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/intakeinternal.html')
        self.assertIsInstance(resp.context['form'],IntakeInternalForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id)})

        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(IntakeInternal.objects.all().count(),8)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_no_student_id(self):
        url = reverse('intake_internal',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/intakeinternal.html')
        self.assertIsInstance(resp.context['form'],IntakeInternalForm)
        self.assertEqual(resp.context['form'].data,{})

        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(IntakeInternal.objects.all().count(),8)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_post(self):
       enrollment_date = date.today().isoformat()
       starting_grade = 1
       student_id = self.student.student_id
       data = {
           "student_id":student_id,
           "enrollment_date":enrollment_date,
           "starting_grade":starting_grade
       }
       url = reverse('intake_internal',kwargs={'student_id':student_id})
       resp = self.client.post(url,data)
       self.assertRedirects(
            resp,
            expected_url=reverse('student_detail',kwargs={'student_id':student_id}),
            status_code=302, target_status_code=200
       )

       self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
       self.assertEqual(IntakeInternal.objects.all().count(),9)
       self.assertEqual(NotificationLog.objects.all().count(),2)

       self.assertTrue(IntakeInternal.objects.filter(student_id=student_id,starting_grade=starting_grade,enrollment_date=enrollment_date).exists())
       instance = IntakeInternal.objects.get(student_id=student_id,starting_grade=starting_grade,enrollment_date=enrollment_date)
       message = ( 'Enrolled  '+unicode(instance.student_id.name)+
                   ' in '+instance.get_starting_grade_display())
       self.assertTrue(
           NotificationLog.objects.filter(
               text=message, font_awesome_icon='fa-user-plus',
               user=self.client.session['_auth_user_id']
           ).exists()
       )

    def test_context_post_existed(self):
       enrollment_date = date.today().isoformat()
       starting_grade = 1
       student_id = 1
       data = {
           "student_id":student_id,
           "enrollment_date":enrollment_date,
           "starting_grade":starting_grade
       }
       url = reverse('intake_internal',kwargs={'student_id':student_id})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/intakeinternal.html')
       self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
       self.assertEqual(IntakeInternal.objects.all().count(),8)
       self.assertEqual(NotificationLog.objects.all().count(),1)
       self.assertFalse(resp.context['form'].is_valid())
       self.assertEqual(resp.context['form'].errors,{'student_id': [u'Intake internal with this Student ID already exists.']})

class IntakeUpdateViewTestCase(TestCase):
    fixtures = ['users.json','intakesurveys.json',
                'intakeupdates.json','classrooms.json',
                'schools.json','notificationlogs.json',
                'currentstudentInfos.json'
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_no_student_id(self):
        # no student_id
        url = reverse('intake_update',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/intakeupdate.html')
        self.assertEqual(resp.context['survey'],None)
        self.assertEqual(resp.context['student_id'],0)
        self.assertEqual(resp.context['next'],None)
        self.assertEqual(resp.context['tab'],None)
        self.assertIsInstance(resp.context['form'],IntakeUpdateForm)
        self.assertEqual(resp.context['form'].data,{'date':date.today().isoformat()})

        # expect data_guardian_profession is json format
        raised = True
        try:
            json.loads(resp.context['data_guardian_profession'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_guardian_profession'],'["123", "456", "NA"]')

        self.assertEqual(IntakeUpdate.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

    def test_context_with_student_id(self):
        # with student_id
        student_id = 1
        url = reverse('intake_update',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/intakeupdate.html')

        instance = IntakeSurvey.objects.get(pk=student_id)
        most_recent = instance.getRecentFields()
        most_recent['date'] = date.today().isoformat()
        self.assertEqual(resp.context['survey'],instance)
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertIsInstance(resp.context['form'],IntakeUpdateForm)
        self.assertEqual(resp.context['form'].data,most_recent)
        self.assertEqual(resp.context['next'],None)
        self.assertEqual(resp.context['tab'],None)
        # expect data_guardian_profession is json format
        raised = True
        try:
            json.loads(resp.context['data_guardian_profession'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_guardian_profession'],'["123", "456", "NA"]')

        self.assertEqual(IntakeUpdate.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

    def test_context_post(self):
        student_id = 1
        survey_date = "2017-10-19"
        data = {
            "student_id":student_id,
            "minors_in_public_school":0,
            "minors_in_other_school":0,
            "guardian1_relationship":'FATHER',
            "guardian1_employment":1,
            "minors":0,
            "date":survey_date,
            "address": "test",
        }
        url = reverse('intake_update',kwargs={'student_id':student_id})
        next_url = reverse('student_detail',kwargs={'student_id':student_id})
        resp = self.client.post(url+'?next='+next_url+'&tab=enrollment',data)
        self.assertRedirects(resp, expected_url=next_url+'#enrollment', status_code=302, target_status_code=200)
        instance = IntakeUpdate.objects.get(student_id=student_id,date__startswith=survey_date)
        self.assertEqual(IntakeUpdate.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        message = 'Updated '+unicode(instance.student_id.name)+'\'s record'
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-upload',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        student = IntakeSurvey.objects.get(student_id=instance.student_id.student_id)
        current = student.getRecentFields()
        self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=student.student_id,
                name = current['name'],
                site = current['site'],
                date = current['date'],
                dob = current['dob'],
                gender = current['gender'],
                age_appropriate_grade = student.age_appropriate_grade(),
                in_public_school = True if student.get_pschool().status=='Y' else False,
                at_grade_level = studentAtAgeAppropriateGradeLevel(student.student_id),
                vdp_grade = student.current_vdp_grade(),
                refresh = date.today().isoformat(),
                ).exists()
        )

class ExitSurveyViewTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json',
                'exitsurveys.json','classroomenrollment.json','notificationlogs.json','classrooms.json'
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('exit_survey',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/exitsurvey.html')
        self.assertEqual(resp.context['student_id'],0)
        self.assertIsInstance(resp.context['form'],ExitSurveyForm)
        self.assertEqual(resp.context['form'].data,{})

        student_id = 1
        url = reverse('exit_survey',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/exitsurvey.html')
        self.assertEqual(ExitSurvey.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertTrue(
            ClassroomEnrollment.objects.filter(
                student_id=student_id, drop_date=None,
            ).exists()
        )
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertIsInstance(resp.context['form'],ExitSurveyForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id)})

    def test_context_post(self):
        student_id = 1
        exit_date = date.today().isoformat()
        data = {
            'student_id':student_id,
            'last_grade':1,
            'early_exit':'Y',
            'early_exit_reason':'MOVING',
            'exit_date':exit_date,
            'survey_date':date.today().isoformat(),
            'early_exit_comment':'',
            'secondary_enrollment':'Y'
        }
        url = reverse('exit_survey',kwargs={'student_id':student_id})
        resp = self.client.post(url,data)
        self.assertRedirects(
              resp,
              expected_url=reverse('student_detail',kwargs={'student_id':student_id}),
              status_code=302, target_status_code=200
         )
        # instance = IntakeUpdate.objects.get(student_id=student_id,date=date.today().isoformat())
        self.assertEqual(ExitSurvey.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),2)

        self.assertTrue(
            ClassroomEnrollment.objects.filter(student_id=student_id,drop_date=exit_date).exists()
        )
        instance = ExitSurvey.objects.get(student_id=student_id,exit_date=exit_date)
        message = 'Did an exit survey for '+unicode(instance.student_id.name)
        self.assertTrue(
             NotificationLog.objects.filter(
                 text=message, font_awesome_icon='fa-user-times',
                 user=self.client.session['_auth_user_id']
             ).exists()
        )

class PostExitSurveyViewTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json',
                'postexitsurveys.json','classroomenrollment.json',
                'notificationlogs.json','classrooms.json','exitsurveys.json'
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):
        student_id = 1
        url = reverse('post_exit_survey',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/postexitsurvey.html')
        instance = IntakeSurvey.objects.get(pk=student_id)
        most_recent = instance.getRecentFields()
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertIsInstance(resp.context['form'],PostExitSurveyForm)
        self.assertEqual(resp.context['form'].data,most_recent)

        # no instance
        student_id = 15
        url = reverse('post_exit_survey',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/postexitsurvey.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertIsInstance(resp.context['form'],PostExitSurveyForm)
        self.assertEqual(resp.context['form'].data,{})

        self.assertEqual(PostExitSurvey.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_post(self):
        student_id = 1
        exit_date = date.today().isoformat()
        data = {
            'student_id':student_id,
            'post_exit_survey_date':date.today().isoformat(),
            'exit_date':exit_date,
            'minors':0,
            'enrolled':'Y',
            'grade_previous':1,
            'grade_current':1,
            'guardian1_relationship':'MOTHER',
            'guardian1_employment':1,
            'early_exit':'Y',
            'guardian1_profession':'test'
        }
        url = reverse('post_exit_survey',kwargs={'student_id':student_id})
        resp = self.client.post(url,data)
        self.assertRedirects(
              resp,
              expected_url=reverse('post_exit_survey',kwargs={}),
              status_code=302, target_status_code=200
         )
        instance = PostExitSurvey.objects.get(student_id=student_id,exit_date=exit_date)
        self.assertEqual(PostExitSurvey.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)

        message = 'Did a post exit survey for '+unicode(instance.student_id.name)
        self.assertTrue(
             NotificationLog.objects.filter(
                 text=message, font_awesome_icon='fa-heart',
                 user=self.client.session['_auth_user_id']
             ).exists()
        )

class PostExitSurveyListViewTestCase(TestCase):
    fixtures = ['users.json','schools.json','intakesurveys.json','postexitsurveys.json',
                'exitsurveys.json'
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):
        url = reverse('post_exit_survey')
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/postexitsurveylist.html')
        exitsurveys = ExitSurvey.objects.exclude(
                                          student_id__in=PostExitSurvey.objects.all().values_list('student_id',flat=True)
                                     ).order_by('-exit_date')
        context = {'exitsurveys':exitsurveys}
        self.assertEqual(list(resp.context['exitsurveys']),list(exitsurveys))

class DeleteSpiritualActivitiesSurveyViewTestCase(TestCase):
    fixtures = [
                'users.json','schools.json',
                'intakesurveys.json','spiritualactivities.json',
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_fail(self):
        next_url = reverse('student_detail',kwargs={'student_id':1})
        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),1)
        url = reverse('delete_spiritualactivities_survey',kwargs={'id':2})
        resp = self.client.get(url+'?next='+next_url,follow=True)
        self.assertRedirects(
               resp,
               expected_url=next_url,
               status_code=302, target_status_code=200
        )
        message = list(resp.context.get('messages'))[0]
        self.assertEqual(message.tags, 'delete_spiritualactivities_survey error')
        self.assertTrue('Fail to delete Spiritual Activity Survey! (SpiritualActivitiesSurvey matching query does not exist.)' in message.message)
        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),1)

    def test_success(self):
        next_url = reverse('student_detail',kwargs={'student_id':1})
        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),1)
        url = reverse('delete_spiritualactivities_survey',kwargs={'id':1})
        resp = self.client.get(url+'?next='+next_url,follow=True)
        self.assertRedirects(
               resp,
               expected_url=next_url,
               status_code=302, target_status_code=200
        )
        message = list(resp.context.get('messages'))[0]
        self.assertEqual(message.tags, 'delete_spiritualactivities_survey success')
        self.assertTrue('Spiritual Activity Survey has been deleted successfully!' in message.message)
        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),0)

class SpiritualActivitiesSurveyViewTestCase(TestCase):
    fixtures = [
                'users.json','schools.json',
                'intakesurveys.json','spiritualactivities.json','notificationlogs.json',
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # no student_id and survey_id
        url = reverse('spiritualactivities_survey',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/spiritualactivitiessurvey.html')
        self.assertEqual(resp.context['student_id'],0)
        self.assertEqual(resp.context['survey_id'],None)
        self.assertEqual(resp.context['next_url'],None)
        self.assertEqual(resp.context['action'],'Performing')
        self.assertIsInstance(resp.context['form'],SpiritualActivitiesSurveyForm)
        self.assertEqual(resp.context['form'].initial,{})
        # expect data_church_names is json format
        raised = True
        try:
            json.loads(resp.context['data_church_names'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_church_names'],'["abc"]')

        # no survey_id
        student_id = 1
        url = reverse('spiritualactivities_survey',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/spiritualactivitiessurvey.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['survey_id'],None)
        self.assertEqual(resp.context['next_url'],None)
        self.assertEqual(resp.context['action'],'Adding')
        self.assertIsInstance(resp.context['form'],SpiritualActivitiesSurveyForm)
        self.assertEqual(resp.context['form'].initial,{'date':date.today().isoformat(), 'student_id':str(student_id)})

        # have student_id and survey_id
        student_id = 1
        survey_id = 1
        url = reverse('spiritualactivities_survey',kwargs={'student_id':student_id,'survey_id':survey_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/spiritualactivitiessurvey.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['survey_id'],str(survey_id))
        self.assertEqual(resp.context['next_url'],None)
        self.assertEqual(resp.context['action'],'Editing')
        self.assertIsInstance(resp.context['form'],SpiritualActivitiesSurveyForm)
        instance = SpiritualActivitiesSurvey.objects.get(pk=survey_id)
        self.assertEqual(resp.context['form'].instance,instance)

        # SpiritualActivitiesSurvey with id = 2 not exist
        student_id = 1
        survey_id = 2
        url = reverse('spiritualactivities_survey',kwargs={'student_id':student_id,'survey_id':survey_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/spiritualactivitiessurvey.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['survey_id'],str(survey_id))
        self.assertEqual(resp.context['next_url'],None)
        self.assertEqual(resp.context['action'],'Adding')
        self.assertIsInstance(resp.context['form'],SpiritualActivitiesSurveyForm)
        self.assertEqual(resp.context['form'].data,{})
        self.assertEqual(resp.context['form'].initial,{'student_id': str(student_id),'date':date.today().isoformat()})

        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),1)
        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),1)

    def test_context_post_add(self):
        student_id = 1
        exit_date = date.today().isoformat()
        data = {
            'student_id':student_id,
            'date':date.today().isoformat(),
            'personal_attend_church':'Y',
            'frequency_of_attending':'EVERY_WEEK'
        }
        url = reverse('spiritualactivities_survey',kwargs={'student_id':student_id})
        resp = self.client.post(url,data)
        self.assertRedirects(
              resp,
              expected_url=reverse('success'),
              status_code=302, target_status_code=200
         )

        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)

        instance = SpiritualActivitiesSurvey.objects.get(student_id=student_id,date=date.today().isoformat())
        message = ('Added spiritual activities survey for '+
                    unicode(instance.student_id.name))
        self.assertTrue(
             NotificationLog.objects.filter(
                 text=message, font_awesome_icon='fa-fire',
                 user=self.client.session['_auth_user_id']
             ).exists()
        )

    def test_context_post_edit(self):
        student_id = 1
        survey_id = 1
        exit_date = date.today().isoformat()
        data = {
            'student_id':student_id,
            'date':date.today().isoformat(),
            'personal_attend_church':'Y',
            'frequency_of_attending':'EVERY_WEEK'
        }
        url = reverse('spiritualactivities_survey',kwargs={'student_id':student_id,'survey_id':1})
        resp = self.client.post(url,data)
        self.assertRedirects(
              resp,
              expected_url=reverse('success'),
              status_code=302, target_status_code=200
         )

        self.assertEqual(SpiritualActivitiesSurvey.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),2)

        instance = SpiritualActivitiesSurvey.objects.get(student_id=student_id,pk=1)
        message = ('Edited spiritual activities survey for '+
                    unicode(instance.student_id.name))
        self.assertTrue(
             NotificationLog.objects.filter(
                 text=message, font_awesome_icon='fa-fire',
                 user=self.client.session['_auth_user_id']
             ).exists()
        )

class SurveySuccessViewTestCase(TestCase):
    fixtures = ['users.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('success')
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/success.html')

class HealthFormViewTestCase(TestCase):
    fixtures = [
                'users.json','schools.json',
                'intakesurveys.json','healths.json','notificationlogs.json',
              ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # no student_id and appropriate_type
        url = reverse('health_form',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/healthform.html')
        self.assertEqual(resp.context['student_id'],0)
        self.assertEqual(resp.context['next_url'],None)
        self.assertIsInstance(resp.context['form'],HealthForm)
        self.assertEqual(resp.context['form'].data,{})

        # have student_id, no appropriate_type
        student_id = 1
        url = reverse('health_form',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/healthform.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['next_url'],None)
        self.assertIsInstance(resp.context['form'],HealthForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'appointment_date':date.today().isoformat()})

        # have student_id and appropriate_type
        student_id = 1
        appointment_type = 'DENTAL'
        appointment_date = '2016-03-30'
        url = reverse('health_form',kwargs={'student_id':student_id,'appointment_type':appointment_type,'appointment_date':appointment_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/healthform.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['next_url'],None)
        self.assertIsInstance(resp.context['form'],HealthDentalForm)
        instance = Health.objects.get(student_id=IntakeSurvey.objects.get(pk=student_id),
                                  appointment_date=appointment_date,
                                  appointment_type=appointment_type)
        self.assertEqual(resp.context['form'].instance,instance)

        # have student_id and appropriate_type, checkup
        student_id = 1
        appointment_type = 'CHECKUP'
        appointment_date = '2016-03-30'
        url = reverse('health_form',kwargs={'student_id':student_id,'appointment_type':appointment_type,'appointment_date':appointment_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/healthform.html')

        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['next_url'],None)
        self.assertIsInstance(resp.context['form'],HealthCheckupForm)
        instance = Health.objects.get(student_id=IntakeSurvey.objects.get(pk=student_id),
                                  appointment_date=appointment_date,
                                  appointment_type=appointment_type)
        self.assertEqual(resp.context['form'].instance,instance)

        # have student_id ObjectDoesNotExist
        student_id = 2
        appointment_date = date.today().isoformat()
        appointment_type = 'CHECKUP'
        url = reverse('health_form',kwargs={'student_id':student_id,'appointment_type':appointment_type,'appointment_date':appointment_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/healthform.html')
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['next_url'],None)
        self.assertIsInstance(resp.context['form'],HealthForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'appointment_date':appointment_date,'appointment_type':appointment_type})

        self.assertEqual(Health.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_post_add(self):
        student_id = 1
        appointment_date = date.today().isoformat()
        appointment_type = 'CHECKUP'
        next_url = reverse('student_detail',kwargs={'student_id':student_id})
        data = {
            'student_id':student_id,
            'appointment_date':appointment_date,
            'appointment_type':appointment_type

        }
        url = reverse('health_form',kwargs={'student_id':student_id})
        resp = self.client.post(url+'?next='+next_url,data)
        self.assertRedirects(
              resp,
              expected_url=next_url+"#health",
              status_code=302, target_status_code=200
        )
        self.assertEqual(Health.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),2)

        instance = Health.objects.get(student_id=student_id,appointment_date=appointment_date,appointment_type=appointment_type)
        message = ('Input '+instance.appointment_type+' for '+instance.student_id.name)
        self.assertTrue(
             NotificationLog.objects.filter(
                 text=message, font_awesome_icon='fa-medkit',
                 user=self.client.session['_auth_user_id']
             ).exists()
        )

    def test_context_post_edit(self):
        student_id = 1
        appointment_date = '2016-03-30'
        appointment_type = 'CHECKUP'
        next_url = reverse('student_detail',kwargs={'student_id':student_id})
        data = {
            'student_id':student_id,
            'appointment_date':appointment_date,
            'appointment_type':appointment_type
        }
        url = reverse('health_form',kwargs={'student_id':student_id})
        resp = self.client.post(url+'?next='+next_url,data)
        self.assertRedirects(
              resp,
              expected_url=next_url+"#health",
              status_code=302, target_status_code=200
        )
        self.assertEqual(Health.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        instance = Health.objects.get(student_id=student_id,appointment_date=appointment_date,appointment_type=appointment_type)
        message = ('Updated '+instance.appointment_type+' for '+instance.student_id.name)
        self.assertTrue(
             NotificationLog.objects.filter(
                 text=message, font_awesome_icon='fa-medkit',
                 user=self.client.session['_auth_user_id']
             ).exists()
        )
