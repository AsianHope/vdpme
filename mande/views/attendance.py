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
Attendance
 - display a list of attendance related actions
*****************************************************************************
'''
def attendance(request):
    context= {}
    return render(request, 'mande/attendance.html', context)


'''
*****************************************************************************
Attendance Calendar
 - display a list of calendars to modify
*****************************************************************************
'''
def attendance_calendar(request):
    classrooms = Classroom.objects.all()
    attendance_date = date.today().replace(day=1).isoformat()
    context= {'classrooms':classrooms, 'attendance_date':attendance_date}
    return render(request, 'mande/attendancecalendar.html', context)

'''
*****************************************************************************
Take Class Attendance
 - generate a valid list of students for the classroom and date
 - process a AttendanceFormSet and log the action
*****************************************************************************
'''
def take_class_attendance(request, classroom_id, attendance_date=TODAY):
    message = ''
    submit_enabled = True
    if attendance_date != TODAY:
        warning = 'The selected date is not today!'
    else:
        warning = ''

    classroom = Classroom.objects.get(pk=classroom_id)
    students = ClassroomEnrollment.objects.filter(classroom_id=classroom_id
                                                 ).exclude(
                                                  drop_date__lte=attendance_date
                                                 )

    #find out if any student attendance has been taken, excluding placeholder attendance
    student_attendance = Attendance.objects.filter(student_id=students,
                                                   date=attendance_date
                                                   ).exclude(attendance=None)
    if len(student_attendance) > 0:
        message = 'Attendance for one or more students has been taken'

    #pre instantiate data for this form so that we can update the whole queryset later
    for student in students:
        Attendance.objects.get_or_create(student_id=student.student_id,
                                         date=attendance_date,
                                         defaults={'attendance':None,
                                                   'classroom':classroom})

    try:
        offered = AttendanceDayOffering.objects.get(classroom_id=classroom_id,
                                                    date=attendance_date)
    except ObjectDoesNotExist:
        submit_enabled = False
        Attendance.objects.filter(attendance=None).delete()

    #now get the whole set of attendance objects and create the formset
    student_attendance = Attendance.objects.filter(student_id=students,
                                                   date=attendance_date)
    AttendanceFormSet = modelformset_factory(Attendance,
                                             form=AttendanceForm,
                                             extra=0)

    if request.method == 'POST':

        formset = AttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()

            #zero things out
            absent = 0
            present = 0
            attendancecodes = dict(ATTENDANCE_CODES)
            for key,code in attendancecodes.iteritems():
                attendancecodes[key]=0
            #count attendance codes
            for form in formset:
                attendancecodes[form.cleaned_data['attendance']] +=1
                #attendance codes with 'A' in them mean absences.
                if 'A' in form.cleaned_data['attendance']:
                    absent +=1
                else:
                    present +=1


            alog,created = AttendanceLog.objects.get_or_create(
                                                          classroom=classroom,
                                                          date=attendance_date,)
            alog.absent = absent
            alog.present = present
            alog.save()
            message = ('Took attendance for '+unicode(classroom) +
                      ' (A:'+unicode(absent)+
                      ',P:'+unicode(present)+')')
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-check-square')
            log.save()
            #clean up the mess we created making blank rows to update.
            Attendance.objects.filter(attendance=None).delete()

    else:
        formset = AttendanceFormSet(queryset = student_attendance)
    context= {  'classroom':classroom,
                'students':students,
                'attendance_date':attendance_date,
                'formset':formset,
                'warning': mark_safe(warning),
                'message': message,
                'submit_enabled': submit_enabled}

    return render(request, 'mande/takeclassattendanceformset.html', context)

'''
*****************************************************************************
AttendanceCalendar
 - displays a nicely formatted HTML calendar
*****************************************************************************
'''
class AttendanceCalendar(HTMLCalendar):

    def __init__(self, attendance_offerings):
        super(AttendanceCalendar, self).__init__()
        self.firstweekday = 6
        self.attendance_offerings = self.breakout(attendance_offerings)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'

            if day in self.attendance_offerings:
                cssclass += ' filled'
                return self.day_cell(cssclass, '%d %s' % (day, ''))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(AttendanceCalendar, self).formatmonth(year, month)

    def breakout(self, attendance_offerings):
        days = []
        for attendance_offering in attendance_offerings:
            days.append(attendance_offering.date.day)
        return days

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

'''
*****************************************************************************
Attendance Days
 - toggles the specified attendance day for the specified classroom
*****************************************************************************
'''
def attendance_days(request,classroom_id,attendance_date=TODAY):

    attendance_date = datetime.strptime(attendance_date,'%Y-%m-%d')
    classroom = Classroom.objects.get(pk=classroom_id)


    #submitting a day to be added or removed
    if request.method == 'GET' and request.GET.get('day'):
        day = request.GET.get('day')
        #if we don't get an exception, we want to delete this object
        try:
            attendance_days = AttendanceDayOffering.objects.get(
                                            classroom_id=classroom,
                                            date__year=attendance_date.year,
                                            date__month=attendance_date.month,
                                            date__day=day)
            attendance_days.delete()
        #if we do get an exception, we want to create this object
        except ObjectDoesNotExist:
            newday = datetime.strptime(str(attendance_date.year)+
                    '-'+str(attendance_date.month)+
                    '-'+str(day),'%Y-%m-%d')
            add = AttendanceDayOffering(classroom_id=classroom, date=newday)
            add.save()
        #TODO: make a success template so we can be smarter in our JS
        #TODO: figure out a way to not group requests for slimmer logging
        return render(request,'mande/attendancedays.html','')

    #otherwise display the calendar
    else:
        attendance_days = AttendanceDayOffering.objects.filter(
                                                          classroom_id=classroom
                                                      ).filter(
                                                          date__year=attendance_date.year,
                                                          date__month=attendance_date.month
                                                      )
        lCalendar = AttendanceCalendar(attendance_days).formatmonth(
                                                            attendance_date.year,
                                                            attendance_date.month)

        return render(request, 'mande/attendancedays.html', {'Calendar' : mark_safe(lCalendar),
                                                       'classroom': classroom,
                                                   })
