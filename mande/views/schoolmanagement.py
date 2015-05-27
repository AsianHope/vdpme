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

def student_list(request):
    #get enrolled and accepted students
    exit_surveys = ExitSurvey.objects.all().filter(
                        exit_date__lte=date.today().isoformat()
                        ).values_list('student_id',flat=True)
    surveys = IntakeSurvey.objects.order_by('student_id').exclude(student_id__in=exit_surveys)
    at_grade_level = {}
    for student in surveys:
            at_grade_level[student.student_id] = studentAtAgeAppropriateGradeLevel(student.student_id)
    context = {'surveys': surveys, 'at_grade_level':at_grade_level}
    return render(request, 'mande/studentlist.html', context)

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
    submit_enabled = True
    if attendance_date != date.today().isoformat():
        warning = 'The selected date is not today!'
    else:
        warning = ''

    classroom = Classroom.objects.get(pk=classroom_id)
    students = ClassroomEnrollment.objects.filter(classroom_id=classroom_id).exclude(drop_date__lte=attendance_date)

    #find out if any student attendance has been taken, excluding placeholder attendance
    student_attendance = Attendance.objects.filter(student_id=students, date=attendance_date).exclude(attendance=None)
    if len(student_attendance) > 0:
        message = 'Attendance for one or more students has been taken'

    #pre instantiate data for this form so that we can update the whole queryset later
    for student in students:
        Attendance.objects.get_or_create(student_id=student.student_id, date=attendance_date, defaults={'attendance':None, 'classroom':classroom})

    try:
        offered = AttendanceDayOffering.objects.get(classroom_id=classroom_id,date=attendance_date)
    except ObjectDoesNotExist:
        submit_enabled = False
        Attendance.objects.filter(attendance=None).delete()

    #now get the whole set of attendance objects and create the formset
    student_attendance = Attendance.objects.filter(student_id=students, date=attendance_date)
    AttendanceFormSet = modelformset_factory(Attendance, form=AttendanceForm, extra=0)

    if request.method == 'POST':

        formset = AttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()

            #zero things out
            absent = 0
            present = 0
            attendancecodes = dict(ATTENDANCE_CODES)
            for key,code in attendancecodes.iteritems():
                attendancecodes[key]=0
            #count attendance codes
            for form in formset:
                attendancecodes[form.cleaned_data['attendance']] +=1
                #attendance codes with 'A' in them mean absences.
                if 'A' in form.cleaned_data['attendance']:
                    absent +=1
                else:
                    present +=1


            alog,created = AttendanceLog.objects.get_or_create( classroom=classroom,
                                                                date=attendance_date,
                                                              )
            alog.absent = absent
            alog.present = present
            alog.save()
            message = 'Took attendance for '+unicode(classroom) + ' (A:'+unicode(absent)+',P:'+unicode(present)+')'
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-check-square')
            log.save()
            #clean up the mess we created making blank rows to update.
            Attendance.objects.filter(attendance=None).delete()

    else:
        formset = AttendanceFormSet(queryset = student_attendance)
    context= {  'classroom':classroom,
                'students':students,
                'attendance_date':attendance_date,
                'formset':formset,
                'warning': mark_safe(warning),
                'message': message,
                'submit_enabled': submit_enabled}

    return render(request, 'mande/takeclassattendanceformset.html', context)

def take_attendance(request):
    classrooms = Classroom.objects.all()
    context= {'classrooms':classrooms, 'attendance_date':date.today().isoformat()}
    return render(request, 'mande/takeattendance.html', context)

def student_detail(request, student_id):
    survey = IntakeSurvey.objects.get(pk=student_id)
    updates = survey.intakeupdate_set.all().filter().order_by('-date')
    intake = survey.intakeinternal_set.all().filter().order_by('-enrollment_date')

    try:
        exit_survey = survey.exitsurvey_set.all()[0]
    except IndexError:
        exit_survey = None
    try:
        post_exit_survey = survey.postexitsurvey_set.all()[0]
    except IndexError:
        post_exit_survey = None

    #select only semester tests which have grades in them
    academics = survey.academic_set.all().filter(
        Q(test_grade_khmer__isnull=False) & Q(test_grade_math__isnull=False)).order_by('-test_level')
    discipline = survey.discipline_set.all().filter().order_by('-incident_date')
    dental = survey.health_set.all().filter(appointment_type='DENTAL').order_by('-appointment_date')
    checkups = survey.health_set.all().filter(appointment_type='CHECKUP').order_by('-appointment_date')
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
        #their current grade is one more than that of the last test they passed
        current_grade = (academics.filter(promote=True).latest('test_level').test_level)+1
    except ObjectDoesNotExist:
        current_grade = recent_intake.starting_grade if type(recent_intake) != str else None

    graduation = survey.dob +timedelta(days=365*12) if survey.dob is not None else "No birthday entered"
    context = {
        'survey':survey,
        'updates':updates,
        'recent_update':recent_update,
        'recent_intake':recent_intake,
        'academics':academics,
        'current_grade':current_grade,
        'discipline':discipline,
        'dental':dental,
        'checkups':checkups,
        'cur_year':date.today().year,
        'graduation': graduation,
        'classroomenrollment':classroomenrollment,
        'attendance_present':attendance_present,
        'attendance_approved_absence':attendance_approved_absence,
        'attendance_unapproved_absence':attendance_unapproved_absence,
        'exit_survey':exit_survey,
        'post_exit_survey':post_exit_survey}
    return render(request, 'mande/detail.html', context)

