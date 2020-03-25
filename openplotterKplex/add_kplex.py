#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
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
import re , pyudev, os
import wx


class addkplex(wx.Dialog):
	def __init__(self, edit, extkplex, parent):
		self.parent = parent
		self.currentpath = parent.home
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		wx.Dialog.__init__(self, None, title=_('Add/Edit NMEA 0183 (KPLEX)'), size=(600, 430))
		self.extkplex = extkplex
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self.result = 0
		self.index = -1
		if edit != 0:
			self.index = edit[9]

		self.panel = wx.Panel(self)

		icon = wx.Icon(self.currentdir+"/data/kplex.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		settings = wx.StaticText(self.panel, label=_(' settings '))

		settingsType = wx.StaticText(self.panel, label=_('Type'))
		self.kplex_type_list = ['Serial', 'TCP', 'UDP']
		self.kplex_type = wx.ComboBox(self.panel, choices=self.kplex_type_list, style=wx.CB_READONLY)
		self.kplex_type.Bind(wx.EVT_COMBOBOX, self.on_kplex_type_change)

		vboxS1 = wx.BoxSizer(wx.VERTICAL)
		vboxS1.Add(settingsType, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS1.Add(self.kplex_type, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		settingsName = wx.StaticText(self.panel, label=_('Name'))
		self.kplex_name = wx.TextCtrl(self.panel, -1,)

		vboxS2 = wx.BoxSizer(wx.VERTICAL)
		vboxS2.Add(settingsName, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS2.Add(self.kplex_name, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		self.SerialCheck()
		self.kplex_ser_T1 = wx.StaticText(self.panel, label=_('Port'))
		self.kplex_device_select = wx.ComboBox(self.panel, choices=self.SerDevLs, style=wx.CB_DROPDOWN)
		
		vboxS3 = wx.BoxSizer(wx.VERTICAL)
		vboxS3.Add(self.kplex_ser_T1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS3.Add(self.kplex_device_select, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
			
		if self.SerDevLs: self.kplex_device_select.SetValue(self.SerDevLs[0])
		#self.bauds = ['4800', '9600', '19200', '38400', '57600', '115200']
		self.bauds = ['4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800']
		self.kplex_ser_T2 = wx.StaticText(self.panel, label=_('Bauds'))
		self.kplex_baud_select = wx.ComboBox(self.panel, choices=self.bauds, style=wx.CB_READONLY)

		vboxS4 = wx.BoxSizer(wx.VERTICAL)
		vboxS4.Add(self.kplex_ser_T2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS4.Add(self.kplex_baud_select, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		self.ser_io_list = ['in', 'out', 'both']
		self.SettingIO_ser = wx.StaticText(self.panel, label=_('in/out'))
		self.kplex_io_ser = wx.ComboBox(self.panel, choices=self.ser_io_list, style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.on_kplex_io_change, self.kplex_io_ser)

		vboxS5 = wx.BoxSizer(wx.VERTICAL)
		vboxS5.Add(self.SettingIO_ser, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS5.Add(self.kplex_io_ser, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		
		self.kplex_net_T1 = wx.StaticText(self.panel, label=_('Address'))
		self.kplex_address = wx.TextCtrl(self.panel, -1)
		
		vboxS3a = wx.BoxSizer(wx.VERTICAL)
		vboxS3a.Add(self.kplex_net_T1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS3a.Add(self.kplex_address, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		
		self.kplex_net_T2 = wx.StaticText(self.panel, label=_('Port'))
		self.kplex_netport = wx.TextCtrl(self.panel, -1)

		vboxS4a = wx.BoxSizer(wx.VERTICAL)
		vboxS4a.Add(self.kplex_net_T2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS4a.Add(self.kplex_netport, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		
		self.SettingIO_net = wx.StaticText(self.panel, label=_('in/out'))
		self.net_io_list = ['in', 'out']
		self.kplex_io_net = wx.ComboBox(self.panel, choices=self.net_io_list, style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.on_kplex_io_change, self.kplex_io_net)

		vboxS5a = wx.BoxSizer(wx.VERTICAL)
		vboxS5a.Add(self.SettingIO_net, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS5a.Add(self.kplex_io_net, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		
		hboxS1 = wx.BoxSizer(wx.HORIZONTAL)
		hboxS1.Add(vboxS1, 0, wx.RIGHT | wx.LEFT, 3)
		hboxS1.Add(vboxS2, 1, wx.RIGHT | wx.LEFT, 3)

		hboxS2 = wx.BoxSizer(wx.HORIZONTAL)
		hboxS2.Add(vboxS3, 0, wx.RIGHT | wx.LEFT, 3)
		hboxS2.Add(vboxS4, 0, wx.RIGHT | wx.LEFT, 3)
		hboxS2.Add(vboxS5, 0, wx.RIGHT | wx.LEFT, 3)

		hboxS3 = wx.BoxSizer(wx.HORIZONTAL)
		hboxS3.Add(vboxS3a, 0, wx.RIGHT | wx.LEFT, 3)
		hboxS3.Add(vboxS4a, 0, wx.RIGHT | wx.LEFT, 3)
		hboxS3.Add(vboxS5a, 0, wx.RIGHT | wx.LEFT, 3)
		
		vboxS23 = wx.BoxSizer(wx.VERTICAL)
		vboxS23.Add(hboxS2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vboxS23.Add(hboxS3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		
		hboxS = wx.BoxSizer(wx.HORIZONTAL)
		hboxS.Add(hboxS1, 1, wx.RIGHT | wx.LEFT, 3)
		hboxS.Add(vboxS23, 0, wx.RIGHT | wx.LEFT, 3)
				
		hline1 = wx.StaticLine(self.panel)
	
		self.name_ifilter_list = []
		for i in extkplex:
			if i[3] == 'in' or i[3] == 'both':
				self.name_ifilter_list.append(i[1])

		self.ifilter_T1 = wx.StaticText(self.panel, label=_('in Filter '))
		
		self.mode_ifilter = [_('none'), _('Accept only sentences:'), _('Ignore sentences:')]
		self.ifilter_select = wx.ComboBox(self.panel, choices=self.mode_ifilter, style=wx.CB_READONLY)
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		
		self.italker = wx.TextCtrl(self.panel, -1)
		self.ifilter_T2 = wx.StaticText(self.panel, label=_('-'))
		self.isent = wx.TextCtrl(self.panel, -1)

		hboxF = wx.BoxSizer(wx.HORIZONTAL)
		hboxF.Add(self.ifilter_select, 1, wx.RIGHT | wx.EXPAND, 9)
		hboxF.Add(self.italker, 0, wx.RIGHT | wx.LEFT, 3)
		hboxF.Add(self.ifilter_T2, 0, wx.RIGHT | wx.LEFT, 0)
		hboxF.Add(self.isent, 0, wx.RIGHT | wx.LEFT, 3)
	
		self.ifilter_sentences = wx.TextCtrl(self.panel, -1, style=wx.CB_READONLY)
		self.ifilter_sentences.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		vboxF1 = wx.BoxSizer(wx.VERTICAL)
		vboxF1.Add(hboxF, 0, wx.RIGHT | wx.LEFT, 3)
		vboxF1.AddSpacer(5)
		vboxF1.Add(self.ifilter_sentences, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 3)

		self.ifilter_add_b = wx.Button(self.panel, label=_('Add sentence'))
		self.ifilter_add_b.Bind(wx.EVT_BUTTON, self.ifilter_add)
		
		self.ifilter_del_b = wx.Button(self.panel, label=_('Delete'))
		self.ifilter_del_b.Bind(wx.EVT_BUTTON, self.ifilter_del)

		vboxF2 = wx.BoxSizer(wx.VERTICAL)
		vboxF2.Add(self.ifilter_add_b, 0, wx.RIGHT | wx.LEFT, 3)
		vboxF2.AddSpacer(5)
		vboxF2.Add(self.ifilter_del_b, 0, wx.RIGHT | wx.LEFT, 3)

		hboxF2 = wx.BoxSizer(wx.HORIZONTAL)
		hboxF2.Add(vboxF1, 1, wx.RIGHT | wx.LEFT, 3)
		hboxF2.Add(vboxF2, 0, wx.RIGHT | wx.LEFT, 3)

		hline2 = wx.StaticLine(self.panel)

		self.ofilter_T1 = wx.StaticText(self.panel, label=_('out Filter '))

		self.mode_ofilter = [_('none'), _('Accept only sentences:'), _('Ignore sentences:')]
		self.ofilter_select = wx.ComboBox(self.panel, choices=self.mode_ofilter, style=wx.CB_READONLY)
		self.ofilter_select.SetValue(self.mode_ofilter[0])
		self.otalker = wx.TextCtrl(self.panel, -1)
		self.ofilter_T2 = wx.StaticText(self.panel, label=_('-'))
		self.osent = wx.TextCtrl(self.panel, -1)
		self.name_ofilter_select = wx.ComboBox(self.panel, choices=self.name_ifilter_list, style=wx.CB_READONLY)

		hboxFo = wx.BoxSizer(wx.HORIZONTAL)
		hboxFo.Add(self.ofilter_select, 1, wx.RIGHT | wx.EXPAND, 9)
		hboxFo.Add(self.otalker, 0, wx.RIGHT | wx.LEFT, 3)
		hboxFo.Add(self.ofilter_T2, 0, wx.RIGHT | wx.LEFT, 0)
		hboxFo.Add(self.osent, 0, wx.RIGHT | wx.LEFT, 3)
		hboxFo.Add(self.name_ofilter_select, 0, wx.RIGHT | wx.LEFT, 3)

		self.ofilter_sentences = wx.TextCtrl(self.panel, -1, style=wx.CB_READONLY)
		self.ofilter_sentences.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		vboxFo1 = wx.BoxSizer(wx.VERTICAL)
		vboxFo1.Add(hboxFo, 0, wx.RIGHT | wx.LEFT, 3)
		vboxFo1.AddSpacer(5)
		vboxFo1.Add(self.ofilter_sentences, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 3)

		self.ofilter_add_b = wx.Button(self.panel, label=_('Add sentence'))
		self.Bind(wx.EVT_BUTTON, self.ofilter_add, self.ofilter_add_b)
		self.ofilter_del_b = wx.Button(self.panel, label=_('Delete'))
		self.Bind(wx.EVT_BUTTON, self.ofilter_del, self.ofilter_del_b)

		vboxFo2 = wx.BoxSizer(wx.VERTICAL)
		vboxFo2.Add(self.ofilter_add_b, 0, wx.RIGHT | wx.LEFT, 3)
		vboxFo2.AddSpacer(5)
		vboxFo2.Add(self.ofilter_del_b, 0, wx.RIGHT | wx.LEFT, 3)

		hboxFo2 = wx.BoxSizer(wx.HORIZONTAL)
		hboxFo2.Add(vboxFo1, 1, wx.RIGHT | wx.LEFT, 3)
		hboxFo2.Add(vboxFo2, 0, wx.RIGHT | wx.LEFT, 3)

		hline3 = wx.StaticLine(self.panel)

		self.ifilter_sentences.SetValue(_('nothing'))
		self.italker.SetValue('**')
		self.isent.SetValue('***')

		self.ofilter_sentences.SetValue(_('nothing'))
		self.otalker.SetValue('**')
		self.osent.SetValue('***')

		self.getSK_examp_b = wx.Button(self.panel, label=_('getSK examp'))
		self.getSK_examp_b.Bind(wx.EVT_BUTTON, self.getSK_examp)

		self.putSK_examp_b = wx.Button(self.panel, label=_('putSK examp'))
		self.putSK_examp_b.Bind(wx.EVT_BUTTON, self.putSK_examp)

		self.AP_examp_b = wx.Button(self.panel, label=_('AP examp'))
		self.AP_examp_b.Bind(wx.EVT_BUTTON, self.AP_examp)

		self.GPS_examp_b = wx.Button(self.panel, label=_('GPS examp'))
		self.GPS_examp_b.Bind(wx.EVT_BUTTON, self.GPS_examp)

		self.gpsd_examp_b = wx.Button(self.panel, label=_('gpsd examp'))
		self.gpsd_examp_b.Bind(wx.EVT_BUTTON, self.gpsd_examp)

		self.ok = wx.Button(self.panel, label=_('OK'))
		self.ok.Bind(wx.EVT_BUTTON, self.ok_conn)
		cancelBtn = wx.Button(self.panel, wx.ID_CANCEL)
		
		hboxB1 = wx.BoxSizer(wx.HORIZONTAL)
		hboxB1.Add(self.getSK_examp_b, 0, wx.RIGHT | wx.LEFT, 5)
		hboxB1.Add(self.putSK_examp_b, 0, wx.RIGHT | wx.LEFT, 5)
		hboxB1.AddStretchSpacer(1)

		hboxB = wx.BoxSizer(wx.HORIZONTAL)
		hboxB.Add(self.AP_examp_b, 0, wx.RIGHT | wx.LEFT, 5)
		hboxB.Add(self.GPS_examp_b, 0, wx.RIGHT | wx.LEFT, 5)
		hboxB.Add(self.gpsd_examp_b, 0, wx.RIGHT | wx.LEFT, 5)
		hboxB.AddStretchSpacer(1)
		hboxB.Add(self.ok, 0, wx.RIGHT | wx.LEFT, 5)
		hboxB.Add(cancelBtn, 0, wx.RIGHT | wx.LEFT, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(settings, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 5)
		vbox.Add(hboxS, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hline1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
		vbox.Add(self.ifilter_T1, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
		vbox.Add(hboxF2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hline2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
		vbox.Add(self.ofilter_T1, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
		vbox.Add(hboxFo2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hline3, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
		vbox.Add((0, 0), 1, wx.RIGHT | wx.LEFT, 5)
		vbox.Add(hboxB1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.Add(hboxB, 0, wx.ALL | wx.EXPAND, 10)
		self.panel.SetSizer(vbox)		

		if edit == 0:
			edit = ['0', '0', '0', '0', '0', '0', '0', '0', '0', -1]
			self.kplex_type.SetValue('Serial')
			self.kplex_baud_select.SetValue('4800')
			self.kplex_io_ser.SetValue('in')
			self.kplex_io_net.SetValue('in')
			self.switch_ser_net()
			self.switch_io_out(False)
		else:
			self.kplex_name.SetValue(edit[0])
			self.kplex_type.SetValue(edit[1])
			if edit[1] == 'Serial':
				self.kplex_io_ser.SetValue(edit[2])
				self.switch_ser_net()
				self.kplex_device_select.SetValue(edit[3])
				self.kplex_baud_select.SetValue(edit[4])
			else:
				self.kplex_io_net.SetValue(edit[2])
				self.switch_ser_net()
				self.kplex_address.SetValue(edit[3])
				self.kplex_netport.SetValue(edit[4])
				pass
			self.on_kplex_io_change(0)
			if edit[5] != _('none'):
				if edit[5] == _('accept'):
					self.ifilter_select.SetValue(self.mode_ifilter[1])
				if edit[5] == _('ignore'):
					self.ifilter_select.SetValue(self.mode_ifilter[2])
				self.ifilter_sentences.SetValue(edit[6])
			else:
				self.ifilter_select.SetValue(self.mode_ifilter[0])
			if edit[7] != _('none'):
				if edit[7] == _('accept'):
					self.ofilter_select.SetValue(self.mode_ofilter[1])
				if edit[7] == _('ignore'):
					self.ofilter_select.SetValue(self.mode_ofilter[2])
				self.ofilter_sentences.SetValue(edit[8])
			else:
				self.ofilter_select.SetValue(self.mode_ofilter[0])
	
	def getSK_examp(self, e):
		self.kplex_type.SetValue('TCP')
		self.kplex_io_net.SetValue('in')
		self.switch_ser_net()
		self.switch_io_out(False)
		self.switch_io_in(True)
		self.kplex_address.SetValue('127.0.0.1')
		self.kplex_netport.SetValue('10110')
		self.kplex_name.SetValue('get_sk')
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.ifilter_sentences.SetValue(_('nothing'))
		self.ofilter_select.SetValue(self.mode_ifilter[0])
		self.ofilter_sentences.SetValue(_('nothing'))

	def putSK_examp(self, e):
		self.kplex_type.SetValue('UDP')
		self.kplex_io_net.SetValue('out')
		self.switch_ser_net()
		self.switch_io_out(True)
		self.switch_io_in(False)
		self.kplex_address.SetValue('127.0.0.1')
		self.kplex_netport.SetValue('50000')
		self.kplex_name.SetValue('put_sk')
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.ifilter_sentences.SetValue(_('nothing'))
		self.ofilter_select.SetValue(self.mode_ifilter[0])
		self.ofilter_sentences.SetValue(_('nothing'))

	def GPS_examp(self, e):
		self.kplex_type.SetValue('Serial')
		self.kplex_io_ser.SetValue('in')
		self.switch_ser_net()
		self.switch_io_out(False)
		self.switch_io_in(True)
		self.kplex_baud_select.SetValue('4800')
		self.kplex_name.SetValue('gps')
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.ifilter_sentences.SetValue(_('nothing'))
		self.ofilter_select.SetValue(self.mode_ifilter[0])
		self.ofilter_sentences.SetValue(_('nothing'))

	def AP_examp(self, e):
		self.kplex_type.SetValue('Serial')
		self.kplex_io_ser.SetValue('both')
		self.switch_ser_net()
		self.switch_io_out(True)
		self.switch_io_in(True)
		self.kplex_baud_select.SetValue('4800')
		self.kplex_name.SetValue('ap')
		self.ifilter_select.SetValue(self.mode_ifilter[1])
		self.ifilter_sentences.SetValue('**HDM,**RSA')
		self.ofilter_select.SetValue(self.mode_ifilter[1])
		self.ofilter_sentences.SetValue('**RM*,**VHW,**VWR,**XT*')

	def gpsd_examp(self, e):
		self.kplex_type.SetValue('TCP')
		self.kplex_io_net.SetValue('in')
		self.switch_ser_net()
		self.switch_io_out(False)
		self.switch_io_in(True)
		#self.switch_ser_net()
		self.kplex_address.SetValue('127.0.0.1')
		self.kplex_netport.SetValue('2947')
		self.kplex_baud_select.SetValue('4800')
		self.kplex_name.SetValue('gpsd')
		self.ifilter_select.SetValue(self.mode_ifilter[0])
		self.ifilter_sentences.SetValue(_('nothing'))
		self.ofilter_select.SetValue(self.mode_ifilter[0])
		self.ofilter_sentences.SetValue(_('nothing'))

	def SerialCheck(self):
		self.SerDevLs = [_('none')]
		context = pyudev.Context()
		for device in context.list_devices(subsystem='tty'):
			i = device['DEVNAME']
			if '/dev/ttyU' in i or '/dev/ttyA' in i or '/dev/ttyS' in i or '/dev/ttyO' in i or '/dev/r' in i or '/dev/i' in i or '/dev/naviDev' in i:
				self.SerDevLs.append(i[5:])
				try:
					ii = device['DEVLINKS']
					value = ii[ii.rfind('/dev/ttyOP_'):]
					if value.find('/dev/ttyOP_') >= 0:
						self.SerDevLs.append(value.split(' ')[0][5:])
				except:
					pass
		self.SerDevLs.sort()

	def ifilter_del(self, event):
		self.ifilter_sentences.SetValue(_('nothing'))

	def ofilter_del(self, event):
		self.ofilter_sentences.SetValue(_('nothing'))

	def ifilter_add(self, event):
		talker = self.italker.GetValue()
		sent = self.isent.GetValue()

		if not re.match('^[*A-Z]{2}$', talker):
			self.ShowMessage(_('Talker must have 2 uppercase characters. The symbol * matches any character.'))
			return
		if not re.match('^[*A-Z]{3}$', sent):
			self.ShowMessage(_('Sentence must have 3 uppercase characters. The symbol * matches any character.'))
			return

		r_sentence = talker + sent
		if r_sentence == '*****':
			self.ShowMessage(_(
				'You must enter 2 uppercase characters for talker or 3 uppercase characters for sentence. The symbol * matches any character.'))
			return
		if r_sentence in self.ifilter_sentences.GetValue():
			self.ShowMessage(_('This sentence already exists.'))
			return
		if self.ifilter_sentences.GetValue() == _('nothing'):
			self.ifilter_sentences.SetValue(r_sentence)
		else:
			self.ifilter_sentences.SetValue(self.ifilter_sentences.GetValue() + ',' + r_sentence)

	def ofilter_add(self, event):
		talker = self.otalker.GetValue()
		sent = self.osent.GetValue()

		if not re.match('^[*A-Z]{2}$', talker):
			self.ShowMessage(_('Talker must have 2 uppercase characters. The symbol * matches any character.'))
			return
		if not re.match('^[*A-Z]{3}$', sent):
			self.ShowMessage(_('Sentence must have 3 uppercase characters. The symbol * matches any character.'))
			return

		r_sentence = talker + sent
		if self.name_ofilter_select.GetValue() != '':
			r_sentence += '%' + self.name_ofilter_select.GetValue()
		if r_sentence == '*****':
			self.ShowMessage(_(
				'You must enter 2 uppercase characters for talker or 3 uppercase characters for sentence. The symbol * matches any character.'))
			return
		if r_sentence in self.ofilter_sentences.GetValue():
			self.ShowMessage(_('This sentence already exists.'))
			return
		if self.ofilter_sentences.GetValue() == _('nothing'):
			self.ofilter_sentences.SetValue(r_sentence)
		else:
			self.ofilter_sentences.SetValue(self.ofilter_sentences.GetValue() + ',' + r_sentence)

	def on_kplex_type_change(self, event):
		self.switch_ser_net()

	def switch_ser_net(self):
		b = self.kplex_type.GetValue()
		if b == 'Serial':
			self.kplex_ser_T1.Enable()
			self.kplex_device_select.Enable()
			self.kplex_ser_T2.Enable()
			self.kplex_baud_select.Enable()
			self.kplex_io_ser.Enable()
			self.SettingIO_ser.Enable()
			self.kplex_net_T1.Disable()
			self.kplex_address.Disable()
			self.kplex_net_T2.Disable()
			self.kplex_netport.Disable()
			self.kplex_io_net.Disable()
			self.SettingIO_net.Disable()
		else:
			self.kplex_ser_T1.Disable()
			self.kplex_device_select.Disable()
			self.kplex_ser_T2.Disable()
			self.kplex_baud_select.Disable()
			self.kplex_io_ser.Disable()
			self.SettingIO_ser.Disable()
			self.kplex_net_T2.Enable()
			self.kplex_netport.Enable()
			self.kplex_io_net.Enable()
			self.SettingIO_net.Enable()
			if b in ['TCP','UDP']:
				self.kplex_net_T1.Enable()
				self.kplex_address.Enable()
			else:
				self.kplex_net_T1.Disable()
				self.kplex_address.Disable()
		

	def on_kplex_io_change(self, event):
		if self.kplex_type.GetValue() == 'Serial':
			in_out = str(self.kplex_io_ser.GetValue())
		else:
			in_out = str(self.kplex_io_net.GetValue())
		
		if in_out != 'out':
			self.switch_io_in(True)
		else:
			self.switch_io_in(False)
		if in_out != 'in':
			self.switch_io_out(True)
		else:
			self.switch_io_out(False)

	def switch_io_in(self, b):
		if b:
			self.ifilter_T1.Enable()
			self.ifilter_select.Enable()
			self.italker.Enable()
			self.ifilter_T2.Enable()
			self.isent.Enable()
			self.ifilter_add_b.Enable()
			self.ifilter_sentences.Enable()
			self.ifilter_del_b.Enable()
		else:
			self.ifilter_T1.Disable()
			self.ifilter_select.Disable()
			self.italker.Disable()
			self.ifilter_T2.Disable()
			self.isent.Disable()
			self.ifilter_add_b.Disable()
			self.ifilter_sentences.Disable()
			self.ifilter_del_b.Disable()
			self.ifilter_sentences.SetValue(_('nothing'))
			self.ifilter_select.SetValue(_('none'))

	def switch_io_out(self, b):
		if b:
			self.ofilter_T1.Enable()
			self.ofilter_select.Enable()
			self.otalker.Enable()
			self.ofilter_T2.Enable()
			self.osent.Enable()
			self.name_ofilter_select.Enable()
			self.ofilter_add_b.Enable()
			self.ofilter_sentences.Enable()
			self.ofilter_del_b.Enable()
		else:
			self.ofilter_T1.Disable()
			self.ofilter_select.Disable()
			self.otalker.Disable()
			self.ofilter_T2.Disable()
			self.osent.Disable()
			self.name_ofilter_select.Disable()
			self.ofilter_add_b.Disable()
			self.ofilter_sentences.Disable()
			self.ofilter_del_b.Disable()
			self.ofilter_sentences.SetValue(_('nothing'))
			self.ofilter_select.SetValue(_('none'))

	def create_gpsd(self, event):
		self.name.SetValue('gpsd')
		self.typeComboBox.SetValue('TCP')
		self.address.SetValue('127.0.0.1')
		self.port.SetValue('2947')

	def ok_conn(self, event):
		name = str(self.kplex_name.GetValue())
		name = name.replace(' ', '_')
		self.kplex_name.SetValue(name)
		type_conn = self.kplex_type.GetValue()
		port_address = ''
		bauds_port = ''
		if type_conn == 'Serial':
			in_out = str(self.kplex_io_ser.GetValue())
		else:
			in_out = str(self.kplex_io_net.GetValue())

		if not re.match('^[_0-9a-z]{1,13}$', name):
			self.ShowMessage(_(
				'"Name" must be a string between 1 and 13 lowercase letters and/or numbers which is not used as name for another input/output.'))
			return

		for index, sublist in enumerate(self.extkplex):
			if sublist[1] == name and index != self.index:
				self.ShowMessage(_('This name is already in use.'))
				return

		if name == 'system_input' or name == 'system_output':
			self.ShowMessage(_('This name is reserved by the system.'))
			return

		if type_conn == 'Serial':
			if str(self.kplex_device_select.GetValue()) != 'none':
				port_address = str(self.kplex_device_select.GetValue())
			else:
				self.ShowMessage(_('You must select a port.'))
				return
			bauds_port = str(self.kplex_baud_select.GetValue())
			for index, sublist in enumerate(self.extkplex):
				if sublist[4] == port_address and index != self.index:
					self.ShowMessage(_('This output is already in use.'))
					return

		if type_conn in ['TCP','UDP']:
			#if type_conn == 'TCP':
			if type_conn == type_conn:
				if self.kplex_address.GetValue():
					port_address = self.kplex_address.GetValue()
				else:
					self.ShowMessage(_('You must enter an address.'))
					return
			if self.kplex_netport.GetValue():
				bauds_port = self.kplex_netport.GetValue()
			else:
				self.ShowMessage(_('You must enter a port.'))
				return

			if bauds_port >= '10111' and bauds_port <= '10113' and type_conn == 'TCP':
				self.ShowMessage(_('Cancelled. Ports 10111-10113 are reserved.'))
				return

			new_address_port = str(type_conn) + str(port_address) + str(bauds_port)
			for index, sublist in enumerate(self.extkplex):
				old_address_port = str(sublist[2]) + str(sublist[4]) + str(sublist[5])
				if old_address_port == new_address_port and index != self.index:
					self.ShowMessage(_('This input is already in use.'))
					return

		if self.ifilter_select.GetValue() == _('none') and self.ifilter_sentences.GetValue() != _('nothing'):
			self.ShowMessage(_('You must select a Filter type.'))
			return

		if self.ofilter_select.GetValue() == _('none') and self.ofilter_sentences.GetValue() != _('nothing'):
			self.ShowMessage(_('You must select a Filter type.'))
			return

		filter_type = _('none')
		filtering = _('nothing')

		if self.ifilter_select.GetValue() == _('Accept only sentences:') and self.ifilter_sentences.GetValue() != _('nothing'):
			filter_type = 'accept'
			filtering = ''
			r = self.ifilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: filtering += ':'
				filtering += '+' + item
			filtering += ':-all'

		if self.ifilter_select.GetValue() == _('Ignore sentences:') and self.ifilter_sentences.GetValue() != _(
				'nothing'):
			filter_type = 'ignore'
			filtering = ''
			r = self.ifilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: filtering += ':'
				filtering += '-' + item

		ofilter_type = _('none')
		ofiltering = _('nothing')

		if self.ofilter_select.GetValue() == _('Accept only sentences:') and self.ofilter_sentences.GetValue() != _(
				'nothing'):
			ofilter_type = 'accept'
			ofiltering = ''
			r = self.ofilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: ofiltering += ':'
				ofiltering += '+' + item
			ofiltering += ':-all'

		if self.ofilter_select.GetValue() == _('Ignore sentences:') and self.ofilter_sentences.GetValue() != _(
				'nothing'):
			ofilter_type = 'ignore'
			ofiltering = ''
			r = self.ofilter_sentences.GetValue()
			l = r.split(',')
			for index, item in enumerate(l):
				if index != 0: ofiltering += ':'
				ofiltering += '-' + item

		self.add_kplex_out = ['None', name, type_conn, in_out, port_address, bauds_port, filter_type, filtering,
							  ofilter_type, ofiltering, '1', self.index]
		self.result = self.add_kplex_out
		self.Destroy()

	def ShowMessage(self, w_msg):
		wx.MessageBox(w_msg, 'Info', wx.OK | wx.ICON_INFORMATION)
