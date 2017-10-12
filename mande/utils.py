from datetime import date

from mande.models import ExitSurvey
from mande.models import IntakeSurvey
from mande.models import IntakeInternal
from mande.permissions import perms_required

from django.core.exceptions import ObjectDoesNotExist
def getEnrolledStudents(grade_id=None):
    ''' enrolled students are those who have:
          - completed an intake survey
          - have completed an internal intake
          AND
              - do not have an exit survey
              OR
              - have an exit survey with an exit date after today

    '''
    #get a flat list of student_ids to exclude
    exit_surveys = ExitSurvey.objects.all().filter(exit_date__lte=date.today().isoformat()).values_list('student_id',flat=True)

    #filter out students who have exit surveys
    surveys = IntakeSurvey.objects.all().filter(date__lte=date.today().isoformat()).order_by('student_id').exclude(student_id__in=exit_surveys)

    #figure out students who have internal intakes
    enrolled_students = IntakeInternal.objects.all().values_list('student_id',flat=True)
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
    # latest current grade in intakeupdate , if not get grade from intake internal
    current_grade = 0  #not enrolled
    try:
        student = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        return current_grade

    try:
        updates = student.intakeupdate_set.exclude(current_grade=None).latest('date')
        current_grade = updates.current_grade
        print current_grade
    except ObjectDoesNotExist:
        try:
            intake = student.intakeinternal_set.all().filter().latest('enrollment_date')
            current_grade = intake.starting_grade
        except ObjectDoesNotExist:
            pass
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

def getStudentAgeAppropriateGradeLevel(student_id):
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

    return age_appropriate_grade

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
    age_appropriate_grade = getStudentAgeAppropriateGradeLevel(student_id)
    if (current_grade >= age_appropriate_grade) and current_grade is not 0:
        return True
    else:
        return False

#returns true if user has required permissions
def user_permissions(method_name, user):
    user_perms = user.get_all_permissions()
    allow_access = True
    for perm in perms_required[method_name]:
        if perm not in user_perms:
            allow_access = False
    return allow_access
