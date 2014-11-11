from django.forms import ModelForm, CharField
import models

class SurveyForm(ModelForm):
    class Meta:
        model = models.Survey
        fields = ['name', 'title', 'author', 'globalid']

    # Is there a way to get the max_length from the Model?
    name = CharField(min_length=4, max_length=100)

