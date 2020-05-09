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

available_survey_languages = [
        ( "english"          , "English"          ),    #"en"
        ( "german"           , "German"           ),    #"de" succ
        ( "spanish"          , "Spanish"          ),    #"es" 
        ( "finnish"          , "Finnish"          ),    #"fi"
        ( "french"           , "French"           ),    #"fr" succ
        ( "italian"          , "Italian"          ),    #"it"
        ( "korean"           , "Korean"           ),    #"ko"
        ( "norwegianbokmal"  , "Norwegian bokmål" ),    #"nb"
        ( "dutch"            , "Dutch"            ),    #"nl" succ
        ( "polish"           , "Polish"           ),    #"pl"
        ( "portuguese"       , "Portuguese"       ),    #"pt" succ
        ( "portuguese-brazil", "Portuguese (BRA)" ),    #"pt_BR"
        ( "romanian"         , "Romanian"         ),    #"ro"
        ( "russian"          , "Russian"          ),    #"ru"   
        ( "sinhala"          , "Sinhala"          ),    #"si"   
        ( "swedish"          , "Swedish"          ),    #"sv"   
        ( "ukrainian"        , "Ukrainian"        ),    #"uk"   
        ( "chinese-hans-hk"  , "Chinese (HK)"     ),    #"zh_Hans"
        ]

class SurveyModelForm(forms.ModelForm):
    # Is there a way to get the max_length from the Model?
    name = forms.CharField(min_length=4, max_length=100)
    language = forms.ChoiceField(widget=forms.Select, choices=available_survey_languages)

    class Meta:
        model = models.Survey
        fields = ('name', 'title', 'author', 'language', 'globalid')
        labels = {
                'name': "Name",
                'title': "Title",
                'author': "Author(s)",
                'language': "Language",
                'globalid': "Global ID",
                }
        help_texts = {
                'title': "The title that gets printed on the survey",
                'author': "The author(s) or responsible persons or organisations of the survey that gets printed on the survey",
                'language': "Select a language of the header",
                'globalid': "To differentiate between different versions of similar surveys, an id will be printed on the survey",
                'name': "Name of the Survey, so you'll find it easily in this interface",
                }
        error_messages = {
                'name' : {
                    'max_length': "The name of the survey is to long.",
                    'min_length': "The name of the survey has to have at least 4 characters.",
                    },
                }
