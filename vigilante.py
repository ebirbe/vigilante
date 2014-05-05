#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Erick Birbe <erickcion@gmail.com>
#
# This file is part of Tribus.
#
# Tribus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import os
import sys
from debian import deb822

def get_packages_info(path):
	'''
	'''
	
	packages={}
	
	#print "Reading \"%s\" file..." % os.path.basename(path)
	try:
		paragraphs = deb822.Packages.iter_paragraphs(gzip.open(path))
	except IOError, e:
		#print "Could not read %s file, error %s." % (path, e)
		return None
	else:
		for paragraph in paragraphs:
			name = paragraph['Package']
			info = paragraph
			packages[name] = info
		#print "%i package(s) readed." % len(packages)
		
	return packages

def format_output(data, f=None):
	'''
	Arguments:
	- data: A tuple with this format (type_change, old_data,
	new_data)
	'''
	output = None
	t, old, new = data
	if f:
		pass
	else:
		output = "%s\t%s\t%s\t%s" % (t,
		    new['Package'],
		    old['Version'],
	            new['Version'])

	return output

def compare_packages(old, new):
	'''
	'''
	for package in new:
		data = None
		try:
			if new[package]['md5sum'] != old[package]['md5sum']:
				data = ('C', new[package], old[package])
		except KeyError, e:
			data = ('N', new[package], new[package])

		if data:
			print format_output(data)

if __name__ == "__main__":
	
	# FIXME: Test Files, it will be changed to automated paths.
	path_old = "./cache/Packages_kerepakupai.gz"
	path_new = "./cache/Packages_kukenan.gz"
	
	# TODO: Use threads if it's possible, to reduce processing time.
	old_packages = get_packages_info(path_old)
	new_packages = get_packages_info(path_new)

	compare_packages(old_packages, new_packages)
