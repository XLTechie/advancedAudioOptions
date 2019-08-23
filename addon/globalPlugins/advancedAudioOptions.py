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
from configobj import ConfigObj
import globalPluginHandler, globalVars, addonHandler, config, gui, wx

# This is an apparently undocumented function of addonHandler. Since everybody seems to call it, I do, but just guessing what it probably does.
addonHandler.initTranslation()

# CONSTANTS:

class GlobalPlugin (globalPluginHandler.GlobalPlugin):

	# __init__, onConfigDialog, and terminate methods borrowed heavily from Joseph Lee's stuff.

	# Needed for NVDA configuration dialog setup.
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.getAppRestriction = None	# FixMe: why do we do this?
		self.restriction = False	# FixMe: why do we do this?
		# Dialog or the panel.
		if hasattr(gui.settingsDialogs, "SettingsPanel"):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(AdvancedAudioOptions)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
			self.aaOptions = self.prefsMenu.Append(wx.ID_ANY, _("&Advanced Audio Options..."), _("Advanced Audio Options"))
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onConfigDialog, self.aaOptions)

	# Needed for NVDA configuration dialog setup
	def onConfigDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(AdvancedAudioOptions)

	# Needed for NVDA configuration dialog cleanup
	def terminate(self):
		if hasattr(gui.settingsDialogs, "SettingsPanel"):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(AdvancedAudioOptions)
		else:
			try:
				if wx.version().startswith("4"):
					self.prefsMenu.Remove(self.aaOptions)
				else:
					self.prefsMenu.RemoveItem(self.aaOptions)
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
config.conf.spec["advancedAudioOptions"] = confspec

# Decide whether to present either the old settings dialog or a settings panel.
if hasattr(gui.settingsDialogs, "SettingsPanel"):
	_configParent = gui.settingsDialogs.SettingsPanel
	_configType = 1	# New
else:
	_configParent = gui.SettingsDialog
	_configType = 0	# Old

class AdvancedAudioOptions (_configParent):
	# Translators: This is the label for the Advanced Audio Options settings dialog, or the category in NVDA Settings screen.
	title = _("Advanced Audio Options")

	def makeSettings(self, settingsSizer):
		conObj = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: a label for a setting
		self.beepSpeechModePitch = conObj.addLabeledControl(_("beepSpeechModePitch"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=55, max=8372, initial=config.conf["advancedAudioOptions"]["beepSpeechModePitch"])
		# Translators: The label for a setting in Advanced Audio Options
		self.audioCoordinates_minPitch = conObj.addLabeledControl(_("audioCoordinates_minPitch"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=55, max=4186, initial=config.conf["advancedAudioOptions"]["audioCoordinates_minPitch"])
		# Translators: The label for a setting in Advanced Audio Options
		self.audioCoordinates_maxPitch = conObj.addLabeledControl(_("audioCoordinates_maxPitch"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=55, max=8372, initial=config.conf["advancedAudioOptions"]["audioCoordinates_maxPitch"])

	def onSave(self):
		config.conf["debugHelper"]["newlinesBefore"] = self.newlinesBefore.Value
		config.conf["debugHelper"]["newlinesAfter"] = self.newlinesAfter.Value
