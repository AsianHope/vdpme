from django.test import TestCase
from django.test import Client

from mande.models import *
from mande.forms import *

from datetime import date,datetime,timedelta
import json

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from django.utils.safestring import mark_safe

from mande.utils import studentAtAgeAppropriateGradeLevel
from mande.utils import getStudentGradebyID


activate('en')
class StudentListViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'currentstudentInfos.json',
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('student_list',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentlist.html')
        self.assertEqual(list(resp.context['surveys']),list(CurrentStudentInfo.objects.all().select_related('site')))

class StudentDetailViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'intakeinternals.json','academic.json','studentevaluations.json',
        'disciplines.json','healths.json','attendances.json','postexitsurveys.json',
        'exitsurveys.json','classroomenrollment.json','publicschoolhistorys.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        student_id = 1
        url = reverse('student_detail',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/detail.html')
        survey = IntakeSurvey.objects.get(pk=student_id)
        self.assertEqual(resp.context['survey'],survey.getRecentFields())
        intake = survey.intakeinternal_set.all().filter().order_by(
                                                           '-enrollment_date'
                                                       )
        self.assertEqual(resp.context['recent_intake'],intake[0])
        #select only semester tests which have grades in them
        academics = survey.academic_set.all().filter(
           Q(test_grade_khmer__isnull=False) &
           Q(test_grade_math__isnull=False)).order_by('-test_level')
        self.assertEqual(list(resp.context['academics']),list(academics))
        evaluations = survey.studentevaluation_set.all().order_by('-date').exclude(
                                                           Q(academic_score=None)&
                                                           Q(study_score=None)&
                                                           Q(personal_score=None)&
                                                           Q(hygiene_score=None)&
                                                           Q(faith_score=None)
        )
        self.assertEqual(list(resp.context['evaluations']),list(evaluations))
        self.assertEqual(resp.context['current_grade'],getStudentGradebyID(student_id))
        discipline = survey.discipline_set.all().filter().order_by('-incident_date')
        self.assertEqual(list(resp.context['discipline']),list(discipline))
        dental = survey.health_set.all().filter(
                                          appointment_type='DENTAL'
                                      ).order_by('-appointment_date')
        self.assertEqual(list(resp.context['dental']),list(dental))
        checkups = survey.health_set.all().filter(
                                           appointment_type='CHECKUP'
                                           ).order_by('-appointment_date')
        self.assertEqual(list(resp.context['checkups']),list(checkups))
        self.assertEqual(resp.context['cur_year'],date.today().year)
        graduation = survey.dob +timedelta(days=365*12) if survey.dob is not None else "No birthday entered"
        self.assertEqual(resp.context['graduation'],graduation)
        classroomenrollment = survey.classroomenrollment_set.all().filter().order_by('drop_date')
        self.assertEqual(list(resp.context['classroomenrollment']),list(classroomenrollment))
        attendance_present = survey.attendance_set.all().filter(attendance='P').count()
        self.assertEqual(resp.context['attendance_present'],attendance_present)
        attendance_approved_absence = survey.attendance_set.all().filter(attendance='AA').count()
        self.assertEqual(resp.context['attendance_approved_absence'],attendance_approved_absence)
        attendance_unapproved_absence = survey.attendance_set.all().filter(attendance='UA').count()
        self.assertEqual(resp.context['attendance_unapproved_absence'],attendance_unapproved_absence)
        self.assertEqual(resp.context['exit_survey'],None)
        self.assertEqual(resp.context['post_exit_survey'],None)
        self.assertEqual(resp.context['notes'],survey.getNotes())
        self.assertEqual(resp.context['TODAY'],date.today().isoformat())

        attendances = Attendance.objects.filter(student_id=student_id)
        attendance_years = []

        years = datetime.now().year-2012
        list_of_years = []
        # generate list of year
        for i in range(years):
          list_of_years.append(2013+i)

        for list_of_year in list_of_years:
          attendance_years.extend(
                [
                    {
                    'year':list_of_year,
                    'present':[],
                    'unapproved':[],
                    'approved':[]
                    }
                ]
            )
        for attendance in attendances:
          for attendance_year in attendance_years:
               if attendance_year['year'] == attendance.date.year or int(attendance_year['year'])+1 == attendance.date.year:
                   beginning = str(attendance_year['year'])+"-08-01"
                   end = str(attendance_year['year']+1)+"-07-31"

                   beginning_of_school_year = datetime.strptime(beginning, "%Y-%m-%d").date()
                   end_of_school_year = datetime.strptime(end, "%Y-%m-%d").date()

                   if attendance.date >= beginning_of_school_year and attendance.date <= end_of_school_year:
                      if attendance.attendance == 'P':
                          attendance_year['present'].append(attendance)
                      elif attendance.attendance == 'UA':
                          attendance_year['unapproved'].append(attendance)
                      elif attendance.attendance == 'AA':
                          attendance_year['approved'].append(attendance)
        self.assertEqual(resp.context['attendance_years'],attendance_years)
        publich_school_historys = survey.publicschoolhistory_set.all()
        self.assertEqual(list(resp.context['publich_school_historys']),list(publich_school_historys))
        spiritual_activities = survey.spiritualactivitiessurvey_set.all()
        self.assertEqual(list(resp.context['spiritual_activities']),list(spiritual_activities))
        pschool = survey.get_pschool()
        self.assertEqual(resp.context['pschool'],pschool)

        # test exit survey not none
        student_id = 11
        url = reverse('student_detail',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        survey = IntakeSurvey.objects.get(pk=student_id)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/detail.html')
        self.assertEqual(resp.context['exit_survey'],survey.exitsurvey_set.all()[0])
        self.assertEqual(resp.context['post_exit_survey'],survey.postexitsurvey_set.all()[0])

    def test_context_not_exist(self):
        student_id = 20
        url = reverse('student_detail',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/errors/intakesurveynotexist.html')
        self.assertEqual(resp.context['error_sms'],'IntakeSurvey matching query does not exist.')

class DisciplineFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','disciplines.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # student_id is none
        url = reverse('discipline_form',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/disciplineform.html')
        self.assertIsInstance(resp.context['form'],DisciplineForm)
        self.assertEqual(resp.context['form'].data,{})
        self.assertEqual(resp.context['student_id'],0)

        # student_id not none
        student_id = 1
        url = reverse('discipline_form',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/disciplineform.html')
        self.assertIsInstance(resp.context['form'],DisciplineForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id)})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(Discipline.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post(self):
        student_id = 1
        classroom_id = 1
        data = {
            'student_id':student_id,
            'classroom_id':1,
            'incident_date':date.today().isoformat(),
            'incident_code':1,
            'incident_description':'test'
        }
        url = reverse('discipline_form',kwargs={})
        resp = self.client.post(url,data)
        instance = Discipline.objects.get(student_id=student_id,classroom_id=1,incident_date=date.today().isoformat())
        self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':instance.student_id.student_id}), status_code=302, target_status_code=200)
        message = 'Logged discipline for '+unicode(instance.student_id.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-meh-o',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(Discipline.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)

class TeacherFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','teachers.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # teacher_id and status is none
        url = reverse('teacher_form',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/teacherform.html')
        self.assertIsInstance(resp.context['form'],TeacherForm)
        self.assertEqual(resp.context['teacher_id'],0)
        self.assertEqual(list(resp.context['current_teachers']),list(Teacher.objects.filter(active=True)))
        self.assertEqual(resp.context['action'],None)
        self.assertEqual(resp.context['status'],'active')

        # student_id and status not none
        teacher_id = 1
        status = 'inactive'
        url = reverse('teacher_form',kwargs={'teacher_id':teacher_id,'status':status})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/teacherform.html')
        self.assertIsInstance(resp.context['form'],TeacherForm)

        instance = Teacher.objects.get(pk=teacher_id)
        self.assertEqual(resp.context['teacher_id'],str(teacher_id))
        self.assertEqual(list(resp.context['current_teachers']),list(Teacher.objects.filter(active=False)))
        self.assertEqual(resp.context['action'],'editing '+str(instance))
        self.assertEqual(resp.context['status'],status)

        self.assertEqual(Teacher.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post_add(self):
        data = {
            'name':'test',
            'active':False
        }
        url = reverse('teacher_form',kwargs={})
        resp = self.client.post(url,data)
        instance = Teacher.objects.get(name='test',active=False)
        self.assertRedirects(resp, expected_url=reverse('teacher_form')+'active', status_code=302, target_status_code=301)
        message = 'Added a new teacher: '+unicode(instance.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-street-view',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(Teacher.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),2)
    def test_post_edit(self):
        teacher_id = 1
        data = {
            'teacher_id':teacher_id,
            'name':'test',
            'active':False
        }
        url = reverse('teacher_form',kwargs={'teacher_id':teacher_id,'status':'inactive'})
        resp = self.client.post(url,data)
        instance = Teacher.objects.get(name='test',active=False)
        self.assertRedirects(resp, expected_url=reverse('teacher_form')+'inactive', status_code=302, target_status_code=301)
        message = 'Updated teachers name: '+unicode(instance.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-street-view',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(Teacher.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)

class ClassroomFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','classroomenrollment.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):
        # classroom_id is none
        url = reverse('classroom_form',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomform.html')
        self.assertIsInstance(resp.context['form'],ClassroomForm)
        self.assertEqual(resp.context['classroom_id'],0)
        self.assertNotEqual(resp.context['selected_classroom'],None)
        self.assertIsInstance(resp.context['selected_classroom'],Classroom)

        self.assertEqual(list(resp.context['current_classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['enrollments'],None)

        # classroom_id is not none
        classroom_id = 1
        url = reverse('classroom_form',kwargs={'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomform.html')
        self.assertIsInstance(resp.context['form'],ClassroomForm)
        self.assertEqual(resp.context['classroom_id'],str(classroom_id))
        instance = Classroom.objects.get(pk=classroom_id)
        self.assertEqual(resp.context['selected_classroom'],instance)
        self.assertIsInstance(resp.context['selected_classroom'],Classroom)

        self.assertEqual(list(resp.context['current_classrooms']),list(Classroom.objects.all()))
        enrollments = instance.classroomenrollment_set.all().filter(
                        Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))
        self.assertEqual(list(resp.context['enrollments']),list(enrollments))

        self.assertEqual(Classroom.objects.all().count(),4)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post_edit(self):
        classroom_id = 1
        data = {
            'classroom_id':classroom_id,
            'cohort':1,
            'school_id':1
        }
        url = reverse('classroom_form',kwargs={'classroom_id':classroom_id})
        resp = self.client.post(url,data)
        instance = Classroom.objects.get(classroom_id=classroom_id,cohort=1,school_id=1)
        self.assertRedirects(resp, expected_url=reverse('classroom_form',kwargs={'classroom_id':instance.classroom_id}), status_code=302, target_status_code=200)
        message = 'Edited classroom '+unicode(instance)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-university',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(Classroom.objects.all().count(),4)
        self.assertEqual(NotificationLog.objects.all().count(),2)

    def test_post_add(self):
        data = {
            'cohort':1,
            'school_id':1
        }
        url = reverse('classroom_form',kwargs={})
        resp = self.client.post(url,data)
        instance = Classroom.objects.filter(cohort=1,school_id=1).latest('classroom_id')
        self.assertRedirects(resp, expected_url=reverse('classroom_form',kwargs={'classroom_id':instance.classroom_id}), status_code=302, target_status_code=200)
        message = 'Added classroom '+unicode(instance)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-university',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(Classroom.objects.all().count(),5)
        self.assertEqual(NotificationLog.objects.all().count(),2)

class ClassroomTeacherFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','classroomteachers.json','teachers.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # teacher_id is none
        url = reverse('classroomteacher_form',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomteacherform.html')
        self.assertIsInstance(resp.context['form'],ClassroomTeacherForm)
        self.assertEqual(resp.context['teacher_id'],0)

        current_assignments = ClassroomTeacher.objects.all()
        classrooms_with_teachers = []
        for classroom in current_assignments:
          classrooms_with_teachers.append(int(classroom.classroom_id.classroom_id))

        unassigned_classrooms = Classroom.objects.all().filter(active=True).exclude(
                                      classroom_id__in=classrooms_with_teachers)

        self.assertEqual(list(resp.context['current_assignments']),list(current_assignments))
        self.assertEqual(list(resp.context['unassigned_classrooms']),list(unassigned_classrooms))

        # teacher_id is not none
        teacher_id = 1
        url = reverse('classroomteacher_form',kwargs={'teacher_id':teacher_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomteacherform.html')
        self.assertIsInstance(resp.context['form'],ClassroomTeacherForm)
        self.assertEqual(resp.context['teacher_id'],str(teacher_id))

        current_assignments = ClassroomTeacher.objects.all()
        classrooms_with_teachers = []
        for classroom in current_assignments:
          classrooms_with_teachers.append(int(classroom.classroom_id.classroom_id))

        unassigned_classrooms = Classroom.objects.all().filter(active=True).exclude(
                                      classroom_id__in=classrooms_with_teachers)
        current_assignments = current_assignments.filter(teacher_id=teacher_id)
        self.assertEqual(list(resp.context['current_assignments']),list(current_assignments))
        self.assertEqual(list(resp.context['unassigned_classrooms']),list(unassigned_classrooms))

        self.assertEqual(ClassroomTeacher.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post(self):
        data = {
            'teacher_id':1,
            'classroom_id':1,
        }
        url = reverse('classroomteacher_form',kwargs={})
        resp = self.client.post(url,data)
        self.assertRedirects(resp, expected_url=reverse('classroomteacher_form',kwargs={'teacher_id':0}), status_code=302, target_status_code=200)
        self.assertEqual(ClassroomTeacher.objects.filter(teacher_id=1,classroom_id=1).count(),2)
        instance = ClassroomTeacher.objects.filter(teacher_id=1,classroom_id=1)[1]
        message = ('Made '+unicode(instance.teacher_id)+
                   ' teacher of '+unicode(instance.classroom_id))
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-pencil',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(ClassroomTeacher.objects.all().count(),4)
        self.assertEqual(NotificationLog.objects.all().count(),2)

class ClassroomEnrollmentFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','classroomenrollment.json','intakeupdates.json',
        'intakeinternals.json','currentstudentInfos.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):
        # classroom_id is none
        url = reverse('classroomenrollment_form',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomenrollmentform.html')
        self.assertIsInstance(resp.context['form'],ClassroomEnrollmentForm)
        self.assertEqual(resp.context['form'].data,{})

        self.assertEqual(resp.context['classroom'],None)
        self.assertEqual(resp.context['enrolled_students'],None)

        # classroom_id is not none
        classroom_id = 1
        url = reverse('classroomenrollment_form',kwargs={'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomenrollmentform.html')
        self.assertIsInstance(resp.context['form'],ClassroomEnrollmentForm)
        self.assertEqual(resp.context['form'].data,{'enrollment_date':date.today().isoformat(),'classroom_id':str(classroom_id)})


        instance = Classroom.objects.get(pk=classroom_id)
        self.assertEqual(resp.context['classroom'],instance)
        enrolled_students = instance.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)))
        self.assertEqual(list(resp.context['enrolled_students']),list(enrolled_students))

        self.assertEqual(ClassroomEnrollment.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_post_not_update_current_grade(self):
        classroom_id = 1
        today = date.today().isoformat()
        data = {
            'classroom_id':classroom_id,
            'enrollment_date':date.today().isoformat(),
            'student_id':[1,2]
        }
        url = reverse('classroomenrollment_form',kwargs={})
        resp = self.client.post(url,data)
        self.assertRedirects(resp, expected_url=reverse('classroomenrollment_form',kwargs={'classroom_id':classroom_id}), status_code=302, target_status_code=200)
        classroom = Classroom.objects.get(pk=classroom_id)
        student1 = IntakeSurvey.objects.get(pk=1)
        student2 = IntakeSurvey.objects.get(pk=2)

        message = 'Added 2 students to '+unicode(classroom)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-level-up',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertTrue(
            ClassroomEnrollment.objects.filter(
                student_id=student1,classroom_id=classroom_id,
                enrollment_date=date.today().isoformat(),
            ).exists()
         )
        self.assertTrue(
            ClassroomEnrollment.objects.filter(
                student_id=student2,classroom_id=classroom_id,
                enrollment_date=date.today().isoformat(),
            ).exists()
         )
        self.assertEqual(ClassroomEnrollment.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        self.assertEqual(IntakeUpdate.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

    def test_post_update_current_grade(self):
        classroom_id = 2
        today = date.today().isoformat()
        data = {
            'classroom_id':classroom_id,
            'enrollment_date':date.today().isoformat(),
            'student_id':[1,2]
        }
        url = reverse('classroomenrollment_form',kwargs={})
        resp = self.client.post(url,data)
        self.assertRedirects(resp, expected_url=reverse('classroomenrollment_form',kwargs={'classroom_id':classroom_id}), status_code=302, target_status_code=200)
        classroom = Classroom.objects.get(pk=classroom_id)
        student1 = IntakeSurvey.objects.get(pk=1)
        student2 = IntakeSurvey.objects.get(pk=2)

        message = 'Added 2 students to '+unicode(classroom)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-level-up',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        message = ('Updated current grade for '+student1.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-pencil-square-o',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        message = ('Updated current grade for '+student2.name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-pencil-square-o',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertTrue(
            ClassroomEnrollment.objects.filter(
                student_id=1,classroom_id=classroom_id,
                enrollment_date=date.today().isoformat(),
            ).exists()
         )
        self.assertTrue(
            ClassroomEnrollment.objects.filter(
                student_id=2,classroom_id=classroom_id,
                enrollment_date=date.today().isoformat(),
            ).exists()
         )
        self.assertTrue(
            IntakeUpdate.objects.filter(
                student_id=student1.student_id,
                current_grade = classroom.cohort,
            ).exists()
        )
        self.assertTrue(
            IntakeUpdate.objects.filter(
                student_id=student2.student_id,
                current_grade = classroom.cohort,
            ).exists()
        )
        self.assertTrue(
            CurrentStudentInfo.objects.filter(
                      student_id=student1.student_id,
                      at_grade_level = studentAtAgeAppropriateGradeLevel(student1.student_id),
                      vdp_grade = student1.current_vdp_grade(),
                      refresh = today,
            ).exists()
        )
        self.assertTrue(
            CurrentStudentInfo.objects.filter(
                      student_id=student2.student_id,
                      at_grade_level = studentAtAgeAppropriateGradeLevel(student2.student_id),
                      vdp_grade = student2.current_vdp_grade(),
                      refresh = today,
            ).exists()
        )
        self.assertEqual(ClassroomEnrollment.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),4)
        self.assertEqual(IntakeUpdate.objects.all().count(),3)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

class ClassroomEnrollmentIndividualViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','classroomenrollment.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        # classroom_id is none
        url = reverse('classroomenrollment_individual',kwargs={'classroom_id':1,'student_id':1})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/classroomenrollmentindividual.html')
        self.assertIsInstance(resp.context['form'],IndividualClassroomEnrollmentForm)
        instance = ClassroomEnrollment.objects.get( classroom_id=1,
                                                    student_id=1)
        self.assertEqual(resp.context['form'].instance,instance)

        self.assertEqual(resp.context['classroom_id'],str(1))
        self.assertEqual(resp.context['student_id'],str(1))


        self.assertEqual(ClassroomEnrollment.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post(self):
        classroom_id = 1
        data = {
            'student_id':1,
            'drop_date':date.today().isoformat(),
            'classroom_id':1
        }
        next_url = reverse('student_detail',kwargs={'student_id':1})
        url = reverse('classroomenrollment_individual',kwargs={'student_id':1,'classroom_id':1})
        resp = self.client.post(url+'?next='+next_url,data)
        self.assertRedirects(resp, expected_url=next_url, status_code=302, target_status_code=200)

        instance = ClassroomEnrollment.objects.get(student_id=1,classroom_id=1,drop_date=date.today().isoformat(),)
        message = ( 'Dropped '+unicode(instance.student_id.name)+
                    ' from '+unicode(instance.classroom_id))
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-bell-slash',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(ClassroomEnrollment.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),2)

class AcademicFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','academic.json','academicmarkingperiods.json',
        'classroomenrollment.json','exitsurveys.json','currentstudentInfos.json',
        'intakeupdates.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_locked_true(self):
        today = date.today().isoformat()
        school_id = 1
        classroom_id = 1
        test_date = today
        url = reverse('academic_form',kwargs={'school_id':school_id,'test_date':test_date,'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicform.html')
        self.assertIsInstance(resp.context['formset'],AcademicFormSet)
        exit_surveys = ExitSurvey.objects.all().filter(exit_date__lte=today).values_list('student_id',flat=True)
        students = ClassroomEnrollment.objects.exclude(student_id__in=exit_surveys).exclude(drop_date__lt=today).filter(classroom_id=1,student_id__date__lte=today)
        student_academics = Academic.objects.filter(student_id__in=students.values_list('student_id'), test_date=test_date)

        self.assertEqual(list(resp.context['formset'].queryset),list(student_academics))
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['test_date'],date.today().isoformat())
        self.assertEqual(resp.context['warning'],mark_safe(''))
        self.assertEqual(list(resp.context['classrooms_by_school']),list(Classroom.objects.filter(school_id=school_id,cohort__lt=50)))
        self.assertEqual(resp.context['message'],mark_safe(''))
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['classroom'],Classroom.objects.get(pk=classroom_id))

        self.assertEqual(Academic.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

    def test_context_locked_false(self):
        today = date.today().isoformat()
        AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        school_id = 1
        classroom_id = 1
        test_date = today
        url = reverse('academic_form',kwargs={'school_id':school_id,'test_date':test_date,'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicform.html')
        self.assertEqual(resp.context['locked'],False)

        self.assertEqual(Academic.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

    def test_post_academic_marking_period_not_match(self):
        school_id = 1
        test_date = date.today().isoformat()
        classroom_id = 1
        url = reverse('academic_form',kwargs={'school_id':school_id,'test_date':test_date,'classroom_id':classroom_id})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicform.html')
        self.assertTrue(resp.context['formset'].is_valid())
        warning = "Test date doesn't match with AcademicMarkingPeriod date."
        self.assertEqual(resp.context['warning'],warning)

        self.assertEqual(Academic.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
    def test_post_academic_marking_period_match_not_update_current_grade(self):
        today = date.today().isoformat()
        AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        school_id = 1
        test_date = today
        classroom_id = 1
        student_id = 2
        test_level = 1
        url = reverse('academic_form',kwargs={'school_id':school_id,'test_date':test_date,'classroom_id':classroom_id})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':student_id,
            'form-0-test_level':test_level,
            'form-0-test_grade_math':90,
            'form-0-test_grade_khmer':90,
            'form-0-promote':False,
            'form-0-test_date':today
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicform.html')
        classroom = Classroom.objects.get(pk=classroom_id)
        message = ('Recorded semester tests for '+
                  str(classroom.get_cohort_display())+' - '
                 +str(classroom.classroom_number)+
                ' at '+str(classroom.school_id))
        self.assertEqual(resp.context['message'],mark_safe(message))
        self.assertTrue(
             Academic.objects.filter(
                 student_id=student_id, test_date=today,
                 promote=False,test_level=test_level
             ).exists()
          )
        self.assertEqual(Academic.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(IntakeUpdate.objects.all().count(),1)

    def test_post_academic_marking_period_match_update_current_grade(self):
        today = date.today().isoformat()
        AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        school_id = 1
        test_date = today
        classroom_id = 1
        student_id = 2
        test_level = 1
        url = reverse('academic_form',kwargs={'school_id':school_id,'test_date':test_date,'classroom_id':classroom_id})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':student_id,
            'form-0-test_level':test_level,
            'form-0-test_grade_math':90,
            'form-0-test_grade_khmer':90,
            'form-0-promote':True,
            'form-0-test_date':today
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicform.html')
        classroom = Classroom.objects.get(pk=classroom_id)
        student = IntakeSurvey.objects.get(pk=student_id)
        message = ('Recorded semester tests for '+
                  str(classroom.get_cohort_display())+' - '
                 +str(classroom.classroom_number)+
                ' at '+str(classroom.school_id))
        self.assertEqual(resp.context['message'],mark_safe(message))

        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-calculator',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        message = ('Updated current grade for '+IntakeSurvey.objects.get(pk=student_id).name)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-pencil-square-o',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertTrue(
             Academic.objects.filter(
                 student_id=student_id, test_date=today,
                 promote=True,test_level=test_level
             ).exists()
          )

        self.assertTrue(
            IntakeUpdate.objects.filter(
                student_id=student.student_id,
                current_grade = test_level+1,
            ).exists()
         )

        instance = IntakeSurvey.objects.get(pk=student_id)
        self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=instance.student_id,
                at_grade_level = studentAtAgeAppropriateGradeLevel(instance.student_id),
                vdp_grade = instance.current_vdp_grade(),
                refresh = today,
                ).exists()
        )
        self.assertEqual(Academic.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),3)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(IntakeUpdate.objects.all().count(),2)

class AcademicSelectViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','academic.json','academicmarkingperiods.json',
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_locked_true(self):
        url = reverse('academic_select',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicselect.html')
        classrooms = Classroom.objects.filter(cohort__lt=50)
        self.assertEqual(list(resp.context['classrooms']),list(classrooms))
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['today'],date.today().isoformat())
    def test_context_locked_false(self):
        today = date.today().isoformat()
        AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        url = reverse('academic_select',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicselect.html')
        classrooms = Classroom.objects.filter(cohort__lt=50)
        self.assertEqual(list(resp.context['classrooms']),list(classrooms))
        self.assertEqual(resp.context['locked'],False)
        self.assertEqual(resp.context['today'],today)
class AcademicFormSingleViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','academic.json','academicmarkingperiods.json',
        'currentstudentInfos.json','intakeinternals.json','intakeupdates.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_locked_true(self):
        today =date.today().isoformat()
        student_id = 1
        url = reverse('academic_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicformsingle.html')
        self.assertIsInstance(resp.context['form'],AcademicForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'test_date':today,'test_level':getStudentGradebyID(student_id)})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Adding')
        self.assertEqual(resp.context['form_error_message'],{})
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['test_id'],None)

        self.assertEqual(Academic.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_locked_false(self):
        today =date.today().isoformat()
        AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        student_id = 1
        url = reverse('academic_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicformsingle.html')
        self.assertIsInstance(resp.context['form'],AcademicForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'test_date':today,'test_level':getStudentGradebyID(student_id)})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Adding')
        self.assertEqual(resp.context['form_error_message'],{})
        self.assertEqual(resp.context['locked'],False)
        self.assertEqual(resp.context['test_id'],None)

        self.assertEqual(Academic.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_no_test_id_add(self):
        today =date.today().isoformat()
        student_id = 1
        url = reverse('academic_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicformsingle.html')
        self.assertIsInstance(resp.context['form'],AcademicForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'test_date':today,'test_level':getStudentGradebyID(student_id)})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Adding')
        self.assertEqual(resp.context['form_error_message'],{})
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['test_id'],None)

        self.assertEqual(Academic.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_no_test_id_edit(self):
        today =date.today().isoformat()
        student_id = 2
        Academic.objects.create(
            student_id=IntakeSurvey.objects.get(pk=student_id),
            test_date=today,test_level=1,test_grade_math=10,
            test_grade_khmer=10,promote=False)
        url = reverse('academic_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicformsingle.html')
        self.assertIsInstance(resp.context['form'],AcademicForm)
        instance = Academic.objects.get(student_id=IntakeSurvey.objects.get(pk=student_id),
                                  test_date=today,
                                  test_level=getStudentGradebyID(student_id)
                                )
        self.assertEqual(resp.context['form'].instance,instance)
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Editing')
        self.assertEqual(resp.context['form_error_message'],{})
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['test_id'],None)

        self.assertEqual(Academic.objects.all().count(),2)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_test_id_not_none(self):
        student_id = 1
        test_id = 1
        url = reverse('academic_form_single',kwargs={'student_id':student_id,'test_id':test_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicformsingle.html')
        self.assertIsInstance(resp.context['form'],AcademicForm)
        instance = Academic.objects.get(id=test_id)
        self.assertEqual(resp.context['form'].instance,instance)
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Editing')
        self.assertEqual(resp.context['form_error_message'],{})
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['test_id'],str(test_id))

        self.assertEqual(Academic.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post_locked_true(self):
            today = date.today().isoformat()
            test_date = today
            student_id = 1
            test_level = 1
            url = reverse('academic_form_single',kwargs={'student_id':student_id})
            data = {
                'student_id':student_id,
                'test_date':test_date,
                'test_level':test_level,
                'promote':True
            }
            resp = self.client.post(url,data)
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp,'mande/academicformsingle.html')
            self.assertFalse(resp.context['form'].is_valid())
            self.assertIsInstance(resp.context['form'],AcademicForm)
            instance,created = Academic.objects.get_or_create(student_id=IntakeSurvey.objects.get(pk=student_id),
                                                test_date=test_date,
                                                test_level=test_level)
            self.assertEqual(resp.context['form'].instance,instance)
            self.assertEqual(resp.context['student_id'],str(student_id))
            self.assertEqual(resp.context['action'],'Adding ')
            self.assertEqual(resp.context['form_error_message'],"Test date doesn't match with AcademicMarkingPeriod date.")
            self.assertEqual(resp.context['locked'],True)
            self.assertEqual(resp.context['test_id'],None)

            self.assertEqual(Academic.objects.all().count(),2)
            self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
            self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_post_locked_false_test_id_none_not_update_current_grade(self):
            today = date.today().isoformat()
            AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
            test_date = today
            student_id = 2
            test_level = 1
            url = reverse('academic_form_single',kwargs={'student_id':student_id})
            data = {
                'student_id':student_id,
                'test_date':test_date,
                'test_level':test_level,
                'promote':False
            }
            resp = self.client.post(url,data)
            self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':student_id}), status_code=302, target_status_code=200)
            self.assertTrue(
                Academic.objects.filter(
                    test_level=test_level,test_date=test_date,
                    student_id=student_id,promote=False
                ).exists()
            )
            self.assertEqual(Academic.objects.all().count(),2)
            self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
            self.assertEqual(NotificationLog.objects.all().count(),2)
            self.assertEqual(IntakeUpdate.objects.all().count(),1)

    def test_post_locked_false_test_id_none_update_current_grade(self):
            today = date.today().isoformat()
            AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
            test_date = today
            student_id = 2
            test_level = 1
            url = reverse('academic_form_single',kwargs={'student_id':student_id})
            data = {
                'student_id':student_id,
                'test_date':test_date,
                'test_level':test_level,
                'promote':True
            }
            resp = self.client.post(url,data)
            self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':student_id}), status_code=302, target_status_code=200)

            instance = Academic.objects.get(student_id=student_id,test_date=test_date,test_level=test_level,promote=True)
            message = ('Recorded semester test for '+instance.student_id.name)
            self.assertTrue(
                NotificationLog.objects.filter(
                    text=message, font_awesome_icon='fa-calculator',
                    user=self.client.session['_auth_user_id']
                ).exists()
            )
            message = ('Updated current grade for '+instance.student_id.name)
            self.assertTrue(
                NotificationLog.objects.filter(
                    text=message, font_awesome_icon='fa-pencil-square-o',
                    user=self.client.session['_auth_user_id']
                ).exists()
            )
            student = IntakeSurvey.objects.get(pk=student_id)
            self.assertTrue(
                CurrentStudentInfo.objects.filter(
                    student_id=student.student_id,
                    at_grade_level = studentAtAgeAppropriateGradeLevel(student.student_id),
                    vdp_grade = student.current_vdp_grade(),
                    refresh = today,
                ).exists()
            )
            self.assertTrue(
                IntakeUpdate.objects.filter(
                    student_id=student.student_id,
                    current_grade = test_level+1,
                ).exists()
            )
            self.assertEqual(Academic.objects.all().count(),2)
            self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
            self.assertEqual(NotificationLog.objects.all().count(),3)
            self.assertEqual(IntakeUpdate.objects.all().count(),2)

    def test_post_locked_false_test_id_not_none_not_update_current_grade(self):
            today = date.today().isoformat()
            AcademicMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
            test_date = today
            student_id = 1
            test_level = 6
            test_id = 1
            url = reverse('academic_form_single',kwargs={'student_id':student_id,'test_id':test_id})
            data = {
                'student_id':student_id,
                'test_date':test_date,
                'test_level':test_level,
                'promote':True
            }
            resp = self.client.post(url,data)
            self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':student_id}), status_code=302, target_status_code=200)
            instance = Academic.objects.get(pk=test_id,student_id=student_id,test_date=test_date,test_level=test_level,promote=True)
            message = ('Updated semester test for '+instance.student_id.name)
            self.assertTrue(
                NotificationLog.objects.filter(
                    text=message, font_awesome_icon='fa-calculator',
                    user=self.client.session['_auth_user_id']
                ).exists()
            )
            self.assertEqual(Academic.objects.all().count(),1)
            self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
            self.assertEqual(NotificationLog.objects.all().count(),2)
            self.assertEqual(IntakeUpdate.objects.all().count(),1)

class StudentEvaluationFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','studentevaluations.json','exitsurveys.json',
        'classroomenrollment.json'
    ]

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
        ClassroomEnrollment.objects.create(
            student_id=IntakeSurvey.objects.get(pk=2),
            classroom_id=Classroom.objects.get(pk=1),
            enrollment_date='2014-01-01')

    def test_context_locked_true(self):
        today = date.today().isoformat()
        school_id = 1
        classroom_id = 1
        get_date = today
        url = reverse('studentevaluation_form',kwargs={'school_id':school_id,'get_date':get_date,'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)

        exit_surveys = ExitSurvey.objects.all().filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
        get_enrolled_student = ClassroomEnrollment.objects.exclude(student_id__in=exit_surveys).exclude(drop_date__lt=date.today().isoformat()).filter(classroom_id=classroom_id,student_id__date__lte=date.today().isoformat())
        students = get_enrolled_student
        #pre instantiate data for this form so that we can update the whole queryset later
        students_at_school_id = []
        for student in students:
            StudentEvaluation.objects.get_or_create(
                                                student_id=student.student_id,date=get_date)
            students_at_school_id.append(student.student_id)
          #lets only work with the students at the specified school_id
        students = students_at_school_id
        student_evaluations = StudentEvaluation.objects.filter(student_id__in=students,
                                                   date=get_date)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationform.html')
        self.assertIsInstance(resp.context['formset'],StudentEvaluationFormSet)
        self.assertEqual(list(resp.context['formset'].queryset),list(student_evaluations))
        self.assertEqual(resp.context['classroom'],Classroom.objects.get(pk=classroom_id))
        self.assertEqual(list(resp.context['classrooms_by_school']),list(Classroom.objects.filter(school_id=school_id)))
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['date'],get_date)
        self.assertEqual(resp.context['warning'],mark_safe(''))
        self.assertEqual(resp.context['date'],get_date)
        self.assertEqual(resp.context['grades'],dict(GRADES))
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(resp.context['message'],'')
        self.assertEqual(StudentEvaluation.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_locked_false(self):
        today = date.today().isoformat()
        today = date.today().isoformat()
        EvaluationMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        school_id = 1
        classroom_id = 1
        get_date = today
        url = reverse('studentevaluation_form',kwargs={'school_id':school_id,'get_date':get_date,'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)

        exit_surveys = ExitSurvey.objects.all().filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
        get_enrolled_student = ClassroomEnrollment.objects.exclude(student_id__in=exit_surveys).exclude(drop_date__lt=date.today().isoformat()).filter(classroom_id=classroom_id,student_id__date__lte=date.today().isoformat())
        students = get_enrolled_student
        #pre instantiate data for this form so that we can update the whole queryset later
        students_at_school_id = []
        for student in students:
            StudentEvaluation.objects.get_or_create(
                                                student_id=student.student_id,date=get_date)
            students_at_school_id.append(student.student_id)
          #lets only work with the students at the specified school_id
        students = students_at_school_id
        student_evaluations = StudentEvaluation.objects.filter(student_id__in=students,
                                                   date=get_date)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationform.html')
        self.assertIsInstance(resp.context['formset'],StudentEvaluationFormSet)
        self.assertEqual(list(resp.context['formset'].queryset),list(student_evaluations))
        self.assertEqual(resp.context['classroom'],Classroom.objects.get(pk=classroom_id))
        self.assertEqual(list(resp.context['classrooms_by_school']),list(Classroom.objects.filter(school_id=school_id)))
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['date'],get_date)
        self.assertEqual(resp.context['warning'],mark_safe(''))
        self.assertEqual(resp.context['date'],get_date)
        self.assertEqual(resp.context['grades'],dict(GRADES))
        self.assertEqual(resp.context['locked'],False)
        self.assertEqual(resp.context['message'],'')

        self.assertEqual(StudentEvaluation.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_post_marking_period_not_match(self):
        today = date.today().isoformat()
        school_id = 1
        classroom_id = 1
        get_date = today
        url = reverse('studentevaluation_form',kwargs={'school_id':school_id,'get_date':get_date,'classroom_id':classroom_id})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':3,
            'form-0-faith_score':100,
            'form-0-personal_score':100,
            'form-0-study_score':100,
            'form-0-hygiene_score':100,
            'form-0-academic_score':100,
            'form-0-date':get_date,
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationform.html')
        self.assertIsInstance(resp.context['formset'],StudentEvaluationFormSet)
        self.assertTrue(resp.context['formset'].is_valid())
        self.assertEqual(resp.context['message'],'')
        self.assertEqual(resp.context['warning'],"Date doesn't match with EvaluationMarkingPeriod date.")
        self.assertEqual(StudentEvaluation.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_post_marking_period_match(self):
        today = date.today().isoformat()
        EvaluationMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        school_id = 1
        classroom_id = 1
        get_date = today
        url = reverse('studentevaluation_form',kwargs={'school_id':school_id,'get_date':get_date,'classroom_id':classroom_id})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':3,
            'form-0-faith_score':100,
            'form-0-personal_score':100,
            'form-0-study_score':100,
            'form-0-hygiene_score':100,
            'form-0-academic_score':100,
            'form-0-date':get_date,
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationform.html')
        self.assertIsInstance(resp.context['formset'],StudentEvaluationFormSet)
        self.assertTrue(resp.context['formset'].is_valid())
        self.assertEqual(resp.context['warning'],'')

        message = ('Recorded student evaluations for '+
                        str(Classroom.objects.get(pk=classroom_id).get_cohort_display())
                        +' - '+
                        str(Classroom.objects.get(pk=classroom_id).classroom_number)
                        +' at '+
                        str(Classroom.objects.get(pk=classroom_id).school_id))
        self.assertEqual(resp.context['message'],message)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-calculator',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(StudentEvaluation.objects.all().count(),4)
        self.assertEqual(NotificationLog.objects.all().count(),2)

    def test_post_invalid(self):
        today = date.today().isoformat()
        school_id = 1
        classroom_id = 1
        get_date = today
        url = reverse('studentevaluation_form',kwargs={'school_id':school_id,'get_date':get_date,'classroom_id':classroom_id})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':1,
            'form-0-faith_score':100,
            'form-0-personal_score':100,
            'form-0-study_score':100,
            'form-0-hygiene_score':100,
            'form-0-academic_score':100,
            'form-0-date':get_date,
        }
        resp = self.client.post(url,data)

        exit_surveys = ExitSurvey.objects.all().filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
        get_enrolled_student = ClassroomEnrollment.objects.exclude(student_id__in=exit_surveys).exclude(drop_date__lt=date.today().isoformat()).filter(classroom_id=classroom_id,student_id__date__lte=date.today().isoformat())
        students = get_enrolled_student
        students_at_school_id = []
        for student in students:
                StudentEvaluation.objects.get_or_create(
                                                student_id=student.student_id,date=get_date)
                students_at_school_id.append(student.student_id)

        #lets only work with the students at the specified school_id
        students = students_at_school_id
        student_evaluations = StudentEvaluation.objects.filter(student_id__in=students,
                                                        date=get_date)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationform.html')
        self.assertIsInstance(resp.context['formset'],StudentEvaluationFormSet)
        self.assertFalse(resp.context['formset'].is_valid())
        warning = 'Cannot record student evaluations. Please refresh the page and try again.'
        self.assertEqual(resp.context['warning'],warning)
        self.assertEqual(list(resp.context['formset'].queryset),list(student_evaluations))
        self.assertEqual(list(resp.context['students']),list(students))

        self.assertEqual(StudentEvaluation.objects.all().count(),3)
        self.assertEqual(NotificationLog.objects.all().count(),1)
class StudentEvaluationSelectViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_locked_true(self):
        url = reverse('studentevaluation_select',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationselect.html')
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['today'],date.today().isoformat())
        self.assertEqual(resp.context['locked'],True)

    def test_context_locked_false(self):
        today = date.today().isoformat()
        EvaluationMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        url = reverse('studentevaluation_select',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationselect.html')
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['today'],date.today().isoformat())
        self.assertEqual(resp.context['locked'],False)

class StudentEvaluationFormSingleViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','studentevaluations.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_locked_true(self):
        student_id = 1
        url = reverse('studentevaluation_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationformsingle.html')
        self.assertIsInstance(resp.context['form'],StudentEvaluationForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'date':date.today().isoformat()})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['locked'],True)
        self.assertEqual(StudentEvaluation.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_locked_false(self):
        student_id = 1
        today = date.today().isoformat()
        EvaluationMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        url = reverse('studentevaluation_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationformsingle.html')
        self.assertIsInstance(resp.context['form'],StudentEvaluationForm)
        self.assertEqual(resp.context['form'].data,{'student_id':str(student_id),'date':date.today().isoformat()})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['locked'],False)
        self.assertEqual(StudentEvaluation.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_evaluation_exist(self):
        # exist
        student_id = 1
        today = date.today().isoformat()
        StudentEvaluation.objects.create(
            student_id = IntakeSurvey.objects.get(pk=student_id),
            faith_score=100,
            study_score=100,
            date = today
        )
        url = reverse('studentevaluation_form_single',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationformsingle.html')
        self.assertIsInstance(resp.context['form'],StudentEvaluationForm)
        instance = StudentEvaluation.objects.get(student_id=IntakeSurvey.objects.get(pk=student_id),
                              date=today)
        self.assertEqual(resp.context['form'].instance,instance)
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['locked'],True)

        self.assertEqual(StudentEvaluation.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_post_marking_period_not_match(self):
        today = date.today().isoformat()
        EvaluationMarkingPeriod.objects.create(description="test",test_date='2017-01-01',marking_period_start=today,marking_period_end=today)

        student_id = 1
        url = reverse('studentevaluation_form_single',kwargs={'student_id':student_id})
        data = {
            'student_id':student_id,
            'faith_score':100,
            'study_score':100,
            'date':today
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationformsingle.html')
        self.assertIsInstance(resp.context['form'],StudentEvaluationForm)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['locked'],False)
        self.assertEqual(StudentEvaluation.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_post_marking_period_match(self):
        today = date.today().isoformat()
        EvaluationMarkingPeriod.objects.create(description="test",test_date=today,marking_period_start=today,marking_period_end=today)
        student_id = 1
        url = reverse('studentevaluation_form_single',kwargs={'student_id':student_id})
        data = {
            'student_id':student_id,
            'faith_score':100,
            'study_score':100,
            'date':today
        }
        resp = self.client.post(url,data)
        instance = StudentEvaluation.objects.get(student_id=student_id,faith_score=100,study_score=100,date=today)
        self.assertRedirects(resp, expected_url=reverse('student_detail',kwargs={'student_id':instance.student_id.student_id}), status_code=302, target_status_code=200)
        message = 'Recorded student evaluation for '+instance.student_id.name
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-calculator',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(StudentEvaluation.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)
class PublicSchoolFormViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','publicschoolhistorys.json','currentstudentInfos.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_add(self):
        student_id = 1
        url = reverse('publicschool_form',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/publicschoolhistoryform.html')
        self.assertIsInstance(resp.context['form'],StudentPublicSchoolHistoryForm)
        self.assertEqual(resp.context['form'].initial,{'student_id':str(student_id)})
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Adding')
        # expect data_guardian_profession is json format
        raised = True
        try:
            json.loads(resp.context['data_public_schools'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_public_schools'],'["test"]')

        self.assertEqual(PublicSchoolHistory.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
    def test_context_edit(self):
        student_id = 1
        id = 1
        url = reverse('publicschool_form',kwargs={'student_id':student_id,'id':id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/publicschoolhistoryform.html')
        self.assertIsInstance(resp.context['form'],StudentPublicSchoolHistoryForm)
        instance = PublicSchoolHistory.objects.get(pk=id)
        self.assertEqual(resp.context['form'].instance,instance)
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['action'],'Editing')
        # expect data_guardian_profession is json format
        raised = True
        try:
            json.loads(resp.context['data_public_schools'])
        except:
            raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_public_schools'],'["test"]')

        self.assertEqual(PublicSchoolHistory.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
    def test_post_add(self):
       student_id = 1
       today = date.today().isoformat()
       data = {
           'student_id':1,
           'status':'N',
           'enroll_date':today,
           'drop_date':today,
           'grade':1,
           'reasons':'test'
       }
       student_id = 1
       url = reverse('publicschool_form',kwargs={'student_id':student_id})
       resp = self.client.post(url,data)
       next_url = reverse('student_detail',kwargs={'student_id':student_id})+'#enrollment'
       self.assertRedirects(resp, expected_url=next_url, status_code=302, target_status_code=200)
       instance = PublicSchoolHistory.objects.get(student_id=1,enroll_date=today,drop_date=today)
       message = 'Added a public school history for '+instance.student_id.name
       self.assertTrue(
            NotificationLog.objects.filter(
                text=message,font_awesome_icon='fa-graduation-cap',
                user=self.client.session['_auth_user_id']
            ).exists()
       )
       student = IntakeSurvey.objects.get(pk=student_id)
       self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=student.student_id,
                in_public_school = True if student.get_pschool().status=='Y' else False,
                refresh = today,
                ).exists()
       )
       self.assertEqual(PublicSchoolHistory.objects.all().count(),3)
       self.assertEqual(NotificationLog.objects.all().count(),2)
       self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
    def test_post_edit(self):
       student_id = 1
       id = 1
       today = date.today().isoformat()
       data = {
           'student_id':1,
           'status':'N',
           'enroll_date':today,
           'drop_date':today,
           'grade':1,
           'reasons':'test'
       }
       student_id = 1
       url = reverse('publicschool_form',kwargs={'student_id':student_id,'id':id})
       resp = self.client.post(url,data)
       next_url = reverse('student_detail',kwargs={'student_id':student_id})+'#enrollment'
       self.assertRedirects(resp, expected_url=next_url, status_code=302, target_status_code=200)
       instance = PublicSchoolHistory.objects.get(pk=id)
       message = 'Edited a public school history for '+instance.student_id.name
       self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-graduation-cap',
                user=self.client.session['_auth_user_id']
            ).exists()
       )
       student = IntakeSurvey.objects.get(pk=student_id)
       self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=student.student_id,
                in_public_school = True if student.get_pschool().status=='Y' else False,
                refresh = today,
                ).exists()
       )
       self.assertEqual(PublicSchoolHistory.objects.all().count(),2)
       self.assertEqual(NotificationLog.objects.all().count(),2)
       self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
class DeletePublicSchoolViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','publicschoolhistorys.json','currentstudentInfos.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_fail(self):
        self.assertEqual(PublicSchoolHistory.objects.all().count(),2)
        id = 3
        next_url = reverse('student_detail',kwargs={'student_id':1})
        url = reverse('delete_public_school',kwargs={'id':id})
        resp = self.client.get(url+'?next='+next_url,follow=True)
        self.assertRedirects(resp, expected_url=next_url, status_code=302, target_status_code=200)
        message = list(resp.context.get('messages'))[0]
        self.assertEqual(message.tags, 'delete_public_school error')
        self.assertTrue('Fail to delete Public School History! (PublicSchoolHistory matching query does not exist.)' in message.message)
        self.assertEqual(PublicSchoolHistory.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),1)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)
    def test_context_success(self):
        self.assertEqual(PublicSchoolHistory.objects.all().count(),2)
        id = 1
        pschool = PublicSchoolHistory.objects.get(pk=id)
        student = IntakeSurvey.objects.get(student_id=pschool.student_id.student_id)
        next_url = reverse('student_detail',kwargs={'student_id':1})
        url = reverse('delete_public_school',kwargs={'id':id})
        resp = self.client.get(url+'?next='+next_url,follow=True)
        self.assertRedirects(resp, expected_url=next_url, status_code=302, target_status_code=200)
        message = list(resp.context.get('messages'))[0]
        self.assertEqual(message.tags, 'delete_public_school success')
        # self.assertEqual(message.message,'Public School History has been deleted successfully!'.decode('utf-8'))
        self.assertTrue('Public School History has been deleted successfully!' in message.message)
        sms = 'Deleted a public school history for '+student.name
        self.assertTrue(
              NotificationLog.objects.filter(
                  text=sms,font_awesome_icon='fa-graduation-cap',
                  user=self.client.session['_auth_user_id']
              ).exists()
        )
        self.assertEqual(PublicSchoolHistory.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),2)
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

class AcademicMakingPeriodViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','academicmarkingperiods.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):
        url = reverse('academic_making_period',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicmarkingperiodform.html')
        self.assertIsInstance(resp.context['form'],AcademicMarkingPeriodForm)
        self.assertEqual(list(resp.context['marking_periods']),list(AcademicMarkingPeriod.objects.all()))
        self.assertEqual(resp.context['form_message'],{'status':''})

        self.assertEqual(AcademicMarkingPeriod.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_post_invalid(self):
        today = date.today().isoformat()
        data = {
                'description':'testtest',
                'test_date':today,
                'marking_period_start':today,
                }
        url = reverse('academic_making_period',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicmarkingperiodform.html')
        self.assertIsInstance(resp.context['form'],AcademicMarkingPeriodForm)
        self.assertEqual(list(resp.context['marking_periods']),list(AcademicMarkingPeriod.objects.all()))
        self.assertEqual(resp.context['form_message'],{'status': 'error', 'sms': u'* marking_period_end\n  * This field is required.'})
        self.assertEqual(AcademicMarkingPeriod.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)
    def test_context_post_valid(self):
        today = date.today().isoformat()
        data = {
                'description':'testtest',
                'test_date':today,
                'marking_period_start':today,
                'marking_period_end':today,
                }
        url = reverse('academic_making_period',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/academicmarkingperiodform.html')
        self.assertIsInstance(resp.context['form'],AcademicMarkingPeriodForm)
        self.assertEqual(list(resp.context['marking_periods']),list(AcademicMarkingPeriod.objects.all()))
        self.assertEqual(resp.context['form_message'],{'status':'success','sms':'Successfully added an Academic Marking Period'})
        instance = AcademicMarkingPeriod.objects.get(description='testtest',test_date=today,marking_period_start=today,marking_period_end=today)
        message = 'Added an Academics Marking Period ('+instance.description+')'
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-calendar',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(AcademicMarkingPeriod.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)


class EvaluationMakingPeriodViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'notificationlogs.json','evaluationmarkingperiods.json'
    ]

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('evaluation_making_period',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/evaluationmarkingperiodform.html')
        self.assertIsInstance(resp.context['form'],EvaluationMarkingPeriodForm)
        self.assertEqual(list(resp.context['marking_periods']),list(EvaluationMarkingPeriod.objects.all()))
        self.assertEqual(resp.context['form_message'],{'status':''})

        self.assertEqual(EvaluationMarkingPeriod.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_post_invalid(self):
        today = date.today().isoformat()
        data = {
                'description':'testtest',
                'test_date':today,
                'marking_period_start':today,
                }
        url = reverse('evaluation_making_period',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/evaluationmarkingperiodform.html')
        self.assertIsInstance(resp.context['form'],EvaluationMarkingPeriodForm)
        self.assertEqual(list(resp.context['marking_periods']),list(EvaluationMarkingPeriod.objects.all()))
        self.assertEqual(resp.context['form_message'],{'status': 'error', 'sms': u'* marking_period_end\n  * This field is required.'})
        self.assertEqual(EvaluationMarkingPeriod.objects.all().count(),1)
        self.assertEqual(NotificationLog.objects.all().count(),1)

    def test_context_post_valid(self):
        today = date.today().isoformat()
        data = {
                'description':'testtest',
                'test_date':today,
                'marking_period_start':today,
                'marking_period_end':today,
                }
        url = reverse('evaluation_making_period',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/evaluationmarkingperiodform.html')
        self.assertIsInstance(resp.context['form'],EvaluationMarkingPeriodForm)
        self.assertEqual(list(resp.context['marking_periods']),list(EvaluationMarkingPeriod.objects.all()))
        self.assertEqual(resp.context['form_message'],{'status':'success','sms':'Successfully added a Student Evaluation Marking Period'})
        instance = EvaluationMarkingPeriod.objects.get(description='testtest',test_date=today,marking_period_start=today,marking_period_end=today)
        message = 'Added a Student Evaluation Marking Period ('+instance.description+')'
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-calendar-o',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(EvaluationMarkingPeriod.objects.all().count(),2)
        self.assertEqual(NotificationLog.objects.all().count(),2)
