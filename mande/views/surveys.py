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
from mande.forms import HealthDentalForm
from mande.forms import HealthCheckupForm

from mande.utils import getEnrolledStudents
from mande.utils import getStudentGradebyID
from mande.utils import studentAtSchoolGradeLevel
from mande.utils import studentAtAgeAppropriateGradeLevel
from mande.utils import user_permissions

import inspect

from django.contrib.auth.models import User
from mande.utils import user_permissions

import inspect

'''
*****************************************************************************
Intake Survey
 - process an IntakeSurveyForm and log the action
*****************************************************************************
'''
def intake_survey(request,student_id=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        next_url = request.GET.get('next') #where we're going next
        limit = request.GET.get('limit') #limit to a single field
        instance = IntakeSurvey.objects.get(pk=student_id) if student_id else None
        form = IntakeSurveyForm(request.POST or None,
                                instance=instance)
        if request.method == 'POST':
            if form.is_valid():
                instance = form.save()
                icon = 'fa-female' if instance.gender == 'F' else 'fa-male'
                if student_id:
                    action = 'Updated'
                    if limit:
                        action = action+' '+limit+ 'on' #Updated dob on intake...
                else:
                    action='Performed'
                message = action+' intake survey for '+unicode(instance.name)
                log = NotificationLog(  user=request.user,
                                        text=message,
                                        font_awesome_icon=icon)
                log.save()
                #then return, defaulting to an intake internal
                if next_url is None:
                    next_url = reverse('intake_internal',kwargs={'student_id':instance.student_id})

                return HttpResponseRedirect(next_url)

        context = {'form': form, 'student':instance, 'next_url':next_url, 'limit':limit}
        return render(request, 'mande/intakesurvey.html', context)
    else:
        return render(request, 'mande/errors/permissiondenied.html')

'''
*****************************************************************************
Internal Intake
 - process an IntakeInteralForm and log the action
*****************************************************************************
'''
def intake_internal(request, student_id=0):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):

      if request.method == 'POST':
        form = IntakeInternalForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = ( 'Enrolled  '+unicode(instance.student_id.name)+
                        ' in '+instance.get_starting_grade_display())
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-user-plus')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail',kwargs=
                                {'student_id':instance.student_id.student_id}))
      else:
        if student_id > 0:
            form = IntakeInternalForm({'student_id':student_id})
        else:
            form = IntakeInternalForm()

      context = {'form': form,}
      return render(request, 'mande/intakeinternal.html', context)
    else:
      return render(request, 'mande/errors/permissiondenied.html')

'''
*****************************************************************************
Intake Update
 - update student information and log the action
*****************************************************************************
'''
def intake_update(request,student_id=0):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      next_url = request.GET.get('next')
      next_tab = request.GET.get('tab')
      try:
        survey = IntakeSurvey.objects.get(pk=student_id)
        most_recent = survey.getRecentFields()
      except ObjectDoesNotExist:
        survey = None
        most_recent = {}

      if request.method == 'POST':
        form = IntakeUpdateForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = 'Updated '+unicode(instance.student_id.name)+'\'s record'
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-upload')
            log.save()
            #then return
            return HttpResponseRedirect(next_url+'#'+next_tab)
      else:
        #change the date today, for convenience
        most_recent['date'] = date.today().isoformat()
        form = IntakeUpdateForm(most_recent)

      context = {'form': form, 'survey':survey, 'student_id':student_id, 'next':next_url, 'tab':next_tab}
      return render(request, 'mande/intakeupdate.html', context)
    else:
      return render(request, 'mande/errors/permissiondenied.html')
'''
*****************************************************************************
Exit Survey
 - process an ExitsurveyForm and log the action
*****************************************************************************
'''
def exit_survey(request,student_id=0):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):

      if request.method == 'POST':
        form = ExitSurveyForm(request.POST)

        if form.is_valid():
            instance = form.save()
            message = 'Did an exit survey for '+unicode(instance.student_id.name)
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-user-times')
            log.save()

            # drop student from classroom enrollment
            ClassroomEnrollment.objects.filter(student_id=instance.student_id,drop_date=None).update(drop_date=instance.exit_date)

            #then return
            return HttpResponseRedirect(reverse('student_detail', kwargs=
                                {'student_id':instance.student_id.student_id}))
      else:
        if student_id > 0:
            form = ExitSurveyForm({'student_id':student_id})
        else:
            form = ExitSurveyForm()

      context = {'form': form,'student_id':student_id}
      return render(request, 'mande/exitsurvey.html', context)
    else:
      return render(request, 'mande/errors/permissiondenied.html')
