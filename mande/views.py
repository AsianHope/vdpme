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
from mande.forms import DisciplineForm
from mande.forms import TeacherForm
from mande.forms import ClassroomForm
from mande.forms import ClassroomTeacherForm
from mande.forms import ClassroomEnrollmentForm

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
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success/')
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
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success/')
    else:
        print "form is invalid"
        form = IntakeUpdateForm(instance=most_recent)

    context = {'form': form, 'survey':survey, 'student_id':student_id}
    return render(request, 'mande/intakeupdate.html', context)

def exit_survey(request,student_id=0):

    if request.method == 'POST':
        form = ExitSurveyForm(request.POST)

        if form.is_valid():
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success/')
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
            form.save
            #then return
            return HttpResponseRedirect('/mande/success/')
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
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success')
    else:
        if student_id > 0:
            form = SpiritualActivitiesSurveyForm({'student_id':student_id})
        else:
            form = SpiritualActivitiesSurveyForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/spiritualactivitiessurvey.html', context)

def survey_success(request):
    return render(request, 'mande/success.html',{})

def discipline_form(request,student_id=0):

    if request.method == 'POST':
        form = DisciplineForm(request.POST)

        if form.is_valid():
            #process
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success/')
    else:
        if student_id > 0:
            form = DisciplineForm({'student_id':student_id})
        else:
            form = DisciplineForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/disciplineform.html', context)

def teacher_form(request, teacher_id=0):
    current_teachers = Teacher.objects.all()

    if int(teacher_id)>0:
        instance = Teacher.objects.get(pk=teacher_id)
    else:
        instance = Teacher()

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            #then return
            return HttpResponseRedirect('/mande/school-management/teachers/'+str(teacher_id))
    else:
            form = TeacherForm(instance=instance)

    context = {'form': form, 'teacher_id':teacher_id,'current_teachers':current_teachers}
    return render(request, 'mande/teacherform.html', context)

def classroom_form(request, classroom_id=0):
    current_classrooms = Classroom.objects.all()

    if int(classroom_id)>0:
        instance = Classroom.objects.get(pk=classroom_id)
    else:
        instance = Classroom()


    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=instance)
        print form
        if form.is_valid():
            form.save()
            #then return
            return HttpResponseRedirect('/mande/school-management/classrooms/'+str(classroom_id))
    else:
        form = ClassroomForm(instance=instance)


    context = {'form': form, 'classroom_id':classroom_id, 'current_classrooms':current_classrooms}
    return render(request, 'mande/classroomform.html', context)

def classroomteacher_form(request, teacher_id=0):
    current_assignments = ClassroomTeacher.objects.all()

    classrooms_with_teachers = []
    for classroom in current_assignments:
        classrooms_with_teachers.append(int(classroom.classroom_id.classroom_id))

    unassigned_classrooms = Classroom.objects.all().exclude(classroom_id__in=classrooms_with_teachers)

    if int(teacher_id)>0:
        current_assignments = current_assignments.filter(teacher_id=teacher_id)

    if request.method == 'POST':
        form = ClassroomTeacherForm(request.POST)
        print form
        if form.is_valid():
            form.save()
            #then return
            return HttpResponseRedirect('/mande/school-management/classrooms/assignment/'+str(teacher_id))
    else:
        form = ClassroomTeacherForm()


    context = {'form': form, 'teacher_id':teacher_id, 'current_assignments':current_assignments, 'unassigned_classrooms':unassigned_classrooms}
    return render(request, 'mande/classroomteacherform.html', context)

def classroomenrollment_form(request,student_id=0):

    if request.method == 'POST':
        classroom_id = Classroom.objects.get(pk=request.POST.get('classroom_id'))
        enrollment_date = request.POST.get('enrollment_date')

        for student in request.POST.getlist('student_id'):
            student_id = IntakeSurvey.objects.get(pk=student)
            enrollment = ClassroomEnrollment(classroom_id=classroom_id, student_id=student_id, enrollment_date=enrollment_date)
            enrollment.save()

        return HttpResponseRedirect('/mande/success/')
    else:
        if student_id > 0:
            form = ClassroomEnrollmentForm({'student_id':student_id})
        else:
            form = ClassroomEnrollmentForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/classroomenrollmentform.html', context)
