from django import forms
from mande.models import IntakeSurvey
from django.forms.extras.widgets import SelectDateWidget

class Html5DateInput(forms.DateInput):
        input_type = 'date'

class IntakeSurveyForm(forms.ModelForm):
    date = forms.DateField(label="Date",widget=Html5DateInput)
    dob =  forms.DateField(label="Date of Birth",widget=Html5DateInput)
    graduation =  forms.DateField("Expected 6th Grade Graduation",widget=Html5DateInput)

    class Meta:
        model = IntakeSurvey
