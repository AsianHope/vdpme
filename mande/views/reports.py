from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from django.db.models import Q,Sum,Count
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

TOO_YOUNG = 4
TOO_OLD = 25
'''
*****************************************************************************
Daily Attendance Report
 - lists all classrooms who take attendance and their attendance status
*****************************************************************************
'''
def daily_attendance_report(request,attendance_date=date.today().isoformat()):
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
def daily_absence_report(request,attendance_date=date.today().isoformat()):
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
    ''' students who have unapproved absences with no comment '''
    uastudents = Attendance.objects.all().filter(attendance__exact="UA").filter(Q(notes=u"")|Q(notes=None)).order_by('-date')
    for uastudent in uastudents:
        text = 'Unapproved absence with no comment'
        attendance_date = uastudent.date
        attendance_class = uastudent.classroom
        ''' historical data has null classroom. need to determine how to resolve '''
        if attendance_class is None:
          resolution = ''
          text = 'Unapproved abscence with no comment - missing class id'
        if attendance_class is not None:
          resolution = reverse('take_class_attendance',kwargs={'attendance_date':attendance_date.strftime('%Y-%m-%d'), 'classroom_id':attendance_class.classroom_id})
        addAnomaly(anomalies, uastudent.student_id, text, resolution)
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
                                        Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None))
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
Exit Surveys list
 -filter exit Surveys by date range
*****************************************************************************
'''
def exit_surveys_list(request):
    if request.method == 'POST':
        from_exit_date = request.POST['from_exit_date']
        to_exit_date = request.POST['to_exit_date']
        exit_surveys = ExitSurvey.objects.all().filter(exit_date__gte=from_exit_date , exit_date__lte=to_exit_date)
    else:
        #get today date and subtract two months
        from_exit_date=(datetime.now()- timedelta(days=2 * 365/12)).strftime("%Y-%m-%d")
        to_exit_date=(datetime.now()).strftime("%Y-%m-%d")
        exit_surveys = ExitSurvey.objects.all().filter(exit_date__gte=from_exit_date , exit_date__lte=to_exit_date)

    post_exit_surveys = PostExitSurvey.objects.all()
    return render(request, 'mande/exitsurveylist.html',
                            {'exit_surveys':exit_surveys,'post_exit_surveys':post_exit_surveys,'from_exit_date':from_exit_date,'to_exit_date':to_exit_date})

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

    if request.method == 'POST':
        view_date = request.POST['view_date']
    else:
        # convert to correct format with html input type date
        view_date = date.today().strftime("%Y-%m-%d")

    for student in enrolled_students:
        #only students in the scope of grade levels
        if student.current_vdp_grade(view_date) < 12:
            students_lag[student] = {
                    'lag':student.age_appropriate_grade(view_date) - student.current_vdp_grade(view_date),
                    'appropriate_grade':student.age_appropriate_grade(view_date),
                    'vdp_grade':student.current_vdp_grade(view_date)

            }

    return render(request, 'mande/student_lag_report.html',
                                {'students_lag':students_lag,'view_date':view_date})


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
                                Q(drop_date__gte=date.today().isoformat()) | Q(drop_date=None)).values_list('student_id',flat=True)


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
def student_dental_report(request,site_id=None):
    if site_id is not None:
        dentals= Health.objects.all().filter(appointment_type='Dental',student_id__site=site_id)
        current_site =  School.objects.get(school_id=site_id)
    else:
        current_site = 'All Site'
        dentals= Health.objects.all().filter(appointment_type='Dental')

    unique_students = dentals.values('student_id').annotate(dcount=Count('student_id')).count()

    year = datetime.now().year-2013
    dentals_by_month_year=[]
    for x in range(year):
        dentals_by_month_year.extend([{'group_by_date':str(datetime.now().year-x)+'-'+format(i+1, '02d'),'dentals':[], 'unique':0} for i in range(12)])

    for dental in dentals:
        for dental_by_month_year in dentals_by_month_year:
            generate_to_date=datetime.strptime(dental_by_month_year['group_by_date'], '%Y-%m')
            if(generate_to_date.year==dental.appointment_date.year and generate_to_date.month==dental.appointment_date.month):
                dental_by_month_year['dentals'].append(dental)
                unique_students_by_month = dentals.filter(appointment_date__year=generate_to_date.year, appointment_date__month=generate_to_date.month).values('student_id').annotate(dcount=Count('student_id')).count()
                dental_by_month_year['unique'] = unique_students_by_month

    sites = School.objects.all()
    return render(request, 'mande/studentdentalreport.html',
                            {
                                'dentals_by_month_year':dentals_by_month_year,
                                'sites':sites,
                                'current_site':current_site,
                                'unique_students':unique_students
                            })
'''
*****************************************************************************
M&E summary Report
 -
