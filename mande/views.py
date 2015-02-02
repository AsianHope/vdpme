from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from django.views.generic import ListView
from mande.models import IntakeSurvey
from mande.models import IntakeUpdate

def index(request):
    surveys = IntakeSurvey.objects.order_by('student_id')
    context = {'surveys': surveys}
    return render(request, 'mande/index.html', context)

def student_detail(request, student_id):
    survey = IntakeSurvey.objects.get(pk=student_id)
    context = {'survey':survey}
    return render(request, 'mande/detail.html', context)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
