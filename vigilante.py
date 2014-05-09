#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Erick Birbe <erickcion@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import hashlib
import os
import re
import sys
import urllib, urllib2

from debian import deb822

from config import COMPARE_REPOS, CACHE_DIR

def download_file(url, filename):
	'''
	'''
	f_obj = urllib.urlopen(url)
	if f_obj.getcode() != 200:
		raise Exception("HTTP devolvió el status: %s" % f_obj.getcode())
	f_cache =  open(filename, "wb")
	line = True
	while line:
		line = f_obj.read()
		f_cache.write(line)
	return True

def md5Checksum(filePath):
	'''
	Returns the md5sum from a file. Taken from:
	http://www.joelverhagen.com/blog/2011/02/md5-hash-of-file-in-python/

	:param filePath: path to the file from which its md5sum will be calculated.
	.. versionadded:: 0.1
	'''
	if os.path.exists(filePath):
		with open(filePath, 'rb') as fh:
			m = hashlib.md5()
			while True:
				data = fh.read(8192)
				if not data:
					break
				m.update(data)
		return m.hexdigest()

def format_output(data, f=None):
	'''
	Arguments:
	- data: A tuple with this format:
		(type_change, old_data, new_data)
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

class Repo:
	'''
	'''
	def __init__(self, debline, architectures):
		'''
		'''
		self.debline = debline
		self.repo = None
		self.branch = None
		self.architectures = architectures
		self.components = []
		for word in self.debline.split():
			if not self.repo:
				self.repo = word
				continue;
			if not self.branch:
				self.branch = word
				continue;
			self.components.append(word)

	def get_local_path(self, component, arch):
		'''
		'''
		local_name = "_".join([self.branch, component, arch])
		repo_dir = re.sub(r'(http|ftp|file|ssh)://|/$', "", self.repo)
		return os.path.join(CACHE_DIR, repo_dir,local_name + ".gz")

	def get_packages_gz(self):
		'''
		'''
		remote_branch_path = os.path.join(self.repo, "dists", self.branch)
		release_path = os.path.join(remote_branch_path, "Release")
		changes = []
		try:
			# TODO: Use tmpfile library here
			tmp = "/tmp/Release"
			download_file(release_path, tmp)
			rls_file = open(tmp, "r")
			md5list = deb822.Release(rls_file).get('MD5sum')
			rls_file.close()
		except urllib2.URLError, e:
			print 'Could not read release file in %s, error code #%s' % (remote_branch_path, e.code)
		else:
			for package_control_file in md5list:
				if re.match("[\w]*-?[\w]*/[\w]*-[\w]*/Packages.gz$", package_control_file['name']):
					component, architecture, _ = package_control_file['name'].split("/")
					arch = architecture.replace("binary-", "")
					if arch in self.architectures:
						remote_package_path = os.path.join(remote_branch_path, package_control_file['name'])
						f = self.get_local_path(component, arch)
						if package_control_file['md5sum'] != md5Checksum(f):
							if os.path.exists(f):
								os.remove(f)
							try:
								if not os.path.exists(os.path.dirname(f)):
									os.mkdir(os.path.dirname(f))
								if download_file(remote_package_path, f):
									changes.append(f)
								else:
									print "Could not download %s" % remote_package_path
							except urllib2.URLError, e:
								print 'Could not get %s, error code #%s' % (remote_package_path, e.code)
						else:
							print 'There are no changes in %s' % f
		return changes
		
	def get_packages_info(self, component, arch):
		'''
		'''
		path = self.get_local_path(component, arch)
		packages={}
		paragraphs = deb822.Packages.iter_paragraphs(gzip.open(path))
		for paragraph in paragraphs:
			name = paragraph['Package']
			info = paragraph
			packages[name] = info
		return packages
		
	def compare(self, repo_obj):
		'''
		'''
		self.get_packages_gz()
		repo_obj.get_packages_gz()
		
		for comp in self.components:
			i = self.components.index(comp)
			for arch in self.architectures:
				comp2 = repo_obj.components[i]
				old_packages = self.get_packages_info(comp, arch)
				new_packages = repo_obj.get_packages_info(comp2, arch)
				print "===%s===%s===%s===%s===" % (self.repo, self.branch, comp, arch)
				print "===%s===%s===%s===%s===" % (repo_obj.repo, repo_obj.branch, comp2, arch)
				compare_packages(old_packages, new_packages)


if __name__ == "__main__":
	'''
	'''
	for data in COMPARE_REPOS:
		r_old = Repo(data[0], data[2])
		r_new = Repo(data[1], data[2])
		
		r_old.compare(r_new)
		
		exit(0)