'''
*****************************************************************************
Post Exit Survey
 - process a PostExitSurveyForm and log the action
*****************************************************************************
'''
def post_exit_survey(request,student_id):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      #if the student hasn't had an exit survey performed alert the user
      try:
        exit = ExitSurvey.objects.get(student_id=student_id)
      except ObjectDoesNotExist:
        return render(
                        request,'mande/errors/noexitsurvey.html',
                        {'student_id':student_id})

      #get students current info for pre-filling the survey
      try:
        survey = IntakeSurvey.objects.get(pk=student_id)
        most_recent = survey.getRecentFields()
      except ObjectDoesNotExist:
        survey = None
        most_recent = None

      if request.method == 'POST':
        form = PostExitSurveyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = 'Did a post exit survey for '+unicode(instance.student_id.name)
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-heart')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('post_exit_survey'))
      else:
        form = PostExitSurveyForm(most_recent)

      context = {'form': form,'student_id':student_id }
      return render(request, 'mande/postexitsurvey.html', context)
    else:
      return render(request, 'mande/errors/permissiondenied.html')

'''
*****************************************************************************
Post Exit Survey List
 - show a list of all students who are eligible to do a post exit survey
*****************************************************************************
'''
def post_exit_survey_list(request):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      exitsurveys = ExitSurvey.objects.exclude(
                                        student_id__in=
                                        [x.student_id.student_id for x in PostExitSurvey.objects.all()]
                                   ).order_by('-exit_date')

      context = {'exitsurveys':exitsurveys}
      return render(request, 'mande/postexitsurveylist.html',context)
    else:
      return render(request, 'mande/errors/permissiondenied.html')

'''
*****************************************************************************
Spiritual Acitivies Survey
 - process a SpiritualActivitiesSurveyForm and log the action
*****************************************************************************
'''
def spiritualactivities_survey(request,student_id=0):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):

      if request.method == 'POST':
        form = SpiritualActivitiesSurveyForm(request.POST)

        if form.is_valid():
            instance = form.save()
            message = ('Performed spiritual activities survey for '+
                        unicode(instance.student_id.name))
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-fire')
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
    else:
      return render(request, 'mande/errors/permissiondenied.html')

'''
*****************************************************************************
Survey Success
 - display a success message
*****************************************************************************
'''
def survey_success(request):
    return render(request, 'mande/success.html',{})

'''
*****************************************************************************
Health Form
 - process a HealthForm and log the action
*****************************************************************************
'''
def health_form(request, student_id=0, appointment_date=date.today().isoformat(), appointment_type=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        next_url = request.GET.get('next')
        if request.method == 'POST':
            form = HealthForm(request.POST)
            instance,created = Health.objects.get_or_create(student_id=IntakeSurvey.objects.get(pk=form.data['student_id']),
                                          appointment_date=form.data['appointment_date'],
                                          appointment_type=form.data['appointment_type'])
            form = HealthForm(request.POST,instance=instance)
            if form.is_valid():
                #process
                instance = form.save()
                action = 'Input ' if created else 'Updated '
                message = ( action+instance.appointment_type+
                            ' for '+instance.student_id.name)

                log = NotificationLog(  user=request.user,
                                        text=message,
                                        font_awesome_icon='fa-medkit')
                log.save()
                #then return
                return HttpResponseRedirect(next_url+'#health')
        else:
            if student_id > 0 and appointment_type:
                try:
                    instance = Health.objects.get(student_id=IntakeSurvey.objects.get(pk=student_id),
                                              appointment_date=appointment_date,
                                              appointment_type=appointment_type)
                    if appointment_type=='DENTAL':
                        form = HealthDentalForm(instance=instance)
                    else:
                        form = HealthCheckupForm(instance=instance)

                except ObjectDoesNotExist:
                    form = HealthForm({ 'student_id':student_id,
                                    'appointment_date':appointment_date,
                                    'appointment_type':appointment_type})
            else:
                if student_id >0:
                    form = HealthForm({'student_id':student_id,
                                        'appointment_date':appointment_date})
                else:
                    form = HealthForm()

        context = {'form': form,'student_id':student_id,'next_url':next_url}

        return render(request, 'mande/healthform.html',context)
    else:
      return render(request, 'mande/errors/permissiondenied.html')
