#!/usr/bin/env python3
# sdaps_web - Webinterface for SDAPS
# Copyright(C) 2019, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from . import models

available_survey_languages = settings.AVAILABLE_SURVEY_LANGUAGES

class SurveyModelForm(forms.ModelForm):
    # Is there a way to get the max_length from the Model?
    name = forms.CharField(
            widget=forms.TextInput,
            min_length=4,
            max_length=100,
            label="Survey Name",
            help_text="Name of the Survey, so you'll find it easily in this interface",
            error_messages = {
                'max_length': "The name of the survey is to long.",
                'min_length': "The name of the survey has to have at least 4 characters."}
            )
    language = forms.ChoiceField(
            widget=forms.Select(
                attrs={'class': 'custom-select'}
            ),
            choices=available_survey_languages,
            label="Language of Intro Text",
            help_text="Select a language of the header",
            )

    class Meta:
        model = models.Survey
        fields = ('title', 'author', 'globalid', 'name', 'language')
        labels = {
                'title': "Title",
                'author': "Author(s)",
                'globalid': "Global ID",
                }
        help_texts = {
                'title': "The title that gets printed on the survey",
                'author': "The author(s) or responsible persons or organisations of the survey that gets printed on the survey",
                'globalid': "To differentiate between different versions of similar surveys, an id will be printed on the survey",
                }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_style = 'inline'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-12 col-lg-0'),
                Column('title', css_class='form-group col-md-12 col-lg-0'),
                Column('author', css_class='form-group col-md-12'),
                Column('language', css_class='col-md-6'),
                Column('globalid', css_class='col-md-6'),
                css_class='form-row col-md-6'
            ),
            Row(
                Submit('submit', 'Create Survey', css_class='btn btn-success'),
                css_class='form-row col-md-12'
            ),
        )    


class SurveyEditForm(SurveyModelForm):
    language = forms.ChoiceField(
            widget=forms.Select(
                attrs={'class': 'custom-select'}
            ),
            choices=available_survey_languages,
            label="Language of Intro Text",
            help_text="Select a language of the header",
            )
    opts_noinfo = forms.BooleanField(
            widget=forms.CheckboxInput,
            label="No Instruction Header",
            help_text="If checked, then the header for 'How to fill out the form' won't be displayed.",
            required = False
            )
    opts_paper_format = forms.ChoiceField(
            widget=forms.RadioSelect, 
            label="Paper Format",
            choices=[('a4paper', 'A4'), ('letterpaper', 'Letter')],
            )
    opts_print_questionnaire_id = forms.CharField(
            widget=forms.Textarea(attrs = {'placeholder': 'ID02;ID04;...'}),
            label="Print Unique IDs",
            help_text="If a list of IDs seperated by semicolons is entered, those IDs get printed as qr-/barcode on the questionnaire. Example: Multiple choice tests in class.",
            required = False
            )

    class Meta(SurveyModelForm.Meta):
        model = models.Survey
        fields = ('title', 'author', 'globalid', 'name', 'language', 'opts_noinfo', 'opts_paper_format', 'opts_print_questionnaire_id')

    def __init__(self, *args, **kwargs):
        super(SurveyModelForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.fields['opts_noinfo'].initial = instance.opts_noinfo
            self.fields['opts_paper_format'].initial = 'a4paper' if not instance.opts_paper_format else instance.opts_paper_format
            if not instance.opts_print_questionnaire_id == False:
                self.fields['opts_print_questionnaire_id'].initial = instance.opts_print_questionnaire_id
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Row(
                    Column('name', css_class='col-md-12'),
                    Column('title', css_class='col-md-12'),
                    Column('author', css_class='col-md-12'),
                    Column('language', css_class='col-md-12'),
                    Column('globalid', css_class='col-md-12'),
                    css_class='form-row col-md-5'
                ),
                Row(css_class='form-row col-md-2'),
                Row(
                    Column('opts_noinfo', css_class='col-md-12'),
                    Column('opts_paper_format', css_class='col-md-12'),
                    Column('opts_print_questionnaire_id', css_class='col-md-12'),
                    css_class='form-row col-md-5'
                ),
                Submit('submit', 'Update Survey', css_class='btn btn-success form-row'),
                css_class='col-md-12 form-row'
            ),
        )

    def save(self, commit=True):
        instance = super(SurveyEditForm, self).save(commit=False)
        instance.set_tex_cls_opts('noinfo', self.cleaned_data['opts_noinfo'])
        instance.set_tex_cls_opts('paper_format', self.cleaned_data['opts_paper_format'])
        instance.set_tex_cls_opts('print_questionnaire_id', self.cleaned_data['opts_print_questionnaire_id'])
        if commit:
            instance.save()
        return instance
