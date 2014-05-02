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
from debian import deb822

if __name__=="__main__":
	
	path_old="./cache/Packages_testing.gz"
	print "Leyendo paquetes actuales..."
	try:
		old_paragraphs = deb822.Packages.iter_paragraphs(gzip.open(path_old))
	except IOError, e:
		print "No se pudo leer el archivo %s, error %s" % (path, e)
	else:
		old_packages={}
		for paragraph in old_paragraphs:
			name = paragraph['Package']
			info = paragraph
			old_packages[name] = info
		print "Se leyeron %i paquetes" % len(old_packages)

	path_new="./cache/Packages_unstable.gz"
	print "Leyendo paquetes nuevos..."
	try:
		new_paragraphs = deb822.Packages.iter_paragraphs(gzip.open(path_new))
	except IOError, e:
		print "No se pudo leer el archivo %s, error %s" % (path, e)
	else:
		new_packages={}
		for paragraph in new_paragraphs:
			name = paragraph['Package']
			info = paragraph
			new_packages[name] = info
		print "Se leyeron %i paquetes" % len(new_packages)
		
		
	for package in new_packages:
		try:
			if new_packages[package]['md5sum'] != old_packages[package]['md5sum']:
				print "%s ha cambiado de %s a %s." % (package, old_packages[package]['Version'], new_packages[package]['Version'])
		except KeyError, e:
			print "%s es nuevo." % package
