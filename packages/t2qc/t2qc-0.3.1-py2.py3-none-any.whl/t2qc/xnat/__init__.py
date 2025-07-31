import re
import os
import io
import sys
import glob
import yaml
import json
import lxml
import shutil
import zipfile
import logging
import numpy as np
from lxml import etree
from t2qc.bids import BIDS

logger = logging.getLogger(__name__)

MRIQC_METRICS = [
    'cjv', 'cnr', 'efc', 'fber', 
    'fwhm_avg', 'fwhm_x', 'fwhm_y', 'fwhm_z',
    'icvs_csf', 'icvs_gm', 'icvs_wm',
    'inu_med', 'inu_range', 
    'qi_1', 'qi_2',
    'rpve_csf', 'rpve_gm', 'rpve_wm',
    'size_x', 'size_y', 'size_z',
    'snr_csf', 'snr_gm', 'snr_total', 'snr_wm',
    'snrd_csf', 'snrd_gm', 'snrd_total', 'snrd_wm', 
    'spacing_x', 'spacing_y', 'spacing_z',
    'summary_bg_k', 'summary_bg_mad', 'summary_bg_mean', 'summary_bg_median', 
    'summary_bg_n', 'summary_bg_p05', 'summary_bg_p95', 'summary_bg_stdv',
    'summary_csf_k', 'summary_csf_mad', 'summary_csf_mean', 'summary_csf_median',
    'summary_csf_n', 'summary_csf_p05', 'summary_csf_p95', 'summary_csf_stdv',
    'summary_gm_k', 'summary_gm_mad', 'summary_gm_mean', 'summary_gm_median',
    'summary_gm_n', 'summary_gm_p05', 'summary_gm_p95', 'summary_gm_stdv',
    'summary_wm_k', 'summary_wm_mad', 'summary_wm_mean', 'summary_wm_median',
    'summary_wm_n', 'summary_wm_p05', 'summary_wm_p95', 'summary_wm_stdv',
    'tpm_overlap_csf', 'tpm_overlap_gm', 'tpm_overlap_wm',
    'wm2max'
]

