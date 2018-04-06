#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Peter Hanecak <hanecak@opendata.sk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import ConfigParser
import mechanize
import os
import os.path
import sys
import zipfile
from datetime import datetime, timedelta


EKS_OD_HOMEPAGE_URL = 'https://portal.eks.sk/Reporty/OtvoreneUdaje'
EKS_OD_USER_CONFIG = '~/.eks-od-harvestrer.ini'
EKS_OD_DATA_URLS = {
    'Zakazky': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujZakazkyCsv/%Y/%m',
        'filename': 'eks-zakazky-%Y%m.zip',
        'subdir': 'zakazky'
    },
    'Zmluvne vztahy': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujZmluvyCsv/%Y/%m',
        'filename': 'eks-zmluvy-%Y%m.zip',
        'subdir': 'zmluvy'
    },
    'Zakazky a zmluvne vztahy': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujZakazkyZmluvyCsv/%Y/%m',
        'filename': 'eks-zakazky_a_zmluvy-%Y%m.zip',
        'subdir': 'zakazky_a_zmluvy'
    },
    'Referencie': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujZoznamReferencii/%Y/%m',
        'filename': 'eks-referencie-%Y%m.zip',
        'subdir': 'referencie'
    },
    'Opisne formulare': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujZoznamOpisnychFormularov/%Y/%m',
        'filename': 'eks-opisne_formulare-%Y%m.zip',
        'subdir': 'opisne_formulare'
    },
    'Kontraktacne ponuky': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujKontraktacnePonukyCsv/%Y/%m',
        'filename': 'eks-kontraktacne_ponuky-%Y%m.zip',
        'subdir': 'kontraktacne_ponuky'
    },
    'Aukcne ponuky': {
        'url': 'https://portal.eks.sk/Reporty/OtvoreneUdaje/GenerujAukcnePonukyCsv/%Y/%m',
        'filename': 'eks-aukcne_ponuky-%Y%m.zip',
        'subdir': 'aukcne_ponuky'
    }
}


# load configuration
cfg_parser = ConfigParser.SafeConfigParser()
cfg_parser.read(os.path.expanduser(EKS_OD_USER_CONFIG))
try:
    eks_user = cfg_parser.get('eks', 'user')
    eks_password = cfg_parser.get('eks', 'password')
except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
    print '%s (file %s)' % (e, EKS_OD_USER_CONFIG)
    sys.exit(-1)

# visit Open Data homepage and login
print 'login ...',
browser = mechanize.Browser()
browser.open(EKS_OD_HOMEPAGE_URL)
browser.select_form(nr = 0)
browser.form['UserName'] = eks_user
browser.form['Password'] = eks_password
response = browser.submit()
page_body = response.read()
if page_body.find("Odhlásiť sa") < 0:
    print 'login seems to have failed'
    sys.exit(-2)
print 'OK'

# We're be getting data for "yesterday" to make sure we have everything.
# (If we're going to run this script daily and get data for "now", we might
# end up missing data between "now" and midnight.)
yesterday = datetime.now() - timedelta(days = 1)
# Allow overriding the year/month from command line (for now very crude
# commnad line argument handling. Later we can utilize argparse.)
# Usage: eks-od-harvestrer.py YYYY-mm
if len(sys.argv) == 2:
    yesterday = datetime.strptime(sys.argv[1], "%Y-%m")

# now get all CSVs
for dataset in EKS_OD_DATA_URLS.keys():
    # download ZIP
    dataset_url = yesterday.strftime(EKS_OD_DATA_URLS[dataset]['url'])
    dataset_fn = yesterday.strftime(EKS_OD_DATA_URLS[dataset]['filename'])
    print 'downloading "%s" from %s into %s ...' % (dataset, dataset_url, dataset_fn),
    browser.retrieve(dataset_url, dataset_fn)
    print 'OK'

    # extract CSV (discarding dirname from ZIP archive) but into our own subdir structure
    zip_file = zipfile.ZipFile(dataset_fn)
    for name in zip_file.namelist():
        (dirname, filename) = os.path.split(name)
        our_dirname = EKS_OD_DATA_URLS[dataset]['subdir']
        print 'extracting %s from %s into %s/%s ...' % (name, dataset_fn, our_dirname, filename),
        if not os.path.exists(our_dirname):
            os.makedirs(our_dirname)
        zip_file.extract(name, our_dirname)
        print 'OK'

    # clean-up: we do not need ZIPs
    print 'removing %s ...' % dataset_fn,
    os.remove(dataset_fn)
    print 'OK'
