from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.forms.models import modelformset_factory
from django.db.models import Q,Sum,Count
from django.forms.models import model_to_dict

from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import json

from calendar import HTMLCalendar, monthrange
from datetime import date
from datetime import datetime
from datetime import timedelta
from django.views.generic import ListView
from mande.models import IntakeSurvey
from mande.models import IntakeUpdate
from mande.models import Classroom
from mande.models import Teacher
from mande.models import ClassroomEnrollment
from mande.models import ClassroomTeacher
from mande.models import Attendance
from mande.models import ExitSurvey
from mande.models import PostExitSurvey
from mande.models import SpiritualActivitiesSurvey
from mande.models import AttendanceDayOffering
from mande.models import School
from mande.models import Academic
from mande.models import NotificationLog
from mande.models import Health
from mande.models import AttendanceLog
from mande.models import IntakeInternal
from mande.models import StudentEvaluation
from mande.models import PublicSchoolHistory
from mande.models import CurrentStudentInfo

from mande.models import GRADES
from mande.models import GENDERS
from mande.models import ATTENDANCE_CODES
from mande.models import RELATIONSHIPS
from mande.models import YN
from mande.models import EMPLOYMENT

from mande.forms import IntakeSurveyForm
from mande.forms import IntakeUpdateForm
from mande.forms import ExitSurveyForm
from mande.forms import PostExitSurveyForm
from mande.forms import SpiritualActivitiesSurveyForm
from mande.forms import DisciplineForm
from mande.forms import TeacherForm
from mande.forms import ClassroomForm
from mande.forms import ClassroomTeacherForm
from mande.forms import ClassroomEnrollmentForm
from mande.forms import IndividualClassroomEnrollmentForm
from mande.forms import AttendanceForm
from mande.forms import AcademicForm
from mande.forms import IntakeInternalForm
from mande.forms import HealthForm

from mande.utils import getEnrolledStudents
from mande.utils import getStudentGradebyID
from mande.utils import studentAtSchoolGradeLevel
from mande.utils import studentAtAgeAppropriateGradeLevel
from mande.utils import getStudentAgeAppropriateGradeLevel

from django.contrib.auth.models import User
from django.core.cache import cache
from mande.utils import user_permissions

import inspect
import operator
import re
from icu import Locale, Collator

TOO_YOUNG = 4
TOO_OLD = 25
'''
*****************************************************************************
Daily Attendance Report
 - lists all classrooms who take attendance and their attendance status
*****************************************************************************
'''
def daily_attendance_report(request,attendance_date=date.today().isoformat()):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      #only classrooms who take attendance, and who take attendance today.
      classrooms = Classroom.objects.all().filter(active=True)
      classrooms_who_take_attendance = []
      for classroom in classrooms:
          if classroom.getAttendanceDayOfferings(attendance_date):
              classrooms_who_take_attendance.append(classroom)

    #   takesattendance = AttendanceDayOffering.objects.filter(
    #                                                     date=attendance_date
    #                                               ).values_list(
    #                                                    'classroom_id',flat=True)
    #   classrooms = classrooms.filter(classroom_id__in=takesattendance)

      classroomattendance = {}
      for classroom in classrooms_who_take_attendance:
        try:
            classroomattendance[classroom] = AttendanceLog.objects.get(
                                                           classroom=classroom,
                                                           date=attendance_date)
        except ObjectDoesNotExist:
            classroomattendance[classroom] = None

      return render(request, 'mande/attendancereport.html',
                            {'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date
                                                                        })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Student Attendance Detail Report
 - list attendance detail of student
