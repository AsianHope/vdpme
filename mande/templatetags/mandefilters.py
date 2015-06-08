from django import template
from mande.models import IntakeSurvey
from mande.models import GRADES
from mande.models import RELATIONSHIPS
from mande.models import Academic
from mande.models import IntakeInternal
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()
@register.filter(name='name_by_sid')
def name_by_sid(value):
    if value is None:
        return "Not sure who this is!"
    else:
        return IntakeSurvey.objects.get(pk=value).name

@register.filter(name='grade_by_id')
def grade_by_id(value):
    if value is None:
        return "Unknown"
    else:
        grade_dict = dict(GRADES)
        return grade_dict.get(int(value), None)

@register.filter(name='relationship_display')
def relationship_display(value):
    if value is None:
        return "Unknown"
    else:
        rel_dict = dict(RELATIONSHIPS)
        return rel_dict.get(value, None)

#duplicated in views.py - probably should link these methods
@register.filter(name='student_current_grade_by_id')
def getStudentGradebyID(student_id):
    grade_dict = dict(GRADES)
    try:
        student = IntakeSurvey.objects.get(pk=student_id)
    except ObjectDoesNotExist:
        current_grade = 0 #not enrolled

    academics = student.academic_set.all().filter().order_by('-test_date')
    intake = student.intakeinternal_set.all().filter().order_by('-enrollment_date')
    if len(intake) > 0:
        recent_intake = intake[0]
    else:
        recent_intake = 'Not enrolled'

    try:
        #their current grade is one more than that of the last test they passed
        current_grade = (academics.filter(promote=True).latest('test_date').test_level)+1
    except ObjectDoesNotExist:
        current_grade = recent_intake.starting_grade if type(recent_intake) != str else 0

    return grade_dict.get(current_grade, None)

#get dictionary items
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
