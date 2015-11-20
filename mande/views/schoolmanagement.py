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
from mande.models import StudentEvaluation

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
from mande.forms import StudentEvaluationForm

from mande.utils import getEnrolledStudents
from mande.utils import getStudentGradebyID
from mande.utils import studentAtSchoolGradeLevel
from mande.utils import studentAtAgeAppropriateGradeLevel

from django.contrib.auth.models import User

'''
*****************************************************************************
Student List
 - display a list of currently enrolled students
*****************************************************************************
'''
def student_list(request):
    #get enrolled and accepted students
    exit_surveys = ExitSurvey.objects.all().filter(
                        exit_date__lte=date.today().isoformat()
                        ).values_list('student_id',flat=True)
    active_surveys = IntakeSurvey.objects.order_by('student_id'
                                 ).exclude(student_id__in=exit_surveys)
    surveys = []
    for active_survey in active_surveys:
        surveys.append(active_survey.getRecentFields())
    at_grade_level = {}
    for student in surveys:
            at_grade_level[student['student_id']] = (
                            studentAtAgeAppropriateGradeLevel(student['student_id']))
    context = {'surveys': surveys, 'at_grade_level':at_grade_level}
    return render(request, 'mande/studentlist.html', context)

'''
*****************************************************************************
Student Detail
 - display a detailed view of all student information
*****************************************************************************
'''
def student_detail(request, student_id):
    survey = IntakeSurvey.objects.get(pk=student_id)
    intake = survey.intakeinternal_set.all().filter().order_by(
                                                        '-enrollment_date'
                                                    )
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
        Q(test_grade_khmer__isnull=False) &
        Q(test_grade_math__isnull=False)).order_by('-test_level')

    evaluations = survey.studentevaluation_set.all().order_by('-date').exclude(
                                                        Q(academic_score=None)&
                                                        Q(study_score=None)&
                                                        Q(personal_score=None)&
                                                        Q(hygiene_score=None)&
                                                        Q(faith_score=None)
    )

    notes = survey.getNotes()
    discipline = survey.discipline_set.all().filter().order_by('-incident_date')
    dental = survey.health_set.all().filter(
                                        appointment_type='DENTAL'
                                    ).order_by('-appointment_date')
    checkups = survey.health_set.all().filter(
                                        appointment_type='CHECKUP'
                                        ).order_by('-appointment_date')

    classroomenrollment = survey.classroomenrollment_set.all().filter().order_by('drop_date')
    attendance_present = survey.attendance_set.all().filter(attendance='P').count()
    attendance_approved_absence = survey.attendance_set.all().filter(attendance='AA').count()
    attendance_unapproved_absence = survey.attendance_set.all().filter(attendance='UA').count()

    if len(intake) > 0:
        recent_intake = intake[0]
    else:
        recent_intake = 'Not enrolled'

    current_grade = getStudentGradebyID(student_id)
    graduation = survey.dob +timedelta(days=365*12) if survey.dob is not None else "No birthday entered"
    context = {
        'survey': survey.getRecentFields(),
        'recent_intake':recent_intake,
        'academics':academics,
        'evaluations':evaluations,
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
        'post_exit_survey':post_exit_survey,
        'notes':notes,
        'TODAY':date.today().isoformat()}
    return render(request, 'mande/detail.html', context)
'''
*****************************************************************************
Discipline Form
 - process a DisciplineForm and log the action
*****************************************************************************
'''
def discipline_form(request,student_id=0):

    if request.method == 'POST':
        form = DisciplineForm(request.POST)

        if form.is_valid():
            #process
            instance = form.save()
            message = 'Logged discipline for '+unicode(instance.student_id.name)
            log = NotificationLog(user=request.user,
                                  text=message,
                                  font_awesome_icon='fa-meh-o')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('student_detail',kwargs=
                                {'student_id':instance.student_id.student_id}))
    else:
        if student_id > 0:
            form = DisciplineForm({'student_id':student_id})
        else:
            form = DisciplineForm()

    context = {'form': form,'student_id':student_id}
    return render(request, 'mande/disciplineform.html', context)

