# -*- coding: utf-8 -*-

import os
import models

def render_qobject(qobject, allowed_type=None):
    t = qobject.qtype

    assert allowed_type is None or allowed_type == t

    if t == 'qhead':
        return r'\section{%s}' % qobject.text

    elif t == 'qmark':
        answers = [answer.text for answer in models.QAnswer.objects.filter(qobject=qobject)]

        while len(answers) < 2:
            answers.append('invalid')

        return r'\singlemark{%s}{%s}{%s}' % (qobject.text, answers[0], answers[1])

    elif t == 'qmarkgroup':
        subquestions = '\n'.join(render_qobject(obj, 'qmarkline') for obj in models.QObject.objects.filter(parent=qobject))

        return '\\begin{markgroup}{%s}\n%s\n\\end{markgroup}' % (qobject.text, subquestions)

    elif t == 'qmarkline':
        answers = [answer.text for answer in models.QAnswer.objects.filter(qobject=qobject)]

        while len(answers) < 2:
            answers.append('invalid')

        return r'\markline{%s}{%s}{%s}' % (qobject.text, answers[0], answers[1])

    elif t == 'qchoice':
        choices = []

        for answer in models.QAnswer.objects.filter(qobject=qobject):
            if answer.type == 'check':
                if answer.columns <= 1:
                    choices.append('\choiceitem{%s}' % answer.text)
                else:
                    choices.append('\choicemulticolitem{%i}{%s}' % (answer.columns, answer.text))
            else:
                choices.append('\choiceitemtext{%fmm}{%i}{%s}' % (answer.height, answer.columns, answer.text))

        return '\\begin{choicequestion}{%s}\n%s\n\\end{choicequestion}' % (qobject.text, choices)

    elif t == 'qchoicegroup':
        choices = '\n'.join(r'\addchoice{%s}' % answer.text for answer in models.QAnswer.objects.filter(qobject=qobject))
        subquestions = '\n'.join(render_qobject(obj, 'qchoiceline') for obj in models.QObject.objects.filter(parent=qobject))

        return '\\begin{choicegroup}{%s}\n%s\n%s\n\\end{choicegroup}' % (qobject.text, choices, subquestions)
    elif t == 'qchoiceline':
        return r'\choiceline{%s}' % qobject.text
    else:
        raise AssertionError('Unknown qtype %s!' % t)

def texwriter(djsurvey):

    data = {}

    data['language'] = 'english'

    data['author'] = djsurvey.author
    data['title'] = djsurvey.title

    content = []

    for qobject in models.QObject.objects.filter(survey=djsurvey, parent=None):
        content.append(render_qobject(qobject))

    data['content'] = '\n'.join(content)

    document = template % data

    f = open(os.path.join(djsurvey.path, 'questionnaire.tex'), 'w')
    f.write(document.encode('utf-8'))

    return

template = r"""
\documentclass[
  %% Babel language, also used to load translations
  %(language)s,
  %%
  %% If you need it, you can add a custom barcode at the center
  %%globalid=SDAPS,
  %%
  %% And the following adds a per sheet barcode at the bottom left
  %%print_questionnaire_id,
  %%
  %% You can choose between twoside and oneside. twoside is the default, and
  %% requires the document to be printed and scanned in duplex mode.
  %%oneside,
  %%
  %% The following options make sense so that we can get a better feel for the
  %% final look.
  pagemark,
  stamp]{sdaps}
\usepackage[utf8]{inputenc}

\author{%(author)s}
\title{%(title)s}

\begin{document}
  \begin{questionnaire}
    %(content)s
  \end{questionnaire}
\end{document}

"""


