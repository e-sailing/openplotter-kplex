#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-kplex>
#                     
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import subprocess, os
from openplotterSettings import language

class Start():
	def __init__(self, conf, currentLanguage):
		self.initialMessage = ''

		
	def start(self):
		green = ''
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-kplex',currentLanguage)
		allSerialPorts = serialPorts.SerialPorts()
		self.usedSerialPorts = allSerialPorts.getSerialUsedPorts()
		self.initialMessage = _('Start Kplex...')

	def check(self):
		green = _('Kplex is running')
		black = ''
		red = ''

		subprocess.call(['pkill', '-9', 'kplex'])
		while self.util_process_exist('kplex'):
			time.sleep(0.05)
		time.sleep(0.2)
		subprocess.Popen('kplex')

		return {'green': green,'black': black,'red': red}

