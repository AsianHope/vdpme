from django import forms
from mande.models import IntakeSurvey
from mande.models import IntakeUpdate
from mande.models import ExitSurvey
from mande.models import PostExitSurvey
from mande.models import SpiritualActivitiesSurvey
from django.forms.extras.widgets import SelectDateWidget

class Html5DateInput(forms.DateInput):
        input_type = 'date'

class IntakeSurveyForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)
    dob =  forms.DateField(label="Date of Birth",widget=Html5DateInput)

    class Meta:
        model = IntakeSurvey

class IntakeUpdateForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)

    class Meta:
        model = IntakeUpdate

class ExitSurveyForm(forms.ModelForm):
    survey_date = forms.DateField(label="Survey Date",widget=Html5DateInput)
    exit_date = forms.DateField(label="Exit Date",widget=Html5DateInput)
    class Meta:
        model = ExitSurvey

class PostExitSurveyForm(forms.ModelForm):
    post_exit_survey_date = forms.DateField(label="Post Exit Survey Date",widget=Html5DateInput)
    exit_date = forms.DateField(label="Exit Date",widget=Html5DateInput)
    class Meta:
        model = PostExitSurvey

class SpiritualActivitiesSurveyForm(forms.ModelForm):
    date = forms.DateField(label="Survey Date",widget=Html5DateInput)
    class Meta:
        model = SpiritualActivitiesSurvey
