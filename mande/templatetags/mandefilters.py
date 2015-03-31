from django import template
from mande.models import IntakeSurvey
from mande.models import GRADES
register = template.Library()
@register.filter(name='name_by_sid')
def name_by_sid(value):
    if value is None:
        return "Not sure who this is!"
    else:
        return IntakeSurvey.objects.get(pk=value).name

@register.filter(name='grade_by_id')
def grade_by_id(value):
    grade_dict = dict(GRADES)
    return grade_dict.get(value, None)
