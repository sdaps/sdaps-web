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

from celery.task import task

from sdaps import defs
import tempfile
import shutil
import subprocess
import resource
import os

class SecureEnv:
    def __init__(self, timeout):
        self.timeout = timeout

    def __call__(self):
        # Clean up environ a bit
        for k in list(os.environ.keys()):
            if k.startswith('TEX'):
                del os.environ[k]

        # Use a hard limit one second above soft limit
        resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout+1))

        # And prevent certain attacks trough LaTeX.
        os.environ['openin_any'] = 'p'
        os.environ['openout_any'] = 'p'
        os.environ['shell_escape'] = 'f'

@task
def atomic_latex_compile(path, target, timeout=10, need_sdaps=False):

    setup_env = SecureEnv(timeout)

    tmpdir = tempfile.mkdtemp(prefix='sdaps-web-')

    output_pdf = target[:-4] + '.pdf'
    output_log = target[:-4] + '.log'
    # We sometimes create an SDAPS file that we need
    output_sdaps = target[:-4] + '.sdaps'

    try:
        print("Running %s now three times to generate the questionnaire." % defs.latex_engine)
        for i in range(0, 3):
            subprocess.call([defs.latex_engine, '-halt-on-error', '-output-directory', tmpdir,
                             '-interaction', 'batchmode', target],
                            cwd=path, preexec_fn=setup_env)

        # Move the created log file right away
        shutil.move(os.path.join(tmpdir, output_log), os.path.join(path, output_log))

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

