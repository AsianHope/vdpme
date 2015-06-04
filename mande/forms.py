from django import forms
from datetime import date

from mande.models import IntakeSurvey
from mande.models import IntakeUpdate
from mande.models import ExitSurvey
from mande.models import PostExitSurvey
from mande.models import SpiritualActivitiesSurvey
from mande.models import Discipline
from mande.models import Teacher
from mande.models import Classroom
from mande.models import ClassroomTeacher
from mande.models import ClassroomEnrollment
from mande.models import Attendance
from mande.models import Academic
from mande.models import IntakeInternal
from mande.models import Health
from mande.models import GRADES

from mande.utils import getEnrolledStudents

from django.forms.extras.widgets import SelectDateWidget
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe

class Html5DateInput(forms.DateInput):
        input_type = 'date'

class IntakeSurveyForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)
    dob =  forms.DateField(label="Date of Birth",widget=Html5DateInput)

    class Meta:
        model = IntakeSurvey
        exclude=[]

class IntakeInternalForm(forms.ModelForm):
    enrollment_date = forms.DateField(label="Enrollment Date",widget=Html5DateInput)

    class Meta:
        model = IntakeInternal
        exclude = []

class IntakeUpdateForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)

    class Meta:
        model = IntakeUpdate
        exclude=[]

class ExitSurveyForm(forms.ModelForm):
    survey_date = forms.DateField(label="Survey Date",widget=Html5DateInput)
    exit_date = forms.DateField(label="Exit Date",widget=Html5DateInput)
    class Meta:
        model = ExitSurvey
        exclude=[]

class PostExitSurveyForm(forms.ModelForm):
    post_exit_survey_date = forms.DateField(label="Post Exit Survey Date",widget=Html5DateInput)
    exit_date = forms.DateField(label="Exit Date",widget=Html5DateInput)
    class Meta:
        model = PostExitSurvey
        exclude=[]

class SpiritualActivitiesSurveyForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)
    class Meta:
        model = SpiritualActivitiesSurvey
        exclude=[]

class DisciplineForm(forms.ModelForm):
    incident_date = forms.DateField(label="Incident Date",widget=Html5DateInput)
    class Meta:
        model = Discipline
        fields = ['student_id', 'classroom_id','incident_date','incident_code','incident_description']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude=[]

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        exclude=['classroom_location']

class ClassroomTeacherForm(forms.ModelForm):
    class Meta:
        model = ClassroomTeacher
        exclude=[]


#hackity hack custom renderer for ClassroomEnrollmentForm - TODO: learn how to do this properly ;)
class CheckboxSelectMultipleP(forms.CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(CheckboxSelectMultipleP, self).render(*args,**kwargs)

        return mark_safe(output.replace(u'<ul id="id_student_id">', u'<table class="table table-border" id="id_student_id"><thead><tr><td>Student</td></tr></thead><tbody>').replace(u'</ul>', u'</tbody></table>').replace(u'<li>', u'<tr><td>').replace(u'</li>', u'</td></tr>'))

class ClassroomEnrollmentForm(forms.ModelForm):
    enrolled_students = getEnrolledStudents()
    student_id = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultipleP,queryset=enrolled_students)
    enrollment_date = forms.DateField(label="Enrollment Date",widget=Html5DateInput,initial=date.today().isoformat())

    class Meta:
        model = ClassroomEnrollment
        exclude=[]

class IndividualClassroomEnrollmentForm(forms.ModelForm):
    drop_date = forms.DateField(label="Drop Date",widget=Html5DateInput,initial=date.today().isoformat())

    class Meta:
        model = ClassroomEnrollment
        exclude=['enrollment_date']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude=[]

class AcademicForm(forms.ModelForm):
    promote = forms.BooleanField(label='',required=False)
    test_grade_math = forms.IntegerField(label='',widget=forms.TextInput(attrs={'size':'3'}), required=False)
    test_grade_khmer = forms.IntegerField(label='',widget=forms.TextInput(attrs={'size':'3'}), required=False)
    test_date = forms.DateField(label='',widget=Html5DateInput)
    test_level = forms.ChoiceField(label='',choices=GRADES)
    class Meta:
        model = Academic
        exclude = []

class HealthForm(forms.ModelForm):
    appointment_date = forms.DateField(label="Appointment Date",widget=Html5DateInput,initial=date.today().isoformat())
    class Meta:
        model = Health
        exclude=[]

class HealthDentalForm(forms.ModelForm):
    appointment_date = forms.DateField(label="Appointment Date",widget=Html5DateInput,initial=date.today().isoformat())
    class Meta:
        model = Health
        exclude=['height','weight']

class HealthCheckupForm(forms.ModelForm):
    appointment_date = forms.DateField(label="Appointment Date",widget=Html5DateInput,initial=date.today().isoformat())
    class Meta:
        model = Health
        exclude=[
            'extractions',
            'sealent',
            'filling',
            'endo',
            'scaling',
            'pulped',
            'xray'
        ]
