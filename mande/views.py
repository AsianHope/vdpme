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

def take_attendance(request, classroom_id):
    classroom = Classroom.objects.get(pk=classroom_id)
    students = ClassroomEnrollment.objects.filter(classroom_id=1)
    #students.exclude(drop_date<date.today())
    context= {'classroom':classroom, 'students':students}
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
