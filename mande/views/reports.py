from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from django.db.models import Q,Sum
from django.forms.models import model_to_dict

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

from mande.utils import getEnrolledStudents
from mande.utils import getStudentGradebyID
from mande.utils import studentAtSchoolGradeLevel
from mande.utils import studentAtAgeAppropriateGradeLevel
from mande.utils import getStudentAgeAppropriateGradeLevel

from django.contrib.auth.models import User


TODAY = date.today().isoformat()
TOO_YOUNG = 4
TOO_OLD = 18
'''
*****************************************************************************
Daily Attendance Report
 - lists all classrooms who take attendance and their attendance status
*****************************************************************************
'''
def daily_attendance_report(request,attendance_date=TODAY):
    #only classrooms who take attendance, and who take attendance today.
    classrooms = Classroom.objects.all().filter(active=True)
    takesattendance = AttendanceDayOffering.objects.filter(
                                                        date=attendance_date
                                                  ).values_list(
                                                       'classroom_id',flat=True)
    classrooms = classrooms.filter(classroom_id__in=takesattendance)

    classroomattendance = {}
    for classroom in classrooms:
        try:
            classroomattendance[classroom] = AttendanceLog.objects.get(
                                                           classroom=classroom,
                                                           date=attendance_date)
        except ObjectDoesNotExist:
            classroomattendance[classroom] = None

    return render(request, 'mande/attendancereport.html',
                            {'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date
                                                                        })
'''
*****************************************************************************
Daily Absence Report
 - lists all students with unexcuses absences for the day and their contact info
*****************************************************************************
'''
def daily_absence_report(request,attendance_date=TODAY):
    #only classrooms who take attendance, and who take attendance today.
    classrooms = Classroom.objects.all().filter(active=True)
    takesattendance = AttendanceDayOffering.objects.filter(
                                                        date=attendance_date
                                                  ).values_list(
                                                       'classroom_id',flat=True)
    classrooms = classrooms.filter(classroom_id__in=takesattendance)

    classroomattendance = {}
    for classroom in classrooms:
        try:
            #only displays unexcused absences
            classroomattendance[classroom] = Attendance.objects.filter(
                                                           classroom=classroom,
                                                           date=attendance_date,
                                                           attendance='UA')
        except ObjectDoesNotExist:
            classroomattendance[classroom] = None

    return render(request, 'mande/absencereport.html',
                            {'classroomattendance' : classroomattendance,
                             'attendance_date': attendance_date
                                                                        })
'''
*****************************************************************************
Data Audit
 - Generate a list of student records with missing or anomalous data
*****************************************************************************
'''
def data_audit(request,audit_type='ALL'):
    #modelfields = model_to_dict(IntakeSurvey.objects.all()[0])

    students = getEnrolledStudents()
    filters = []

    #a
    anomalies = {}

    for student in students:
        '''students with missing information'''
        text = 'Missing '
        resolution = reverse('intake_update',kwargs={'student_id':student.student_id})

        student_data = student.getRecentFields()
        temp = IntakeSurveyForm(data=student_data)
        for field in temp:
            #blank fields
            if ((field.data is None or len(unicode(field.data))==0) and
                field.label!="Notes" and
               (field.name=='reasons' and student_data['enrolled']=='N')): #students who aren't enrolled and have no reason
                    addAnomaly(anomalies, student, text+field.label, resolution)
                    filters.append(text+field.label)

        '''students who have grade and enrollment status mismatched'''
        if ((student_data['grade_last']<0 and student_data['enrolled']=='N') or #students who aren't enrolled and have no last grade
            (student_data['grade_current']<0 and student_data['enrolled']=='Y')): #students who are enrolled but don't have a current grade
            text = 'Enrollment status and grade data mismatch'
            resolution = reverse('intake_survey',kwargs={'student_id':student.student_id})
            addAnomaly(anomalies, student, text, resolution)
            filters.append(text)

        '''students who are quite young or quite old'''
        if (student.dob.year > (datetime.now().year-TOO_YOUNG)) or (student.dob.year<datetime.now().year-TOO_OLD):
            text = 'Incorrect DOB '
            age = '(~'+unicode(datetime.now().year-student.dob.year)+' years old)'
            resolution = reverse('intake_survey',kwargs={'student_id':student.student_id})
            limit = 'dob'

            addAnomaly(anomalies, student, text+age, resolution, limit)
            filters.append(text)
        '''students who have never been present'''
        if Attendance.objects.filter(student_id=student,attendance='P').count()==0:

            '''are either not enrolled'''
            if len(ClassroomEnrollment.objects.filter(student_id=student))==0:
                text = 'Not enrolled in any classes'
                resolution = reverse('classroomenrollment_form')
                addAnomaly(anomalies, student, text, resolution)
                filters.append(text)

            '''... or just not good at showing up!'''
            if Attendance.objects.filter(student_id=student).count()>0:
                text = 'Has never attended class'
                resolution = reverse('student_detail',kwargs={'student_id':student.student_id})
                addAnomaly(anomalies, student, text, resolution)
                filters.append(text)

    #remove duplicates in a now long array
    filters = set(filters)
    filters = sorted(filters)
    return render(request, 'mande/data_audit.html',
                            {'students' : anomalies,'filters':filters})