'''
*****************************************************************************
Teacher Form
 - process a TeacherForm and log the action
*****************************************************************************
'''
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
            stem = 'Added a new teacher:' if action is None else 'Updated teachers name:'
            message = stem+unicode(instance.name)
            log = NotificationLog(user=request.user,
                                  text=message,
                                  font_awesome_icon='fa-street-view')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('teacher_form'))
    else:
            form = TeacherForm(instance=instance)

    context = { 'form': form,
                'teacher_id':teacher_id,
                'current_teachers':current_teachers,
                'action':action}
    return render(request, 'mande/teacherform.html', context)

'''
*****************************************************************************
Classroom Form
 - process a ClassroomForm and log the action
*****************************************************************************
'''
def classroom_form(request, classroom_id=0):
    current_classrooms = Classroom.objects.all()

    if int(classroom_id)>0:
        instance = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrollments = instance.classroomenrollment_set.all().filter(
                        Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))
    else:
        instance = Classroom()
        enrollments = None


    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            stem = 'Added classroom ' if int(classroom_id)==0 else 'Edited classroom '
            message = stem+unicode(instance)
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-university')
            log.save()
            #then return
            return HttpResponseRedirect(reverse('classroom_form', kwargs=
                                        {'classroom_id':instance.classroom_id}))
    else:
        form = ClassroomForm(instance=instance)


    context = { 'form': form,
                'classroom_id': classroom_id,
                'selected_classroom':instance,
                'current_classrooms':current_classrooms,
                'enrollments':enrollments}
    return render(request, 'mande/classroomform.html', context)
'''
*****************************************************************************
Discipline Form
 - process a ClassroomTeacherForm and log the action
*****************************************************************************
'''
def classroomteacher_form(request, teacher_id=0):
    current_assignments = ClassroomTeacher.objects.all()

    classrooms_with_teachers = []
    for classroom in current_assignments:
        classrooms_with_teachers.append(int(classroom.classroom_id.classroom_id))

    unassigned_classrooms = Classroom.objects.all().filter(active=True).exclude(
                                    classroom_id__in=classrooms_with_teachers)
    if int(teacher_id)>0:
        current_assignments = current_assignments.filter(teacher_id=teacher_id)

    if request.method == 'POST':
        form = ClassroomTeacherForm(request.POST)
        if form.is_valid():
            instance = form.save()
            message = ('Made '+unicode(instance.teacher_id)+
                       ' teacher of '+unicode(instance.classroom_id))
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-pencil')
            log.save()
            #then return
            return HttpResponseRedirect(reverse(classroomteacher_form, kwargs=
                                                     {'teacher_id':teacher_id}))
    else:
        form = ClassroomTeacherForm()


    context = { 'form': form,
                'teacher_id':teacher_id,
                'current_assignments':current_assignments,
                'unassigned_classrooms':unassigned_classrooms}
    return render(request, 'mande/classroomteacherform.html', context)

'''
*****************************************************************************
Classroom Enrollment Form
 - process a ClassroomEnrollmentForm and log the action
*****************************************************************************
'''
def classroomenrollment_form(request,classroom_id=0):

    if int(classroom_id)>0:
        instance = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrolled_students = instance.classroomenrollment_set.all().filter(
                                    Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))
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
            e_date, enrollment = ClassroomEnrollment.objects.get_or_create(
                                                    classroom_id=classroom_id,
                                                    student_id=student_id)
            e_date.enrollment_date = enrollment_date
            e_date.save()
        num = len(request.POST.getlist('student_id'))
        plural = 's' if num>1 else ''
        message = 'Added '+str(num)+' student'+plural+' to '+unicode(classroom_id)
        log = NotificationLog(  user=request.user,
                                text=message,
                                font_awesome_icon='fa-level-up')
        log.save()
        return HttpResponseRedirect(reverse('classroomenrollment_form', kwargs=
                                    {'classroom_id':classroom_id.classroom_id}))
    else:
        if classroom_id > 0:
            form = ClassroomEnrollmentForm({'classroom_id':classroom_id,
                                            'enrollment_date':date.today().isoformat()})
        else:
            form = ClassroomEnrollmentForm()

    context = { 'form': form,
                'classroom':instance,
                'enrolled_students':enrolled_students}

    return render(request, 'mande/classroomenrollmentform.html', context)

