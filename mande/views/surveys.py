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

import json

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

from icu import Locale, Collator
from django.contrib import messages
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

        context = {
            'form': form,
            'student':instance,
            'next_url':next_url,
            'limit':limit,
        }
        return render(request, 'mande/intakesurvey.html', context)
    else:
        raise PermissionDenied

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
      raise PermissionDenied

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
        initial_grade_current = request.POST.get('initial_grade_current')
        initial_public_school_name = request.POST.get('initial_school_name')

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

      context = {
          'form':form,
          'survey':survey,
          'student_id':student_id,
          'next':next_url,
          'tab':next_tab,
      }
      return render(request, 'mande/intakeupdate.html', context)
    else:
      raise PermissionDenied
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
      raise PermissionDenied
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
        # exit = ExitSurvey.objects.get(student_id=student_id)
        exit = ExitSurvey.objects.filter(student_id=student_id)
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
      raise PermissionDenied

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
      raise PermissionDenied
'''
*****************************************************************************
Delete Spiritual Acitivies Survey
 - process delete Spiritual Acitivies Survey and log the action
*****************************************************************************
'''
def delete_spiritualactivities_survey(request,id):
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
        next_url = request.GET.get('next')
        try:
            SpiritualActivitiesSurvey.objects.get(pk=id).delete()
            messages.success(request, 'Spiritual Activity Survey has been deleted successfully!',extra_tags='delete_spiritualactivities_survey')
        except Exception as e:
            messages.error(request,'Fail to delete Spiritual Activity Survey! ('+e.message+')',extra_tags='delete_spiritualactivities_survey')

        return HttpResponseRedirect(next_url)
    else:
        raise PermissionDenied


'''
*****************************************************************************
Spiritual Acitivies Survey
 - process a SpiritualActivitiesSurveyForm and log the action
*****************************************************************************
'''
def spiritualactivities_survey(request,student_id=0,survey_id=None):
    #get current method name
    method_name = inspect.currentframe().f_code.co_name
    if user_permissions(method_name,request.user):
      next_url = request.GET.get('next')
      data_church_names = list(SpiritualActivitiesSurvey.objects.all().values_list('church_name',flat=True).distinct())
      # sort khmer
      data_church_names = [x.encode('utf-8').strip() for x in data_church_names]
      locale = Locale('km_KH')
      collator = Collator.createInstance(locale)
      data_public_schools = sorted(set(data_church_names),key=collator.getSortKey)
      if int(student_id)>0:
          if survey_id != None:
               try:
                   #editing
                   instance = SpiritualActivitiesSurvey.objects.get(pk=survey_id)
                   form = SpiritualActivitiesSurveyForm(instance=instance)
                   action = "Editing"
               except ObjectDoesNotExist:
                   #adding form
                   instance = None
                   form = SpiritualActivitiesSurveyForm(initial={'student_id': student_id,'date':date.today().isoformat()})
                   action = 'Adding'
          else:
              instance = None
              form = SpiritualActivitiesSurveyForm(initial={'student_id':student_id,'date':date.today().isoformat()})
              action = "Adding"
      else:
          instance = None
          form = SpiritualActivitiesSurveyForm()
          action = "Performing"
      if request.method == 'POST':
        if instance != None:
            form = SpiritualActivitiesSurveyForm(request.POST,instance=instance)
        else:
            form = SpiritualActivitiesSurveyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            sms = action.replace('ing', 'ed')
            message = (sms+' spiritual activities survey for '+
                        unicode(instance.student_id.name))
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-fire')
            log.save()
            #then return
            if (next_url != None) & (next_url !='None'):
                return HttpResponseRedirect(next_url+'#spiritual_activities')
            return HttpResponseRedirect(reverse('success'))

      context = {
        'form': form,
        'student_id':student_id,
        'survey_id':survey_id,
        'next_url':next_url,
        'action':action,
        'data_church_names' :json.dumps(data_church_names),
      }
      return render(request, 'mande/spiritualactivitiessurvey.html', context)
    else:
      raise PermissionDenied

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
      raise PermissionDenied
