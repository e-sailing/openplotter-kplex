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

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
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
		self.diagnostic = False
	
		self.selected = -1

		if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr': v = version
		else: v = version.version
		wx.Frame.__init__(self, None, title='Kplex '+v, size=(800,444))
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
		#self.toolbar1.AddSeparator()
		skConnections = self.toolbar1.AddTool(103, _('SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkConnections, skConnections)
		opSerial = self.toolbar1.AddTool(104, _('OP Serial'), wx.Bitmap(self.currentdir+"/data/usb.png"))
		self.Bind(wx.EVT_TOOL, self.OnOpSerial, opSerial)
		#self.toolbar1.AddSeparator()
		advanced = self.toolbar1.AddTool(106, _('manual settings'), wx.Bitmap(self.currentdir+"/data/kplex.png"))
		self.Bind(wx.EVT_TOOL, self.OnAdvanced, advanced)
		self.toolbar1.AddSeparator()
		apply = self.toolbar1.AddTool(107, _('Apply changes'), wx.Bitmap(self.currentdir+"/data/ok.png"))
		self.Bind(wx.EVT_TOOL, self.OnApply, apply)
		
		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.p_kplex = wx.Panel(self.notebook)
		self.systemd = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.p_kplex, _('Devices'))
		self.notebook.AddPage(self.systemd, _('Processes'))
		self.notebook.AddPage(self.output, '')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/kplex.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/process.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.appsDict = []
		
		app = {
		'name': 'Kplex',
		'included': True,
		'show': '',
		'service': ['openplotter-kplex'],
		'edit': False,
		'install': '',
		'uninstall': '',
		}
		self.appsDict.append(app)
		
		self.pageKplex()
		self.pageSystemd()
		self.pageOutput()
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
		
		tab = self.notebook.GetSelection()
		if tab == 0:
			self.toolbar1.EnableTool(105,True)
			self.toolbar1.EnableTool(106,True)
			self.toolbar1.EnableTool(107,True)
		else:
			self.toolbar1.EnableTool(105,False)
			self.toolbar1.EnableTool(106,False)
			self.toolbar1.EnableTool(107,False)

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/kplex/kplex_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def OnSkConnections(self,e):
		if self.platform.skPort:
			url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
			webbrowser.open(url, new=2)	
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def OnOpSerial(self, event=0): 
		if self.conf.get('APPS', 'serial') != '':
			subprocess.call(['pkill', '-f', 'openplotter-serial'])
			subprocess.Popen('openplotter-serial')
		else: 
			self.ShowStatusBarRED(_('Please install "Serial" OpenPlotter app'))
			self.OnToolSettings()

	def OnAdvanced(self, event):
		self.ShowMessage(_(
			'Add manual settings at the end of the configuration file. Restart to apply changes.'))
		try:
			subprocess.Popen(['mousepad', self.home + '/.kplex.conf'])
		except:
			self.ShowMessage(_('Editor mousepad not found'))
		
################################################################################
		
	def pageKplex(self):
		self.list_kplex = CheckListCtrl(self.p_kplex, 152)
		self.list_kplex.InsertColumn(0, _('Name'), width=130)
		self.list_kplex.InsertColumn(1, _('Type'), width=45)
		self.list_kplex.InsertColumn(2, _('io'), width=45)
		self.list_kplex.InsertColumn(3, _('Port/Address'), width=95)
		self.list_kplex.InsertColumn(4, _('Bauds/Port'), width=60)
		self.list_kplex.InsertColumn(5, _('inFilter'), width=55)
		self.list_kplex.InsertColumn(6, _('Filtering'), width=80)
		self.list_kplex.InsertColumn(7, _('outFilter'), width=60)
		self.list_kplex.InsertColumn(8, _('Filtering'), width=80)
		
		self.list_kplex.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)
		self.list_kplex.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselected)
		
		self.list_kplex.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEditButton)

		self.toolbar2 = wx.ToolBar(self.p_kplex, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.addButton = self.toolbar2.AddTool(201, _('Add'), wx.Bitmap(self.currentdir+"/data/kplex.png"))
		self.Bind(wx.EVT_TOOL, self.OnAddButton, self.addButton)
		self.editButton = self.toolbar2.AddTool(202, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.OnEditButton, self.editButton)
		self.showButton = self.toolbar2.AddTool(203, _('Diagnostic'), wx.Bitmap(self.currentdir+"/data/show.png"))
		self.Bind(wx.EVT_TOOL, self.OnShowButton, self.showButton)	
		self.removeButton = self.toolbar2.AddTool(204, _('Remove'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.OnRemoveButton, self.removeButton)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.list_kplex, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar2, 0)

		self.p_kplex.SetSizer(sizer)
		self.onDeselected()

	def stop_kplex(self):
		subprocess.Popen([self.platform.admin, 'pkill', '-f', 'diagnostic-NMEA.py'])
		subprocess.Popen([self.platform.admin, 'pkill', '-f', 'debugkplex'])

	def OnEditButton(self, e):
		idx = self.selected
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

	def OnAddButton(self, e):
		self.edit_add_kplex()

	def edit_add_kplex(self, edit=0):
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

	def OnApply(self, event):
		state = ''
		data = '# For advanced manual configuration, please visit: http://www.stripydog.com/kplex/configuration.html\n# Please do not modify OpenPlotter GUI settings.\n# Add manual settings at the end of the document.\n\n'

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
		time.sleep(1)
		self.OnRestart()
		self.read_kplex_conf()

	def OnRemoveButton(self, event):
		selected = self.list_kplex.GetFirstSelected()
		if selected == -1:
			self.ShowStatusBarRED(_('Select an item.'))
			return
		num = len(self.kplex)
		for i in range(num):
			if self.list_kplex.IsSelected(i):
				del self.kplex[i]
		self.set_list_kplex()

	def OnShowButton(self, event):
		selected = self.list_kplex.GetFirstSelected()
		if selected == -1:
			self.ShowStatusBarRED(_('Select an item.'))
			return
		
		command = 'systemctl show openplotter-kplex --no-page'
		output = subprocess.check_output(command.split(),universal_newlines=True)
		if 'SubState=running' in output: 
			self.ShowStatusBarRED(_('Please stop the process before you use Diagnostic.'))
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
					self.diagnostic = True

					time.sleep(0.2)
					subprocess.Popen(['kplex', '-f', self.home + '/.debugkplex.conf'])
					time.sleep(0.5)
					subprocess.call(['pkill', '-f', 'diagnostic-NMEA.py'])
					if self.kplex[i][3] == 'in' or self.kplex[i][3] == 'both':
						subprocess.Popen(['python3', self.currentdir + '/diagnostic-NMEA.py', '10112', 'diagnostic_input'])
					if self.kplex[i][3] == 'out' or self.kplex[i][3] == 'both':
						subprocess.Popen(['python3', self.currentdir + '/diagnostic-NMEA.py', '10113', 'diagnostic_output'])

	def onSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.onDeselected()
		self.selected = i
		if self.list_kplex.GetItemBackgroundColour(i) != (200,200,200):
			self.toolbar2.EnableTool(202,True)
			if self.kplex[i][10] == '1':
				self.toolbar2.EnableTool(203,True)

	def onDeselected(self, event=0):
		self.selected = -1
		self.toolbar2.EnableTool(202,False)
		self.toolbar2.EnableTool(203,False)
	
	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
		
	def write(self, string):
		wx.CallAfter(self.logger.WriteText, string)		

################################################################################
		

	def pageSystemd(self):
		self.started = False
		self.aStatusList = [_('inactive'),_('active')]
		self.bStatusList = [_('dead'),_('running')] 

		self.listSystemd = CheckListCtrl(self.systemd, 152)
		self.listSystemd.InsertColumn(0, _('Autostart'), width=90)
		self.listSystemd.InsertColumn(1, _('App'), width=90)
		self.listSystemd.InsertColumn(2, _('Process'), width=140)
		self.listSystemd.InsertColumn(3, _('Status'), width=120)
		self.listSystemd.InsertColumn(4, '  ', width=100)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSystemdSelected)
		self.listSystemd.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSystemdDeselected)
		self.listSystemd.SetTextColour(wx.BLACK)

		self.listSystemd.OnCheckItem = self.OnCheckItem

		self.toolbar3 = wx.ToolBar(self.systemd, style=wx.TB_TEXT | wx.TB_VERTICAL)
		start = self.toolbar3.AddTool(301, _('Start'), wx.Bitmap(self.currentdir+"/data/start.png"))
		self.Bind(wx.EVT_TOOL, self.onStart, start)
		stop = self.toolbar3.AddTool(302, _('Stop'), wx.Bitmap(self.currentdir+"/data/stop.png"))
		self.Bind(wx.EVT_TOOL, self.onStop, stop)
		restart = self.toolbar3.AddTool(303, _('Restart'), wx.Bitmap(self.currentdir+"/data/restart.png"))
		self.Bind(wx.EVT_TOOL, self.onRestart, restart)	

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listSystemd, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar3, 0)

		self.systemd.SetSizer(sizer)

		self.set_listSystemd()
		self.started = True

	def onListSystemdSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.toolbar3.EnableTool(301,True)
		self.toolbar3.EnableTool(302,True)
		self.toolbar3.EnableTool(303,True)

	def onListSystemdDeselected(self, event=0):
		self.toolbar3.EnableTool(301,False)
		self.toolbar3.EnableTool(302,False)
		self.toolbar3.EnableTool(303,False)

	def OnRefreshButton(self, event=0):
		self.listSystemd.DeleteAllItems()
		self.started = False
		self.set_listSystemd()
		self.started = True

	def set_listSystemd(self):
		apps = list(reversed(self.appsDict))
		for i in apps:
			if i['service']:
				for ii in i['service']:
					index = self.listSystemd.InsertItem(sys.maxsize, '')
					self.listSystemd.SetItem(index, 1, i['name'])
					self.listSystemd.SetItem(index, 2, ii)
					command = 'systemctl show '+ii+' --no-page'
					output = subprocess.check_output(command.split(),universal_newlines=True)
				if 'UnitFileState=enabled' in output: self.listSystemd.CheckItem(index)
		self.statusUpdate()

	def statusUpdate(self):
		listCount = range(self.listSystemd.GetItemCount())
		for i in listCount:
			service = self.listSystemd.GetItemText(i, 2)
			command = 'systemctl show '+service+' --no-page'
			output = subprocess.check_output(command.split(),universal_newlines=True)
			if 'ActiveState=active' in output: self.listSystemd.SetItem(i, 3, _('active'))
			else: self.listSystemd.SetItem(i, 3, _('inactive'))
			if 'SubState=running' in output: 
				self.listSystemd.SetItem(i, 4, _('running'))
				self.listSystemd.SetItemBackgroundColour(i,(0,255,0))
			else: 
				self.listSystemd.SetItem(i, 4, _('dead'))
				self.listSystemd.SetItemBackgroundColour(i,(-1,-1,-1))

						
	def onStart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Starting process...'))
		subprocess.Popen([self.platform.admin, 'pkill', '-f', 'diagnostic-NMEA.py'])
		subprocess.Popen([self.platform.admin, 'pkill', '-f', 'debugkplex'])
		subprocess.call((self.platform.admin + ' systemctl start ' + self.listSystemd.GetItemText(index, 2)).split())
		time.sleep(1)
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))

	def onStop(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Stopping process...'))
		subprocess.call((self.platform.admin + ' systemctl stop ' + self.listSystemd.GetItemText(index, 2)).split())
		time.sleep(1)
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))

	def onRestart(self,e):
		index = self.listSystemd.GetFirstSelected()
		if index == -1: return
		self.ShowStatusBarYELLOW(_('Restarting process...'))
		subprocess.Popen([self.platform.admin, 'pkill', '-f', 'diagnostic-NMEA.py'])
		subprocess.Popen([self.platform.admin, 'pkill', '-f', 'debugkplex'])
		subprocess.call((self.platform.admin + ' systemctl restart ' + self.listSystemd.GetItemText(index, 2)).split())
		time.sleep(1)
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))
		
	def OnCheckItem(self, index, flag):
		if not self.started: return
		self.ShowStatusBarYELLOW(_('Enabling/Disabling process...'))
		if flag:
			subprocess.call((self.platform.admin + ' systemctl enable ' + self.listSystemd.GetItemText(index, 2)).split())
		else:
			subprocess.call((self.platform.admin + ' systemctl disable ' + self.listSystemd.GetItemText(index, 2)).split())
		self.OnRefreshButton()
		self.ShowStatusBarGREEN(_('Done'))

################################################################################

	def pageOutput(self):
		self.logger = wx.TextCtrl(self.output, wx.ID_ANY, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

		sys.stdout = self.logger
		sys.stderr = self.logger

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
	time.sleep(1.5)
	app.MainLoop()

if __name__ == '__main__':
	main()
