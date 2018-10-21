from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from . import models

class SurveyModelForm(forms.ModelForm):
    # Is there a way to get the max_length from the Model?
    name = forms.CharField(min_length=4, max_length=100)

    class Meta:
        model = models.Survey
        fields = ('name', 'title', 'author', 'globalid')
        labels = {
                'name': "Name",
                'title': "Title",
                'author': "Author(s)",
                'globalid': "Global ID",
                }
        help_texts = {
                'title': "The title that gets printed on the survey",
                'author': "The author(s) or responsible persons or organisations of the survey that gets printed on the survey",
                'globalid': "To differentiate between different versions of similar surveys, an id will be printed on the survey",
                'name': "Name of the Survey, so you'll find it easily in this interface",
                }
        error_messages = {
                'name' : {
                    'max_length': "The name of the survey is to long.",
                    'min_length': "The name of the survey has to have at least 4 characters.",
                    },
                }
