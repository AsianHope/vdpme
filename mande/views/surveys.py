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

def intake_survey(request):
    if request.method == 'POST':
        form = IntakeSurveyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            icon = 'fa-female' if instance.gender == 'F' else 'fa-male'
            #message = 'Performed intake survey for <a href="'+reverse('student_detail',kwargs={'student_id':instance.student_id})+'">'+unicode(instance.name)+'</a>'
            log = NotificationLog(user=request.user, text='Performed intake survey for '+unicode(instance.name), font_awesome_icon=icon)
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail', kwargs={'student_id':instance.student_id}))
    else:
        form = IntakeSurveyForm()

    context = {'form': form,}
    return render(request, 'mande/intakesurvey.html', context)

def intake_internal(request, student_id=0):


    if request.method == 'POST':
        form = IntakeInternalForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = 'Enrolled  '+unicode(instance.student_id.name)+' in '+instance.get_starting_grade_display()
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-user-plus')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail',kwargs={'student_id':instance.student_id.student_id}))
    else:
        if student_id > 0:
            form = IntakeInternalForm({'student_id':student_id})
        else:
            form = IntakeInternalForm()

    context = {'form': form,}
    return render(request, 'mande/intakeinternal.html', context)

def intake_update(request,student_id=0):
    try:
        survey = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        survey = None
    try:
        update = IntakeUpdate.objects.filter(student_id=student_id).latest('date')
        most_recent = update
    except ObjectDoesNotExist:
        most_recent = survey
    if request.method == 'POST':
        form = IntakeUpdateForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = 'Updated '+unicode(instance.student_id.name)+'\'s record'
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-upload')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('success'))
    else:
        form = IntakeUpdateForm(instance=most_recent)

    context = {'form': form, 'survey':survey, 'student_id':student_id}
    return render(request, 'mande/intakeupdate.html', context)

def exit_survey(request,student_id=0):

    if request.method == 'POST':
        form = ExitSurveyForm(request.POST)

        if form.is_valid():
            instance = form.save()
            message = 'Did an exit survey for '+unicode(instance.student_id.name)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-user-times')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail', kwargs={'student_id':instance.student_id.student_id}))
    else:
        if student_id > 0:
            form = ExitSurveyForm({'student_id':student_id})
        else:
            form = ExitSurveyForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/exitsurvey.html', context)

def post_exit_survey(request,student_id):
    #if the student hasn't had an exit survey performed alert the user
    try:
        exit = ExitSurvey.objects.get(student_id=student_id)
    except ObjectDoesNotExist:
        return render(request,'mande/errors/noexitsurvey.html',{'student_id':student_id})

    #get students current info for pre-filling the survey
    try:
        survey = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        survey = None
    try:
        update = IntakeUpdate.objects.filter(student_id=student_id).latest('date')
        most_recent = update
    except ObjectDoesNotExist:
        most_recent = survey

    if request.method == 'POST':
        form = PostExitSurveyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = 'Did a post exit survey for '+unicode(instance.student_id.name)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-heart')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('post_exit_survey'))
    else:
        form = PostExitSurveyForm({
            'student_id':student_id,
            'exit_date':exit.exit_date,
            'early_exit':exit.early_exit,
            'father_profession':most_recent.father_profession,
            'father_employment':most_recent.father_employment,
            'mother_profession':most_recent.mother_profession,
            'mother_employment':most_recent.father_employment,
            'minors':most_recent.minors,
            'enrolled':most_recent.enrolled,
            'grade_current':most_recent.grade_current,
            'grade_previous':most_recent.grade_last,
            'reasons':most_recent.reasons,
        })

    context = {'form': form,'student_id':student_id }
    return render(request, 'mande/postexitsurvey.html', context)

def post_exit_survey_list(request):
    exitsurveys = ExitSurvey.objects.exclude(student_id__in=[x.student_id.student_id for x in PostExitSurvey.objects.all()]).order_by('-exit_date')

    context = {'exitsurveys':exitsurveys}
    return render(request, 'mande/postexitsurveylist.html',context)

def spiritualactivities_survey(request,student_id=0):

    if request.method == 'POST':
        form = SpiritualActivitiesSurveyForm(request.POST)

        if form.is_valid():
            instance = form.save()
            message = 'Performed spiritual activities survey for '+unicode(instance.student_id.name)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-fire')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('success'))
    else:
        if student_id > 0:
            form = SpiritualActivitiesSurveyForm({'student_id':student_id})
        else:
            form = SpiritualActivitiesSurveyForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/spiritualactivitiessurvey.html', context)

def survey_success(request):
    return render(request, 'mande/success.html',{})

def health_form(request, student_id=0):
        if request.method == 'POST':
            form = HealthForm(request.POST)
            if form.is_valid():
                #process
                instance = form.save()
                message = 'Input '+instance.appointment_type+' for '+instance.student_id.name

                log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-medkit')
                log.save()
                #then return
                return HttpResponseRedirect(reverse('student_detail',kwargs={'student_id':instance.student_id.student_id}))
        else:
            if student_id > 0:
                form = HealthForm({'student_id':student_id, 'appointment_date':date.today().isoformat()})
            else:
                form = HealthForm()

        context = {'form': form,'student_id':student_id}

        return render(request, 'mande/healthform.html',context)
