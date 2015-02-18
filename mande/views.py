from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
from mande.models import ExitSurvey
from mande.models import PostExitSurvey
from mande.models import SpiritualActivitiesSurvey


from mande.forms import IntakeSurveyForm
from mande.forms import IntakeUpdateForm
from mande.forms import ExitSurveyForm
from mande.forms import PostExitSurveyForm
from mande.forms import SpiritualActivitiesSurveyForm
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

def intake_survey(request):
    if request.method == 'POST':
        form = IntakeSurveyForm(request.POST)
        print form
        if form.is_valid():
            #process
            intake = IntakeSurvey(
            date = form.cleaned_data['date'],
            site = form.cleaned_data['site'],
            name = form.cleaned_data['name'],
            dob = form.cleaned_data['dob'],
            grade_appropriate = form.cleaned_data['grade_appropriate'],
            gender = form.cleaned_data['gender'],
            address = form.cleaned_data['address'],
            enrolled = form.cleaned_data['enrolled'],
            grade_current = form.cleaned_data['grade_current'],
            grade_last = form.cleaned_data['grade_last'],
            reasons = form.cleaned_data['reasons'],
            father_name = form.cleaned_data['father_name'],
            father_phone = form.cleaned_data['father_phone'],
            father_profession = form.cleaned_data['father_profession'],
            father_employment = form.cleaned_data['father_employment'],
            mother_name = form.cleaned_data['mother_name'],
            mother_phone = form.cleaned_data['mother_phone'],
            mother_profession = form.cleaned_data['mother_profession'],
            mother_employment= form.cleaned_data['mother_employment'],
            minors = form.cleaned_data['minors'],
            minors_in_school = form.cleaned_data['minors_in_school'],
            minors_working = form.cleaned_data['minors_working'],
            minors_profession = form.cleaned_data['minors_profession'],
            minors_encouraged = form.cleaned_data['minors_encouraged'],
            minors_training = form.cleaned_data['minors_training'],
            minors_training_type = form.cleaned_data['minors_training_type'],
            notes = form.cleaned_data['notes'],
            )
            intake.save()
            #then return
            return HttpResponseRedirect('/mande/surveys/success')
    else:
        print "form is invalid"
        form = IntakeSurveyForm()

    context = {'form': form,}
    return render(request, 'mande/intakesurvey.html', context)

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
        print form
        if form.is_valid():
            #process
            print form.cleaned_data
            intake = IntakeUpdate(
                student_id = form.cleaned_data['student_id'],
                date = form.cleaned_data['date'],
                address = form.cleaned_data['address'],
                enrolled = form.cleaned_data['enrolled'],
                grade_current = form.cleaned_data['grade_current'],
                grade_last = form.cleaned_data['grade_last'],
                reasons = form.cleaned_data['reasons'],
                father_name = form.cleaned_data['father_name'],
                father_phone = form.cleaned_data['father_phone'],
                father_profession = form.cleaned_data['father_profession'],
                father_employment = form.cleaned_data['father_employment'],
                mother_name = form.cleaned_data['mother_name'],
                mother_phone = form.cleaned_data['mother_phone'],
                mother_profession = form.cleaned_data['mother_profession'],
                mother_employment= form.cleaned_data['mother_employment'],
                minors = form.cleaned_data['minors'],
                minors_in_school = form.cleaned_data['minors_in_school'],
                minors_working = form.cleaned_data['minors_working'],
                minors_profession = form.cleaned_data['minors_profession'],
                minors_encouraged = form.cleaned_data['minors_encouraged'],
                minors_training = form.cleaned_data['minors_training'],
                minors_training_type = form.cleaned_data['minors_training_type'],
                notes = form.cleaned_data['notes'],
            )
            intake.save()
            #then return
            return HttpResponseRedirect('/mande/surveys/success')
    else:
        print "form is invalid"
        form = IntakeUpdateForm(instance=most_recent)

    context = {'form': form, 'survey':survey, 'student_id':student_id}
    return render(request, 'mande/intakeupdate.html', context)

def exit_survey(request,student_id=0):

    if request.method == 'POST':
        form = ExitSurveyForm(request.POST)

        if form.is_valid():
            #process
            exit = ExitSurvey(
                student_id = form.cleaned_data['student_id'],
                survey_date = form.cleaned_data['survey_date'],
                exit_date = form.cleaned_data['exit_date'],
                early_exit = form.cleaned_data['early_exit'],
                last_grade = form.cleaned_data['last_grade'],
                early_exit_reason =  form.cleaned_data['early_exit_reason'],
                early_exit_comment = form.cleaned_data['early_exit_comment'],
                secondary_enrollment = form.cleaned_data['secondary_enrollment'],
            )
            exit.save()
            #then return
            return HttpResponseRedirect('/mande/surveys/success')
    else:
        if student_id > 0:
            form = ExitSurveyForm({'student_id':student_id})
        else:
            form = ExitSurveyForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/exitsurvey.html', context)

def post_exit_survey(request,student_id):
    try:
        exit = ExitSurvey.objects.get(student_id=student_id)
    except ObjectDoesNotExist:
        return render(request,'mande/errors/noexitsurvey.html',{'student_id':student_id})
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
        print form
        if form.is_valid():
            #process
            print form.cleaned_data
            exit = PostExitSurvey(
                student_id = form.cleaned_data['student_id'],
                post_exit_survey_date = form.cleaned_data['post_exit_survey_date'],
                exit_date = form.cleaned_data['exit_date'],
                early_exit = form.cleaned_data['early_exit'],
                father_profession = form.cleaned_data['father_profession'],
                father_employment = form.cleaned_data['father_employment'],
                mother_profession = form.cleaned_data['mother_profession'],
                mother_employment= form.cleaned_data['mother_employment'],
                minors = form.cleaned_data['minors'],
                enrolled = form.cleaned_data['enrolled'],
                grade_current = form.cleaned_data['grade_current'],
                grade_previous = form.cleaned_data['grade_previous'],
                reasons = form.cleaned_data['reasons'],
            )
            exit.save()
            #then return
            return HttpResponseRedirect('/mande/surveys/success')
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
    postexitsurveys = PostExitSurvey.objects.all()
    pexitsurveysids= []
    for pexitsurvey in postexitsurveys:
        pexitsurveysids.append(int(pexitsurvey.student_id.student_id))

    exitsurveys = ExitSurvey.objects.exclude(student_id__in=pexitsurveysids)

    context = {'exitsurveys':exitsurveys}
    return render(request, 'mande/postexitsurveylist.html',context)

def spiritualactivities_survey(request,student_id=0):

    if request.method == 'POST':
        form = SpiritualActivitiesSurveyForm(request.POST)

        if form.is_valid():
            #process
            survey = SpiritualActivitiesSurvey(
                student_id = form.cleaned_data['student_id'],
                date = form.cleaned_data['date'],
                family_attend_church = form.cleaned_data['family_attend_church'],
                personal_attend_church = form.cleaned_data['personal_attend_church'],
                personal_prayer = form.cleaned_data['personal_prayer'],
                personal_baptism = form.cleaned_data['personal_baptism'],
                personal_bible_reading =  form.cleaned_data['personal_bible_reading'],
                personal_prayer_aloud = form.cleaned_data['personal_prayer_aloud'],
            )
            survey.save()
            #then return
            return HttpResponseRedirect('/mande/surveys/success')
    else:
        if student_id > 0:
            form = SpiritualActivitiesSurveyForm({'student_id':student_id})
        else:
            form = SpiritualActivitiesSurveyForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/spiritualactivitiessurvey.html', context)

def survey_success(request):
    return render(request, 'mande/success.html',{})
