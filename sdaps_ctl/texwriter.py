
import os

import simplejson as json

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

def texwriter(djsurvey):

    data = {}

    data['language'] = 'english'

    data['author'] = djsurvey.author
    data['title'] = djsurvey.title

    content = []

    questionnaire = djsurvey.questionnaire
    questionnaire = json.loads(questionnaire)

    for qobject in questionnaire:
        content.append(render_qobject(qobject))

    data['content'] = '\n'.join(content)

    document = template % data

    f = open(os.path.join(djsurvey.path, 'questionnaire.tex'), 'w')
    f.write(document)

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
  stamp]{sdapsclassic}
\usepackage[utf8]{inputenc}
\usepackage{multicol}

\author{%(author)s}
\title{%(title)s}

\begin{document}
  \begin{questionnaire}
    %(content)s
  \end{questionnaire}
\end{document}

"""