*****************************************************************************
'''
def student_attendance_detail(request,student_id=None,start_date=None,end_date=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        if request.method == 'POST':
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            attendances = Attendance.objects.all().filter(Q(student_id=student_id) & Q(Q(date__gte=start_date) & Q(date__lte=end_date))).order_by('-date')
        else:
            attendances = Attendance.objects.all().filter(student_id=student_id).order_by('-date')
        return render(request, 'mande/student_attendance_detail.html',
                            {
                                'attendances' : attendances,
                                'student_id' : student_id,
                                'start_date' : start_date,
                                'end_date' : end_date
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Attendance Summary
 - lists attendance summary for student
*****************************************************************************
'''
def attendance_summary_report(request,start_date=None,end_date=None,id=None,select_type=None):
 #get current method name
 method_name = inspect.currentframe().f_code.co_name
 if user_permissions(method_name,request.user):

      exit_surveys = ExitSurvey.objects.filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
      students = IntakeSurvey.objects.exclude(student_id__in=exit_surveys).filter(date__lte=date.today().isoformat())

      schools = School.objects.all()
      classrooms = Classroom.objects.all()
      current_selected = None
      studentattendance = {}

      #filter student by site
      if id != None and select_type == 'site':
        #select students who have not dropped the class, or have not dropped it yet. by site
        students = ClassroomEnrollment.objects.all().filter(Q(classroom_id__school_id=id) & Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)))
        current_selected =  School.objects.get(school_id=id)
      #filter by classroom
      elif id != None and select_type == 'classroom':
        #select students who have not dropped the class, or have not dropped it yet. by classroom
        students = ClassroomEnrollment.objects.all().filter(Q(classroom_id__classroom_id=id) & Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)))
        current_selected =  Classroom.objects.get(classroom_id=id)

      if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        for stu in students:
            if id != None:
                student = stu.student_id
            else:
                student = stu
            try:
                studentattendance[student] = {
                    'classroom' : ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(drop_date=None) | Q(drop_date__gte=date.today().isoformat()))),
                    'present' : Attendance.objects.filter(student_id=student,attendance='P',date__gte=start_date,date__lte=end_date).count(),
                    'unapproved' : Attendance.objects.filter(student_id=student,attendance='UA',date__gte=start_date,date__lte=end_date).count(),
                    'approved' : Attendance.objects.filter(student_id=student,attendance='AA',date__gte=start_date,date__lte=end_date).count(),
                    'total' : Attendance.objects.filter(student_id=student,attendance='P',date__gte=start_date,date__lte=end_date).count()
                            +Attendance.objects.filter(student_id=student,attendance='UA',date__gte=start_date,date__lte=end_date).count()
                            +Attendance.objects.filter(student_id=student,attendance='AA',date__gte=start_date,date__lte=end_date).count(),
                     }
            except ObjectDoesNotExist:
               studentattendance[student] = None
      else:
        for stu in students:
            if id != None:
                student = stu.student_id
            else:
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

      return render(request, 'mande/attendance_summary_report.html',
                            {'studentattendance' : studentattendance,
                            'start_date' : start_date,
                            'end_date' : end_date,
                            'schools' : schools,
                            'classrooms' : classrooms,
                            'current_selected' : current_selected,
                            'select_type' : select_type,
                            'id' : id
                                                                        })
 else:
     raise PermissionDenied


'''
*****************************************************************************
Daily Absence Report
 - lists all students with unexcuses absences for the day and their contact info
*****************************************************************************
'''
def daily_absence_report(request,attendance_date=date.today().isoformat(),attendance_end_date=date.today().isoformat()):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        site = None
        classroom_id = None

        current_site = None
        current_classroom = None
        schools = School.objects.all()
        classroom_list = Classroom.objects.filter(active=True)

        if request.method == 'POST':
          classroom_id = request.POST['classroom']
          site = request.POST['site']
          attendance_date = request.POST['attendance_date']
          attendance_end_date = request.POST['attendance_end_date']

        #only classrooms who take attendance, and who take attendance today.
        classrooms = Classroom.objects.all().filter(active=True)
        takesattendance = AttendanceDayOffering.objects.filter(
                                                               Q(date__gte=attendance_date) & Q(date__lte=attendance_end_date)
                                                         ).values_list('classroom_id',flat=True)
        # filter by site, classroom
        if (site=='None' or site==None) and (classroom_id=='None' or classroom_id==None):
            classrooms = classrooms.filter(classroom_id__in=takesattendance)
        else:
              if site != 'None' and site != None:
                classrooms = classrooms.filter(classroom_id__in=takesattendance,school_id=site)
                current_site = School.objects.get(school_id=site)
              elif classroom_id != 'None' and classroom_id != None:
                classrooms = classrooms.filter(classroom_id__in=takesattendance,classroom_id=classroom_id)
                current_classroom = Classroom.objects.get(classroom_id=classroom_id)
              else:
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
        return render(request, 'mande/absencereport.html',
                            {
                             'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date,
                             'attendance_end_date':attendance_end_date,
                             'schools' : schools,
                             'classroom_list' : classroom_list,
                             'current_site' : current_site,
                             'current_classroom':current_classroom
                                                                        })
    else:
      raise PermissionDenied
