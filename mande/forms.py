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
from mande.models import StudentEvaluation
from mande.models import Health
from mande.models import GRADES
from mande.models import SCORES
from mande.models import PublicSchoolHistory
from mande.models import COHORTS

from mande.utils import getEnrolledStudents

from django.forms.extras.widgets import SelectDateWidget
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe

class Html5DateInput(forms.DateInput):
        input_type = 'date'

class IntakeSurveyForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput,initial=date.today().isoformat())
    dob =  forms.DateField(label="Date of Birth",widget=Html5DateInput)

    def clean(self):
        cleaned_data = super(IntakeSurveyForm, self).clean()
        enrolled = cleaned_data.get("enrolled")
        grade_last = cleaned_data.get("grade_last")
        grade_current = cleaned_data.get("grade_current")

        msg = u"Must select value other than Not Applicable"
        top_msg = u"Enrollment status and grade data mismatch triggered"
        if enrolled == 'N' and grade_last < 0:
            self.add_error('grade_last', msg)
            raise forms.ValidationError(top_msg)
        if enrolled == 'Y' and grade_current < 0:
            self.add_error('grade_current', msg)
            raise forms.ValidationError(top_msg)

    class Meta:
        model = IntakeSurvey
        exclude=[
        'minors_working',
        'minors_profession',
        'minors_encouraged',
        'minors_training',
        'minors_training_type',
        'grade_appropriate'
        ]

class IntakeInternalForm(forms.ModelForm):
    enrollment_date = forms.DateField(label="Enrollment Date",widget=Html5DateInput)

    class Meta:
        model = IntakeInternal
        exclude = []

class IntakeUpdateForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)

    def clean(self):
        cleaned_data = super(IntakeUpdateForm, self).clean()
        enrolled = cleaned_data.get("enrolled")
        grade_last = cleaned_data.get("grade_last")
        grade_current = cleaned_data.get("grade_current")

        msg = u"Must select value other than Not Applicable"
        top_msg = u"Enrollment status and grade data mismatch triggered"
        if enrolled == 'N' and grade_last < 0:
            self.add_error('grade_last', msg)
            raise forms.ValidationError(top_msg)
        if enrolled == 'Y' and grade_current < 0:
            self.add_error('grade_current', msg)
            raise forms.ValidationError(top_msg)

    class Meta:
        model = IntakeUpdate
        exclude=[
        'minors_working',
        'minors_profession',
        'minors_encouraged',
        'minors_training',
        'minors_training_type',
        'grade_appropriate'
        ]

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
    def __init__(self, *args, **kwargs):
         super(ClassroomTeacherForm, self).__init__(*args, **kwargs)
         self.fields['classroom_id'].queryset = Classroom.objects.filter(active=True).order_by('school_id')
         self.fields['teacher_id'].queryset = Teacher.objects.filter(active=True)
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

    def __init__(self, *args, **kwargs):
         super(ClassroomEnrollmentForm, self).__init__(*args, **kwargs)
         self.fields['classroom_id'].queryset = Classroom.objects.filter(active=True).order_by('school_id')

    class Meta:
        model = ClassroomEnrollment
        exclude=[]

class IndividualClassroomEnrollmentForm(forms.ModelForm):
    drop_date = forms.DateField(label="Drop Date",widget=Html5DateInput,initial=date.today().isoformat())

    def __init__(self, *args, **kwargs):
         super(IndividualClassroomEnrollmentForm, self).__init__(*args, **kwargs)
         self.fields['classroom_id'].queryset = Classroom.objects.filter(active=True)

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

class StudentEvaluationForm(forms.ModelForm):
    date = forms.DateField(label='',widget=Html5DateInput)
    academic_score = forms.IntegerField(label='',required=False,min_value=0,max_value=100)
    study_score = forms.IntegerField(label='',required=False,min_value=0,max_value=100)
    personal_score = forms.IntegerField(label='',required=False,min_value=0,max_value=100)
    hygiene_score = forms.IntegerField(label='',required=False,min_value=0,max_value=100)
    faith_score = forms.IntegerField(label='',required=False,min_value=0,max_value=100)
    #comments = forms.TextField(label='')
    class Meta:
        model = StudentEvaluation
        exclude = []

class StudentPublicSchoolHistoryForm(forms.ModelForm):
    enroll_date = forms.DateField(widget=Html5DateInput)
    drop_date = forms.DateField(widget=Html5DateInput,required=False)
    reasons = forms.CharField( widget=forms.Textarea,required=False)
    def clean(self):
        cleaned_data = super(StudentPublicSchoolHistoryForm, self).clean()
        status = cleaned_data.get("status")
        reasons = cleaned_data.get("reasons")
        enroll_date = cleaned_data.get("enroll_date")
        drop_date = cleaned_data.get('drop_date')
        msg = u"This field is required."
        top_msg = u"Enrollment status and grade data mismatch triggered"
        if (status == 'DROPPED') & ((reasons=='') | (reasons==None)):
            self.add_error('reasons', msg)

        if (status == 'DROPPED') & ((drop_date=='') | (drop_date==None)):
            self.add_error('drop_date', msg)
        if (drop_date != None):
            if(drop_date < enroll_date):
                msg = u"Drop date should be greater than enroll date."
                self.add_error('drop_date',msg)

    class Meta:
        model = PublicSchoolHistory
        exclude = []