def addAnomaly(anomalies, student, text, resolution, limit=None):
    try:
        anomalies[student].append(
                            {'text':text,
                             'resolution':resolution,
                            'limit':limit})
    except KeyError:
        anomalies[student] = [{'text':text,
                               'resolution':resolution,
                               'limit':limit}]
    return anomalies

'''
*****************************************************************************
Class List
 - Generate a summary for each class in each site:
    + VDP Campus
    + Class Name
    + Teacher
    + # of Students Enrolled
*****************************************************************************
'''
def class_list(request,site='ALL'):
    class_list={}
    classrooms = Classroom.objects.all()
    for classroom in classrooms:
        instance = Classroom.objects.get(classroom_id=classroom.pk)
        class_list[classroom]={
            'site':classroom.school_id,
            'target_grade':classroom.cohort,
            'classroom_number':classroom.classroom_number,
            'teacher': 'Not assigned',
            'students': 0,
            'female': 0,
        }
        try:
            class_list[classroom]['teacher'] = ClassroomTeacher.objects.filter(classroom_id=classroom.pk)
        except ObjectDoesNotExist:
            pass
        try:
            enrolled_students =  instance.classroomenrollment_set.all().filter(
                                        Q(drop_date__gte=TODAY) | Q(drop_date=None))
            female_students = 0
            for student in enrolled_students:
                if student.student_id.gender == 'F':
                    female_students +=1
            class_list[classroom]['students'] = len(enrolled_students)
            class_list[classroom]['female'] = female_students
        except ObjectDoesNotExist:
            pass


    return render(request, 'mande/class_list.html',
                            {'class_list' : class_list,})
'''
*****************************************************************************
Student Absence Report
 - makes a summary of all students and lists their daily absences/presence
*****************************************************************************
'''
def student_absence_report(request):
    attendances = Attendance.objects.all()

    #set up dict of attendance codes with zero values
    default_attendance ={}
    attendancecodes = dict(ATTENDANCE_CODES)
    for key,code in attendancecodes.iteritems():
        default_attendance[key]=0

    #default out all current students
    attendance_by_sid = {}
    currently_enrolled_students = getEnrolledStudents()
    for student in currently_enrolled_students:
        attendance_by_sid[student]=dict(default_attendance)


    for attendance in attendances:
        try:
            attendance_by_sid[attendance.student_id][attendance.attendance] +=1
        except KeyError:
            pass; #students no longer in attendance that have attendance

    return render(request, 'mande/student_absence_report.html',
                                {'attendance_by_sid':attendance_by_sid, 'attendancecodes':attendancecodes})


'''
*****************************************************************************
Student Lag Report
 - makes a summary of all students and lists their daily absences/presence
*****************************************************************************
'''
def student_lag_report(request):
    enrolled_students = getEnrolledStudents()
    students_lag = {}
    for student in enrolled_students:
        #only students in the scope of grade levels
        if student.current_vdp_grade() < 12:
            students_lag[student] = student.age_appropriate_grade() - student.current_vdp_grade()

    return render(request, 'mande/student_lag_report.html',
                                {'students_lag':students_lag})


'''
*****************************************************************************
Student Evaluation Report
 - lists all student evaluations
*****************************************************************************
'''
def student_evaluation_report(request,classroom_id=None):
    evaluations = StudentEvaluation.objects.all().exclude(  academic_score=None,
                                                            study_score=None,
                                                            personal_score=None,
                                                            hygiene_score=None,
                                                            faith_score=None)
    active_classrooms = Classroom.objects.all().filter(active=True).order_by('classroom_location')
    if classroom_id is not None:
        selected_classroom = Classroom.objects.get(pk=classroom_id)
        #select students who have not dropped the class, or have not dropped it yet.
        enrolled_students = selected_classroom.classroomenrollment_set.all().filter(
                                Q(drop_date__gte=TODAY) | Q(drop_date=None)).values_list('student_id',flat=True)


        evaluations = evaluations.filter(student_id__in=enrolled_students)
    else:
        selected_classroom = None
    return render(request, 'mande/studentevaluationreport.html',
                                {'evaluations':evaluations, 'selected_classroom':selected_classroom, 'active_classrooms':active_classrooms})

'''
*****************************************************************************
Student Medical Report
 - lists all student medical visits
*****************************************************************************
'''
def student_medical_report(request):
    enrolled_students = getEnrolledStudents()
    visits = {}
    for student in enrolled_students:
        try:
            visits[student] = len(Health.objects.all().filter(student_id=student))
        except ObjectDoesNotExist:
            pass
    return render(request, 'mande/studentmedicalreport.html',
                                {'visits':visits})
'''
*****************************************************************************
Student Dental Report
 - lists all student Dental visits
*****************************************************************************
'''
def student_dental_report(request):
    dentals= Health.objects.all().filter(appointment_type='Dental')
    year = datetime.now().year-2013
    dentals_by_month_year=[]
    for x in range(year):
        dentals_by_month_year.extend([{'group_by_date':str(datetime.now().year-x)+'-'+format(i+1, '02d'),'dentals':[]} for i in range(12)])

    for dental in dentals:
        for dental_by_month_year in dentals_by_month_year:
            generate_to_date=datetime.strptime(dental_by_month_year['group_by_date'], '%Y-%m')
            if(generate_to_date.year==dental.appointment_date.year and generate_to_date.month==dental.appointment_date.month):
                dental_by_month_year['dentals'].append(dental)

    return render(request, 'mande/studentdentalreport.html',
                            {'dentals_by_month_year':dentals_by_month_year})
