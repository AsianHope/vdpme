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

def index(request):
    surveys = IntakeSurvey.objects.order_by('student_id')
    context = {'surveys': surveys}
    return render(request, 'mande/index.html', context)

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
        'graduation':survey.dob + timedelta(days=365*11)}
    print survey.student_id
    return render(request, 'mande/detail.html', context)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
