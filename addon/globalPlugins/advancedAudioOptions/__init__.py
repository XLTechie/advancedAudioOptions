# -*- coding: utf-8 -*-
# Advanced Audio Options (advancedAudioOptions.py), version 0.1.0-dev
# An NVDA global plugin to provide UI access to the "hidden" NVDA audio options

#    Copyright (C) 2019 Luke Davis <newanswertech@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by    the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals
#from configobj import ConfigObj
import globalPluginHandler, config, gui, wx
#import globalVars

#from addonHandler import initTranslation
#initTranslation()	# Make _() work correctly

_DEBUGGING = False

if _DEBUGGING:
	from logHandler import log
	def l(msg):
		log.info("-- StateTrack --\n" + msg)
else:
	def l(ignored): pass

# Config system settings and messages
# Translators: an item in the NVDA preferences menu, or the NVDA settings category menu
_menuItemTitle = _("Advanced Audio Options...")
# Translators: wx help string, currently unused by NVDA. Describes the menu item
_menuItemHelp = _("Configure beep pitch and other less common audio settings")
# Translators: This is the label for the Advanced Audio Options settings dialog, or the category dialog in NVDA Settings screen.
_configDialogTitle = _("Advanced Audio Options")
_myConfName = "advancedAudioOptions"
# Choose between new config panel-off-of-settings-tree method, or old config dialog method
if hasattr(gui.settingsDialogs, "SettingsPanel"):
	USES_NEW_CONFIG = True
	l("Uses new config")
	_configParent = gui.settingsDialogs.SettingsPanel
else:
	USES_NEW_CONFIG = False
	_configParent = gui.SettingsDialog
	l("Uses old config")

class GlobalPlugin (globalPluginHandler.GlobalPlugin):

	l("In globalPlugin")
	# Needed for NVDA configuration dialog setup.
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if USES_NEW_CONFIG:
			l("Setting up for new config with config class. " + str(_MyConfCls))
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(_MyConfCls)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
			self.myConf = self.prefsMenu.Append(wx.ID_ANY, "&" + _menuItemTitle, _menuItemHelp)
			l("Setting up for old config. Menu item title: " + _menuItemTitle)
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onConfigDialog, self.myConf)

	# Needed for NVDA configuration dialog setup
	def onConfigDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(_MyConfCls)
		l("In onConfigDialog. Using config class: " + _MyConfCls)

	# Needed for NVDA configuration dialog cleanup
	def terminate(self):
		if USES_NEW_CONFIG:
			l("Terminating new config.")
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(_MyConfCls)
		else:
			try:
				l("Terminating old config.")
				if wx.version().startswith("4"):
					self.prefsMenu.Remove(self.myConf)
				else:
					self.prefsMenu.RemoveItem(self.myConf)
			except:
				pass

	# Main program logic

# Add-on config database
# Pretty well ripped off from Enhanced Touch Gestures and Golden Cursor by Joseph Lee
confspec = {
	"beepSpeechModePitch": "integer(min=55, max=8372, default=8000)",
	"audioCoordinates_minPitch": "integer(min=55, max=4186, default=220)",
	"audioCoordinates_maxPitch": "integer(min=110, max=8372, default=880)",
}
config.conf.spec[_myConfName] = confspec

class _MyConfCls(_configParent):
	l("In _MyConfCls with title: " + _configDialogTitle)
	title = _configDialogTitle

	def makeSettings(self, settingsSizer):
		l("In _MyConfCls.makeSettings()")
		conObj = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: the label for a numeric setting
		self.beepSpeechModePitch = conObj.addLabeledControl(_("beepSpeechModePitch"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=55, max=8372, initial=config.conf["advancedAudioOptions"]["beepSpeechModePitch"])
		# Translators: The label for a numeric setting
		self.audioCoordinates_minPitch = conObj.addLabeledControl(_("audioCoordinates_minPitch"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=55, max=4186, initial=config.conf["advancedAudioOptions"]["audioCoordinates_minPitch"])
		# Translators: The label for a numeric setting
		self.audioCoordinates_maxPitch = conObj.addLabeledControl(_("audioCoordinates_maxPitch"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=55, max=8372, initial=config.conf["advancedAudioOptions"]["audioCoordinates_maxPitch"])

	def onSave(self):
		l("In _MyConfCls.onSave().")
		for name in confspec:
			config.conf[_myConfName][name] = getattr(self, name).Value
