from django import forms
from datetime import date
from django.forms.models import modelformset_factory

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
from mande.models import YESNO
from mande.models import AcademicMarkingPeriod

from mande.utils import getEnrolledStudents

from django.forms.extras.widgets import SelectDateWidget
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _
VDP_GRADES = [g for g in GRADES if (g[0]>=1 and g[0]<=6) or (g[0] in [50,70])]

class Html5DateInput(forms.DateInput):
        input_type = 'date'

class IntakeSurveyForm(forms.ModelForm):
    date = forms.DateField(label=_('Survey Date'),widget=Html5DateInput,initial=date.today().isoformat())
    dob =  forms.DateField(label=_('Date of Birth'),widget=Html5DateInput)
    address = forms.CharField(label=_('Home Address'),widget=forms.Textarea(attrs={'rows': 4}))
    notes = forms.CharField(label=_('Notes'),widget=forms.Textarea(attrs={'rows': 4}),required=False)
    enrollment_date = forms.DateField(label=_('Enrollment Date'),widget=Html5DateInput)
    starting_grade = forms.ChoiceField(label=_('Starting Grade'),choices=VDP_GRADES)

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
    enrollment_date = forms.DateField(label=_('Enrollment Date'),widget=Html5DateInput)

    class Meta:
        model = IntakeInternal
        exclude = []

class IntakeUpdateForm(forms.ModelForm):
    date = forms.DateField(label=_('Survey Date'),widget=Html5DateInput)

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
    survey_date = forms.DateField(label=_("Survey Date"),widget=Html5DateInput)
    exit_date = forms.DateField(label=_("Exit Date"),widget=Html5DateInput)
    class Meta:
        model = ExitSurvey
        exclude=[]

class PostExitSurveyForm(forms.ModelForm):
    post_exit_survey_date = forms.DateField(label=_('Post Exit Survey Date'),widget=Html5DateInput)
    exit_date = forms.DateField(label=_("Exit Date"),widget=Html5DateInput)
    class Meta:
        model = PostExitSurvey
        exclude=[]

class SpiritualActivitiesSurveyForm(forms.ModelForm):
    date = forms.DateField(label=_('Survey Date'),widget=Html5DateInput,initial=date.today().isoformat())
    class Meta:
        model = SpiritualActivitiesSurvey
        exclude=['family_attend_church','personal_prayer','personal_baptism','personal_bible_reading','personal_prayer_aloud']
    def clean(self):
       cleaned_data = super(SpiritualActivitiesSurveyForm, self).clean()
       personal_attend_church = cleaned_data.get("personal_attend_church")
       frequency_of_attending = cleaned_data.get("frequency_of_attending")
       msg = _(u"This field is required.")
       if (personal_attend_church == 'Y'):
           if(frequency_of_attending==None or frequency_of_attending==''):
               self.add_error('frequency_of_attending', msg)
class DisciplineForm(forms.ModelForm):
    incident_date = forms.DateField(label=_('Incident Date'),widget=Html5DateInput)
    class Meta:
        model = Discipline
        fields = ['student_id', 'classroom_id','incident_date','incident_code','incident_description']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude=[]

class ClassroomForm(forms.ModelForm):
    cohort = forms.ChoiceField(label=_('Target Grade'),choices=VDP_GRADES)
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
    enrollment_date = forms.DateField(label=_('Enrollment Date'),widget=Html5DateInput,initial=date.today().isoformat())

    def __init__(self, *args, **kwargs):
         super(ClassroomEnrollmentForm, self).__init__(*args, **kwargs)
         self.fields['classroom_id'].queryset = Classroom.objects.filter(active=True).order_by('school_id')
    class Meta:
        model = ClassroomEnrollment
        exclude=[]

class IndividualClassroomEnrollmentForm(forms.ModelForm):
    drop_date = forms.DateField(label=_('Drop Date'),widget=Html5DateInput,initial=date.today().isoformat())

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

