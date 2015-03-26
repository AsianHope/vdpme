from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory

from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
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
from mande.forms import AttendanceForm


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
    attendance_date = date.today().replace(day=1).isoformat()
    context= {'classrooms':classrooms, 'attendance_date':attendance_date}
    return render(request, 'mande/attendancecalendar.html', context)


def take_class_attendance(request, classroom_id, attendance_date=date.today().isoformat()):
    message = ''
    if attendance_date != date.today().isoformat():
        warning = 'The selected date is not today!'
    else:
        warning = ''

    classroom = Classroom.objects.get(pk=classroom_id)
    students = ClassroomEnrollment.objects.filter(classroom_id=classroom_id).exclude(drop_date__lte=attendance_date)

    #pre instantiate data for this form so that we can update the whole queryset later
    for student in students:
        Attendance.objects.get_or_create(student_id=student.student_id, date=attendance_date, defaults={'attendance':None})

    #now get the whole set of attendance objects and create the formset
    student_attendance = Attendance.objects.filter(student_id=students, date=attendance_date)
    AttendanceFormSet = modelformset_factory(Attendance, form=AttendanceForm, extra=0)

    if request.method == 'POST':

        formset = AttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            message = "Attendance saved."
            #clean up the mess we created making blank rows to update.
            Attendance.objects.filter(attendance=None).delete()

    else:
        formset = AttendanceFormSet(queryset = student_attendance)
    context= {  'classroom':classroom,
                'students':students,
                'attendance_date':attendance_date,
                'formset':formset,
                'warning': warning,
                'message': message}

    return render(request, 'mande/takeclassattendanceformset.html', context)

def take_attendance(request):
    classrooms = Classroom.objects.all()
    context= {'classrooms':classrooms, 'attendance_date':date.today().isoformat()}
    return render(request, 'mande/takeattendance.html', context)



def student_detail(request, student_id):
    survey = IntakeSurvey.objects.get(pk=student_id)
    updates = survey.intakeupdate_set.all().filter().order_by('-date')
    intake = survey.intakeinternal_set.all().filter().order_by('-enrollment_date')
    academics = survey.academic_set.all().filter().order_by('-test_date')
    discipline = survey.discipline_set.all().filter().order_by('-incident_date')
    classroomenrollment = survey.classroomenrollment_set.all().filter().order_by('drop_date')
    attendance_present = survey.attendance_set.all().filter(attendance='P').count()
    attendance_approved_absence = survey.attendance_set.all().filter(attendance='AA').count()
    attendance_unapproved_absence = survey.attendance_set.all().filter(attendance='UA').count()
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

    graduation = survey.dob +timedelta(days=365*12) if survey.dob is not None else "No birthday entered"
    context = {
        'survey':survey,
        'updates':updates,
        'recent_update':recent_update,
        'recent_intake':recent_intake,
        'academics':academics,
        'current_grade':current_grade,
        'discipline':discipline,
        'cur_year':date.today().year,
        'graduation': graduation,
        'classroomenrollment':classroomenrollment,
        'attendance_present':attendance_present,
        'attendance_approved_absence':attendance_approved_absence,
        'attendance_unapproved_absence':attendance_unapproved_absence}
    return render(request, 'mande/detail.html', context)

def intake_survey(request):
    if request.method == 'POST':
        form = IntakeSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success/')
    else:
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
        if form.is_valid():
            form.save()
            #then return
            return HttpResponseRedirect('/mande/success/')
    else:
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

        #this seems janky to me - surely there is a better way?
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

def attendance_days(request,classroom_id,attendance_date=date.today().isoformat()):

    attendance_date = datetime.strptime(attendance_date,'%Y-%m-%d')
    classroom = Classroom.objects.get(pk=classroom_id)


    #submitting a day to be added or removed
    if request.method == 'GET' and request.GET.get('day'):
        day = request.GET.get('day')
        #if we don't get an exception, we want to delete this object
        try:
            attendance_days = AttendanceDayOffering.objects.get(classroom_id=classroom,
                                                                date__year=attendance_date.year,
                                                                date__month=attendance_date.month,
                                                                date__day=day)
            attendance_days.delete()
        #if we do get an exception, we want to create this object
        except ObjectDoesNotExist:
            newday = datetime.strptime(str(attendance_date.year)+'-'+str(attendance_date.month)+'-'+str(day),'%Y-%m-%d')
            add = AttendanceDayOffering(classroom_id=classroom, date=newday)
            add.save()
        #TODO: make a success template so we can be smarter in our JS
        return render(request,'mande/attendancedays.html','')

    #otherwise display the calendar
    else:
        attendance_days = AttendanceDayOffering.objects.filter(classroom_id=classroom).filter(date__year=attendance_date.year, date__month=attendance_date.month)
        lCalendar = AttendanceCalendar(attendance_days).formatmonth(attendance_date.year,attendance_date.month)

        return render(request, 'mande/attendancedays.html', {'Calendar' : mark_safe(lCalendar),
                                                       'classroom': classroom,
                                                   })