def discipline_form(request,student_id=0):

    if request.method == 'POST':
        form = DisciplineForm(request.POST)

        if form.is_valid():
            #process
            instance = form.save()
            message = 'Logged discipline for '+unicode(instance.student_id.name)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-meh-o')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail',kwargs={'student_id':instance.student_id.student_id}))
    else:
        if student_id > 0:
            form = DisciplineForm({'student_id':student_id})
        else:
            form = DisciplineForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/disciplineform.html', context)

def teacher_form(request, teacher_id=0):
    current_teachers = Teacher.objects.all()
    action = None

    if int(teacher_id)>0:
        instance = Teacher.objects.get(pk=teacher_id)
        action = 'editing '+str(instance)
    else:
        instance = Teacher()
        action = None

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            message = 'Added a new teacher: '+unicode(instance.name) if action is None else 'Updated '+unicode(instance.name)+'\'s name'
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-street-view')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('teacher_form'))
    else:
            form = TeacherForm(instance=instance)

    context = {'form': form, 'teacher_id':teacher_id,'current_teachers':current_teachers, 'action':action}
    return render(request, 'mande/teacherform.html', context)

def classroom_form(request, classroom_id=0):
    current_classrooms = Classroom.objects.all()

    if int(classroom_id)>0:
        instance = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrollments = instance.classroomenrollment_set.all().filter(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))
    else:
        instance = Classroom()
        enrollments = None


    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            message = 'Added classroom '+unicode(instance) if int(classroom_id)==0 else 'Edited classroom '+unicode(instance)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-university')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('classroom_form', kwargs={'classroom_id':instance.classroom_id}))
    else:
        form = ClassroomForm(instance=instance)


    context = {'form': form, 'classroom_id': classroom_id, 'selected_classroom':instance, 'current_classrooms':current_classrooms, 'enrollments':enrollments}
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
            instance = form.save()
            message = 'Made '+unicode(instance.teacher_id)+' teacher of '+unicode(instance.classroom_id)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-pencil')
            log.save()
            #then return
            return HttpResponseRedirect(reverse(classroomteacher_form, kwargs={'teacher_id':teacher_id}))
    else:
        form = ClassroomTeacherForm()


    context = {'form': form, 'teacher_id':teacher_id, 'current_assignments':current_assignments, 'unassigned_classrooms':unassigned_classrooms}
    return render(request, 'mande/classroomteacherform.html', context)

def classroomenrollment_form(request,classroom_id=0):

    if int(classroom_id)>0:
        instance = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrolled_students = instance.classroomenrollment_set.all().filter(Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))
    else:
        instance = None;
        enrolled_students = None


    if request.method == 'POST':
        #can't rely on classroom_id set by url - it may have been changed by the user.
        classroom_id = Classroom.objects.get(pk=request.POST.get('classroom_id'))
        enrollment_date = request.POST.get('enrollment_date')

        #this seems janky to me - surely there is a better way?
        for student in request.POST.getlist('student_id'):
            student_id = IntakeSurvey.objects.get(pk=student)
            e_date, enrollment = ClassroomEnrollment.objects.get_or_create(classroom_id=classroom_id, student_id=student_id)
            e_date.enrollment_date = enrollment_date
            e_date.save()
        num = len(request.POST.getlist('student_id'))
        message = 'Added '+str(num)+' students to '+unicode(classroom_id) if num >1 else 'Added '+str(num)+' student to '+unicode(classroom_id)
        log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-level-up')
        log.save()
        return HttpResponseRedirect(reverse('classroomenrollment_form', kwargs={'classroom_id':classroom_id.classroom_id}))
    else:
        if classroom_id > 0:
            form = ClassroomEnrollmentForm({'classroom_id':classroom_id, 'enrollment_date':date.today().isoformat()})
        else:
            form = ClassroomEnrollmentForm()

    context = {'form': form,'classroom':instance, 'enrolled_students':enrolled_students}
    return render(request, 'mande/classroomenrollmentform.html', context)


