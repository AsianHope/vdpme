from django import template
from mande.models import IntakeSurvey
from mande.models import GRADES
from mande.models import RELATIONSHIPS
from mande.models import Academic
from mande.models import IntakeInternal
from mande.models import ClassroomEnrollment
from mande.models import COHORTS
from mande.models import STATUS
from mande.models import FREQUENCY
from mande.models import YN
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import date

from django.core.urlresolvers import resolve, reverse
from django.utils.translation import activate, get_language

register = template.Library()
@register.filter(name='frequency_display')
def frequency_display(value):
    if value is None:
        return "Unknown"
    else:
        rel_dict = dict(FREQUENCY)
        return rel_dict.get(value, None)

@register.filter(name='yn_display')
def yn_display(value):
    if value is None:
        return "Unknown"
    else:
        rel_dict = dict(YN)
        return rel_dict.get(value, None)
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
        if current_grade > 6:
            current_grade = 50
    except ObjectDoesNotExist:
        current_grade = recent_intake.starting_grade if type(recent_intake) != str else 0

    return grade_dict.get(current_grade, None)
# get subtotal of each field in dental that group by date (year, month)
@register.filter(name='get_subtotal_of_dental')
def get_subtotal_of_dental(dental,arg):
    subtotal = 0
    for student in dental:
        if getattr(student, arg) is not None:
            subtotal +=getattr(student, arg)
    return subtotal
# get total of dentals,extractions,etc
@register.filter(name='get_total_of_dental')
def get_total_of_dental(dentals,arg):
    total = 0
    for dental in dentals:
        if arg == 'None':
            total+=len(dental['dentals'])
        else:
            for student in dental['dentals']:
                if getattr(student, arg) is not None:
                    total +=getattr(student, arg)
    return total
# check if student have already performed post exit survey
@register.filter(name='check_if_already_perform_post_exit')
def check_if_already_perform_post_exit(exit_survey_student_id,arg):
    check_already_perform= False
    post_exit_surveys = arg
    for post_exit_survey in post_exit_surveys:
        if(post_exit_survey.student_id.student_id==exit_survey_student_id.student_id):
            check_already_perform = True
            break
        else:
            check_already_perform = False
    return check_already_perform

# get total of students by gender
@register.filter(name='get_students_length_by_gender')
def get_students_length_by_gender(students,arg):
    gender = arg
    students_by_gender=[]
    for student in students:
        if student.getRecentFields()['gender'] == gender:
            students_by_gender.append(student)
    return len(students_by_gender)
# increase one year
@register.filter(name='add_year')
def add_year(year):
    return year+1

#get dictionary items
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

#get student classroom
@register.filter
def student_classroom(student):
    return ClassroomEnrollment.objects.filter(Q(student_id=student) & Q(Q(drop_date=None) | Q(drop_date__gte=date.today().isoformat())))

#get academic year
@register.filter(name='get_academic_year')
def get_academic_year(value):
    if value is None:
        return "Unknown"
    else:
        academic_year_dict = dict(COHORTS)
        return academic_year_dict.get(int(value), None)

#get status
@register.filter(name='get_status')
def get_status(value):
    if value is None:
        return "Unknown"
    else:
        status_dict = dict(STATUS)
        return status_dict.get(value, None)

#change language
@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    """
    Get active page's url by a specified language
    Usage: {% change_lang 'en' %}
    """

    path = context['request'].path
    url_parts = resolve( path )

    url = path
    cur_language = get_language()
    try:
        activate(lang)
        url = reverse( url_parts.view_name, kwargs=url_parts.kwargs )
    finally:
        activate(cur_language)

    return "%s" % url
