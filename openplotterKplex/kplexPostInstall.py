#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter-kplex>
#                     e-sailing <https://github.com/e-sailing/openplotter-kplex>
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
import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-kplex',currentLanguage)

	print(_('Adding kplex service...'))
	try:
		fo = open('/etc/systemd/system/openplotter-kplex.service', "w")
		fo.write(
		'[Unit]\n'+
		'Description = NMEA 0183 Multiplexer\n'+
		'Documentation = http://www.stripydog.com/kplex/configuration.html\n'+
		'After=syslog.target network.target audit.service\n'+
		'[Service]\n'+
		'Type=forking\n'+
		'PIDFILE=/var/run/kplex.pid\n'+
		'ExecStart=/usr/bin/kplex -f ' + conf2.home + '/.kplex.conf -p /var/run/kplex.pid -o mode=background\n'+
		'KillMode=process\n'+
		'[Install]\n'+
		'WantedBy=multi-user.target\n'
		)
		
		#fo.write( #'[Service]\nExecStart=kplex\nStandardOutput=syslog\nStandardError=syslog\nUser='+conf2.user+'\nRestart=always\nRestartSec=5\n\n[#Install]\nWantedBy=multi-user.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'enable', 'openplotter-kplex'])

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'kplex', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
if __name__ == '__main__':
	main()