class Report:
    def __init__(self, bids, sub, ses, run, params):
        self.module = os.path.dirname(__file__)
        self.bids = bids
        self.sub = sub
        self.run = run
        self.ses = ses if ses else ''
        self.params = params
 
    def getdirs(self):
        self.dirs = {
            'mriqc': None,
            'vnav': None,
            'snapshots': None
        }
        for task in self.dirs.keys():
            d = os.path.join(
                self.bids,
                'derivatives',
                't2qc',
                task,
                'sub-' + self.sub.replace('sub-', ''),
                'ses-' + self.ses.replace('ses-', ''),
                'anat'
            )
            mod = 'T2w'
            if task == 'vnav':
                mod = 'T2vnav'
            basename = BIDS.basename(**{
                'sub': self.sub,
                'ses': self.ses,
                'run': self.run,
                'mod': mod
            })
            dirname = os.path.join(d, basename)
            if os.path.exists(dirname):
                self.dirs[task] = dirname
        logger.debug('mriqc dir: %s', self.dirs['mriqc'])
        logger.debug('vnav dir: %s', self.dirs['vnav'])
        logger.debug('snapshots dir: %s', self.dirs['snapshots'])

    def build_assessment(self, output):
        '''
        Build XNAT assessment

        :param output: Base output directory
        '''
        basename = BIDS.basename(**{
                'sub': self.sub,
                'ses': self.ses,
                'run': self.run,
                'mod': 'T2w'
        })
        self.getdirs()
        if not self.dirs['mriqc']:
            raise AssessmentError('need mriqc data to build assessment')
        # initialize namespaces
        ns = {
            None: 'http://www.neuroinfo.org/neuroinfo',
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xnat': 'http://nrg.wustl.edu/xnat',
            'neuroinfo': 'http://www.neuroinfo.org/neuroinfo'
        }
        # read mriqc and vnav json sidecar for scan number
        T2w_ds = self.datasource('mriqc')
        vNav_ds = self.datasource('vnav') if self.dirs['vnav'] else None
        logger.info('T2w info %s', '|'.join(T2w_ds))
        if vNav_ds:
            logger.info('T2vnav info %s', '|'.join(vNav_ds))        
        # assessment id
        aid = '{0}_T2w_{1}_T2QC'.format(T2w_ds['experiment'], T2w_ds['scan'])
        logger.info('Assessor ID %s', aid)
        # root element
        xnatns = '{%s}' % ns['xnat']
        root = etree.Element('T2QC', nsmap=ns)
        root.attrib['project'] = T2w_ds['project']
        root.attrib['ID'] = aid
        root.attrib['label'] = aid
        # get start date and time from mriqc provenance
        fname = os.path.join(self.dirs['mriqc'], 'logs', 'provenance.json')
        with open(fname) as fo:
            prov = json.load(fo)
        # add date and time
        etree.SubElement(root, xnatns + 'date').text = prov['start_date']
        etree.SubElement(root, xnatns + 'time').text = prov['start_time']
        # compile a list of files to be added to xnat:out section
        resources = [
            {
                'source': os.path.join(self.dirs['snapshots'], 'img-T2w_axis-axial_mosaic.png'),
                'dest': os.path.join('t2w-axial', '{0}_T2w_axial.png'.format(aid))
            },
            {
                'source': os.path.join(self.dirs['mriqc'], basename + '.html'),
                'dest': os.path.join('mriqc-html', '{0}_mriqc.html'.format(aid))
            }
        ]
        # not all T1w scans have a vNav
        if self.dirs['vnav']:
            resources.extend([
                {
                    'source': os.path.join(self.dirs['vnav'], 'vNav_Motion.json'),
                    'dest': os.path.join('vnav-motion-json', '{0}_vNav_Motion.json'.format(aid))
                },
                {
                    'source': os.path.join(self.dirs['vnav'], 'vNavMotionScoresMax.png'),
                    'dest': os.path.join('vnav-max', '{0}_vNavMotionScoresMax.png'.format(aid))
                },
                {
                    'source': os.path.join(self.dirs['vnav'], 'vNavMotionScoresRMS.png'),
                    'dest': os.path.join('vnav-rms', '{0}_vNavMotionScoresRMS.png'.format(aid))
                }
            ])
        # start building XML
        xnatns = '{%s}' % ns['xnat']
        etree.SubElement(root, xnatns + 'imageSession_ID').text = T2w_ds['experiment_id']
        etree.SubElement(root, 't2w_scan_id').text = T2w_ds['scan']
        if self.dirs['vnav']:
            etree.SubElement(root, 'vnav_scan_id').text = vNav_ds['scan']
        else:
            etree.SubElement(root, 'vnav_scan_id').text = 'n/a'
        etree.SubElement(root, 'session_label').text = T2w_ds['experiment']
        # add <mriqc> element
        mriqc_elm = etree.SubElement(root, 'mriqc')
        fname = os.path.join(
            self.dirs['mriqc'],
            self.sub,
            self.ses,
            'anat',
            basename + '.json'
        )
        floatfmt = '{:.5f}'.format
        with open(fname) as fo:
            mriqc = json.load(fo)
        for metric in MRIQC_METRICS:
            value = mriqc[metric]
            if isinstance(value, float):
                value = floatfmt(value)
            etree.SubElement(mriqc_elm, metric).text = str(value)
        # add <vnav> element
        if self.dirs['vnav']:
            vnav_elm = etree.SubElement(root, 'vnav')
            # count the number of vNav transforms
            fname = os.path.join(self.dirs['vnav'], 'vNav_Motion.json')
            with open(fname) as fo:
                vnav = json.load(fo)
            n_vnav_acq = len(vnav['Transforms'])
            rms_per_min = vnav['MeanMotionScoreRMSPerMin']
            max_per_min = vnav['MeanMotionScoreMaxPerMin']
            moco_fail = '0'
            if vnav['Failed']:
                moco_fail = vnav['Failed']['Acquisition']
            T2w_protocol = self.protocol('mriqc')
            T2w_software = self.software_version('mriqc')
            logger.info(f'looking up vNav settings for software={T2w_software}, series={T2w_protocol}')
            vnav_min = self.params['vnav'][T2w_software][T2w_protocol]['min']
            vnav_max = self.params['vnav'][T2w_software][T2w_protocol]['max']
            logger.info(f'found vNav settings min={vnav_min}, max={vnav_max}')
            etree.SubElement(vnav_elm, 'vnav_min').text = str(vnav_min)
            etree.SubElement(vnav_elm, 'vnav_max').text = str(vnav_max)
            etree.SubElement(vnav_elm, 'vnav_acq_tot').text = str(n_vnav_acq)
            etree.SubElement(vnav_elm, 'vnav_reacq').text = str(n_vnav_acq - vnav_min)
            etree.SubElement(vnav_elm, 'mean_mot_rms_per_min').text = floatfmt(rms_per_min)
            etree.SubElement(vnav_elm, 'mean_mot_max_per_min').text = floatfmt(max_per_min)
            etree.SubElement(vnav_elm, 'vnav_failed').text = str(moco_fail)

        # write assessor to output mount location.
        xmlstr = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        assessor_dir = os.path.join(output, 'assessor')
        os.makedirs(assessor_dir, exist_ok=True)
        assessment_xml = os.path.join(assessor_dir, 'assessment.xml')
        with open(assessment_xml, 'wb') as fo:
            fo.write(xmlstr)

        # copy resources to output mount location
        resources_dir = os.path.join(output, 'resources')
        os.makedirs(resources_dir, exist_ok=True)
        for resource in resources:
            src = resource['source']
            dest = os.path.join(resources_dir, resource['dest'])
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)

    def datasource(self, task):
        basename = os.path.basename(self.dirs[task])
        sidecar = os.path.join(self.dirs[task], 'logs', basename + '.json')
        if task == 'vnav':
            sidecar = sidecar.replace('_T1vnav.json', '_split-1_T1vnav.json')
        if not os.path.exists(sidecar):
            raise FileNotFoundError(sidecar)
        with open(sidecar) as fo:
            js = json.load(fo)
        return js['DataSource']['application/x-xnat']

    def protocol(self, task):
        basename = os.path.basename(self.dirs[task])
        sidecar = os.path.join(self.dirs[task], 'logs', basename + '.json')
        if not os.path.exists(sidecar):
            raise FileNotFoundError(sidecar)
        with open(sidecar) as fo:
            js = json.load(fo)
        return js['ProtocolName']

    def software_version(self, task):
        basename = os.path.basename(self.dirs[task])
        sidecar = os.path.join(self.dirs[task], 'logs', basename + '.json')
        if not os.path.exists(sidecar):
            raise FileNotFoundError(sidecar)
        with open(sidecar) as fo:
            js = json.load(fo)
        return js['SoftwareVersions']

class AssessmentError(Exception):
    pass