*****************************************************************************
'''
def mande_summary_report(request,view_date=(date.today().replace(day=1)-timedelta(days=1)).isoformat()):
    if request.method == 'POST':
        start_view_date = request.POST['start_view_date']
        view_date = request.POST['view_date']
    else:
        start_view_date = (date.today().replace(day=1)-timedelta(days=1 * 365/12)).isoformat()
        view_date=(date.today().replace(day=1)-timedelta(days=1)).isoformat()
    # Catch-up school report
    schools = School.objects.all()
    exit_surveys = ExitSurvey.objects.filter(exit_date__lte=start_view_date).values_list('student_id',flat=True)
    students = IntakeSurvey.objects.exclude(student_id__in=exit_surveys).filter(date__lte=view_date)
    enrolled_students = ClassroomEnrollment.objects.filter( Q( Q( Q(drop_date__gte=view_date) | Q(drop_date__gte=start_view_date) ) | Q(drop_date=None)) & Q(enrollment_date__lte=view_date) ).order_by('student_id')

    students_by_site_grade =[]
    students_by_site=[]
    students_by_site_grade_plus_skill_vietnamese = []
    students_enrolled_in_english_by_level = []
    all_students = []
    # generate_list of students group by site and grade
    for school in schools:
        students_by_site_grade.extend(
            [
                {
                'school':school,
                'total':[],
                'total_student_appropriate_level':[],
                'grades':[{'grade'+str(i+1)+'':{'grade':i+1,'students':[],'students_appropriate_level':[],'not':[]}} for i in range(12)],
                }
            ]
        )

        # students by site
        students_by_site.extend([{'school':school,'students':[]}])
        # student by site grade plus vietnamese
        students_by_site_grade_plus_skill_vietnamese.extend(
            [
                {
                'school':school,
                'vietnamese_only':[],
                'total':[],
                'grades':[{'grade'+str(i+1)+'':{'grade':i+1,'students':[]}} for i in range(12)],
                }
            ]
        )

        students_enrolled_in_english_by_level.extend(
            [
                {
                    'school':school,
                    'total':[],
                    'english_classes':[{'english_level'+str(i+1)+'':{'level':'Level '+str(i+1),'students':[]}} for i in range(6)],
                }
            ]
        )
    for student in students:
        if student.current_vdp_grade(view_date) != 50:
            # get student by site and grade
            for student_by_site_grade in students_by_site_grade:
                if student_by_site_grade['school'] == student.getRecentFields(view_date)['site']:
                    for grade in  student_by_site_grade['grades']:
                        for i in range(12):
                            try:
                                if grade['grade'+str(i+1)+'']['grade'] == student.current_vdp_grade(view_date):
                                    # Achieved age appropriate level
                                    if (student.age_appropriate_grade(view_date) - student.current_vdp_grade(view_date)) < 1:
                                        grade['grade'+str(i+1)+'']['students_appropriate_level'].append(student)
                                        student_by_site_grade['total_student_appropriate_level'].append(student)
                                    student_by_site_grade['total'].append(student)
                                    grade['grade'+str(i+1)+'']['students'].append(student)
                            except:
                                pass

            # get student enrolleds plus skill vietnamese
            for student_by_site_grade_plus_skill in students_by_site_grade_plus_skill_vietnamese:
                if student_by_site_grade_plus_skill['school'] == student.getRecentFields(view_date)['site']:
                    for grade in  student_by_site_grade_plus_skill['grades']:
                        only_vietnamese = []
                        for i in range(12):
                            try:
                                if grade['grade'+str(i+1)+'']['grade'] == student.current_vdp_grade(view_date):
                                    enrolleds = ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(classroom_id__cohort=student.current_vdp_grade(view_date)) | Q(classroom_id__cohort=70)) & Q( Q( Q(drop_date__gte=start_view_date) | Q(drop_date__gte=view_date)) | Q(drop_date=None)) &Q(enrollment_date__lte=view_date)
                                        ).order_by('classroom_id__cohort')
                                    # if student enrolled in more than class (grade + vietnamese)
                                    if len(enrolleds)>1:
                                        if(enrolleds[0].classroom_id.cohort==grade['grade'+str(i+1)+'']['grade']):
                                            if(enrolleds[1].classroom_id.cohort==70):
                                                student_by_site_grade_plus_skill['total'].append(student)
                                                grade['grade'+str(i+1)+'']['students'].append(student)

                                else:
                                    if student.current_vdp_grade(view_date) == 70:
                                        if i == 5:
                                            student_by_site_grade_plus_skill['total'].append(student)
                                            student_by_site_grade_plus_skill['vietnamese_only'].append(student)
                            except:
                                pass


        # if enrolled student is english class
        if student.current_vdp_grade(view_date) == 50:
            for student_enrolled_in_english_by_level in students_enrolled_in_english_by_level:
                if student_enrolled_in_english_by_level['school'] == student.site:
                    english_student = None
                    enrolleds = ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(classroom_id__cohort=50) & Q( Q(Q(drop_date__gte=view_date)| Q(drop_date__gte=start_view_date)) | Q(drop_date=None) ) &Q(enrollment_date__lte=view_date)
                        ).order_by('drop_date')
                    # print enrolleds.filter(drop_date=None)
                    if len(enrolleds) > 1:
                        if len(enrolleds.filter(drop_date=None)) != 0:
                            english_student = enrolleds.filter(drop_date=None).latest('enrollment_date')
                        else:
                            english_student = enrolleds.latest('drop_date')
                    else:
                        try:
                            english_student = enrolleds[0]
                        except:
                            pass
                    if english_student is not None:
                        for english_class in  student_enrolled_in_english_by_level['english_classes']:

                            for i in range(6):
                                try:
                                    if(english_class['english_level'+str(i+1)+'']['level'] == english_student.classroom_id.classroom_number):
                                        english_class['english_level'+str(i+1)+'']['students'].append(english_student.student_id)
                                        student_enrolled_in_english_by_level['total'].append(english_student.student_id)
                                except:
                                    pass


        # get all students by site
        for student_by_site in students_by_site:
            if student_by_site['school'] == student.getRecentFields(view_date)['site']:
                student_by_site['students'].append(student)
    # # get students enrolled in english by level
    # for enrolled_student in enrolled_students:
    #
    #     # if enrolled student is english class
    #     if enrolled_student.classroom_id.cohort == 50:
    #         for student_enrolled_in_english_by_level in students_enrolled_in_english_by_level:
    #             if student_enrolled_in_english_by_level['school'] == enrolled_student.classroom_id.school_id:
    #                 for english_class in  student_enrolled_in_english_by_level['english_classes']:
    #                     for i in range(6):
    #                         try:
    #                             if(english_class['english_level'+str(i+1)+'']['level'] == enrolled_student.classroom_id.classroom_number):
    #                                 english_class['english_level'+str(i+1)+'']['students'].append(enrolled_student.student_id)
    #                                 student_enrolled_in_english_by_level['total'].append(enrolled_student.student_id)
    #                                 all_students.append(enrolled_student.student_id)
    #                         except:
    #                             pass

    #     # get student by site and grade
    #     if enrolled_student.classroom_id.cohort != 50 :
    #         #  get student by site and grade
    #             for student_by_site_grade in students_by_site_grade:
    #                 if student_by_site_grade['school'] == enrolled_student.classroom_id.school_id:
    #                     for grade in  student_by_site_grade['grades']:
    #                         for i in range(6):
    #                             try:
    #                                 if grade['grade'+str(i+1)+'']['grade'] == enrolled_student.classroom_id.cohort:
    #                                     student_by_site_grade['total'].append(enrolled_student.student_id)
    #                                     grade['grade'+str(i+1)+'']['students'].append(enrolled_student.student_id)
    #                                     all_students.append(enrolled_student.student_id)
    #
    #                             except:
    #                                 pass
    # # get all students by site
    # # grade + english + vietnamese
    # for student in all_students:
    #     for student_by_site in students_by_site:
    #         if student_by_site['school'] == student.getRecentFields(view_date)['site']:
    #             student_by_site['students'].append(student)
    return render(request, 'mande/mandesummaryreport.html',
                            {
                                'students' : students,
                                'view_date':view_date,
                                'start_view_date':start_view_date,
                                'schools':schools,
                                'grades':dict(GRADES),
                                'students_by_site_grade' : students_by_site_grade,
                                'students_by_site' : students_by_site,
                                'students_by_site_grade_plus_skill_vietnamese':students_by_site_grade_plus_skill_vietnamese,
                                'students_enrolled_in_english_by_level':students_enrolled_in_english_by_level,
                                'level':range(1,7)
                            })

'''
*****************************************************************************
Student Promoted Report
 - lists all student Promoted
*****************************************************************************
'''
def student_promoted_report(request,start_date=None,view_date=None):
    if request.method == 'POST':
        from_view_date = request.POST['from_view_date']
        to_view_date = request.POST['to_view_date']
    else:
        from_view_date = (date.today().replace(day=1)-timedelta(days=1 * 365/12)).isoformat()
        to_view_date = (date.today().replace(day=1)-timedelta(days=1)).isoformat()

    academics = Academic.objects.filter(promote = True,test_date__lte=to_view_date,test_date__gte=from_view_date)
    schools = School.objects.all()
    break_promoted_student_by_sites =[]
    # generate_list of students group by site
    for school in schools:
        break_promoted_student_by_sites.extend(
            [
                {
                'school':school,
                'total':[],
                'students':[],
                }
            ]
        )
    for academic in academics:
        for break_promoted_student_by_site in break_promoted_student_by_sites:
            if break_promoted_student_by_site['school'] == academic.student_id.site:
                break_promoted_student_by_site['students'].append(academic.student_id)

    return render(request, 'mande/student_promoted_report.html',
                            {
                                'break_promoted_student_by_sites':break_promoted_student_by_sites,
                                'from_view_date':from_view_date,
                                'to_view_date' : to_view_date
                            })
