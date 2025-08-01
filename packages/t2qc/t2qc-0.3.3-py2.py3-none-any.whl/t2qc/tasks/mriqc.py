import os
import shutil
import logging
import t2qc.tasks as tasks
from executors.models import Job
from t2qc.bids import BIDS

logger = logging.getLogger(__name__)

class Task(tasks.BaseTask):
    def __init__(self, sub, ses, run, bids, outdir, tempdir=None, pipenv=None):
        self._sub = sub
        self._ses = ses
        self._run = run
        self._bids = bids
        super().__init__(outdir, tempdir, pipenv)

    def build(self):
        self._command = [
            'selfie',
            '--lock',
            '--output-file', self._prov,
            'mriqc',
            '--participant_label', self._sub.replace('sub-', ''),
        ]
        if self._ses:
            self._command.extend([
                '--session-id', self._ses.replace('ses-', '')
            ])
        self._command.extend([
            '--run-id', str(self._run),
            '--work-dir', self.workdir(),
            '--verbose-reports',
            '--float32',
            '--n_procs', '2',
            '--no-sub',
            self._bids.base(),
            self._outdir,
            'participant'
        ])
        if self._pipenv:
            os.chdir(self._pipenv)
            self._command[:0] = ['pipenv', 'run']
        logdir = self.logdir()
        # get T2w file
        t2w = self._bids.raw_anat(
            mod='T2w',
            run=self._run
        )
        sidecar = os.path.join(*t2w) + '.json'
        # copy json sidecar into output logs directory
        destination = os.path.join(logdir, os.path.basename(sidecar))
        logger.debug('copying %s to %s', sidecar, destination)
        shutil.copy2(sidecar, destination)
        # return job object
        logfile = os.path.join(logdir, 'mriqc.log')
        self.job = Job(
            name='t2qc-mriqc',
            time='30',
            memory='4G',
            cpus=2,
            nodes=1,
            command=self._command,
            output=logfile,
            error=logfile
        )

