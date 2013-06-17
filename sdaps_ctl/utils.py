
from celery.task import task

from sdaps import defs
import tempfile
import shutil
import subprocess
import resource
import os

@task
def atomic_latex_compile(path, target, timeout=10, need_sdaps=False):

    def set_ulimits():
        # Use a hard limit one second above soft limit
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout+1))

    tmpdir = tempfile.mkdtemp(prefix='sdaps-web-')

    output_pdf = target[:-4] + '.pdf'
    # We sometimes create an SDAPS file that we need
    output_sdaps = target[:-4] + '.sdaps'

    try:
        print "Running %s now twice to generate the questionnaire." % defs.latex_engine
        subprocess.call([defs.latex_engine, '-halt-on-error', '-output-directory', tmpdir,
                         '-interaction', 'batchmode', 'questionnaire.tex'],
                        cwd=path, preexec_fn=set_ulimits)
        # And again, without the draft mode
        subprocess.call([defs.latex_engine, '-halt-on-error', '-output-directory', tmpdir,
                         '-interaction', 'batchmode', 'questionnaire.tex'],
                        cwd=path, preexec_fn=set_ulimits)

        if not os.path.exists(os.path.join(tmpdir, output_pdf)):
            return None

        if need_sdaps:
            if os.path.exists(os.path.join(tmpdir, output_sdaps)):
                shutil.move(os.path.join(tmpdir, output_sdaps), os.path.join(path, output_sdaps))
            else:
                return False

        # Move the created PDF file
        shutil.move(os.path.join(tmpdir, output_pdf), os.path.join(path, output_pdf))

    finally:
        # Ensure that temporary files are deleted
        shutil.rmtree(tmpdir)

    # Return the filename of the PDF
    return output_pdf

