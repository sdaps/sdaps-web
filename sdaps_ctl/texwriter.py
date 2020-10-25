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

import os

import json

def get(d, attr, val):
    try:
        return d[attr]
    except KeyError:
        return val

def render_qobject(qobject, allowed_types=None):
    t = get(qobject, 'type', '')

    assert allowed_types is None or t in allowed_types

    if t == 'section':
        return r'\section{%s}' % get(qobject, 'title', '')

    elif t == 'textbody':
        return get(qobject, 'text', '') + '\n\n'

    elif t == 'singlemark':
        return r'\setcounter{markcheckboxcount}{%i}\singlemark{%s}{%s}{%s}' % (get(qobject, 'checkboxcount', 2), get(qobject, 'question', ''), get(qobject, 'lower', ''), get(qobject, 'upper', ''))

    elif t == 'choicequestion':
        choices = []

        for answer in get(qobject, 'children', []):
            if answer['type'] == 'choiceitem':
                if get(answer, 'colspan', 1) <= 1:
                    choices.append('\choiceitem{%s}' % get(answer, 'answer', ''))
                else:
                    choices.append('\choicemulticolitem{%i}{%s}' % (answer['colspan'], get(answer, 'answer', '')))
            else:
                choices.append('\choiceitemtext{%fcm}{%i}{%s}' % (get(answer, 'height', 1.2), get(answer, 'colspan', 1), get(answer, 'answer', 1)))

        return '\\begin{choicequestion}[cols=%i]{%s}\n%s\n\\end{choicequestion}' % (get(qobject, 'columns', 4), get(qobject, 'question', ''), '\n'.join(choices))

    elif t == 'textbox':

        children = []

        for child in get(qobject, 'children', []):
            children.append(render_qobject(child))

        return '\\textbox%s{%fcm}{%s}' % ('' if get(qobject, 'expand', True) else '*', get(qobject, 'height', 2.0), get(qobject, 'question', ''))

    elif t == 'multicol':

        children = []

        for child in get(qobject, 'children', []):
            children.append(render_qobject(child))

        return '\\begin{multicols}{%i}\n%s\n\\end{multicols}' % (get(qobject, 'columns', 2), '\n'.join(children))

    elif t == 'markgroup':
        marklines = []

        for markline in get(qobject, 'children', []):
            assert markline['type'] == 'markline'

            marklines.append('\\markline{%s}{%s}{%s}' % (get(markline, 'question', ''), get(markline, 'lower', ''), get(markline, 'upper', '')))

        return '\\setcounter{markcheckboxcount}{%i}\n\\begin{markgroup}{%s}\n%s\n\\end{markgroup}' % (get(qobject, 'checkboxcount', 5), get(qobject, 'heading', ''), '\n'.join(marklines))

    elif t == 'choicegroup':
        items = []

        for child in get(qobject, 'children', []):
            if child['type'] == 'groupaddchoice':
                items.append('\\groupaddchoice{%s}' % get(child, 'choice', ''))

        for child in get(qobject, 'children', []):
            if child['type'] == 'choiceline':
                items.append('\\choiceline{%s}' % get(child, 'question', ''))

        return '\\begin{choicegroup}{%s}\n%s\n\\end{choicegroup}' % (get(qobject, 'heading', ''), '\n'.join(items))

    else:
        raise AssertionError('Unknown qtype %s!' % t)

def return_template():
    template = r"""
\documentclass[
  %% Babel language, also used to load translations
  %(language)s
  %% Use A4 paper size, you can change this to eg. letterpaper if you need
  %% the letter format. The normal methods to modify the paper size should
  %% be picked up by SDAPS automatically.
  %% a4paper, setting this might break the example scan unfortunately
  %% letterpaper
  %(paper_format)s
  %%
  %% If you need it, you can add a custom barcode at the center
  %(globalid)s
  %%
  %% And the following adds a per sheet barcode at the bottom left
  %(print_questionnaire_id)s
  %%
  %% You can choose between twoside and oneside. twoside is the default, and
  %% requires the document to be printed and scanned in duplex mode.
  %%oneside,
  %%
  %% With SDAPS 1.1.6 and newer you can choose the mode used when recognizing
  %% checkboxes. valid modes are "checkcorrect" (default), "check" and
  %% "fill".
  %%checkmode=checkcorrect,
  %%
  %% The following options make sense so that we can get a better feel for the
  %% final look.
  pagemark,
  stamp]{sdapsclassic}
\usepackage[utf8]{inputenc}
\usepackage{multicol}

\author{%(author)s}
\title{%(title)s}

\begin{document}
  \begin{questionnaire}[%(noinfo)s]
    %(content)s
  \end{questionnaire}
\end{document}
"""
    return template

def texwriter(djsurvey):
    template = return_template()
    data = {}

    data['author'] = djsurvey.author
    data['title'] = djsurvey.title

    data['language'] = djsurvey.language + ","
    
    data['globalid'] = ("globalid=" + djsurvey.globalid + ",") if djsurvey.globalid else "%"

    data['paper_format'] = "a4paper," if djsurvey.opts_paper_format == "a4paper" else "letterpaper,"
    data['noinfo'] = "noinfo" if djsurvey.opts_noinfo == True else ""
    data['print_questionnaire_id'] = "print_questionnaire_id," if djsurvey.opts_print_questionnaire_id == True else "%"

    content = []

    questionnaire = json.loads(djsurvey.questionnaire)

    for qobject in questionnaire:
        content.append(render_qobject(qobject))

    data['content'] = '\n'.join(content)
    document = template % data

    f = open(os.path.join(djsurvey.path, 'questionnaire.tex'), 'w')
    f.write(document)

    return
