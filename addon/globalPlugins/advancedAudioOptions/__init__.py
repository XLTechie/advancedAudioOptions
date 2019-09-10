# -*- coding: utf-8 -*-
# Advanced Audio Options (advancedAudioOptions.py), version 0.1.0-test
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

from __future__ import unicode_literals # So we don't need strings like u"blah" in Python 2
import globalPluginHandler
import config
import gui
import wx
import aoconf # Add-on config tools module included with add-on

from addonHandler import initTranslation
initTranslation()	# Make _() work correctly

_DEBUGGING = True # Change to False for release versions!

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
# Use only for config items in the [my_add-on_name] section of config, represented here by _myConfName
confspec = {
	"beepSpeechModePitch": "integer(min=50, max=11025, default=10000)",
	"audioCoordinates_minPitch": "integer(min=55, max=4186, default=220)",
	"audioCoordinates_maxPitch": "integer(min=110, max=8372, default=880)",
}
config.conf.spec[_myConfName] = confspec
# Use for config keys that belong to other config sections (not part of this add-on).
# For example, if our "reportKeyboardShortcuts" variable was to be assigned to the global config, in the "input" section, you would use this:
# foreignConfig = { "reportKeyboardShortcuts" : [ "input" ] }
foreignConfig = {
	"beepSpeechModePitch" : [ "speech" ],
	"audioCoordinates_minPitch" : [ "mouse" ],
	"audioCoordinates_maxPitch" : [ "mouse" ],
}

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

	# Performs onSave service for settings panel, and customizable part of onOk services for settings dialog. Do all changes here.
	def onSave(self):
		l("In onSave() of _MyConfCls.")
		# Apply the add-on's own config keys to the global config dictionary
		for name in confspec:
			config.conf[_myConfName][name] = getattr(self, name).Value
		# Apply any foreign config keys to the global config dictionary
		for name, configPath in foreignConfig.iteritems():
			l("Setting up foreign config item {0}, with config path {1}.".format(name, configPath))
			firstLoop = True # Track the first loop because that has to set the value, the rest just builds the dict path
			tempConfig = {}
			for element in reversed(configPath):
				l("Acting on: {0}".format(element))
				if firstLoop: # This is the right-most key: assign the value
					tempConfig[name] = getattr(self, name)
					firstLoop = False
				tempConfig = {element : tempConfig} # Prepend the current element
			l("Adding the following configuration: {0}".format(tempConfig))
			# Merge the resulting dictionary into the global configuration
			aoconf.mergeWithConfig(tempConfig)

def onOk(self, evt):
	l("In onOk() of _MyConfCls.")
	self.onSave()
	super(_MyConfCls, self).onOk(evt)
