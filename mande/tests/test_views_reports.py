from django.test import TestCase
from django.test import Client

from mande.models import *
from mande.forms import *

from datetime import date,datetime
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from django.db.models import Q,Count

import json
from datetime import timedelta
import re
import operator

from mande.utils import studentAtAgeAppropriateGradeLevel
from mande.utils import getEnrolledStudents

activate('en')
class DailyAttendanceReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendancelogs.json','attendancedayofferings.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        today = date.today().isoformat()
        attendance_date = today
        url = reverse('daily_attendance_report',kwargs={'attendance_date':attendance_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendancereport.html')
        classrooms = Classroom.objects.all().filter(active=True)
        classrooms_who_take_attendance = []
        for classroom in classrooms:
            if classroom.getAttendanceDayOfferings(attendance_date):
                classrooms_who_take_attendance.append(classroom)
        classroomattendance = {}
        for classroom in classrooms_who_take_attendance:
          try:
              classroomattendance[classroom] = AttendanceLog.objects.get(
                                                             classroom=classroom,
                                                             date=attendance_date)
          except ObjectDoesNotExist:
              classroomattendance[classroom] = None
        self.assertEqual(list(resp.context['classroomattendance']),list(classroomattendance))
        self.assertEqual(resp.context['attendance_date'],attendance_date)

class StudentAttendanceDetailViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendances.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        today = date.today().isoformat()
        student_id = 1
        url = reverse('student_attendance_detail',kwargs={'student_id':student_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/student_attendance_detail.html')
        attendances = Attendance.objects.all().filter(student_id=student_id).order_by('-date')
        self.assertEqual(list(resp.context['attendances']),list(attendances))
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)

    def test_context_post(self):
        today = date.today().isoformat()
        start_date = today
        end_date = today
        data = {
            'start_date' : start_date,
            'end_date' : end_date
        }
        student_id = 1
        url = reverse('student_attendance_detail',kwargs={'student_id':student_id})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/student_attendance_detail.html')
        attendances = Attendance.objects.all().filter(Q(student_id=student_id) & Q(Q(date__gte=start_date) & Q(date__lte=end_date))).order_by('-date')
        self.assertEqual(list(resp.context['attendances']),list(attendances))
        self.assertEqual(resp.context['student_id'],str(student_id))
        self.assertEqual(resp.context['start_date'],start_date)
        self.assertEqual(resp.context['end_date'],end_date)

class AttendanceSummaryReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendances.json','exitsurveys.json','classroomenrollment.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_id_none(self):
        url = reverse('attendance_summary_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendance_summary_report.html')
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['current_selected'],None)
        self.assertEqual(resp.context['select_type'],None)
        self.assertEqual(resp.context['id'],None)
        exit_surveys = ExitSurvey.objects.filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
        students = IntakeSurvey.objects.exclude(student_id__in=exit_surveys).filter(date__lte=date.today().isoformat())
        studentattendance = {}
        for stu in students:
            student = stu
            try:
                studentattendance[student] = {
                    'classroom' : ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(drop_date=None) | Q(drop_date__gte=date.today().isoformat()))),
                    'present' : Attendance.objects.filter(student_id=student,attendance='P').count(),
                    'unapproved' : Attendance.objects.filter(student_id=student,attendance='UA').count(),
                    'approved' : Attendance.objects.filter(student_id=student,attendance='AA').count(),
                    'total' : Attendance.objects.filter(student_id=student,attendance='P').count()
                            +Attendance.objects.filter(student_id=student,attendance='UA').count()
                            +Attendance.objects.filter(student_id=student,attendance='AA').count()
                     }
            except ObjectDoesNotExist:
               studentattendance[student] = None
        self.assertEqual(list(resp.context['studentattendance']),list(studentattendance))

    def test_context_id_not_none(self):
        id = 1
        url = reverse('attendance_summary_report',kwargs={'id':id,'select_type':'other'})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendance_summary_report.html')
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['current_selected'],None)
        self.assertEqual(resp.context['select_type'],'other')
        self.assertEqual(resp.context['id'],str(id))
        exit_surveys = ExitSurvey.objects.filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
        students = IntakeSurvey.objects.exclude(student_id__in=exit_surveys).filter(date__lte=date.today().isoformat())
        studentattendance = {}
        for stu in students:
            student = stu.student_id
            try:
                studentattendance[student] = {
                    'classroom' : ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(drop_date=None) | Q(drop_date__gte=date.today().isoformat()))),
                    'present' : Attendance.objects.filter(student_id=student,attendance='P').count(),
                    'unapproved' : Attendance.objects.filter(student_id=student,attendance='UA').count(),
                    'approved' : Attendance.objects.filter(student_id=student,attendance='AA').count(),
                    'total' : Attendance.objects.filter(student_id=student,attendance='P').count()
                            +Attendance.objects.filter(student_id=student,attendance='UA').count()
                            +Attendance.objects.filter(student_id=student,attendance='AA').count()
                     }
            except ObjectDoesNotExist:
               studentattendance[student] = None
        self.assertEqual(list(resp.context['studentattendance']),list(studentattendance))

    def test_context_id_not_none_and_select_type_is_site(self):
        id = 1
        url = reverse('attendance_summary_report',kwargs={'id':id,'select_type':'site'})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendance_summary_report.html')
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['current_selected'],School.objects.get(school_id=id))
        self.assertEqual(resp.context['select_type'],'site')
        self.assertEqual(resp.context['id'],str(id))
        students = ClassroomEnrollment.objects.all().filter(Q(classroom_id__school_id=id) & Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)))

        studentattendance = {}
        for stu in students:
            student = stu.student_id
            try:
                studentattendance[student] = {
                    'classroom' : ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(drop_date=None) | Q(drop_date__gte=date.today().isoformat()))),
                    'present' : Attendance.objects.filter(student_id=student,attendance='P').count(),
                    'unapproved' : Attendance.objects.filter(student_id=student,attendance='UA').count(),
                    'approved' : Attendance.objects.filter(student_id=student,attendance='AA').count(),
                    'total' : Attendance.objects.filter(student_id=student,attendance='P').count()
                            +Attendance.objects.filter(student_id=student,attendance='UA').count()
                            +Attendance.objects.filter(student_id=student,attendance='AA').count()
                     }
            except ObjectDoesNotExist:
               studentattendance[student] = None
        self.assertEqual(list(resp.context['studentattendance']),list(studentattendance))

    def test_context_id_not_none_and_select_type_is_classroom(self):
        id = 1
        url = reverse('attendance_summary_report',kwargs={'id':id,'select_type':'classroom'})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendance_summary_report.html')
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.all()))
        self.assertEqual(resp.context['current_selected'],Classroom.objects.get(classroom_id=id))
        self.assertEqual(resp.context['select_type'],'classroom')
        self.assertEqual(resp.context['id'],str(id))
        students = ClassroomEnrollment.objects.all().filter(Q(classroom_id__classroom_id=id) & Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)))

        studentattendance = {}
        for stu in students:
            student = stu.student_id
            try:
                studentattendance[student] = {
                    'classroom' : ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(drop_date=None) | Q(drop_date__gte=date.today().isoformat()))),
                    'present' : Attendance.objects.filter(student_id=student,attendance='P').count(),
                    'unapproved' : Attendance.objects.filter(student_id=student,attendance='UA').count(),
                    'approved' : Attendance.objects.filter(student_id=student,attendance='AA').count(),
                    'total' : Attendance.objects.filter(student_id=student,attendance='P').count()
                            +Attendance.objects.filter(student_id=student,attendance='UA').count()
                            +Attendance.objects.filter(student_id=student,attendance='AA').count()
                     }
            except ObjectDoesNotExist:
               studentattendance[student] = None
        self.assertEqual(list(resp.context['studentattendance']),list(studentattendance))

class DailyAbsenceReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendances.json','attendancedayofferings.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_no_attendance_date(self):
        today = date.today().isoformat()
        attendance_date = today
        attendance_end_date = today
        url = reverse('daily_absence_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/absencereport.html')
        self.assertEqual(resp.context['attendance_date'],today)
        self.assertEqual(resp.context['attendance_end_date'],today)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classroom_list']),list(Classroom.objects.filter(active=True)))
        self.assertEqual(resp.context['current_site'],None)
        self.assertEqual(resp.context['current_classroom'],None)
        # if site and classrooom is none
        takesattendance = AttendanceDayOffering.objects.filter(
                                                               Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date)
                                                         ).values_list('classroom_id',flat=True)
        classrooms = Classroom.objects.all().filter(active=True)
        classrooms = classrooms.filter(classroom_id__in=takesattendance)
        classroomattendance = {}
        for classroom in classrooms:
           try:
               #only displays unexcused absences
               classroomattendance[classroom] = Attendance.objects.filter(
                                                              Q(Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date))
                                                              & Q(classroom=classroom)
                                                           #    & Q(attendance='UA')
                                                              )
           except ObjectDoesNotExist:
               classroomattendance[classroom] = None
        self.assertEqual(list(resp.context['classroomattendance']),list(classroomattendance))

    def test_context_attendance_date_not_none(self):
        today = date.today().isoformat()
        attendance_date = '2017-01-01'
        attendance_end_date = today
        url = reverse('daily_absence_report',kwargs={'attendance_date':attendance_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/absencereport.html')
        self.assertEqual(resp.context['attendance_date'],attendance_date)
        self.assertEqual(resp.context['attendance_end_date'],attendance_end_date)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classroom_list']),list(Classroom.objects.filter(active=True)))
        self.assertEqual(resp.context['current_site'],None)
        self.assertEqual(resp.context['current_classroom'],None)
        # if site and classrooom is none
        takesattendance = AttendanceDayOffering.objects.filter(
                                                               Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date)
                                                         ).values_list('classroom_id',flat=True)
        classrooms = Classroom.objects.all().filter(active=True)
        classrooms = classrooms.filter(classroom_id__in=takesattendance)
        classroomattendance = {}
        for classroom in classrooms:
           try:
               #only displays unexcused absences
               classroomattendance[classroom] = Attendance.objects.filter(
                                                              Q(Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date))
                                                              & Q(classroom=classroom)
                                                           #    & Q(attendance='UA')
                                                              )
           except ObjectDoesNotExist:
               classroomattendance[classroom] = None
        self.assertEqual(list(resp.context['classroomattendance']),list(classroomattendance))

    def test_context_attendance_side_not_none_and_classroom_is_none(self):
        today = date.today().isoformat()
        attendance_date = today
        attendance_end_date = today
        classroom_id = None
        site = 1
        data = {
            'classroom':classroom_id,
            'site':site,
            'attendance_date':today,
            'attendance_end_date':attendance_end_date
        }
        url = reverse('daily_absence_report',kwargs={'attendance_date':attendance_date})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/absencereport.html')
        self.assertEqual(resp.context['attendance_date'],attendance_date)
        self.assertEqual(resp.context['attendance_end_date'],attendance_end_date)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classroom_list']),list(Classroom.objects.filter(active=True)))
        self.assertEqual(resp.context['current_site'], School.objects.get(school_id=site))
        self.assertEqual(resp.context['current_classroom'],None)
        # if site and classrooom is none
        takesattendance = AttendanceDayOffering.objects.filter(
                                                               Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date)
                                                         ).values_list('classroom_id',flat=True)
        classrooms = Classroom.objects.all().filter(active=True)
        classrooms = classrooms.filter(classroom_id__in=takesattendance,school_id=site)
        classroomattendance = {}
        for classroom in classrooms:
           try:
               #only displays unexcused absences
               classroomattendance[classroom] = Attendance.objects.filter(
                                                              Q(Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date))
                                                              & Q(classroom=classroom)
                                                           #    & Q(attendance='UA')
                                                              )
           except ObjectDoesNotExist:
               classroomattendance[classroom] = None
        self.assertEqual(list(resp.context['classroomattendance']),list(classroomattendance))

    def test_context_attendance_classroom_id_not_none_and_site_is_none(self):
        today = date.today().isoformat()
        attendance_date = today
        attendance_end_date = today
        classroom_id = 1
        site = None
        data = {
            'classroom':classroom_id,
            'site':site,
            'attendance_date':today,
            'attendance_end_date':attendance_end_date
        }
        url = reverse('daily_absence_report',kwargs={'attendance_date':attendance_date})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/absencereport.html')
        self.assertEqual(resp.context['attendance_date'],attendance_date)
        self.assertEqual(resp.context['attendance_end_date'],attendance_end_date)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(list(resp.context['classroom_list']),list(Classroom.objects.filter(active=True)))
        self.assertEqual(resp.context['current_site'],None)
        self.assertEqual(resp.context['current_classroom'],Classroom.objects.get(classroom_id=classroom_id))
        # if site and classrooom is none
        takesattendance = AttendanceDayOffering.objects.filter(
                                                               Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date)
                                                         ).values_list('classroom_id',flat=True)
        classrooms = Classroom.objects.all().filter(active=True)
        classrooms = classrooms.filter(classroom_id__in=takesattendance,classroom_id=classroom_id)
        classroomattendance = {}
        for classroom in classrooms:
           try:
               #only displays unexcused absences
               classroomattendance[classroom] = Attendance.objects.filter(
                                                              Q(Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date))
                                                              & Q(classroom=classroom)
                                                           #    & Q(attendance='UA')
                                                              )
           except ObjectDoesNotExist:
               classroomattendance[classroom] = None
        self.assertEqual(list(resp.context['classroomattendance']),list(classroomattendance))

class DataAuditViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'intakeupdates.json','exitsurveys.json','intakeinternals.json',
        'publicschoolhistorys.json','classroomenrollment.json','attendancedayofferings.json',
        'attendances.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
        # Incorrect DOB
        self.dob = '1989-01-01'
        intake = IntakeSurvey.objects.get(pk=1)
        intake.dob = self.dob
        intake.save()

        today = date.today()
      #   today = datetime.strptime("2014-08-01", "%Y-%m-%d").date()
        if (today < datetime.strptime(str(today.year)+"-08-01", "%Y-%m-%d").date()):
             school_year = today.year - 1
        else:
             school_year = today.year
        # Has never attended class,Unapproved absence with no comment
        self.attendance_date = str(school_year)+"-08-01"
        self.classroom = Classroom.objects.get(pk=1)
        Attendance.objects.create(
            student_id=IntakeSurvey.objects.get(pk=2),
            classroom=self.classroom,
            attendance='UA',
    		date=self.attendance_date
        )
        # Unapproved abscence with no comment - missing class id
        Attendance.objects.create(
            student_id=IntakeSurvey.objects.get(pk=3),
            classroom=None,
            attendance='UA',
    		date=self.attendance_date
        )

    def test_context(self):
        url = reverse('data_audit',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/data_audit.html')
        self.assertIn('No Public School History',resp.context['filters'])
        self.assertIn('Not enrolled in any classes',resp.context['filters'])
        self.assertIn('Incorrect DOB',resp.context['filters'])
        self.assertIn('Unapproved absence with no comment',resp.context['filters'])
        self.assertIn('Unapproved abscence with no comment - missing class id',resp.context['filters'])
        students = resp.context['students']
        student1 = IntakeSurvey.objects.get(pk=1)
        student2 = IntakeSurvey.objects.get(pk=2)
        student3 = IntakeSurvey.objects.get(pk=3)
        student4 = IntakeSurvey.objects.get(pk=4)
        student5 = IntakeSurvey.objects.get(pk=5)
        student6 = IntakeSurvey.objects.get(pk=6)
        student7 = IntakeSurvey.objects.get(pk=7)
        student8 = IntakeSurvey.objects.get(pk=8)

        text = 'Incorrect DOB'
        age = '(~'+unicode(datetime.now().year-datetime.strptime(self.dob, '%Y-%m-%d').year)+' years old)'
        self.assertIn(
            {'text': text+age, 'resolution': reverse('intake_survey',kwargs={'student_id':student1.student_id}), 'limit': 'dob'},
            students[student1]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student2]
        )
        self.assertIn(
            {'text': 'Has never attended class', 'resolution': reverse('student_detail',kwargs={'student_id':student2.student_id}), 'limit': None}
            ,students[student2]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student2.student_id}), 'limit': None}
            ,students[student2]
        )
        self.assertIn(
            {'text': 'Unapproved absence with no comment', 'resolution': reverse('take_class_attendance',kwargs={'attendance_date':self.attendance_date, 'classroom_id':self.classroom.classroom_id}), 'limit': None}
            ,students[student2]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student3]
        )
        self.assertIn(
            {'text': 'Has never attended class', 'resolution': reverse('student_detail',kwargs={'student_id':student3.student_id}), 'limit': None}
            ,students[student3]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student3.student_id}), 'limit': None}
            ,students[student3]
        )
        self.assertIn(
            {'text': 'Unapproved abscence with no comment - missing class id', 'resolution': '', 'limit': None}
            ,students[student3]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student4.student_id}), 'limit': None}
            ,students[student4]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student4]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student5.student_id}), 'limit': None}
            ,students[student5]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student5]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student6.student_id}), 'limit': None}
            ,students[student6]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student6]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student7.student_id}), 'limit': None}
            ,students[student7]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student7]
        )
        self.assertIn(
            {'text': 'No Public School History', 'resolution': reverse('student_detail',kwargs={'student_id':student8.student_id}), 'limit': None}
            ,students[student8]
        )
        self.assertIn(
            {'text': 'Not enrolled in any classes', 'resolution': reverse('classroomenrollment_form'), 'limit': None}
            ,students[student8]
        )

class ClassListViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'classroomteachers.json','classroomenrollment.json','teachers.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):

        url = reverse('class_list',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/class_list.html')
        class_list={}
        classrooms = Classroom.objects.all()
        for classroom in classrooms:
          instance = Classroom.objects.get(classroom_id=classroom.pk)
          class_list[classroom]={
              'site':classroom.school_id,
              'target_grade':classroom.cohort,
              'classroom_number':classroom.classroom_number,
              'teacher': 'Not assigned',
              'students': 0,
              'female': 0,
          }
          try:
              class_list[classroom]['teacher'] = ClassroomTeacher.objects.filter(classroom_id=classroom.pk)
          except ObjectDoesNotExist:
              pass
          try:
              enrolled_students =  instance.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)))
              female_students = 0
              for student in enrolled_students:
                  if student.student_id.gender == 'F':
                      female_students +=1
              class_list[classroom]['students'] = len(enrolled_students)
              class_list[classroom]['female'] = female_students
          except ObjectDoesNotExist:
              pass
        self.assertEqual(list(resp.context['class_list']),list(class_list))

class ExitSurveysListViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'exitsurveys.json','postexitsurveys.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('exit_surveys_list',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/exitsurveylist.html')
        from_exit_date=(datetime.now()- timedelta(days=2 * 365/12)).strftime("%Y-%m-%d")
        to_exit_date=(datetime.now()).strftime("%Y-%m-%d")
        exit_surveys = ExitSurvey.objects.all().filter(exit_date__gte=from_exit_date , exit_date__lte=to_exit_date)
        post_exit_surveys = PostExitSurvey.objects.all()
        self.assertEqual(resp.context['from_exit_date'],from_exit_date)
        self.assertEqual(resp.context['to_exit_date'],to_exit_date)
        self.assertEqual(list(resp.context['exit_surveys']),list(exit_surveys))
        self.assertEqual(list(resp.context['post_exit_surveys']),list(post_exit_surveys))

    def test_context_post(self):
        url = reverse('exit_surveys_list',kwargs={})
        from_exit_date=date.today().isoformat()
        to_exit_date=date.today().isoformat()
        data = {
            'from_exit_date':from_exit_date,
            'to_exit_date':to_exit_date
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/exitsurveylist.html')

        exit_surveys = ExitSurvey.objects.all().filter(exit_date__gte=from_exit_date , exit_date__lte=to_exit_date)
        post_exit_surveys = PostExitSurvey.objects.all()
        self.assertEqual(resp.context['from_exit_date'],from_exit_date)
        self.assertEqual(resp.context['to_exit_date'],to_exit_date)
        self.assertEqual(list(resp.context['exit_surveys']),list(exit_surveys))
        self.assertEqual(list(resp.context['post_exit_surveys']),list(post_exit_surveys))

class StudentAbsenceReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendances.json','exitsurveys.json','intakeinternals.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('student_absence_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/student_absence_report.html')
        attendances = Attendance.objects.all()

        #set up dict of attendance codes with zero values
        default_attendance ={}
        attendancecodes = dict(ATTENDANCE_CODES)
        for key,code in attendancecodes.iteritems():
          default_attendance[key]=0

        #default out all current students
        attendance_by_sid = {}
        currently_enrolled_students = getEnrolledStudents()
        for student in currently_enrolled_students:
          attendance_by_sid[student]=dict(default_attendance)


        for attendance in attendances:
          try:
              attendance_by_sid[attendance.student_id][attendance.attendance] +=1
          except KeyError:
              pass; #students no longer in attendance that have attendance
        self.assertEqual(resp.context['attendance_by_sid'],attendance_by_sid)
        self.assertEqual(resp.context['attendancecodes'],attendancecodes)

class StudentLagReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendances.json','exitsurveys.json','intakeinternals.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('student_lag_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/student_lag_report.html')
        view_date=date.today().strftime("%Y-%m-%d")
        enrolled_students = getEnrolledStudents()
        students_lag = {}
        for student in enrolled_students:
          #only students in the scope of grade levels
          if student.current_vdp_grade(view_date) < 12:
              age_appropriate_grade = student.age_appropriate_grade(view_date)
              current_vdp_grade = student.current_vdp_grade(view_date)
              lag = age_appropriate_grade - current_vdp_grade
              students_lag[student] = {
                      'lag':lag,
                      'appropriate_grade':age_appropriate_grade,
                      'vdp_grade':current_vdp_grade,
                      'date_achieved_age_appropriate_level': student.date_enrolled_grade(current_vdp_grade) if current_vdp_grade - age_appropriate_grade<=0 else student.date_enrolled_grade(current_vdp_grade-(current_vdp_grade - age_appropriate_grade))
              }
        self.assertEqual(resp.context['view_date'],view_date)
        self.assertEqual(resp.context['students_lag'],students_lag)

    def test_context_post(self):
        view_date = date.today().isoformat()
        data = {
            'view_date': view_date
        }
        url = reverse('student_lag_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/student_lag_report.html')
        enrolled_students = getEnrolledStudents()
        students_lag = {}
        for student in enrolled_students:
          #only students in the scope of grade levels
          if student.current_vdp_grade(view_date) < 12:
              age_appropriate_grade = student.age_appropriate_grade(view_date)
              current_vdp_grade = student.current_vdp_grade(view_date)
              lag = age_appropriate_grade - current_vdp_grade
              students_lag[student] = {
                      'lag':lag,
                      'appropriate_grade':age_appropriate_grade,
                      'vdp_grade':current_vdp_grade,
                      'date_achieved_age_appropriate_level': student.date_enrolled_grade(current_vdp_grade) if current_vdp_grade - age_appropriate_grade<=0 else student.date_enrolled_grade(current_vdp_grade-(current_vdp_grade - age_appropriate_grade))
              }
        self.assertEqual(resp.context['view_date'],view_date)
        self.assertEqual(resp.context['students_lag'],students_lag)

class StudentEvaluationReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'studentevaluations.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_classroom_id_none(self):
        url = reverse('student_evaluation_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationreport.html')
        active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
        evaluations = StudentEvaluation.objects.all().exclude(  academic_score=None,
                                                              study_score=None,
                                                              personal_score=None,
                                                              hygiene_score=None,
                                                              faith_score=None)

        self.assertEqual(list(resp.context['evaluations']),list(evaluations))
        self.assertEqual(resp.context['selected_classroom'],None)
        self.assertEqual(list(resp.context['active_classrooms']),list(active_classrooms))

    def test_context_classroom_id_not_none(self):
        classroom_id = 1
        url = reverse('student_evaluation_report',kwargs={'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentevaluationreport.html')
        active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')

        evaluations = StudentEvaluation.objects.all().exclude(  academic_score=None,
                                                              study_score=None,
                                                              personal_score=None,
                                                              hygiene_score=None,
                                                              faith_score=None)
        selected_classroom = Classroom.objects.get(pk=classroom_id)
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))).values_list('student_id',flat=True)

        evaluations = evaluations.filter(student_id__in=enrolled_students)
        #select students who have not dropped the class, or have not dropped it yet.
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))).values_list('student_id',flat=True)
        self.assertEqual(list(resp.context['evaluations']),list(evaluations))
        self.assertEqual(resp.context['selected_classroom'],selected_classroom)
        self.assertEqual(list(resp.context['active_classrooms']),list(active_classrooms))

class StudentAchievementTestReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'academic.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_classroom_id_none(self):
        url = reverse('student_achievement_test_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentachievementtestreport.html')
        active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
        achievement_tests = Academic.objects.all().exclude(
                                                       test_grade_math=None,
                                                       test_grade_khmer=None,
                                                       )
        self.assertEqual(list(resp.context['achievement_tests']),list(achievement_tests))
        self.assertEqual(resp.context['selected_classroom'],None)
        self.assertEqual(list(resp.context['active_classrooms']),list(active_classrooms))
        self.assertEqual(resp.context['classroom_id'],None)
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)

    def test_context_classroom_id_not_none(self):
        classroom_id = 1
        url = reverse('student_achievement_test_report',kwargs={'classroom_id':classroom_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentachievementtestreport.html')
        active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
        selected_classroom = Classroom.objects.get(pk=classroom_id)

        achievement_tests = Academic.objects.all().exclude(
                                                       test_grade_math=None,
                                                       test_grade_khmer=None,
                                                       )
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))).values_list('student_id',flat=True)
        achievement_tests = achievement_tests.filter(student_id__in=enrolled_students)
        self.assertEqual(list(resp.context['achievement_tests']),list(achievement_tests))
        self.assertEqual(resp.context['selected_classroom'],selected_classroom)
        self.assertEqual(list(resp.context['active_classrooms']),list(active_classrooms))
        self.assertEqual(resp.context['classroom_id'],str(classroom_id))
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)

    def test_context_post_classroom_id_not_none(self):
        classroom_id = 1
        start_date = date.today().isoformat()
        end_date = date.today().isoformat()
        data = {
            'search_start_date':start_date,
            'search_end_date':end_date
        }
        url = reverse('student_achievement_test_report',kwargs={'classroom_id':classroom_id})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentachievementtestreport.html')
        active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
        selected_classroom = Classroom.objects.get(pk=classroom_id)
        achievement_tests = Academic.objects.all().filter(Q(test_date__gte=start_date) & Q(test_date__lte=end_date)).exclude(
                                                        test_grade_math=None,
                                                        test_grade_khmer=None,
                                                        )
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))).values_list('student_id',flat=True)
        achievement_tests = achievement_tests.filter(student_id__in=enrolled_students)
        self.assertEqual(list(resp.context['achievement_tests']),list(achievement_tests))
        self.assertEqual(resp.context['selected_classroom'],selected_classroom)
        self.assertEqual(list(resp.context['active_classrooms']),list(active_classrooms))
        self.assertEqual(resp.context['classroom_id'],str(classroom_id))
        self.assertEqual(resp.context['start_date'],start_date)
        self.assertEqual(resp.context['end_date'],end_date)

class StudentMedicalReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'exitsurveys.json','healths.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('student_medical_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentmedicalreport.html')
        enrolled_students = getEnrolledStudents()
        visits = {}
        for student in enrolled_students:
          try:
              visits[student] = len(Health.objects.all().filter(student_id=student))
          except ObjectDoesNotExist:
              pass
        self.assertEqual(list(resp.context['visits']),list(visits))

class StudenDentalSummaryReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'healths.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context_site_is_none(self):
        url = reverse('student_dental_summary_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentdentalreport.html')
        dentals= Health.objects.all().filter(appointment_type='Dental')
        unique_students = dentals.values('student_id').annotate(dcount=Count('student_id')).count()
        year = datetime.now().year-2013
        dentals_by_month_year=[]
        for x in range(year):
          dentals_by_month_year.extend([{'group_by_date':str(datetime.now().year-x)+'-'+format(i+1, '02d'),'dentals':[], 'unique':0} for i in range(12)])

        for dental in dentals:
          for dental_by_month_year in dentals_by_month_year:
              generate_to_date=datetime.strptime(dental_by_month_year['group_by_date'], '%Y-%m')
              if(generate_to_date.year==dental.appointment_date.year and generate_to_date.month==dental.appointment_date.month):
                  dental_by_month_year['dentals'].append(dental)
                  unique_students_by_month = dentals.filter(appointment_date__year=generate_to_date.year, appointment_date__month=generate_to_date.month).values('student_id').annotate(dcount=Count('student_id')).count()
                  dental_by_month_year['unique'] = unique_students_by_month
        self.assertEqual(list(resp.context['dentals_by_month_year']),list(dentals_by_month_year))
        self.assertEqual(resp.context['unique_students'],unique_students)
        self.assertEqual(resp.context['current_site'],"All Site")
        self.assertEqual(list(resp.context['sites']),list(School.objects.all()))

    def test_context_site_not_none(self):
        site_id = 1
        url = reverse('student_dental_summary_report',kwargs={'site_id':site_id})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentdentalreport.html')
        dentals= Health.objects.all().filter(appointment_type='Dental',student_id__site=site_id)
        unique_students = dentals.values('student_id').annotate(dcount=Count('student_id')).count()
        year = datetime.now().year-2013
        dentals_by_month_year=[]
        for x in range(year):
          dentals_by_month_year.extend([{'group_by_date':str(datetime.now().year-x)+'-'+format(i+1, '02d'),'dentals':[], 'unique':0} for i in range(12)])

        for dental in dentals:
          for dental_by_month_year in dentals_by_month_year:
              generate_to_date=datetime.strptime(dental_by_month_year['group_by_date'], '%Y-%m')
              if(generate_to_date.year==dental.appointment_date.year and generate_to_date.month==dental.appointment_date.month):
                  dental_by_month_year['dentals'].append(dental)
                  unique_students_by_month = dentals.filter(appointment_date__year=generate_to_date.year, appointment_date__month=generate_to_date.month).values('student_id').annotate(dcount=Count('student_id')).count()
                  dental_by_month_year['unique'] = unique_students_by_month
        self.assertEqual(list(resp.context['dentals_by_month_year']),list(dentals_by_month_year))
        self.assertEqual(resp.context['unique_students'],unique_students)
        self.assertEqual(resp.context['current_site'],School.objects.get(school_id=site_id))
        self.assertEqual(list(resp.context['sites']),list(School.objects.all()))

class StudenDentalReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'healths.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('student_dental_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentdental.html')
        dentals = Health.objects.filter(appointment_type='Dental')
        self.assertEqual(list(resp.context['dentals']),list(dentals))
        self.assertEqual(resp.context['start_date'],None)
        self.assertEqual(resp.context['end_date'],None)

    def test_context_post(self):
        start_date = date.today().isoformat()
        end_date = date.today().isoformat()
        data = {
            'start_date':start_date,
            'end_date':end_date
        }
        url = reverse('student_dental_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/studentdental.html')
        dentals = Health.objects.filter( Q( Q( Q(appointment_date__gte=start_date) & Q(appointment_date__lte=end_date) ) & Q(appointment_type='Dental')) )
        self.assertEqual(list(resp.context['dentals']),list(dentals))
        self.assertEqual(resp.context['start_date'],start_date)
        self.assertEqual(resp.context['end_date'],end_date)

class MandeSummaryReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'exitsurveys.json','classroomenrollment.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('mande_summary_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/mandesummaryreport.html')
        view_date = date.today().isoformat()
        start_view_date = date.today().isoformat()

        schools = School.objects.all()
        exit_surveys = ExitSurvey.objects.filter(exit_date__lte=start_view_date).values_list('student_id',flat=True)
        students = IntakeSurvey.objects.exclude(student_id__in=exit_surveys).filter(date__lte=view_date)

        students_by_site_grade = {}
        students_by_site_grade_plus_skill_vietnamese = {}
        students_enrolled_in_english_by_level = {}
        students_by_site= {}

        # get biggest english levle
        english_class_latest_level = Classroom.objects.filter(cohort=50).latest('classroom_number');
        english_biggest_level = int(english_class_latest_level.classroom_number.rsplit(None, 1)[-1])

        grades_level = range(1,7)
        english_level = ['Level '+str(x) for x in range(1,english_biggest_level+1)]

        # generate dict
        for school in schools:
           name = school.school_name
           students_by_site_grade[name] = {}
           students_by_site_grade_plus_skill_vietnamese[name] = {}
           students_enrolled_in_english_by_level[name] = {}
           students_by_site[name] = {'M':0,'F':0}

           for a in grades_level:
               students_by_site_grade[name][a] = {'M':0,'F':0}
               students_by_site_grade[name]['appropriate'+str(a)] = {'M':0,'F':0}

               students_by_site_grade_plus_skill_vietnamese[name][a] = {'M':0,'F':0}

           students_by_site_grade[name][70] = {'M':0,'F':0}
           students_by_site_grade[name]['total'] = {'M':0,'F':0}

           students_by_site_grade[name]['appropriate_total'] = {'M':0,'F':0}

           students_by_site_grade_plus_skill_vietnamese[name][70] = {'M':0,'F':0}
           students_by_site_grade_plus_skill_vietnamese[name]['total'] = {'M':0,'F':0}

           for a in english_level:
                students_enrolled_in_english_by_level[name][a] = {'M':0,'F':0}
           students_enrolled_in_english_by_level[name]['total'] = {'M':0,'F':0}
        for student in students:
            grade = student.current_vdp_grade(view_date)
            site = student.site
            gender = student.gender

            # total student
            students_by_site[unicode(site)][gender] +=1

            if (grade >= 1 and grade <= 6) or grade == 70:
               #    -----students_by_site_grade (catch-up school)----
               students_by_site_grade[unicode(site)][grade][gender] +=1
               students_by_site_grade[unicode(site)]['total'][gender] +=1

               if grade in grades_level:
                   #student appropriate level
                   if (student.age_appropriate_grade(view_date) - grade < 1):
                       students_by_site_grade[unicode(site)]["appropriate"+str(grade)][gender] +=1
                       students_by_site_grade[unicode(site)]["appropriate_total"][gender] +=1

                   #-------------students_by_site_grade_plus_skill_vietnamese-------------

                   enrolleds = ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(classroom_id__cohort=grade) | Q(classroom_id__cohort=70)) & Q( Q( Q(drop_date__gte=start_view_date) | Q(drop_date__gte=view_date)) | Q(drop_date=None)) &Q(enrollment_date__lte=view_date)
                        ).order_by('classroom_id__cohort')
                   if len(enrolleds)>1:
                     classroom_number = enrolleds[0].classroom_id.cohort
                     classroom_number1 = enrolleds[1].classroom_id.cohort

                     if(classroom_number in grades_level) and (classroom_number1==70):
                        students_by_site_grade_plus_skill_vietnamese[unicode(site)][grade][gender] +=1
                        students_by_site_grade_plus_skill_vietnamese[unicode(site)]['total'][gender] +=1
               else:
                #    ------------vietnamese only (catch-up school)----------------
                   students_by_site_grade_plus_skill_vietnamese[unicode(site)][grade][gender] +=1
                   students_by_site_grade_plus_skill_vietnamese[unicode(site)]['total'][gender] +=1
            # english student by level
            elif grade == 50:
                english_student = None
                enrolleds = ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(classroom_id__cohort=50) & Q( Q(Q(drop_date__gte=view_date)| Q(drop_date__gte=start_view_date)) | Q(drop_date=None) ) &Q(enrollment_date__lte=view_date)
                ).order_by('drop_date')
                if len(enrolleds) > 1:
                    if len(enrolleds.filter(drop_date=None)) != 0:
                        english_student = enrolleds.filter(drop_date=None).latest('enrollment_date')
                    else:
                        english_student = enrolleds.latest('drop_date')
                else:
                    try:
                        english_student = enrolleds[0]
                    except:
                        pass
                if english_student is not None:
                    level = english_student.classroom_id.classroom_number
                    students_enrolled_in_english_by_level[unicode(site)][level][gender] +=1
                    students_enrolled_in_english_by_level[unicode(site)]['total'][gender] +=1
        self.assertEqual(list(resp.context['schools']),list(schools))
        self.assertEqual(list(resp.context['students_by_site_grade']),list(students_by_site_grade))
        self.assertEqual(list(resp.context['students_by_site']),list(students_by_site))
        self.assertEqual(list(resp.context['students_by_site_grade_plus_skill_vietnamese']),list(students_by_site_grade_plus_skill_vietnamese))
        self.assertEqual(list(resp.context['students_enrolled_in_english_by_level']),list(students_enrolled_in_english_by_level))
        self.assertEqual(list(resp.context['grades_level']),list(grades_level))
        self.assertEqual(list(resp.context['english_level']),list(english_level))
        self.assertEqual(resp.context['view_date'],date.today().isoformat())
        self.assertEqual(resp.context['start_view_date'],date.today().isoformat())

    def test_context_view_date_not_none(self):
        view_date = date.today().isoformat()
        start_view_date = date.today().isoformat()
        url = reverse('mande_summary_report',kwargs={'view_date':view_date,'start_view_date':start_view_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/mandesummaryreport.html')
        self.assertEqual(resp.context['view_date'],view_date)
        self.assertEqual(resp.context['start_view_date'],start_view_date)

class StudentPromotedReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'academic.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('student_promoted_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/student_promoted_report.html')
        academics = Academic.objects.filter(promote = True)
        students = IntakeSurvey.objects.all().filter(date__lte=date.today().isoformat())
        schools = School.objects.all()
        promoted_years = []
        years = datetime.now().year-2012
        list_of_years = []
        # generate list of year
        for r in range(years):
          list_of_years.append(datetime.now().year-r)
        # generate list of student break down by site and year
        for school in schools:
          promoted_years.extend(
              [
                  {
                  'school':school,
                  'total':[],
                  'years':[{'year'+str(i):{'years':str(i),'students':[]}} for i in list_of_years],

                  }
              ]
          )
        for student in students:
          academics = Academic.objects.filter(student_id=student,promote=True)
          for promoted_year in promoted_years:
                  if promoted_year['school'] == student.site:
                      for each_year in  promoted_year['years']:
                          for i in range(years):
                                  try:
                                      if len(academics) != 0:
                                          for academic in academics:
                                              # get academic by school year
                                              # the 2014 school year is 1 Aug 2014 - 31 July 2015
                                              # the 2015 school year is 1 Aug 2015 - 31 July 2016
                                              if each_year['year'+str(datetime.now().year-i)]['years'] == str(academic.test_date.year) or int(each_year['year'+str(datetime.now().year-i)]['years'])+1 == academic.test_date.year:
                                                  beginning = str(each_year['year'+str(datetime.now().year-i)]['years'])+"-08-01"
                                                  end = str(int(each_year['year'+str(datetime.now().year-i)]['years'])+1)+"-07-31"

                                                  beginning_of_school_year = datetime.strptime(beginning, "%Y-%m-%d").date()
                                                  end_of_school_year = datetime.strptime(end, "%Y-%m-%d").date()

                                                  if academic.test_date >= beginning_of_school_year and academic.test_date <= end_of_school_year:
                                                      each_year['year'+str(datetime.now().year-i)]['students'].append(academic.student_id)
                                                      promoted_year['total'].append(academic.student_id)

                                  except:
                                      pass
        self.assertEqual(resp.context['promoted_years'],promoted_years)
        self.assertEqual(resp.context['list_of_years'],list_of_years)

class StudentPromotedTimesReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'exitsurveys.json','academic.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('students_promoted_times_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/students_promoted_times_report.html')
        exit_surveys = ExitSurvey.objects.filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
        students = IntakeSurvey.objects.exclude(student_id__in=exit_surveys).filter(date__lte=date.today().isoformat())

        students_promoted = {}
        for student in students:
          #if the student has a valid current grade
          if 0 < student.current_vdp_grade() < 12:
              students_promoted[student] = {
                  'promoted_times':len(Academic.objects.filter(student_id=student,promote=True)),
                  'lastest_promoted_date':Academic.objects.filter(student_id=student,promote=True).latest('test_date').test_date if len(Academic.objects.filter(student_id=student,promote=True)) > 0 else None,
                  'enrolled_date' : student.intakeinternal_set.all().filter().order_by(
                                                                      '-enrollment_date'
                                                                  )[0].enrollment_date
                                            }

        self.assertEqual(resp.context['students_promoted'],students_promoted)
        self.assertEqual(resp.context['filter_seach'],None)
        self.assertEqual(list(resp.context['sites']),list(School.objects.all()))
        self.assertEqual(resp.context['grades'],dict(GRADES))

    def test_context_filter_search_not_none(self):
        filter_seach = 'ALL'
        url = reverse('students_promoted_times_report',kwargs={'filter_seach':filter_seach})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/students_promoted_times_report.html')
        students = IntakeSurvey.objects.all().filter(date__lte=date.today().isoformat())

        students_promoted = {}
        for student in students:
          #if the student has a valid current grade
          if 0 < student.current_vdp_grade() < 12:
              students_promoted[student] = {
                  'promoted_times':len(Academic.objects.filter(student_id=student,promote=True)),
                  'lastest_promoted_date':Academic.objects.filter(student_id=student,promote=True).latest('test_date').test_date if len(Academic.objects.filter(student_id=student,promote=True)) > 0 else None,
                  'enrolled_date' : student.intakeinternal_set.all().filter().order_by(
                                                                      '-enrollment_date'
                                                                  )[0].enrollment_date
                                            }

        self.assertEqual(resp.context['students_promoted'],students_promoted)
        self.assertEqual(resp.context['filter_seach'],filter_seach)
        self.assertEqual(list(resp.context['sites']),list(School.objects.all()))
        self.assertEqual(resp.context['grades'],dict(GRADES))

class PublicSchoolReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'exitsurveys.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('public_school_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/public_school_report.html')
        students = getEnrolledStudents()
        grades = {k:v for k, v in dict(GRADES).items() if (k>0 and k<=6) or k in [50,60,70] }
        self.assertEqual(resp.context['grades'],grades)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(list(resp.context['sites']),list(School.objects.all()))

class StudentsLagSummaryViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'intakeupdates.json','academic.json','intakeinternals.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('students_lag_summary',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/students_lag_summary.html')
        enrolled_students = getEnrolledStudents()
        schools = School.objects.all()
        students_lag_by_site = []
        students_all_site ={
          'students_age_not_appropriate_grade_level':[],
          'total':[]
        }
        for school in schools:
          students_lag_by_site.extend(
              [
                  {
                  'school':school,
                  'students_age_not_appropriate_grade_level':[],
                  'all_students':[]
                  }
              ]
          )
        for student in enrolled_students:
          if student.current_vdp_grade() != 70:
              if student.current_vdp_grade() != 50:
                  # for each site
                  for student_lag_by_site in students_lag_by_site :
                      if student.site == student_lag_by_site['school']:
                          if (student.age_appropriate_grade() - student.current_vdp_grade()) > 0:
                              student_lag_by_site['students_age_not_appropriate_grade_level'].append(student)
                          student_lag_by_site['all_students'].append(student)
                  # for all site
                  if (student.age_appropriate_grade() - student.current_vdp_grade()) > 0:
                      students_all_site['students_age_not_appropriate_grade_level'].append(student)
                  students_all_site['total'].append(student)
        self.assertEqual(list(resp.context['students_lag_by_site']),list(students_lag_by_site))
        self.assertEqual(list(resp.context['students_all_site']),list(students_all_site))

class AnomalousDataViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('anomalous_data',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/anomalous_data_report.html')
        future_students = IntakeSurvey.objects.all().filter(date__gte=date.today().isoformat()).order_by('student_id')
        self.assertEqual(list(resp.context['future_students']),list(future_students))

class AdvancedReportViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'intakeupdates.json','publicschoolhistorys.json','spiritualactivities.json',
        'classroomenrollment.json','academic.json','intakeinternals.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('advanced_report',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')

        self.assertEqual(resp.context['students'],None)
        self.assertEqual(list(resp.context['schools']),list(School.objects.all()))
        self.assertEqual(resp.context['genders'],dict(GENDERS))
        self.assertEqual(resp.context['grades'],dict(GRADES))
        self.assertEqual(resp.context['relationships'],dict(RELATIONSHIPS))
        self.assertEqual(resp.context['yns'],dict(YN))
        self.assertEqual(resp.context['employments'],dict(EMPLOYMENT))
        self.assertEqual(list(resp.context['classrooms']),list(Classroom.objects.filter(active=True)))
        self.assertEqual(resp.context['show_data'],'no')

        raised = True
        try:
                json.loads(resp.context['data_guardian1_profession'])
        except:
                raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_guardian1_profession'],'["123", "456"]')

        raised = True
        try:
                json.loads(resp.context['data_guardian2_profession'])
        except:
                raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_guardian2_profession'],'["NA"]')

        raised = True
        try:
                json.loads(resp.context['data_minors_profession'])
        except:
                raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_minors_profession'],'["", "NA"]')

        raised = True
        try:
                json.loads(resp.context['data_minors_training_type'])
        except:
                raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_minors_training_type'],'["", "NA"]')

        raised = True
        try:
                json.loads(resp.context['data_reasons'])
        except:
                raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_reasons'],'["test"]')

        raised = True
        try:
                json.loads(resp.context['data_public_schools'])
        except:
                raised = False
        self.assertTrue(raised)
        self.assertEqual(resp.context['data_public_schools'],'["test"]')

        def convert_field_to_readable(string):
             s = string
             s1= re.sub(r'([^0-9])([0-9])', r'\1 \2',s)
             s2 =  re.sub(r'([$0-9])([a-z])', r'\1 \2',s1)
             s3 = s2.replace('_', ' ').title()
             return s3

        all_fields = IntakeSurvey._meta.fields
        list_of_fields = dict((field.name, convert_field_to_readable(field.name)) for field in all_fields if not field.primary_key)
        list_of_fields.update({
               "vdp_grade":"VDP Grade", "classroom": "Classroom","id":"ID",
               "enrolled":"Enrolled","grade_current":"Grade Current",
               "grade_last":"Grade Last","reasons":"Reasons",
               "public_school_name":"Public School Name"
               })
        self.assertEqual(resp.context['list_of_fields'],sorted(list_of_fields.iteritems()))

    def test_context_post(self):
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_student_id(self):
        student_id = 1
        data = {
            'studnet_id':student_id,
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains=student_id) &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_name(self):
        name = 'test'
        data = {
            'studnet_id':'',
            'name':name,
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains=name)
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_school(self):
        school = 1
        data = {
            'studnet_id':'',
            'name':'',
            'school':school,
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        q=[]
        filter_query = Q()
        q.append(Q(site=school))
        if len(q) > 0:
            filter_query = reduce(operator.and_, q)

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_intake_date(self):
        intake_date = '2015-07-01'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':intake_date,
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        q=[]
        filter_query = Q()
        q.append(Q(date=intake_date))
        if len(q) > 0:
            filter_query = reduce(operator.and_, q)

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_dob(self):
        dob = '2005-07-01'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':dob,
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        q=[]
        filter_query = Q()
        q.append(Q(dob=dob))
        if len(q) > 0:
            filter_query = reduce(operator.and_, q)

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_gender(self):
        gender = 'F'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':gender,
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        q=[]
        filter_query = Q()
        q.append(Q(gender=gender))
        if len(q) > 0:
            filter_query = reduce(operator.and_, q)

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_dob_year(self):
        dob_year = '2005'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':dob_year,
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        q=[]
        filter_query = Q()
        q.append(Q(dob__year=int(dob_year)))
        if len(q) > 0:
            filter_query = reduce(operator.and_, q)

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_intake_date_year(self):
        intake_date_year = '2015'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':intake_date_year,
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        q=[]
        filter_query = Q()
        q.append(Q(date__year=int(intake_date_year)))
        if len(q) > 0:
            filter_query = reduce(operator.and_, q)

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_address(self):
        address = '123'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':address,

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['address'] = address

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian1_name(self):
        guardian1_name = '123'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':guardian1_name,
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian1_name'] = guardian1_name

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian1_relationship(self):
        guardian1_relationship = 'FATHER'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':guardian1_relationship,
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian1_relationship'] = guardian1_relationship

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian1_phone(self):
        guardian1_phone = '123'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':guardian1_phone,
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian1_phone'] = guardian1_phone

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian1_profession(self):
        guardian1_profession = '123'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':guardian1_profession,
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian1_profession'] = guardian1_profession

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian1_employment(self):
        guardian1_employment = '1'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':guardian1_employment,

            'guardian2_name':'',
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian1_employment'] = guardian1_employment

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian2_name(self):
        guardian2_name = ''
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':guardian2_name,
            'guardian2_relationship':'',
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian2_name'] = guardian2_name

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian2_relationship(self):
        guardian2_relationship = 'MOTHER'
        data = {
            'studnet_id':'',
            'name':'',
            'school':'',
            'gender':'',
            'intake_date':'',
            'intake_date_year':'',
            'dob':'',
            'dob_year':'',
            'address':'',

            'guardian1_name':'',
            'guardian1_relationship':'',
            'guardian1_phone':'',
            'guardian1_profession':'',
            'guardian1_employment':'',

            'guardian2_name':'',
            'guardian2_relationship':guardian2_relationship,
            'guardian2_phone':'',
            'guardian2_profession':'',
            'guardian2_employment':'',

             #Household Information
            'minors':'',
            'minors_in_public_school':'',
            'minors_in_other_school':'',
            'minors_working':'',
            'minors_profession':'',
            'minors_encouraged':'',
            'minors_training':'',
            'minors_training_type':'',

            'enrolled':'',
            'grade_current':'',
            'grade_last':'',
            'public_school_name':'',
            'reasons':'',

            'classroom':'',
            'vdp_grade':'',
        }
        url = reverse('advanced_report',kwargs={})
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/advancedreport.html')
        filter_query = Q()
        recent_field_list={}
        recent_field_list['guardian2_relationship'] = guardian2_relationship

        students = IntakeSurvey.objects.filter(
                        Q(student_id__contains='') &
                        Q(name__contains='')
                        ).filter(filter_query)
        equal_value_list = ['guardian1_relationship','guardian2_relationship',
                            'guardian1_employment','guardian2_employment',
                            'minors','minors_in_public_school','minors_in_other_school',
                            'minors_working','minors_encouraged','minors_training',
                           ]
        match_intakeUpdate = []
        for key, value in recent_field_list.iteritems():
            match_intakeUpdate=[]
            for student in students:
               student_recent_data = student.getRecentFields()
               if key not in equal_value_list:
                   if value in student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
               else:
                   if value == student_recent_data[key]:
                       match_intakeUpdate.append(student.student_id)
            students = students.filter(student_id__in=match_intakeUpdate)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian2_phone(self):
       guardian2_phone = ''
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':guardian2_phone,
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['guardian2_phone'] = guardian2_phone

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian2_profession(self):
       guardian2_profession = 'NA'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':guardian2_profession,
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['guardian2_profession'] = guardian2_profession

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_guardian2_employment(self):
       guardian2_employment = '1'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':guardian2_employment,

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['guardian2_employment'] = guardian2_employment

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors(self):
       minors = '0'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':minors,
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors'] = int(minors)

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors_in_public_school(self):
       minors_in_public_school = '0'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':minors_in_public_school,
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors_in_public_school'] = int(minors_in_public_school)

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors_in_other_school(self):
       minors_in_other_school = '0'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':minors_in_other_school,
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors_in_other_school'] = int(minors_in_other_school)

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors_working(self):
       minors_working = '0'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':minors_working,
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors_working'] = int(minors_working)

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors_profession(self):
       minors_profession = ''
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':minors_profession,
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors_profession'] = minors_profession

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors_encouraged(self):
       minors_encouraged = 'NA'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':minors_encouraged,
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors_encouraged'] = minors_encouraged

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_minors_training(self):
       minors_training = 'NA'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':minors_training,
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       recent_field_list={}
       recent_field_list['minors_training'] = minors_training

       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       equal_value_list = ['guardian1_relationship','guardian2_relationship',
                           'guardian1_employment','guardian2_employment',
                           'minors','minors_in_public_school','minors_in_other_school',
                           'minors_working','minors_encouraged','minors_training',
                          ]
       match_intakeUpdate = []
       for key, value in recent_field_list.iteritems():
           match_intakeUpdate=[]
           for student in students:
              student_recent_data = student.getRecentFields()
              if key not in equal_value_list:
                  if value in student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
              else:
                  if value == student_recent_data[key]:
                      match_intakeUpdate.append(student.student_id)
           students = students.filter(student_id__in=match_intakeUpdate)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_classroom(self):
       classroom = 1
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':classroom,
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)
       students = students.filter(Q(classroomenrollment__classroom_id=classroom) & Q(Q(classroomenrollment__drop_date__gte=date.today().isoformat()) | Q(classroomenrollment__drop_date=None)))
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_vdp_grade(self):
       vdp_grade = 1
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':'',
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',
           'reasons':'',

           'classroom':'',
           'vdp_grade':vdp_grade,
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_vdp_grade = []
       for student in students:
           if(student.current_vdp_grade() == int(vdp_grade)):
               student_filter_by_vdp_grade.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_vdp_grade)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_grade_current_none(self):
       enrolled = 'Y'
       grade_current = ''
       public_school_name = ''
       reasons = ''
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':grade_current,
           'grade_last':'',
           'public_school_name':public_school_name,
           'reasons':reasons,

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
            pschool = student.get_pschool()
            if(pschool.status == enrolled):
                student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_grade_current_and_public_school_name(self):
       enrolled = 'Y'
       grade_current = '2'
       public_school_name = 'test'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':grade_current,
           'grade_last':'',
           'public_school_name':public_school_name,
           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
            pschool = student.get_pschool()
            if pschool.status == enrolled and pschool.grade == int(grade_current) and re.search(public_school_name,pschool.school_name, re.IGNORECASE):
                student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_grade_current(self):
       enrolled = 'Y'
       grade_current = '2'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':grade_current,
           'grade_last':'',
           'public_school_name':'',

           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
          pschool = student.get_pschool()
          if pschool.status == enrolled and pschool.grade == int(grade_current):
              student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_public_school_name(self):
       enrolled = 'Y'
       public_school_name = 'test'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':'',
           'grade_last':'',
           'public_school_name':public_school_name,

           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
            pschool = student.get_pschool()
            if pschool.status == enrolled and re.search(public_school_name,pschool.school_name, re.IGNORECASE):
                student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_no_grade_last_and_reason(self):
       enrolled = 'N'
       grade_last = '1'
       reasons = 'test'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':'',
           'grade_last':grade_last,
           'public_school_name':'',

           'reasons':reasons,

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
          pschool = student.get_pschool()
          if pschool.status == enrolled and pschool.last_grade == int(grade_last) and re.search(reasons,pschool.reasons, re.IGNORECASE):
              student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_no_grade_last(self):
       enrolled = 'N'
       grade_last = '1'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':'',
           'grade_last':grade_last,
           'public_school_name':'',

           'reasons':'',

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
           pschool = student.get_pschool()
           if pschool.status == enrolled and pschool.last_grade == int(grade_last):
               student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

    def test_context_post_enrolled_no_reason(self):
       enrolled = 'N'
       reasons = 'test'
       data = {
           'studnet_id':'',
           'name':'',
           'school':'',
           'gender':'',
           'intake_date':'',
           'intake_date_year':'',
           'dob':'',
           'dob_year':'',
           'address':'',

           'guardian1_name':'',
           'guardian1_relationship':'',
           'guardian1_phone':'',
           'guardian1_profession':'',
           'guardian1_employment':'',

           'guardian2_name':'',
           'guardian2_relationship':'',
           'guardian2_phone':'',
           'guardian2_profession':'',
           'guardian2_employment':'',

            #Household Information
           'minors':'',
           'minors_in_public_school':'',
           'minors_in_other_school':'',
           'minors_working':'',
           'minors_profession':'',
           'minors_encouraged':'',
           'minors_training':'',
           'minors_training_type':'',

           'enrolled':enrolled,
           'grade_current':'',
           'grade_last':'',
           'public_school_name':'',

           'reasons':reasons,

           'classroom':'',
           'vdp_grade':'',
       }
       url = reverse('advanced_report',kwargs={})
       resp = self.client.post(url,data)
       self.assertEqual(resp.status_code, 200)
       self.assertTemplateUsed(resp,'mande/advancedreport.html')
       filter_query = Q()
       students = IntakeSurvey.objects.filter(
                       Q(student_id__contains='') &
                       Q(name__contains='')
                       ).filter(filter_query)

       student_filter_by_enrolled = []
       for student in students:
          pschool = student.get_pschool()
          if pschool.status == enrolled and re.search(reasons,pschool.reasons, re.IGNORECASE):
              student_filter_by_enrolled.append(student.student_id)
       students = students.filter(student_id__in=student_filter_by_enrolled)
       self.assertEqual(list(resp.context['students']),list(students))
       self.assertEqual(resp.context['show_data'],'yes')

class UnapprovedAbsenceWithNoCommentViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'attendances.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('unapproved_absence_with_no_comment',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/unapproved_absence_with_no_comment.html')
        thisyear = date.today().year
        school_year_list = [thisyear-i for i in range(thisyear-2013)]
        unapproved_absence_no_comments = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(Q(notes=u"") |Q(notes=None))).order_by('-date')

        self.assertEqual(list(resp.context['unapproved_absence_no_comments']),list(unapproved_absence_no_comments))
        self.assertEqual(resp.context['school_year_list'],school_year_list)
        self.assertEqual(resp.context['school_year'],None)

    def test_context_school_year_not_none(self):
        school_year = 2015
        url = reverse('unapproved_absence_with_no_comment',kwargs={'school_year':school_year})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/unapproved_absence_with_no_comment.html')
        thisyear = date.today().year
        school_year_list = [thisyear-i for i in range(thisyear-2013)]

        school_year_start_date = str(school_year)+"-08-01"
        school_year_end_date = str(int(school_year)+1)+"-07-31"
        unapproved_absence_no_comments = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(Q(notes=u"") |Q(notes=None)) & Q(Q(date__gte=school_year_start_date) & Q(date__lte=school_year_end_date))).order_by('-date')

        self.assertEqual(list(resp.context['unapproved_absence_no_comments']),list(unapproved_absence_no_comments))
        self.assertEqual(resp.context['school_year_list'],school_year_list)
        self.assertEqual(resp.context['school_year'],str(school_year))

