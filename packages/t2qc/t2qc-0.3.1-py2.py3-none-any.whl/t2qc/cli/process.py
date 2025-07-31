import os
import re
import sys
import json
import yaml
import yaxil
import glob
import math
import t2qc
import logging
import tarfile
import executors
import tempfile
import subprocess as sp
from executors.models import Job, JobArray
from t2qc.snapshots import Snapshotter
from t2qc.bids import BIDS
from t2qc.xnat import Report
import t2qc.tasks.mriqc as mriqc
import t2qc.tasks.vnav as vnav
from t2qc.state import State

logger = logging.getLogger(__name__)

def do(args):
    if args.insecure:
        logger.warning('disabling ssl certificate verification')
        yaxil.CHECK_CERTIFICATE = False

    conf = yaml.safe_load(open(args.config))

    # create job executor and job array
    if args.scheduler:
        E = executors.get(args.scheduler, partition=args.partition)
    else:
        E = executors.probe(args.partition)
    jarray = JobArray(E)

    # create BIDS
    B = BIDS(args.bids_dir, args.sub, ses=args.ses)
    raw = B.raw_anat('T2w', run=args.run)
    source = B.raw_anat('T2vnav', run=args.run, sourcedata=True)
    logger.debug(f'T2w raw: {raw}')
    logger.debug(f'T2vnav sourcedata: {source}')

    # get repetition time from T2w sidecar for vNav processing
    sidecar = os.path.join(*raw) + '.json'
    with open(sidecar) as fo:
        js = json.load(fo)
        tr = js['RepetitionTime']

    # mriqc job
    mriqc_outdir = None
    if 'mriqc' in args.sub_tasks:
        logger.info('building mriqc task')
        mriqc_outdir = B.derivatives_dir('t2qc/mriqc')
        mriqc_outdir = os.path.join(
            mriqc_outdir, 
            'anat',
            raw[1]
        )
        task = mriqc.Task(
            sub=args.sub,
            ses=args.ses,
            run=args.run,
            bids=B,
            outdir=mriqc_outdir,
            tempdir=tempfile.gettempdir(),
            pipenv='/sw/apps/mriqc'
        )
        logger.info(json.dumps(task.command, indent=1))
        jarray.add(task.job)

    # vnav job
    vnav_outdir = None
    if 'vnav' in args.sub_tasks:
        logger.info('building vnav task')
        indir = os.path.join(*source) + '.dicom'
        vnav_outdir = B.derivatives_dir('t2qc/vnav')
        vnav_outdir = os.path.join(
            vnav_outdir,
            'anat',
            source[1]
        )
        task = vnav.Task(
            indir,
            vnav_outdir,
            tr
        )
        if task.job:
            logger.info(json.dumps(task.command, indent=1))
            jarray.add(task.job)

    # submit jobs and wait for them to finish
    if not args.dry_run:
        logger.info('submitting jobs')
        jarray.submit(limit=args.rate_limit)
        logger.info('waiting for all jobs to finish')
        jarray.wait()
        numjobs = len(jarray.array)
        failed = len(jarray.failed)
        complete = len(jarray.complete)
        if failed:
            logger.info('%s/%s jobs failed', failed, numjobs)
            for pid,job in iter(jarray.failed.items()):
                logger.error('%s exited with returncode %s', job.name, job.returncode)
                with open(job.output, 'r') as fp:
                    logger.error('standard output\n%s', fp.read())
                with open(job.error, 'r') as fp:
                    logger.error('standard error\n%s', fp.read())
        logger.info('%s/%s jobs completed', complete, numjobs)
        if failed > 0:
            sys.exit(1)

    # snapshots
    if 'snapshots' in args.sub_tasks:
        snaps = Snapshotter(B, raw, headless=True)
        snaps.snap_t2w()

    # artifacts directory
    if not args.artifacts_dir:
        args.artifacts_dir = os.path.join(
            B.derivatives_dir('t2qc'),
            'xnat-artifacts'
        )

    # build data to upload to xnat
    params = conf['t2qc']['params']
    R = Report(args.bids_dir, args.sub, args.ses, args.run, params)
    logger.info('building xnat artifacts to %s', args.artifacts_dir)
    R.build_assessment(args.artifacts_dir)

    # upload data to xnat over rest api
    if args.xnat_upload:
        logger.info('Uploading artifacts to XNAT')
        auth = yaxil.auth2(args.xnat_alias)
        yaxil.storerest(auth, args.artifacts_dir, 't2qc-resource')