'''
*****************************************************************************
Data Audit
 - Generate a list of student records with missing or anomalous data
*****************************************************************************
'''
def data_audit(request,audit_type='ALL'):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      #modelfields = model_to_dict(IntakeSurvey.objects.all()[0])

      students = getEnrolledStudents()
      filters = []

      #a
      anomalies = {}

      for student in students:
        '''students with missing information'''
        text = 'Missing '
        resolution = reverse('intake_update',kwargs={'student_id':student.student_id})

        student_data = student.getRecentFields()

        '''students who are quite young or quite old'''
        if (student.dob.year > (datetime.now().year-TOO_YOUNG)) or (student.dob.year<datetime.now().year-TOO_OLD):
            text = 'Incorrect DOB'
            age = '(~'+unicode(datetime.now().year-student.dob.year)+' years old)'
            resolution = reverse('intake_survey',kwargs={'student_id':student.student_id})
            limit = 'dob'

            addAnomaly(anomalies, student, text+age, resolution, limit)
            filters.append(text)
        '''students who have never been present'''
        if Attendance.objects.filter(student_id=student,attendance='P').count()==0:

            '''are either not enrolled'''
            if len(ClassroomEnrollment.objects.filter(student_id=student))==0:
                text = 'Not enrolled in any classes'
                resolution = reverse('classroomenrollment_form')
                addAnomaly(anomalies, student, text, resolution)
                filters.append(text)

            '''... or just not good at showing up!'''
            if Attendance.objects.filter(student_id=student).count()>0:
                text = 'Has never attended class'
                resolution = reverse('student_detail',kwargs={'student_id':student.student_id})
                addAnomaly(anomalies, student, text, resolution)
                filters.append(text)
        '''student no public school history'''
        if PublicSchoolHistory.objects.filter(student_id=student).count()==0:
            text = 'No Public School History'
            resolution = reverse('student_detail',kwargs={'student_id':student.student_id})
            addAnomaly(anomalies, student, text, resolution)
            filters.append(text)
      ''' students who have unapproved absences with no comment, and get only current school year'''
      today = date.today()
    #   today = datetime.strptime("2014-08-01", "%Y-%m-%d").date()
      if (today < datetime.strptime(str(today.year)+"-08-01", "%Y-%m-%d").date()):
           school_year = today.year - 1
      else:
           school_year = today.year
      print "school_year:" + str(school_year)
      school_year_start_date = str(school_year)+"-08-01"
      school_year_end_date = str(school_year+1)+"-07-31"

      uastudents = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(Q(notes=u"") |Q(notes=None)) & Q(Q(date__gte=school_year_start_date) & Q(date__lte=school_year_end_date))).order_by('-date')

      for uastudent in uastudents:
        text = 'Unapproved absence with no comment'
        attendance_date = uastudent.date

        attendance_class = uastudent.classroom
        ''' historical data has null classroom. need to determine how to resolve '''
        if attendance_class is None:
          resolution = ''
          text = 'Unapproved abscence with no comment - missing class id'
        if attendance_class is not None:
          resolution = reverse('take_class_attendance',kwargs={'attendance_date':attendance_date.strftime('%Y-%m-%d'), 'classroom_id':attendance_class.classroom_id})
        addAnomaly(anomalies, uastudent.student_id, text, resolution)
        filters.append(text)

      #remove duplicates in a now long array
      filters = set(filters)
      filters = sorted(filters)
      return render(request, 'mande/data_audit.html',
                            {'students' : anomalies,'filters':filters})
    else:
      raise PermissionDenied


def addAnomaly(anomalies, student, text, resolution, limit=None):
    try:
        anomalies[student].append(
                            {'text':text,
                             'resolution':resolution,
                            'limit':limit})
    except KeyError:
        anomalies[student] = [{'text':text,
                               'resolution':resolution,
                               'limit':limit}]
    return anomalies

'''
*****************************************************************************
Class List
 - Generate a summary for each class in each site:
    + VDP Campus
    + Class Name
    + Teacher
    + # of Students Enrolled
*****************************************************************************
'''
def class_list(request,site='ALL'):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
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


      return render(request, 'mande/class_list.html',
                            {'class_list' : class_list,})
    else:
      raise PermissionDenied

