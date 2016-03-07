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
import sys


EKS_OD_HOMEPAGE_URL = 'https://portal.eks.sk/Reporty/OtvoreneUdaje'
EKS_OD_TRADES_URL = 'https://portal.eks.sk/reporty/otvoreneudaje/generujzakazkycsv'
EKS_OD_CONTRACTS_URL = 'https://portal.eks.sk/reporty/otvoreneudaje/generujzmluvycsv'
EKS_OD_USER_CONFIG = '~/.eks-od-harvestrer.ini'


# load configuration
cfg_parser = ConfigParser.SafeConfigParser()
cfg_parser.read(os.path.expanduser(EKS_OD_USER_CONFIG))
try:
    eks_user = cfg_parser.get('eks', 'user')
    eks_password = cfg_parser.get('eks', 'password')
except ConfigParser.NoOptionError as e:
    print '%s (file %s)' % (e, EKS_OD_USER_CONFIG)
    sys.exit(-1)

# visit Open Data homepage and login
print 'login ...'
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

# now get trades CSV
print 'downloading eks-zakazky.zip ...'
browser.retrieve(EKS_OD_TRADES_URL, 'eks-zakazky.zip')
print 'OK'

# and get contracts CSV
print 'downloading eks-zmluvy.zip ...'
browser.retrieve(EKS_OD_CONTRACTS_URL, 'eks-zmluvy.zip')
print 'OK'
