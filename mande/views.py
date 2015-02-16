from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
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

def index(request):
    surveys = IntakeSurvey.objects.order_by('student_id')
    females = surveys.filter(gender='F')
    context = {'surveys': surveys, 'females': females}
    return render(request, 'mande/index.html', context)

def student_list(request):
    surveys = IntakeSurvey.objects.order_by('student_id')
    context = {'surveys': surveys}
    return render(request, 'mande/studentlist.html', context)

def report_list(request):
    context= {}
    return render(request, 'mande/reportlist.html', context)

def site_list(request):
    context= {}
    return render(request, 'mande/sitelist.html', context)

def attendance(request):
    context= {}
    return render(request, 'mande/attendance.html', context)

def attendance_calendar(request):
    classrooms = Classroom.objects.all()
    context= {'classrooms':classrooms}
    return render(request, 'mande/attendancecalendar.html', context)

def attendance_days(request,classroom_id):
    classroom = Classroom.objects.get(pk=classroom_id)
    print classroom
    context= {'classroom':classroom}
    return render(request, 'mande/attendancedays.html', context)

def take_class_attendance(request, classroom_id):
    try:
        attendance = request.POST.dict()
        attendance_date = attendance['attendance_date']
    except:
        attendance_date = date.today().isoformat()

    classroom = Classroom.objects.get(pk=classroom_id)
    students = ClassroomEnrollment.objects.filter(classroom_id=classroom_id).exclude(drop_date__lte=attendance_date)
    #get pre-existing attendance entries
    sidlist = []
    for student in students:

        sidlist.append(int(student.student_id.student_id))

    attendance_entries = Attendance.objects.filter(student_id__in=sidlist).filter(date=attendance_date)

    #remove students who already have attendance taken
    already_taken = []
    for attendance in attendance_entries:
        already_taken.append(int(attendance.student_id.student_id))
    students = students.exclude(student_id__in=already_taken)

    context= {'classroom':classroom, 'students':students, 'attendance_date':attendance_date, 'attendance_entries':attendance_entries}

    return render(request, 'mande/takeclassattendance.html', context)

def take_attendance(request):
    classrooms = Classroom.objects.all()
    context= {'classrooms':classrooms}
    return render(request, 'mande/takeattendance.html', context)



def student_detail(request, student_id):
    survey = IntakeSurvey.objects.get(pk=student_id)
    updates = survey.intakeupdate_set.all().filter().order_by('-date')
    intake = survey.intakeinternal_set.all().filter().order_by('-enrollment_date')
    academics = survey.academic_set.all().filter().order_by('-test_date')
    discipline = survey.discipline_set.all().filter().order_by('-incident_date')
    if len(updates) > 0:
        recent_update = updates[0]
    else:
        recent_update = "No recent updates"

    if len(intake) > 0:
        recent_intake = intake[0]
    else:
        recent_intake = 'Not enrolled'

    #is this a better approach?
    try:
        current_grade = academics.filter(promote=True).latest('test_date')
    except ObjectDoesNotExist:
        current_grade = {'test_level':0}

    context = {
        'survey':survey,
        'updates':updates,
        'recent_update':recent_update,
        'recent_intake':recent_intake,
        'academics':academics,
        'current_grade':current_grade,
        'discipline':discipline,
        'cur_year':date.today().year,
        'graduation':survey.dob + timedelta(days=365*12)}
    print survey.student_id
    return render(request, 'mande/detail.html', context)
