from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.forms.models import modelformset_factory
from django.db.models import Q

from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

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
from mande.models import PublicSchoolHistory
from mande.models import CurrentStudentInfo

from mande.models import GRADES
from mande.models import ATTENDANCE_CODES

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

from django.contrib.auth.models import User
from mande.utils import user_permissions

import inspect

'''
*****************************************************************************
Dashboard
 - summarize important student information
*****************************************************************************
'''
def dashboard(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      notifications = NotificationLog.objects.order_by('-date')[:10]

      ''' enrolled students are those who have:
          - completed an intake survey
          - have completed an internal intake
          AND
              - do not have an exit survey
              OR
              - have an exit survey with an exit date after today

      '''
      surveys = CurrentStudentInfo.objects.all()
      #figure out students who have internal intakes with enrollment dates before today
      enrolled_students = IntakeInternal.objects.all(
                                             ).values_list('student_id',flat=True)
      #figure out which students don't have internal intakes
      unenrolled_students = surveys.exclude(student_id__in=enrolled_students) #pass this queryset on
      not_enrolled = unenrolled_students.values_list('student_id',flat=True)
      #filter out students who aren't enrolled, as detailed above
      surveys = surveys.exclude(student_id__in=not_enrolled)

      tot_females = surveys.filter(gender='F').count()
      total_skills = surveys.filter(vdp_grade__gte=50,vdp_grade__lte=70).count()

      #set up for collecting school breakdowns
      schools = School.objects.all()
      breakdown = {}

      students_by_grade = dict(GRADES)
      students_at_gl_by_grade = dict(GRADES)
      students_by_grade_by_site  = dict(GRADES)

      program_breakdown = {}

      #zero things out for accurate counts
      for key,grade in students_by_grade.iteritems():
        students_by_grade_by_site[key] = {}

        students_by_grade[key] = surveys.filter(vdp_grade=key).count()
        students_at_gl_by_grade[key] = surveys.filter(at_grade_level=True,vdp_grade=key).count()

        for school in schools:
            name = school.school_name
            students_by_grade_by_site[key][unicode(name)] = surveys.filter(site=school.school_id,vdp_grade=key).count()

      #get information for morris donut charts
      for school in schools:
        name = school.school_name
        school_id = school.school_id

        breakdown[name] = {'F':0, 'M':0}
        breakdown[name]['F'] = surveys.filter(site=school_id,vdp_grade__gte=1,vdp_grade__lte=6,gender='F').count()
        breakdown[name]['M'] = surveys.filter(site=school_id,vdp_grade__gte=1,vdp_grade__lte=6,gender='M').count()

        program_breakdown[name] = {'Grades': 0, 'Skills': 0}
        program_breakdown[name]['Grades'] = surveys.filter(site=school_id,vdp_grade__gte=1,vdp_grade__lte=6).count()
        program_breakdown[name]['Skills'] = surveys.filter(site=school_id,vdp_grade__gte=50,vdp_grade__lte=70).count()

      #clean up students_by_grade_by_site so we're not displaying a bunch of blank data
      clean_students_by_grade_by_site = dict(students_by_grade_by_site)
      for key,grade in students_by_grade_by_site.iteritems():
        if students_by_grade[key] == 0:
            del clean_students_by_grade_by_site[key]

      #find students with unapproved absences and no notes ; get only current school year
      today = date.today()
    #   today = datetime.strptime("2014-08-01", "%Y-%m-%d").date()
      if (today < datetime.strptime(str(today.year)+"-08-01", "%Y-%m-%d").date()):
          school_year = today.year - 1
      else:
          school_year = today.year
      print "school_year:" + str(school_year)
      school_year_start_date = str(school_year)+"-08-01"
      school_year_end_date = str(school_year+1)+"-07-31"

      unapproved_absence_no_comment = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(Q(notes=u"") |Q(notes=None)) & Q(Q(date__gte=school_year_start_date) & Q(date__lte=school_year_end_date))).order_by('-date')
      context = { 'surveys': surveys,
                'females': tot_females,
                'breakdown':breakdown,
                'program_breakdown':program_breakdown,
                'total_skills':total_skills,
                'students_by_grade':students_by_grade,
                'students_at_gl_by_grade': students_at_gl_by_grade,
                'students_by_grade_by_site':clean_students_by_grade_by_site,
                'schools':schools,
                'notifications':notifications,
                'unenrolled_students':unenrolled_students,
                'unapproved_absence_no_comment':unapproved_absence_no_comment}

      return render(request, 'mande/index.html', context)
    else:
      raise PermissionDenied


'''
*****************************************************************************
Notification Log
 - display the most recent 500 entires in the notification log
*****************************************************************************
'''
def notification_log(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      notifications = NotificationLog.objects.order_by('-date')[:500]
      context = {'notifications':notifications}
      return render(request, 'mande/notificationlog.html',context)
    else:
      raise PermissionDenied