'''
*****************************************************************************
Classroom Enrollment Individual
 - process an IndividualClassroomEnrollmentForm and log the action
*****************************************************************************
'''
def classroomenrollment_individual(request,student_id=0,classroom_id=0):

    if request.method == 'POST':
        next_url = request.GET.get('next')
        #get_or_create returns a tuple with the object and its status
        instance = ClassroomEnrollment.objects.get(classroom_id=classroom_id,
                                                          student_id=student_id)

        instance.drop_date = request.POST.get('drop_date')
        instance.save()

        message = ( 'Dropped '+unicode(instance.student_id.name)+
                    ' from '+unicode(instance.classroom_id))
        log = NotificationLog(  user=request.user,
                                text=message,
                                font_awesome_icon='fa-bell-slash')
        log.save()
        #then return
        return HttpResponseRedirect(next_url)
    else:
        if student_id > 0:
            instance = ClassroomEnrollment.objects.get( classroom_id=classroom_id,
                                                        student_id=student_id)
            form = IndividualClassroomEnrollmentForm(instance=instance)
        else:
            form = IndividualClassroomEnrollmentForm()

    context = {'form': form,'student_id':student_id, 'classroom_id':classroom_id}
    return render(request, 'mande/classroomenrollmentindividual.html', context)

'''
*****************************************************************************
Academic Form
 - process a AcademicForm and log the action
*****************************************************************************
'''
def academic_form(request, school_id, test_date=date.today().isoformat(), grade_id=None):
    school = School.objects.get(pk=school_id)
    warning = ''
    message = ''

    #find only currently enrolled students
    exit_surveys = ExitSurvey.objects.all().filter(
                        exit_date__lte=date.today().isoformat()
                        ).values_list('student_id',flat=True)
    students = IntakeSurvey.objects.all().order_by('student_id'
                                 ).exclude(student_id__in=exit_surveys).filter(site=school_id)

    #find out if any student acadmics have been recorded
    student_academics = Academic.objects.filter(student_id=students, test_date=test_date)

    #pre instantiate data for this form so that we can update the whole queryset later
    if grade_id is None:
        for student in students:
            Academic.objects.get_or_create(
                                            student_id=student,
                                            test_date=test_date,
                                            test_level=getStudentGradebyID(student.student_id))
        student_academics = Academic.objects.filter(student_id=students,
                                                    test_date=test_date)

    else:
        for student in students:
            if getStudentGradebyID(student.student_id) == int(grade_id):
                Academic.objects.get_or_create( student_id=student,
                                                test_date=test_date,
                                                test_level=grade_id)

        student_academics = Academic.objects.filter(student_id=students,
                                                    test_date=test_date,
                                                    test_level=grade_id)

    AcademicFormSet = modelformset_factory(Academic, form=AcademicForm, extra=0)

    if request.method == 'POST':
        formset = AcademicFormSet(request.POST)

        if formset.is_valid():
            formset.save()
            message = "Saved."
            #clean up the mess we created making blank rows to update.
            Academic.objects.filter(
                                        Q(test_grade_khmer=None)&
                                        Q(test_grade_math=None)
                                    ).delete()
            if grade_id is None:
                message = 'Recorded semester tests for '+str(school)
            else:
                message = ('Recorded semester tests for '+
                            str(dict(GRADES)[int(grade_id)])+
                            ' at '+str(school))
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-calculator')
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
'''
*****************************************************************************
Academic Select
 - display a list of all grades for each school
*****************************************************************************
'''
def academic_select(request):
    schools = School.objects.all()
    context = { 'schools':schools,
                'grades': dict(GRADES),
                'today': date.today().isoformat(),
    }
    return render(request, 'mande/academicselect.html',context)

'''
*****************************************************************************
Academic Form Single
 - process a single AcademicForm for requested student and log the action
*****************************************************************************
'''
def academic_form_single(request, student_id=0):
    if request.method == 'POST':
        form = AcademicForm(request.POST)
        if form.is_valid():
            #process
            instance = form.save()
            message = 'Recorded semester test for '+instance.student_id.name
            log = NotificationLog(user=request.user,
                                  text=message,
                                  font_awesome_icon='fa-calculator')
            log.save()
            #then return
            return HttpResponseRedirect(
                        reverse('student_detail',
                                kwargs={'student_id':instance.student_id.student_id}))
    else:
        if student_id > 0:
            form = AcademicForm({
                    'student_id':student_id,
                    'test_date':date.today().isoformat(),
                    'test_level':getStudentGradebyID(student_id)})
        else:
            form = AcademicForm()

    context = {'form': form,'student_id':student_id}

    return render(request, 'mande/academicformsingle.html',context)


