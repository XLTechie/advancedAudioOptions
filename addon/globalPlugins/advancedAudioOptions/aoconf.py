# -*- coding: utf-8 -*-
# aoconftools.py
# Add-on Configuration Tools version 0.1
# A helper module for NVDA add-ons

#    Copyright (C) 2019-2020 Luke Davis <newanswertech@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by    the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Used to write a dictionary of configuration values into the existing NVDA configuration dictionary
# It accepts a multi-dimensional dictionary, and overwrites existing values on conflict.
def mergeWithConfig(newValues):
	"""Merges the passed in (multi-dimensional) dictionary of NVDA configuration values into the existing NVDA config.
	Wraps dictMerge()"""
	import config
	dictMerge(config.conf, newValues)

# Merges dict b into dict a, overwriting duplicate values. Properly handles multiple dimensions.
# Only tested with strings as the final right leaf for each entry.
def dictMerge(a, b, path=None):
	"""merges b into a. Modifies a in-place and also returns it."""
	if path is None: path = []
	for key in b:
		if key in a:
			if isinstance(a[key], dict) and isinstance(b[key], dict):
				dictMerge(a[key], b[key], path + [str(key)])
			elif a[key] == b[key]:
				pass # same leaf value
			else:
				raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
		else:
			a[key] = b[key]
	return a