def classroomenrollment_individual(request,student_id=0,classroom_id=0):

    if request.method == 'POST':
        next_url = request.GET.get('next')
        #get_or_create returns a tuple with the object and its status
        instance = ClassroomEnrollment.objects.get(classroom_id=classroom_id,student_id=student_id)

        instance.drop_date = request.POST.get('drop_date')
        instance.save()

        message = 'Dropped '+unicode(instance.student_id.name)+' from '+unicode(instance.classroom_id)
        log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-bell-slash')
        log.save()
        #then return
        return HttpResponseRedirect(next_url)
    else:
        if student_id > 0:
            instance = ClassroomEnrollment.objects.get(classroom_id=classroom_id,student_id=student_id)
            form = IndividualClassroomEnrollmentForm(instance=instance)
        else:
            form = IndividualClassroomEnrollmentForm()

    context = {'form': form,'student_id':student_id, 'classroom_id':classroom_id}
    return render(request, 'mande/classroomenrollmentindividual.html', context)

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
        #TODO: figure out a way to not group requests for slimmer logging
        return render(request,'mande/attendancedays.html','')

    #otherwise display the calendar
    else:
        attendance_days = AttendanceDayOffering.objects.filter(classroom_id=classroom).filter(date__year=attendance_date.year, date__month=attendance_date.month)
        lCalendar = AttendanceCalendar(attendance_days).formatmonth(attendance_date.year,attendance_date.month)

        return render(request, 'mande/attendancedays.html', {'Calendar' : mark_safe(lCalendar),
                                                       'classroom': classroom,
                                                   })

def daily_attendance_report(request,attendance_date=date.today().isoformat()):
    #only classrooms who take attendance, and who take attendance today.
    classrooms = Classroom.objects.all().filter(active=True)
    takesattendance = AttendanceDayOffering.objects.filter(date=attendance_date).values_list('classroom_id',flat=True)
    classrooms = classrooms.filter(classroom_id__in=takesattendance)

    classroomattendance = {}
    for classroom in classrooms:
        try:
            classroomattendance[classroom] = AttendanceLog.objects.get(classroom=classroom,date=attendance_date)
        except ObjectDoesNotExist:
            classroomattendance[classroom] = None

    return render(request, 'mande/attendancereport.html',
                            {'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date
                                                                        })

def daily_absence_report(request,attendance_date=date.today().isoformat()):
    #only classrooms who take attendance, and who take attendance today.
    classrooms = Classroom.objects.all().filter(active=True)
    takesattendance = AttendanceDayOffering.objects.filter(date=attendance_date).values_list('classroom_id',flat=True)
    classrooms = classrooms.filter(classroom_id__in=takesattendance)

    classroomattendance = {}
    for classroom in classrooms:
        try:
            #only displays unexcused absences
            classroomattendance[classroom] = Attendance.objects.filter(classroom=classroom,date=attendance_date,attendance='UA')
        except ObjectDoesNotExist:
            classroomattendance[classroom] = None

    return render(request, 'mande/absencereport.html',
                            {'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date
                                                                        })


def academic_form(request, school_id, test_date=date.today().isoformat(), grade_id=None):
    school = School.objects.get(pk=school_id)
    warning = ''
    message = ''
    students = IntakeSurvey.objects.all().filter(site=school_id)

    #find out if any student acadmics have been recorded
    student_academics = Academic.objects.filter(student_id=students, test_date=test_date)

    #pre instantiate data for this form so that we can update the whole queryset later
    if grade_id is None:
        for student in students:
            Academic.objects.get_or_create(student_id=student, test_date=test_date, test_level=getStudentGradebyID(student.student_id))
        student_academics = Academic.objects.filter(student_id=students, test_date=test_date)

    else:
        for student in students:
            if getStudentGradebyID(student.student_id) == int(grade_id):
                Academic.objects.get_or_create(student_id=student, test_date=test_date, test_level=grade_id)
        student_academics = Academic.objects.filter(student_id=students, test_date=test_date, test_level=grade_id)

    AcademicFormSet = modelformset_factory(Academic, form=AcademicForm, extra=0)

    if request.method == 'POST':
        formset = AcademicFormSet(request.POST)

        if formset.is_valid():
            formset.save()
            message = "Saved."
            #clean up the mess we created making blank rows to update.
            Academic.objects.filter(Q(test_grade_khmer=None)&Q(test_grade_math=None)).delete()
            if grade_id is None:
                message = 'Recorded semester tests for '+str(school)
            else:
                message = 'Recorded semester tests for '+str(dict(GRADES)[int(grade_id)])+' at '+str(school)
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-calculator')
            log.save()

    else:
        formset = AcademicFormSet(queryset = student_academics)
    context= {  'school':school,
                'grade_id': grade_id,
                'students':students,
                'test_date':test_date,
                'formset':formset,
                'warning': mark_safe(warning),
                'message': message,
                'grades': dict(GRADES)
    }

    return render(request, 'mande/academicform.html', context)

def academic_select(request):
    schools = School.objects.all()
    context = { 'schools':schools,
                'grades': dict(GRADES),
                'today': date.today().isoformat(),
    }
    return render(request, 'mande/academicselect.html',context)

def academic_form_single(request, student_id=0):
    if request.method == 'POST':
        form = AcademicForm(request.POST)
        if form.is_valid():
            #process
            instance = form.save()
            message = 'Recorded semester test for '+instance.student_id.name
            log = NotificationLog(user=request.user, text=message, font_awesome_icon='fa-calculator')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail',kwargs={'student_id':instance.student_id.student_id}))
    else:
        if student_id > 0:
            form = AcademicForm({'student_id':student_id, 'test_date':date.today().isoformat(),'test_level':getStudentGradebyID(student_id)})
        else:
            form = AcademicForm()

    context = {'form': form,'student_id':student_id}

    return render(request, 'mande/academicformsingle.html',context)
