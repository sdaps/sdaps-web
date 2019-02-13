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
