from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from django.db.models import Q
from django.forms.models import model_to_dict

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
from mande.models import TODAY



'''
*****************************************************************************
Daily Attendance Report
 - lists all classrooms who take attendance and their attendance status
*****************************************************************************
'''
def daily_attendance_report(request,attendance_date=TODAY):
    #only classrooms who take attendance, and who take attendance today.
    classrooms = Classroom.objects.all().filter(active=True)
    takesattendance = AttendanceDayOffering.objects.filter(
                                                        date=attendance_date
                                                  ).values_list(
                                                       'classroom_id',flat=True)
    classrooms = classrooms.filter(classroom_id__in=takesattendance)

    classroomattendance = {}
    for classroom in classrooms:
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
'''
*****************************************************************************
Daily Absence Report
 - lists all students with unexcuses absences and their contact info
*****************************************************************************
'''
def daily_absence_report(request,attendance_date=TODAY):
    #only classrooms who take attendance, and who take attendance today.
    classrooms = Classroom.objects.all().filter(active=True)
    takesattendance = AttendanceDayOffering.objects.filter(
                                                        date=attendance_date
                                                  ).values_list(
                                                       'classroom_id',flat=True)
    classrooms = classrooms.filter(classroom_id__in=takesattendance)

    classroomattendance = {}
    for classroom in classrooms:
        try:
            #only displays unexcused absences
            classroomattendance[classroom] = Attendance.objects.filter(
                                                           classroom=classroom,
                                                           date=attendance_date,
                                                           attendance='UA')
        except ObjectDoesNotExist:
            classroomattendance[classroom] = None

    return render(request, 'mande/absencereport.html',
                            {'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date
                                                                        })
'''
*****************************************************************************
Data Audit
 - Generate a list of student records with missing or anomalous data
*****************************************************************************
'''
def data_audit(request,type='ALL'):
    #modelfields = model_to_dict(IntakeSurvey.objects.all()[0])

    students = IntakeSurvey.objects.all()

    #a
    anomalies = {}
    '''students with missing information'''
    for student in students:
        temp = IntakeSurveyForm(data=student.getRecentFields())
        for field in temp:
            #blank fields
            if field.data is None or len(unicode(field.data))==0:
                if field.label!="Notes":
                    try:
                        anomalies[student].append(
                                                {'text':'Missing '+field.label,
                                                 'resolution':reverse('student_detail',kwargs=
                                                                     {'student_id':student.student_id})})
                    except KeyError:
                        anomalies[student] = [{'text':'Missing '+field.label,
                         'resolution':reverse('student_detail',kwargs=
                                             {'student_id':student.student_id})}]



    '''students with odd information'''
    #weird birthdays compared to grade


    '''students we suspect have left (significant number of absences)'''

    print anomalies

    return render(request, 'mande/data_audit.html',
                            {'students' : anomalies,})
