from datetime import date

from mande.models import ExitSurvey
from mande.models import IntakeSurvey
from mande.models import IntakeInternal

from django.core.exceptions import ObjectDoesNotExist
def getEnrolledStudents(grade_id=None):
    ''' enrolled students are those who have:
          - completed an intake survey
          - have completed an internal intake
          - have an enrollment date on their internal intake before today
          AND
              - do not have an exit survey
              OR
              - have an exit survey with an exit date after today

    '''
    #get a flat list of student_ids to exclude
    exit_surveys = ExitSurvey.objects.all().filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)

    #filter out students who have exit surveys
    surveys = IntakeSurvey.objects.order_by('student_id').exclude(student_id__in=exit_surveys)

    #figure out students who have internal intakes with enrollment dates before today
    enrolled_students = IntakeInternal.objects.all().filter(enrollment_date__lte=date.today().isoformat()).values_list('student_id',flat=True)
    #figure out which students don't have internal intakes
    not_enrolled = surveys.exclude(student_id__in=enrolled_students).values_list('student_id',flat=True)
    #filter out students who aren't enrolled, as detailed above
    enrolled = surveys.exclude(student_id__in=not_enrolled)

    #if we have a grade_id, return only a subset of students enrolled in that grade
    if grade_id:
        in_grade_id = []
        for student in enrolled:
            if getStudentGradebyID(student.student_id) == grade_id:
                in_grade_id.append(student)

        enrolled = in_grade_id

    return enrolled

def getStudentGradebyID(student_id):
    try:
        student = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        current_grade = 0 #not enrolled

    academics = student.academic_set.all().filter().order_by('-test_level')
    intake = student.intakeinternal_set.all().filter().order_by('-enrollment_date')
    if len(intake) > 0:
        recent_intake = intake[0]
    else:
        recent_intake = 'Not enrolled'

    try:
        #their current grade is one more than that of the last test they passed
        current_grade = (academics.filter(promote=True).latest('test_level').test_level)+1
    except ObjectDoesNotExist:
        current_grade = recent_intake.starting_grade if type(recent_intake) != str else 0

    return current_grade

def studentAtSchoolGradeLevel(student_id):
    try:
        survey = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        return False

    current_grade = getStudentGradebyID(student_id)
    updates = survey.intakeupdate_set.all().filter().order_by('-date')

    #get most up to date information
    if len(updates) > 0:
        recent_survey = updates[0]
    else:
        recent_survey = survey

    if current_grade == recent_survey.grade_current or current_grade == recent_survey.grade_last:
        return True
    else:
        return False

def studentAtAgeAppropriateGradeLevel(student_id):
    # no record, no dice.
    try:
        survey = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        return False
    # no DOB, no dice
    if survey.dob == None:
        return 'DOB not entered'

    current_grade = getStudentGradebyID(student_id)
    if current_grade>12:
        return "N/A"

    #Look at calendar year child was born in to calculate their age
    approximate_age = date.today().year - survey.dob.year
    #if today is before grades change in August
    if date.today().month < 8:
        age_appropriate_grade = approximate_age - 6
    else:
        age_appropriate_grade = approximate_age - 5
    if current_grade >= age_appropriate_grade:
        return True
    else:
        return False