class GenerateViewTestCase(TestCase):
    fixtures = [
        'users.json','schools.json','classrooms.json','intakesurveys.json',
        'exitsurveys.json','intakeupdates.json','currentstudentInfos.json'
    ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        IntakeSurvey.objects.create(
            date=date.today().isoformat(),
            site=School.objects.get(pk=1),
            name='test',dob='2013-01-01'
            )
        self.assertEqual(CurrentStudentInfo.objects.all().count(),9)

        url = reverse('generate',kwargs={})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/generatestudentinfo.html')
        exit_surveys = ExitSurvey.objects.all().filter(
                         exit_date__lte=date.today().isoformat()
                         ).values_list('student_id',flat=True)
        active_surveys = IntakeSurvey.objects.filter(date__lte=date.today().isoformat()).order_by('student_id'
                                  ).exclude(student_id__in=exit_surveys)
        for survey in active_surveys:
            recent_survey = survey.getRecentFields()
            self.assertTrue(
                CurrentStudentInfo.objects.filter(
                student_id=recent_survey['student_id'], name=recent_survey['name'],site=recent_survey['site'],
                date=recent_survey['date'],dob = recent_survey['dob'],gender = recent_survey['gender'],
                age_appropriate_grade = survey.age_appropriate_grade(),
                in_public_school = True if survey.get_pschool().status=='Y' else False,
                at_grade_level = studentAtAgeAppropriateGradeLevel(recent_survey['student_id']),
                vdp_grade = survey.current_vdp_grade(),
                refresh = date.today().isoformat()
                ).exists()
            )
        self.assertEqual(resp.context['students'],active_surveys.count())
        self.assertEqual(CurrentStudentInfo.objects.all().count(),10)
