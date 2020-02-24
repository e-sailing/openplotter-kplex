#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by e-sailing <https://github.com/e-sailing/openplotter-kplex>
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

import wx, os, webbrowser, subprocess, re, ujson, sys, time
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSettings import selectConnections
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .add_kplex import addkplex
	from .version import version
else:
	import version
	from add_kplex import addkplex

class CheckListCtrl2(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(650, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)


class KplexFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.home = self.conf.home
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-kplex',self.currentLanguage)
	
		if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
			wx.Frame.__init__(self, None, title=_('Graphical user interface for NMEA 0183 multiplexer kplex')+' '+version, size=(800,444))
		else:
			wx.Frame.__init__(self, None, title=_('Graphical user interface for NMEA 0183 multiplexer kplex')+' '+version.version, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/kplex.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		refresh = self.toolbar1.AddTool(104, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.onToolRefresh, refresh)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.p_kplex = wx.Panel(self.notebook)
		self.notebook.AddPage(self.p_kplex, _('Devices'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/kplex.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)
		
		self.pageKplex()
		self.read_kplex_conf()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()

		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except: pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/kplex/kplex_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def onToolRefresh(self,e):
		self.ShowStatusBarBLACK('')
		self.read_kplex_conf()

	def pageKplex(self):
		self.list_kplex = CheckListCtrl2(self.p_kplex, 152)
		self.list_kplex.InsertColumn(0, _('Name'), width=130)
		self.list_kplex.InsertColumn(1, _('Type'), width=45)
		self.list_kplex.InsertColumn(2, _('io'), width=45)
		self.list_kplex.InsertColumn(3, _('Port/Address'), width=95)
		self.list_kplex.InsertColumn(4, _('Bauds/Port'), width=60)
		self.list_kplex.InsertColumn(5, _('inFilter'), width=55)
		self.list_kplex.InsertColumn(6, _('Filtering'), width=80)
		self.list_kplex.InsertColumn(7, _('outFilter'), width=60)
		self.list_kplex.InsertColumn(8, _('Filtering'), width=80)
		self.list_kplex.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.edit_kplex)

		diagnostic = wx.Button(self.p_kplex, label=_('Diagnostic'))
		diagnostic.Bind(wx.EVT_BUTTON, self.on_diagnostic_kplex)

		add = wx.Button(self.p_kplex, label=_('add network'))
		add.Bind(wx.EVT_BUTTON, self.on_add_kplex)
		delete = wx.Button(self.p_kplex, label=_('delete'))
		delete.Bind(wx.EVT_BUTTON, self.on_delete_kplex)

		restart = wx.Button(self.p_kplex, label=_('Restart'))
		restart.Bind(wx.EVT_BUTTON, self.on_restart_kplex)
		advanced = wx.Button(self.p_kplex, label=_('Advanced'))
		advanced.Bind(wx.EVT_BUTTON, self.on_advanced_kplex)
		apply_changes = wx.Button(self.p_kplex, label=_('Apply changes'))
		apply_changes.Bind(wx.EVT_BUTTON, self.on_apply_changes_kplex)
		cancel_changes = wx.Button(self.p_kplex, label=_('Cancel changes'))
		cancel_changes.Bind(wx.EVT_BUTTON, self.on_cancel_changes_kplex)

		hlistbox = wx.BoxSizer(wx.HORIZONTAL)
		hlistbox.Add(self.list_kplex, 1, wx.ALL | wx.EXPAND, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((0, 0), 1, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(add, 0, wx.RIGHT | wx.LEFT, 5)
		hbox.Add(delete, 0, wx.RIGHT | wx.LEFT, 5)

		hboxb = wx.BoxSizer(wx.HORIZONTAL)
		hboxb.Add(diagnostic, 0, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add(restart, 0, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add(advanced, 0, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add((0, 0), 1, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add(apply_changes, 0, wx.RIGHT | wx.LEFT, 5)
		hboxb.Add(cancel_changes, 0, wx.RIGHT | wx.LEFT, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hlistbox, 1, wx.ALL | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(hboxb, 0, wx.ALL | wx.EXPAND, 5)

		self.p_kplex.SetSizer(vbox)

	def on_advanced_kplex(self, event):
		self.ShowMessage(_(
			'GUI kplex will close. Add manual settings at the end of the configuration file. Open GUI kplex again and restart multiplexer to apply changes.'))
		try:
			subprocess.Popen(['mousepad', self.home + '/.kplex.conf'])
		except:
			self.ShowMessage(_('Editor mousepad not found'))
			return
			
		self.Close()

	def on_restart_kplex(self, event):
		self.ShowStatusBarRED(_('Closing Kplex'))
		subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'restart'])
		#subprocess.call(['pkill', '-9', 'kplex'])
		#while self.util_process_exist('kplex'):
		#	time.sleep(0.05)
		#time.sleep(0.2)
		#subprocess.Popen('kplex')
		#try:
		#	Serialinst = eval(self.conf.get('UDEV', 'serialinst'))
		#except:
		#	Serialinst = {}
		#for name in Serialinst:
		#	print(name)
		#	if Serialinst[name]['assignment'] == 'NMEA 0183 out':
		#		subprocess.Popen(['kplex', '-f', self.home+'/.nmea0183out.conf'])
		#		break
		self.ShowStatusBarGREEN(_('Kplex restarted'))
		self.read_kplex_conf()

	def stop_kplex(self):
		subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'stop'])
		#subprocess.call(['pkill', '-9', 'kplex'])
		#while self.util_process_exist('kplex'):
		#	time.sleep(0.05)

	def on_cancel_changes_kplex(self, event):
		self.read_kplex_conf()
		self.ShowStatusBarBLACK('')

	def edit_kplex(self, e):
		idx = e.GetIndex()
		filteronly = 0
		if self.kplex[idx][1] == 'system' or self.kplex[idx][1] == 'signalk' or self.kplex[idx][1] == 'gpsd':
			self.ShowStatusBarBLACK(_('You can only edit filter.'))
			filteronly = 1
		edit = []
		for i in range(9):
			edit.append(self.list_kplex.GetItem(idx, i).GetText())
		edit.append(idx)
		edit.append(filteronly)
		self.edit_add_kplex(edit)

	def on_add_kplex(self, e):
		self.edit_add_kplex(0)

	def edit_add_kplex(self, edit):
		dlg = addkplex(edit, self.kplex, self)
		dlg.ShowModal()
		result = dlg.result
		dlg.Destroy()

		if result != 0:
			k = int(result[11])
			if edit == 0:
				self.kplex.append(result)
				self.set_list_kplex()
			else:
				for i in range(10):
					self.kplex[k][i] = result[i]
				self.set_list_kplex()

	def read_kplex_conf(self):
		self.kplex = []
		self.manual_settings = ''
		try:
			file = open(self.home + '/.kplex.conf', 'r')
			data = file.readlines()
			file.close()

			l_tmp = [None] * 8
			for index, item in enumerate(data):

				if self.manual_settings:
					if item != '\n': self.manual_settings += item
				else:
					if re.search('\[*\]', item):
						if l_tmp[3] == 'in' or l_tmp[3] == 'out' or l_tmp[3] == 'both':
							self.kplex.append(l_tmp)
						l_tmp = [None] * 11
						l_tmp[6] = 'none'
						l_tmp[7] = 'nothing'
						l_tmp[8] = 'none'
						l_tmp[9] = 'nothing'
						if '[serial]' in item: l_tmp[2] = 'Serial'
						if '[tcp]' in item: l_tmp[2] = 'TCP'
						if '[udp]' in item: l_tmp[2] = 'UDP'
						if '#[' in item:
							l_tmp[10] = '0'
						else:
							l_tmp[10] = '1'
					if 'direction=in' in item:
						l_tmp[3] = 'in'
					if 'direction=out' in item:
						l_tmp[3] = 'out'
					if 'direction=both' in item:
						l_tmp[3] = 'both'
					if 'name=' in item and 'filename=' not in item:
						l_tmp[1] = self.extract_value(item)
					if 'address=' in item or 'filename=' in item:
						l_tmp[4] = self.extract_value(item)
						if '/dev' in l_tmp[4]: l_tmp[4] = l_tmp[4][5:]
					if 'port=' in item or 'baud=' in item:
						l_tmp[5] = self.extract_value(item)
					if 'ifilter=' in item and '-all' in item:
						l_tmp[6] = 'accept'
						l_tmp[7] = self.extract_value(item)
					if 'ifilter=' in item and '-all' not in item:
						l_tmp[6] = 'ignore'
						l_tmp[7] = self.extract_value(item)
					if 'ofilter=' in item and '-all' in item:
						l_tmp[8] = 'accept'
						l_tmp[9] = self.extract_value(item)
					if 'ofilter=' in item and '-all' not in item:
						l_tmp[8] = 'ignore'
						l_tmp[9] = self.extract_value(item)
					if '###Manual settings' in item:
						self.manual_settings = '###Manual settings\n\n'

			if l_tmp[3] == 'in' or l_tmp[3] == 'out' or l_tmp[3] == 'both':
				self.kplex.append(l_tmp)

			self.set_list_kplex()

		except IOError:
			self.ShowStatusBarRED(_('Multiplexer configuration file does not exist. Add inputs and apply changes.'))

	def extract_value(self, data):
		option, value = data.split('=')
		value = value.strip()
		return value

	def set_list_kplex(self):
		self.list_kplex.DeleteAllItems()
		index = 1
		for i in self.kplex:
			if i[1]:
				index = self.list_kplex.InsertItem(sys.maxsize, i[1])

			if i[2]: self.list_kplex.SetItem(index, 1, i[2])
			if i[3]: self.list_kplex.SetItem(index, 2, i[3])
			else:    self.list_kplex.SetItem(index, 2, '127.0.0.1')
			if i[4]: self.list_kplex.SetItem(index, 3, i[4])
			if i[5]: self.list_kplex.SetItem(index, 4, i[5])
			if i[6]:
				if i[6] == 'none': self.list_kplex.SetItem(index, 5, _('none'))
				if i[6] == 'accept': self.list_kplex.SetItem(index, 5, _('accept'))
				if i[6] == 'ignore': self.list_kplex.SetItem(index, 5, _('ignore'))
			if i[7] == 'nothing':
				self.list_kplex.SetItem(index, 6, _('nothing'))
			else:
				filters = i[7].replace(':-all', '')
				filters = filters.replace('+', '')
				filters = filters.replace('-', '')
				filters = filters.replace(':', ',')
				self.list_kplex.SetItem(index, 6, filters)
			if i[8]:
				if i[8] == 'none': self.list_kplex.SetItem(index, 7, _('none'))
				if i[8] == 'accept': self.list_kplex.SetItem(index, 7, _('accept'))
				if i[8] == 'ignore': self.list_kplex.SetItem(index, 7, _('ignore'))
			if i[9] == 'nothing':
				self.list_kplex.SetItem(index, 8, _('nothing'))
			else:
				filters = i[9].replace(':-all', '')
				filters = filters.replace('+', '')
				filters = filters.replace('-', '')
				filters = filters.replace(':', ',')
				self.list_kplex.SetItem(index, 8, filters)
			if i[10] == '1': self.list_kplex.CheckItem(index)

	def on_apply_changes_kplex(self, event):
		state = ''
		data = '# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Please do not modify OpenPlotter GUI settings.\n# Add manual settings at the end of the document.\n\n'

		#data += '###defaults\n\n'
		#data += '[udp]\nname=system\ndirection=in\nport=10110\n'
		#for index, item in enumerate(self.kplex):
		#	if 'system' in item[1]:
		#		if not (item[6] == _('none') or item[6] == 'none') and not (item[7] == _('nothing') or item[7] == 'nothing'): 
		#			data += state + 'ifilter=' + item[7] + '\n'
		#		if not (item[8] == _('none') or item[8] == 'none') and not (item[9] == _('nothing') or item[9] == 'nothing'): 
		#			data += state + 'ofilter=' + item[9] + '\n'
		#		data += '\n'
		#data += '[tcp]\nname=signalk\ndirection=out\nmode=server\nport=30330\n\n'
		#for index, item in enumerate(self.kplex):
		#	if 'signalk' in item[1]:
		#		if not (item[6] == _('none') or item[6] == 'none') and not (item[7] == _('nothing') or item[7] == 'nothing'): 
		#			data += state + 'ifilter=' + item[7] + '\n'
		#		if not (item[8] == _('none') or item[8] == 'none') and not (item[9] == _('nothing') or item[9] == 'nothing'): 
		#			data += state + 'ofilter=' + item[9] + '\n'
		#		data += '\n'
		#
		#data += '###end of defaults\n\n###OpenPlotter GUI settings\n\n'

		for index, item in enumerate(self.kplex):
			#if not ('system' in item[1] or 'signalk' in item[1]):
			if 0!=1: 
				if self.list_kplex.IsChecked(index):
					state = ''
				else:
					state = '#'

				if 'Serial' in item[2]:
					data += state + '[serial]\n' + state + 'name=' + item[1] + '\n' + state + 'direction=' + item[
						3] + '\n' + state + 'optional=yes\n'
					data += state + 'filename=/dev/' + item[4] + '\n' + state + 'baud=' + item[5] + '\n'
				if 'TCP' in item[2]:
					data += state + '[tcp]\n' + state + 'name=' + item[1] + '\n' + state + 'direction=' + item[
						3] + '\n' + state + 'optional=yes\n'
					if item[1] == 'gpsd': data += state + 'gpsd=yes\n'
					if item[3] != 'out':
						data += state + 'mode=client\n'
						data += state + 'persist=yes\n' + state + 'retry=10\n'
					else:
						data += state + 'mode=server\n'
					if item[4]: data += state + 'address=' + str(item[4]) + '\n' 
					data += state + 'port=' + str(item[5]) + '\n'
				if 'UDP' in item[2]:
					data += state + '[udp]\n' + state + 'name=' + item[1] + '\n' + state + 'direction=' + item[3] + '\n' + state + 'optional=yes\n'
					if item[3] == 'out':
						data += state + 'address=' + item[4] + '\n' + state + 'port=' + item[5] + '\n'
					else:
						data += state + 'port=' + item[5] + '\n'
				if not (item[6] == _('none') or item[6] == 'none') and not (item[7] == _('nothing') or item[7] == 'nothing'): 
					data += state + 'ifilter=' + item[7] + '\n'
				if not (item[8] == _('none') or item[8] == 'none') and not (item[9] == _('nothing') or item[9] == 'nothing'): 
					data += state + 'ofilter=' + item[9] + '\n'
				data += '\n'

		data += '###end of OpenPlotter GUI settings\n\n'
		if self.manual_settings:
			data += self.manual_settings
		else:
			data += '###Manual settings\n\n'

		file = open(self.home + '/.kplex.conf', 'w')
		file.write(data)
		file.close()
		self.on_restart_kplex(0)
		self.read_kplex_conf()

	def on_delete_kplex(self, event):
		selected = self.list_kplex.GetFirstSelected()
		if selected == -1:
			self.ShowStatusBarRED(_('Select an item.'))
			return
		num = len(self.kplex)
		for i in range(num):
			if self.list_kplex.IsSelected(i):
				#if self.kplex[i][1] == 'system' or self.kplex[i][1] == 'signalk':
				#	self.ShowStatusBarRED(_('You can not delete this'))
				#	return
				#if self.kplex[i][2] == 'Serial' or self.kplex[i][1] == 'gpsd':
				#	self.ShowStatusBarRED(_('Unassign this device on "Serial ports" tab'))
				#	return	
				del self.kplex[i]
		self.set_list_kplex()

	def on_diagnostic_kplex(self, event):
		selected = self.list_kplex.GetFirstSelected()
		if selected == -1:
			self.ShowStatusBarRED(_('Select an item.'))
			return
		num = len(self.kplex)
		for i in range(num):
			if self.list_kplex.IsSelected(i):
				if self.list_kplex.IsChecked(i):
					file = open(self.home + '/.kplex.conf', 'r')
					data = file.read()
					file.close()

					if self.kplex[i][3] == 'in' or self.kplex[i][3] == 'both':
						data = data + '\n\n[tcp]\nname=system_debugi\ndirection=out\nofilter=+*****%' + self.kplex[i][
							1] + ':-all\nmode=server\nport=10112\n\n'
					if self.kplex[i][3] == 'out' or self.kplex[i][3] == 'both':
						data += '\n\n[tcp]\nname=system_debugo\ndirection=out\n'
						if self.kplex[i][8] != 'none' and self.kplex[i] != 'nothing': data += 'ofilter=' + \
																							  self.kplex[i][9] + '\n'
						data += 'mode=server\nport=10113\n\n'

					file = open(self.home + '/.debugkplex.conf', 'w')
					file.write(data)
					file.close()

					self.stop_kplex()
					time.sleep(0.2)
					subprocess.Popen(['kplex', '-f', self.home + '/.debugkplex.conf'])
					time.sleep(0.5)
					subprocess.call(['pkill', '-f', 'diagnostic-NMEA.py'])
					if self.kplex[i][3] == 'in' or self.kplex[i][3] == 'both':
						subprocess.Popen(['python3', self.currentdir + '/diagnostic-NMEA.py', '10112', 'diagnostic_input'])
					if self.kplex[i][3] == 'out' or self.kplex[i][3] == 'both':
						subprocess.Popen(['python3', self.currentdir + '/diagnostic-NMEA.py', '10113', 'diagnostic_output'])
					
					#try:
					#	Serialinst = eval(self.conf.get('UDEV', 'serialinst'))
					#except:
					#	Serialinst = {}
					#for name in Serialinst:
					#	if Serialinst[name]['assignment'] == 'NMEA 0183 out':
					#		subprocess.Popen(['kplex', '-f', self.home+'/.nmea0183out.conf'])
					#		break

	def OnRemoveButton(self, e):
		index = self.list_Kplexinst.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if index < 0:
			self.ShowStatusBarYELLOW(_('No device selected'))
			return
		name = self.list_Kplexinst.GetItemText(index, 3)
		try:
			del self.Kplexinst[name]
		except: return
		self.list_Kplexinst.SetItem(index, 3, '')
		self.list_Kplexinst.SetItem(index, 7, '')
		self.reset_Kplex_fields()
		self.conf.set('UDEV', 'Kplexinst', str(self.Kplexinst))
		self.apply_changes_Kplexinst()	
			
	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'restart'])
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))
		self.read_kplex_conf()

	def util_process_exist(self, process_name):
		pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
		exist = False
		for pid in pids:
			try:
				if process_name in str(open(os.path.join('/proc', pid, 'cmdline'), 'rb').read(),'utf-8', 'ignore'):
					exist = True
			except IOError:  # proc has already terminated
				continue
			if exist:
				break
		return exist
	
	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)

################################################################################

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'kplex'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' kplexPostInstall'])
			return
	except: pass

	app = wx.App()
	KplexFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