AttendanceFormSet = modelformset_factory(Attendance,
                                       form=AttendanceForm,
                                       extra=0)
                                       
class AcademicForm(forms.ModelForm):
    promote = forms.BooleanField(label='',required=False)
    test_grade_math = forms.IntegerField(label='',widget=forms.TextInput(attrs={'size':'3'}), required=False)
    test_grade_khmer = forms.IntegerField(label='',widget=forms.TextInput(attrs={'size':'3'}), required=False)
    test_date = forms.DateField(label='',widget=Html5DateInput)
    test_level = forms.ChoiceField(label='',choices=VDP_GRADES)
    class Meta:
        model = Academic
        exclude = []

AcademicFormSet = modelformset_factory(Academic,
                                       form=AcademicForm,
                                       extra=0)

class HealthForm(forms.ModelForm):
    appointment_date = forms.DateField(label=_('Appointment date'),widget=Html5DateInput,initial=date.today().isoformat())
    class Meta:
        model = Health
        exclude=[]
        error_messages = {
            'height': {
                'max_whole_digits':_('Ensure that there are no more than 3 digits before the decimal point.'),
                'max_digits':_('Ensure that there are no more than 5 digits in total.')
            },
            'weight': {
                'max_whole_digits':_('Ensure that there are no more than 3 digits before the decimal point.'),
                'max_digits':_('Ensure that there are no more than 5 digits in total.')
            },
        }

class HealthDentalForm(forms.ModelForm):
    appointment_date = forms.DateField(label=_('Appointment Date'),widget=Html5DateInput,initial=date.today().isoformat())
    class Meta:
        model = Health
        exclude=['height','weight']

class HealthCheckupForm(forms.ModelForm):
    appointment_date = forms.DateField(label=_("Appointment Date"),widget=Html5DateInput,initial=date.today().isoformat())
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

StudentEvaluationFormSet = modelformset_factory(StudentEvaluation,
                                       form=StudentEvaluationForm,
                                       extra=0)

class StudentPublicSchoolHistoryForm(forms.ModelForm):
    status = forms.ChoiceField(label=_('Enrolled in Public School'),choices=YESNO,initial='Y')
    enroll_date = forms.DateField(label=_('From Date'),widget=Html5DateInput)
    drop_date = forms.DateField(label=_('To Date'),widget=Html5DateInput,required=False)
    reasons = forms.CharField(label=_('Reasons'),widget=forms.Textarea(attrs={'rows': 5}),required=False)
    def clean(self):
        cleaned_data = super(StudentPublicSchoolHistoryForm, self).clean()
        status = cleaned_data.get("status")
        reasons = cleaned_data.get("reasons")
        grade = cleaned_data.get("grade")
        school_name = cleaned_data.get("school_name")
        enroll_date = cleaned_data.get("enroll_date")
        drop_date = cleaned_data.get('drop_date')
        msg = _(u"This field is required.")
        top_msg = _(u"Enrollment status and grade data mismatch triggered")
        if (status == 'Y'):
            if(grade==None):
                self.add_error('grade', msg)
            if(school_name==''):
                self.add_error('school_name', msg)
        else:
            if(reasons==''):
                self.add_error('reasons', msg)
        if (drop_date != None):
            if(drop_date < enroll_date):
                    msg = _(u"To date should be greater than From date")
                    self.add_error('drop_date',msg)
    class Meta:
        model = PublicSchoolHistory
        exclude = []
class AcademicMarkingPeriodForm(forms.ModelForm):
    test_date = forms.DateField(label=_('Test Date'),widget=Html5DateInput)
    marking_period_start = forms.DateField(label=_('Marking Period Start Date'),widget=Html5DateInput)
    marking_period_end = forms.DateField(label=_('Marking Period End Date'),widget=Html5DateInput)

    class Meta:
        model = AcademicMarkingPeriod
        exclude = []
