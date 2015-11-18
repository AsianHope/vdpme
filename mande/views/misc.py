from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
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

TODAY = date.today().isoformat()
'''
*****************************************************************************
Dashboard
 - summarize important student information
*****************************************************************************
'''
def dashboard(request):
    notifications = NotificationLog.objects.order_by('-date')[:10]

    ''' enrolled students are those who have:
          - completed an intake survey
          - have completed an internal intake
          AND
              - do not have an exit survey
              OR
              - have an exit survey with an exit date after today

    '''
    #get a flat list of student_ids to exclude
    exit_surveys = ExitSurvey.objects.all().filter(
                        exit_date__lte=TODAY
                        ).values_list('student_id',flat=True)

    #filter out students who have exit surveys
    surveys = IntakeSurvey.objects.order_by('student_id'
                                 ).exclude(student_id__in=exit_surveys)

    #figure out students who have internal intakes with enrollment dates before today
    enrolled_students = IntakeInternal.objects.all(
                                             ).values_list('student_id',flat=True)
    #figure out which students don't have internal intakes
    unenrolled_students = surveys.exclude(student_id__in=enrolled_students) #pass this queryset on
    not_enrolled = unenrolled_students.values_list('student_id',flat=True)
    #filter out students who aren't enrolled, as detailed above
    surveys = surveys.exclude(student_id__in=not_enrolled)

    tot_females = surveys.filter(gender='F').count()

    #set up for collecting school breakdowns
    schools = School.objects.all()
    breakdown = {}

    students_by_grade = dict(GRADES)
    students_at_gl_by_grade = dict(GRADES)
    students_by_grade_by_site  = dict(GRADES)
    students_at_gl_by_grade_by_site = dict(GRADES)

    #zero things out for accurate counts
    for key,grade in students_by_grade.iteritems():
        students_by_grade[key] = 0
        students_at_gl_by_grade[key] = 0
        students_by_grade_by_site[key] = {}
        students_at_gl_by_grade_by_site[key] = {}

        for school in schools:
            name = school.school_name
            students_by_grade_by_site[key][unicode(name)] = 0
            students_at_gl_by_grade_by_site[key][unicode(name)] = 0

    #get information for morris donut charts
    for school in schools:
         name = school.school_name
         total = surveys.filter(site=school)
         females = total.filter(gender='F').count()
         males = total.filter(gender='M').count()
         breakdown[name] = {'F':females, 'M':males}


    #loop through students and figure out what grades they're currently in
    for student in surveys:
        grade = getStudentGradebyID(student.student_id)
        students_by_grade[grade] += 1
        students_by_grade_by_site[grade][unicode(student.site)] +=1

        if studentAtAgeAppropriateGradeLevel(student.student_id):
            students_at_gl_by_grade[grade] +=1
            students_at_gl_by_grade_by_site[grade][unicode(student.site)] +=1

    #clean up students_by_grade_by_site so we're not displaying a bunch of blank data
    clean_students_by_grade_by_site = dict(students_by_grade_by_site)
    for key,grade in students_by_grade_by_site.iteritems():
        if students_by_grade[key] == 0:
            del clean_students_by_grade_by_site[key]

    #find students with unapproved absences and no notes
    unapproved_absence_no_comment = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(notes=u"") |Q(notes=None)).order_by('-date')

    context = { 'surveys': surveys,
                'females': tot_females,
                'breakdown':breakdown,
                'students_by_grade':students_by_grade,
                'students_at_gl_by_grade': students_at_gl_by_grade,
                'students_by_grade_by_site':clean_students_by_grade_by_site,
                'students_at_gl_by_grade_by_site': students_at_gl_by_grade_by_site,
                'schools':schools,
                'notifications':notifications,
                'unenrolled_students':unenrolled_students,
                'unapproved_absence_no_comment':unapproved_absence_no_comment}

    return render(request, 'mande/index.html', context)


'''
*****************************************************************************
Notification Log
 - display the most recent 500 entires in the notification log
*****************************************************************************
'''
def notification_log(request):
    notifications = NotificationLog.objects.order_by('-date')[:500]
    context = {'notifications':notifications}
    return render(request, 'mande/notificationlog.html',context)
