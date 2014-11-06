from django.forms import ModelForm
import models

class SurveyForm(ModelForm):
    class Meta:
        model = models.Survey
        fields = ['name', 'title', 'author']