'''
*****************************************************************************
Student Evaluation Form
 - process a StudentEvaluationForm and log the action
*****************************************************************************
'''
def studentevaluation_form(request, school_id, date=date.today().isoformat(), grade_id=None):
    school = School.objects.get(pk=school_id)
    warning = ''
    message = ''
    if grade_id is None:
       get_enrolled_student = getEnrolledStudents()
    else:
       get_enrolled_student= getEnrolledStudents(int(grade_id))
    students = get_enrolled_student
    #pre instantiate data for this form so that we can update the whole queryset later
    students_at_school_id = []
    for student in students:
        if student.site == school:
            StudentEvaluation.objects.get_or_create(
                                            student_id=student,date=date)
            students_at_school_id.append(student.student_id)

    #lets only work with the students at the specified school_id
    students = students_at_school_id
    student_evaluations = StudentEvaluation.objects.filter(student_id__in=students,
                                                date=date)


    StudentEvaluationFormSet = modelformset_factory(StudentEvaluation, form=StudentEvaluationForm, extra=0)

    if request.method == 'POST':
        formset = StudentEvaluationFormSet(request.POST)
        print "Is formset valid?"
        if formset.is_valid():
            print "yes!s"
            formset.save()
            message = "Saved."
            if grade_id is None:
                message = 'Recorded student evaluations for '+str(school)
            else:
                message = ('Recorded student evaluations for '+
                            str(dict(GRADES)[int(grade_id)])+
                            ' at '+str(school))
            log = NotificationLog(  user=request.user,
                                    text=message,
                                    font_awesome_icon='fa-calculator')
            log.save()
        else:
            warning = 'Cannot record student evaluations. Please try again.'
            students = get_enrolled_student
            students_at_school_id = []
            for student in students:
                if student.site == school:
                    StudentEvaluation.objects.get_or_create(
                                                    student_id=student,date=date)
                    students_at_school_id.append(student.student_id)

            #lets only work with the students at the specified school_id
            students = students_at_school_id
            student_evaluations = StudentEvaluation.objects.filter(student_id__in=students,
                                                            date=date)

            formset = StudentEvaluationFormSet(queryset = student_evaluations)
    else:
        formset = StudentEvaluationFormSet(queryset = student_evaluations)
    context= {  'school':school,
                'grade_id': grade_id,
                'students':students,
                'date':date,
                'formset':formset,
                'warning': mark_safe(warning),
                'message': message,
                'grades': dict(GRADES)
    }

    return render(request, 'mande/studentevaluationform.html', context)
'''
*****************************************************************************
Student Evaluation Select
 - display a list of all grades for each school
*****************************************************************************
'''
def studentevaluation_select(request):
    schools = School.objects.all()
    context = { 'schools':schools,
                'grades': dict(GRADES),
                'today': date.today().isoformat(),
    }
    return render(request, 'mande/studentevaluationselect.html',context)

'''
*****************************************************************************
Student Evaluation Form Single
 - process a single StudentEvaluationForm for requested student and log the action
*****************************************************************************
'''
def studentevaluation_form_single(request, student_id=0):
    form = StudentEvaluationForm()
    date = request.POST.get('date') if request.method=='POST' else date.today().isoformat()

    if student_id > 0:
        try:
            instance = StudentEvaluation.objects.get(student_id=IntakeSurvey.objects.get(pk=student_id),
                                  date=date)
            form = StudentEvaluationForm(instance=instance)
        except ObjectDoesNotExist:
            form = StudentEvaluationForm({
                    'student_id':student_id,
                    'date':date.today().isoformat()})

    if request.method == 'POST':
        # delete StudentEvaluation where academic_score, study_score... is None so we can add a new StudentEvaluation
        StudentEvaluation.objects.filter(
              Q(academic_score=None) & Q(study_score=None) & Q(personal_score=None) & Q(hygiene_score=None) & Q(faith_score=None)
         ).delete()
        form = StudentEvaluationForm(request.POST)
        if form.is_valid():
            #process
            instance = form.save()
            message = 'Recorded student evaluation for '+instance.student_id.name
            log = NotificationLog(user=request.user,
                                  text=message,
                                  font_awesome_icon='fa-calculator')
            log.save()
            #then return
            return HttpResponseRedirect(
                        reverse('student_detail',
                                kwargs={'student_id':instance.student_id.student_id}))

    context = {'form': form,'student_id':student_id}

    return render(request, 'mande/studentevaluationformsingle.html',context)