'''
*****************************************************************************
Exit Surveys list
 -filter exit Surveys by date range
*****************************************************************************
'''
def exit_surveys_list(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      if request.method == 'POST':
        from_exit_date = request.POST['from_exit_date']
        to_exit_date = request.POST['to_exit_date']
        exit_surveys = ExitSurvey.objects.all().filter(exit_date__gte=from_exit_date , exit_date__lte=to_exit_date)
      else:
        #get today date and subtract two months
        from_exit_date=(datetime.now()- timedelta(days=2 * 365/12)).strftime("%Y-%m-%d")
        to_exit_date=(datetime.now()).strftime("%Y-%m-%d")
        exit_surveys = ExitSurvey.objects.all().filter(exit_date__gte=from_exit_date , exit_date__lte=to_exit_date)

      post_exit_surveys = PostExitSurvey.objects.all()
      return render(request, 'mande/exitsurveylist.html',
                            {'exit_surveys':exit_surveys,'post_exit_surveys':post_exit_surveys,'from_exit_date':from_exit_date,'to_exit_date':to_exit_date})
    else:
      raise PermissionDenied
'''
*****************************************************************************
Student Absence Report
 - makes a summary of all students and lists their daily absences/presence
*****************************************************************************
'''
def student_absence_report(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
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

      return render(request, 'mande/student_absence_report.html',
                                {'attendance_by_sid':attendance_by_sid, 'attendancecodes':attendancecodes})
    else:
      raise PermissionDenied
'''
*****************************************************************************
Student Lag Report
 - makes a summary of all students and lists their daily absences/presence
*****************************************************************************
'''
def student_lag_report(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      enrolled_students = getEnrolledStudents()
      students_lag = {}

      if request.method == 'POST':
        view_date = request.POST['view_date']
      else:
        # convert to correct format with html input type date
        view_date = date.today().strftime("%Y-%m-%d")

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

      return render(request, 'mande/student_lag_report.html',
                                {'students_lag':students_lag,'view_date':view_date})
    else:
      raise PermissionDenied


'''
*****************************************************************************
Student Evaluation Report
 - lists all student evaluations
*****************************************************************************
'''
def student_evaluation_report(request,classroom_id=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
      start_date = None
      end_date = None
      if request.method == 'POST':
        start_date = request.POST['search_start_date']
        end_date = request.POST['search_end_date']
        evaluations = StudentEvaluation.objects.all().filter(
                                    Q(date__gte=start_date) & Q(date__lte=end_date)
                                ).exclude(
                                    academic_score=None,
                                    study_score=None,
                                    personal_score=None,
                                    hygiene_score=None,
                                    faith_score=None
                                )
      else:
        evaluations = StudentEvaluation.objects.all().exclude(academic_score=None,
                                                              study_score=None,
                                                              personal_score=None,
                                                              hygiene_score=None,
                                                              faith_score=None)
      if classroom_id is not None:
        selected_classroom = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))).values_list('student_id',flat=True)

        
        evaluations = evaluations.filter(student_id__in=enrolled_students)
      else:
        selected_classroom = None
      return render(request,
                    'mande/studentevaluationreport.html',
                    {
                        'evaluations':evaluations,
                        'selected_classroom':selected_classroom,
                        'active_classrooms':active_classrooms,
                        'classroom_id':classroom_id,
                        'start_date':start_date,
                        'end_date':end_date,
                    })
    else:
      raise PermissionDenied
'''
*****************************************************************************
Student Achievement Report
 - lists all student Achievement test
*****************************************************************************
'''
def student_achievement_test_report(request,classroom_id=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
      start_date = None
      end_date = None
      if request.method == 'POST':
        start_date = request.POST['search_start_date']
        end_date = request.POST['search_end_date']
        achievement_tests = Academic.objects.all().filter(Q(test_date__gte=start_date) & Q(test_date__lte=end_date)).exclude(
                                                        test_grade_math=None,
                                                        test_grade_khmer=None,
                                                        )
      else:
          achievement_tests = Academic.objects.all().exclude(
                                                            test_grade_math=None,
                                                            test_grade_khmer=None,
                                                            )
      if classroom_id is not None:
        selected_classroom = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(Q(student_id__date__lte=date.today().isoformat()) & Q(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))).values_list('student_id',flat=True)

        achievement_tests = achievement_tests.filter(student_id__in=enrolled_students)
      else:
        selected_classroom = None
      return render(request, 'mande/studentachievementtestreport.html',
                                {
                                    'achievement_tests':achievement_tests,
                                    'selected_classroom':selected_classroom,
                                    'active_classrooms':active_classrooms,
                                    'classroom_id':classroom_id,
                                    'start_date':start_date,
                                    'end_date':end_date
                                })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Student Medical Report
 - lists all student medical visits
*****************************************************************************
'''
def student_medical_report(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      enrolled_students = getEnrolledStudents()
      visits = {}
      for student in enrolled_students:
        try:
            visits[student] = len(Health.objects.all().filter(student_id=student))
        except ObjectDoesNotExist:
            pass
      return render(request, 'mande/studentmedicalreport.html',
                                {'visits':visits})
    else:
      raise PermissionDenied

'''
*****************************************************************************
Student Dental Summary Report
 - lists all student Dental visits
*****************************************************************************
'''
def student_dental_summary_report(request,site_id=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      if site_id is not None:
        dentals= Health.objects.all().filter(appointment_type='Dental',student_id__site=site_id)
        current_site =  School.objects.get(school_id=site_id)
      else:
        current_site = 'All Site'
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

      sites = School.objects.all()
      return render(request, 'mande/studentdentalreport.html',
                            {
                                'dentals_by_month_year':dentals_by_month_year,
                                'sites':sites,
                                'current_site':current_site,
                                'unique_students':unique_students
                            })
    else:
      raise PermissionDenied
'''
*****************************************************************************
Student Dental Report
 - lists all student Dental visits
*****************************************************************************
'''
def student_dental_report(request,start_date=None,end_date=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        if request.method == 'POST':
          start_date = request.POST['start_date']
          end_date = request.POST['end_date']
          dentals = Health.objects.filter( Q( Q( Q(appointment_date__gte=start_date) & Q(appointment_date__lte=end_date) ) & Q(appointment_type='Dental')) )
        else:
          dentals = Health.objects.filter(appointment_type='Dental')

        return render(request, 'mande/studentdental.html',
                            {
                                'dentals':dentals,
                                'start_date':start_date,
                                'end_date' : end_date
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
M&E summary Report
 -
*****************************************************************************
'''
def mande_summary_report(request,start_view_date=date.today().isoformat(),view_date=date.today().isoformat()):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        # Catch-up school report
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
        # generate_list of students group by site and grade

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

        return render(request, 'mande/mandesummaryreport.html',
                                {
                                    'view_date':view_date,
                                    'start_view_date':start_view_date,
                                    'schools':schools,
                                    'students_by_site_grade' : students_by_site_grade,
                                    'students_by_site' : students_by_site,
                                    'students_by_site_grade_plus_skill_vietnamese':students_by_site_grade_plus_skill_vietnamese,
                                    'students_enrolled_in_english_by_level':students_enrolled_in_english_by_level,
                                    'grades_level':grades_level,
                                    'english_level':english_level
                                })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Student Promoted Report
 - lists all student Promoted
*****************************************************************************
'''

def student_promoted_report(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
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
      return render(request, 'mande/student_promoted_report.html',
                            {
                                'promoted_years':promoted_years,
                                'list_of_years':list_of_years
                            })
    else:
      raise PermissionDenied


'''
*****************************************************************************
Students Promoted Times Report
 - lists all number of times student has been promoted
*****************************************************************************
'''
def students_promoted_times_report(request,filter_seach=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      sites = School.objects.all()

      #  get all student include student in ExitSurvey
      if filter_seach is not None:
        students = IntakeSurvey.objects.all().filter(date__lte=date.today().isoformat())
      else:
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
      return render(request, 'mande/students_promoted_times_report.html',
                            {
                                'students_promoted':students_promoted,
                                'filter_seach':filter_seach,
                                'sites':sites,
                                'grades':dict(GRADES)
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Students not enrolled in public school Report
 - lists all students not enrolled in public school
*****************************************************************************
'''
def public_school_report(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      students = getEnrolledStudents()
      grades = {k:v for k, v in dict(GRADES).items() if (k>0 and k<=6) or k in [50,60,70] }
      return render(request, 'mande/public_school_report.html',
                            {
                                'students' : students,
                                'grades' : grades,
                                'sites' : School.objects.all()
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Students intergrated in public school Report
 - lists all students intergrated in public school
*****************************************************************************
'''
def students_intergrated_in_public_school(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      students = IntakeSurvey.objects.all().filter(date__lte=date.today().isoformat())
      intergrated_students = []
      for student in students:
        if student.enrolled == 'N' :
            if student.getRecentFields()['enrolled'] == 'Y':
                intergrated_students.append(student)
      return render(request, 'mande/students_intergrated_in_public_school_report.html',
                            {
                                'intergrated_students' : intergrated_students
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Students Lag Summary Report
 - Summary of student Lag
*****************************************************************************
'''
def students_lag_summary(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
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


      return render(request, 'mande/students_lag_summary.html',
                            {
                                'students_lag_by_site' : students_lag_by_site,
                                'students_all_site' : students_all_site
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Anamolous data report
 - get students have intake survey date in future
*****************************************************************************
'''
def anomalous_data(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      future_students = IntakeSurvey.objects.all().filter(date__gte=date.today().isoformat()).order_by('student_id')

      return render(request, 'mande/anomalous_data_report.html',
                            {
                                'future_students' : future_students,
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
advance report
 - advance report
*****************************************************************************
'''

def advanced_report(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      all_intake_survey = IntakeSurvey.objects.all()
      all_intake_updated = IntakeUpdate.objects.all()

      data_guardian1_profession = list(all_intake_survey.values_list('guardian1_profession',flat=True).distinct())
      guardian1_profession_intake_update = list(all_intake_updated.values_list('guardian1_profession',flat=True).distinct())
      data_guardian1_profession.extend(guardian1_profession_intake_update)

      data_guardian2_profession = list(all_intake_survey.values_list('guardian2_profession',flat=True).distinct())
      guardian2_profession_intake_update = list(all_intake_updated.values_list('guardian2_profession',flat=True).distinct())
      data_guardian2_profession.extend(guardian2_profession_intake_update)

      data_minors_profession = list(all_intake_survey.values_list('minors_profession',flat=True).distinct())
      minors_profession_intake_update = list(all_intake_updated.values_list('minors_profession',flat=True).distinct())
      data_minors_profession.extend(minors_profession_intake_update)

      data_minors_training_type = list(all_intake_survey.values_list('minors_training_type',flat=True).distinct())
      minors_training_type_intake_update = list(all_intake_updated.values_list('minors_training_type',flat=True).distinct())
      data_minors_training_type.extend(minors_training_type_intake_update)

      data_reasons = list(PublicSchoolHistory.objects.all().values_list('reasons',flat=True).distinct())

      data_public_schools = list(PublicSchoolHistory.objects.all().values_list('school_name',flat=True).distinct())
      # sort khmer
      data_public_schools = [x.encode('utf-8').strip() for x in data_public_schools]
      locale = Locale('km_KH')
      collator = Collator.createInstance(locale)
      data_public_schools = sorted(set(data_public_schools),key=collator.getSortKey)

      q=[]
      filter_query = Q()
      recent_field_list={}
      show_data = 'no'
      students = None

      schools = School.objects.all()
      classrooms = Classroom.objects.filter(active=True)
      genders = dict(GENDERS)
      grades = dict(GRADES)
      yns = dict(YN)
      employments = dict(EMPLOYMENT)
      relationships = dict(RELATIONSHIPS)

      #   ------------------
      #   convert object fields to human readable
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
      if request.method == 'POST':

         student_id = request.POST['studnet_id']
         name = request.POST['name']
         school = request.POST['school']
         gender = request.POST['gender']
         intake_date = request.POST['intake_date']
         intake_date_year = request.POST['intake_date_year']
         dob = request.POST['dob']
         dob_year = request.POST['dob_year']

         address = request.POST['address']

         guardian1_name = request.POST['guardian1_name']
     	 guardian1_relationship = request.POST['guardian1_relationship']
     	 guardian1_phone = request.POST['guardian1_phone']
     	 guardian1_profession = request.POST['guardian1_profession']
     	 guardian1_employment = request.POST['guardian1_employment']

         guardian2_name = request.POST['guardian2_name']
     	 guardian2_relationship = request.POST['guardian2_relationship']
     	 guardian2_phone = request.POST['guardian2_phone']
     	 guardian2_profession = request.POST['guardian2_profession']
     	 guardian2_employment = request.POST['guardian2_employment']

          #Household Information
      	 minors = request.POST['minors']
      	 minors_in_public_school = request.POST['minors_in_public_school']
      	 minors_in_other_school = request.POST['minors_in_other_school']
      	 minors_working = request.POST['minors_working']
      	 minors_profession = request.POST['minors_profession']
      	 minors_encouraged = request.POST['minors_encouraged']
      	 minors_training = request.POST['minors_training']
      	 minors_training_type = request.POST['minors_training_type']

         enrolled = request.POST['enrolled']
         grade_current = request.POST['grade_current']
         grade_last = request.POST['grade_last']
         public_school_name = request.POST['public_school_name']
         reasons = request.POST['reasons']

         classroom = request.POST['classroom']
         vdp_grade = request.POST['vdp_grade']

        #  ----field that don't have in intakeupdate----
         if school != '':
             q.append(Q(site=school))
         if intake_date != '':
             q.append(Q(date=intake_date))
         if dob != '':
            q.append(Q(dob=dob))
         if gender != '':
             q.append(Q(gender=gender))
         if dob_year != '':
             q.append(Q(dob__year=int(dob_year)))
         if intake_date_year != '':
             q.append(Q(date__year=int(intake_date_year)))
         if len(q) > 0:
             filter_query = reduce(operator.and_, q)

         students = IntakeSurvey.objects.filter(
                     Q(student_id__contains=student_id) &
                     Q(name__contains=name)
                     ).filter(filter_query)
         #  ----------------------------------------


         # ----- for field that has in intakeupdate -----
         if address != '':
             recent_field_list['address'] = address

         #  guardian 1
         if guardian1_name != '':
             recent_field_list['guardian1_name'] = guardian1_name
         if guardian1_relationship != '':
             recent_field_list['guardian1_relationship'] = guardian1_relationship
         if guardian1_phone != '':
             recent_field_list['guardian1_phone'] = guardian1_phone
         if guardian1_profession != '':
             recent_field_list['guardian1_profession'] = guardian1_profession
         if guardian1_employment != '':
             recent_field_list['guardian1_employment'] = guardian1_employment

        #  guardian 2
         if guardian2_name != '':
             recent_field_list['guardian2_name'] = guardian2_name
         if guardian2_relationship != '':
             recent_field_list['guardian2_relationship'] = guardian2_relationship
         if guardian2_phone != '':
             recent_field_list['guardian2_phone'] = guardian2_phone
         if guardian2_profession != '':
             recent_field_list['guardian2_profession'] = guardian2_profession
         if guardian2_employment != '':
             recent_field_list['guardian2_employment'] = guardian2_employment

        # minors
         if minors != '':
            recent_field_list['minors'] = int(minors)
         if minors_in_public_school != '':
            recent_field_list['minors_in_public_school'] = int(minors_in_public_school)
         if minors_in_other_school != '':
            recent_field_list['minors_in_other_school'] = int(minors_in_other_school)
         if minors_working != '':
            recent_field_list['minors_working'] = int(minors_working)
         if minors_profession != '':
            recent_field_list['minors_profession'] = minors_profession
         if minors_encouraged != '':
            recent_field_list['minors_encouraged'] = minors_encouraged
         if minors_training != '':
            recent_field_list['minors_training'] = minors_training
         if minors_training_type != '':
            recent_field_list['minors_training_type'] = minors_training_type

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
         #  -----end filter field that have in intakeupdate----

        #-----filter classroom and grade-----
         if classroom != '':
             students = students.filter(Q(classroomenrollment__classroom_id=classroom) & Q(Q(classroomenrollment__drop_date__gte=date.today().isoformat()) | Q(classroomenrollment__drop_date=None)))
         if vdp_grade != '':
             student_filter_by_vdp_grade = []
             for student in students:
                 if(student.current_vdp_grade() == int(vdp_grade)):
                     student_filter_by_vdp_grade.append(student.student_id)
             students = students.filter(student_id__in=student_filter_by_vdp_grade)
         #  -----end filter classroom and grede-----
         #  ----- filter public school --------------
         if enrolled != '':
              if grade_current == '' and public_school_name == '' and grade_last == '' and reasons == '':
                 student_filter_by_enrolled = []
                 for student in students:
                      pschool = student.get_pschool()
                      if(pschool.status == enrolled):
                          student_filter_by_enrolled.append(student.student_id)
                 students = students.filter(student_id__in=student_filter_by_enrolled)
              elif grade_current != '' and public_school_name != '':
                   student_filter_by_enrolled = []
                   for student in students:
                        pschool = student.get_pschool()
                        if pschool.status == enrolled and pschool.grade == int(grade_current) and re.search(public_school_name,pschool.school_name, re.IGNORECASE):
                            student_filter_by_enrolled.append(student.student_id)
                   students = students.filter(student_id__in=student_filter_by_enrolled)
              elif grade_current != '':
                   student_filter_by_enrolled = []
                   for student in students:
                      pschool = student.get_pschool()
                      if pschool.status == enrolled and pschool.grade == int(grade_current):
                          student_filter_by_enrolled.append(student.student_id)
                   students = students.filter(student_id__in=student_filter_by_enrolled)
              elif public_school_name != '':
                   student_filter_by_enrolled = []
                   for student in students:
                        pschool = student.get_pschool()
                        if pschool.status == enrolled and re.search(public_school_name,pschool.school_name, re.IGNORECASE):
                            student_filter_by_enrolled.append(student.student_id)
                   students = students.filter(student_id__in=student_filter_by_enrolled)
              elif grade_last != '' and reasons != '':
                   student_filter_by_enrolled = []
                   for student in students:
                      pschool = student.get_pschool()
                      if pschool.status == enrolled and pschool.last_grade == int(grade_last) and re.search(reasons,pschool.reasons, re.IGNORECASE):
                          student_filter_by_enrolled.append(student.student_id)
                   students = students.filter(student_id__in=student_filter_by_enrolled)
              elif grade_last != '':
                   student_filter_by_enrolled = []
                   for student in students:
                       pschool = student.get_pschool()
                       if pschool.status == enrolled and pschool.last_grade == int(grade_last):
                           student_filter_by_enrolled.append(student.student_id)
                   students = students.filter(student_id__in=student_filter_by_enrolled)
              elif reasons != '':
                   student_filter_by_enrolled = []
                   for student in students:
                       pschool = student.get_pschool()
                       if pschool.status == enrolled and re.search(reasons,pschool.reasons, re.IGNORECASE):
                           student_filter_by_enrolled.append(student.student_id)
                   students = students.filter(student_id__in=student_filter_by_enrolled)

         show_data = 'yes'


      else :
          pass
        #   students = IntakeSurvey.objects.all()
      return render(request, 'mande/advancedreport.html',
                            {
                                'students':students,
                                'schools':schools,
                                'genders':genders,
                                'grades' : grades,
                                'relationships':relationships,
                                'yns':yns,
                                'employments':employments,
                                'classrooms':classrooms,
                                'show_data': show_data,
                                'data_guardian1_profession' :json.dumps(list(set(data_guardian1_profession))),
                                'data_guardian2_profession' :json.dumps(list(set(data_guardian2_profession))),
                                'data_minors_profession' : json.dumps(list(set(data_minors_profession))),
                                'data_minors_training_type' :json.dumps(list(set(data_minors_training_type))),
                                'data_reasons' : json.dumps(list(set(data_reasons))),
                                'data_public_schools':json.dumps(list(set(data_public_schools))),
                                'list_of_fields':sorted(list_of_fields.iteritems())
                            })
    else:
      raise PermissionDenied

'''
*****************************************************************************
Unapproved Absence With No Comment Report
 - lists all student attendance that unapproved absence with no comment
*****************************************************************************
'''
def unapproved_absence_with_no_comment(request,school_year=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      thisyear = date.today().year
      school_year_list = [thisyear-i for i in range(thisyear-2013)]
      if school_year != None:
        school_year_start_date = str(school_year)+"-08-01"
        school_year_end_date = str(int(school_year)+1)+"-07-31"
        unapproved_absence_no_comments = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(Q(notes=u"") |Q(notes=None)) & Q(Q(date__gte=school_year_start_date) & Q(date__lte=school_year_end_date))).order_by('-date')
      else:
          unapproved_absence_no_comments = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(Q(notes=u"") |Q(notes=None))).order_by('-date')
      return render(request, 'mande/unapproved_absence_with_no_comment.html',
                            {
                                'unapproved_absence_no_comments':unapproved_absence_no_comments,
                                'school_year_list':school_year_list,
                                'school_year':school_year
                            })
    else:
      raise PermissionDenied
def generate(request):
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
    #    delete all CurrentStudentInfo
       CurrentStudentInfo.objects.all().delete()
       exit_surveys = ExitSurvey.objects.all().filter(
                       exit_date__lte=date.today().isoformat()
                       ).values_list('student_id',flat=True)
       active_surveys = IntakeSurvey.objects.filter(date__lte=date.today().isoformat()).order_by('student_id'
                                ).exclude(student_id__in=exit_surveys)
       for survey in active_surveys:
            recent_survey = survey.getRecentFields()
            student = CurrentStudentInfo(
                student_id=recent_survey['student_id'],
                name = recent_survey['name'],
                site = recent_survey['site'],
                date = recent_survey['date'],
                dob = recent_survey['dob'],
                gender = recent_survey['gender'],
                age_appropriate_grade = survey.age_appropriate_grade(),
                in_public_school = True if survey.get_pschool().status=='Y' else False,
                at_grade_level = studentAtAgeAppropriateGradeLevel(recent_survey['student_id']),
                vdp_grade = survey.current_vdp_grade()
            )
            student.save()
    #    return HttpResponseRedirect(reverse('student_list'))
       return render(request, 'mande/generatestudentinfo.html',
                              {
                               'students':active_surveys.count()
                              })
    else:
      raise PermissionDenied
