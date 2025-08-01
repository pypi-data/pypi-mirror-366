#  apt_soso/__main__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Provides a couple of nice-to-have commands which are not available in the standard apt suite.
"""
import sys, argparse, re, os
from glob import glob
from pprint import pprint
from enum import Enum
import apt_pkg

__version__ = "1.0.1"

_installed_files	= None
_options			= None
_pkg_records		= None
_info_files			= None
_cache				= None

class InfoFileType(Enum):
	CONFFILES		= "conffiles"
	CONFIG			= "config"
	LIST			= "list"
	MD5SUMS			= "md5sums"
	POSTINST		= "postinst"
	POSTRM			= "postrm"
	PREINST			= "preinst"
	PRERM			= "prerm"
	SHLIBS			= "shlibs"
	SYMBOLS			= "symbols"
	TEMPLATES		= "templates"
	TRIGGERS		= "triggers"


def show_package(pkg):
	if isinstance(pkg, str):
		pkg = _cache[pkg]
	print(pkg.name)
	if _options.description:
		print(pkg_description(pkg) + "\n")
	if _options.files:
		for f in package_files(pkg):
			print(f"\t{f}")


def installed_packages():
	return sorted([pkg for pkg in _cache.packages if pkg.current_state == apt_pkg.CURSTATE_INSTALLED], key=lambda p: p.name)


def essential_packages():
	return [ pkg for pkg in installed_packages() if pkg.essential ]


def important_packages():
	return [ pkg for pkg in installed_packages() if pkg.important ]


def pkg_description(pkg):
	global _pkg_records
	if _pkg_records is None:
		_pkg_records = apt_pkg.PackageRecords(_cache)
	if isinstance(pkg, str):
		pkg = _cache[pkg]
	_pkg_records.lookup(pkg.current_ver.file_list[-1])
	return _pkg_records.long_desc


def all_info_files():
	global _info_files
	if _info_files is None:
		for _, _, f in os.walk(_options.info_dir):
			_info_files = f
			break
	return _info_files


def info_files(pkg):
	pkgname = re.escape(pkg if isinstance(pkg, str) else pkg.name)
	return list(filter(lambda s: re.search(f"^{pkgname}(:\w+)?\..+$", s), all_info_files()))


def info_file(pkg, filetype):
	for infofile in filter(lambda s: re.search(f"\.{filetype.value}$", s), info_files(pkg)):
		return infofile


def package_files(pkg):
	infofile = info_file(pkg, InfoFileType.LIST)
	if infofile is None:
		return []
	with open(os.path.join(_options.info_dir, infofile), 'r') as fh:
		return [ line.rstrip("\n") for line in fh.readlines() if line != "/.\n" ]


def all_installed_files():
	global _installed_files
	if _installed_files is None:
		_installed_files = []
		print("Reading files installed by packages...")
		for pkg in installed_packages():
			_installed_files.extend(package_files(pkg))
		_installed_files = sorted(list(set(_installed_files)))
	return _installed_files


def all_installed_dirs():
	return list(	set( filename.split(os.sep)[1] for filename in all_installed_files() )
				- 	set( '.', 'dev', 'home', 'mnt', 'media', 'run', 'proc', 'sys' ))


def show_package(pkg):
	if isinstance(pkg, str):
		pkg = _cache[pkg]
	print(pkg.name)
	if _options.description:
		print(pkg_description(pkg) + "\n")
	if _options.files:
		for f in package_files(pkg):
			print(f"\t{f}")


def main():
	global _cache, _options
	try:
		import apt_pkg
	except ModuleNotFoundError:
		print('This module requires the "python3-apt" package to be installed')
		print('Run "sudo apt install python3-apt" to install')
		sys.exit(1)
	p = argparse.ArgumentParser()
	p.add_argument("--installed-pkgs", "-p", action="store_true", help="List all installed packages.")
	p.add_argument("--essential-pkgs", "-e", action="store_true", help="List installed packages marked \"essential\".")
	p.add_argument("--important-pkgs", "-i", action="store_true", help="List installed packages marked \"important\".")
	p.add_argument("--stand-alones", "-s", action="store_true", help="List packages which no other packages are dependent upon.")
	p.add_argument("--files", "-f", action="store_true", help="Show installed files with packages.")
	p.add_argument("--description", "-d", action="store_true", help="Show package descriptions with packages.")
	p.add_argument("--all-files", "-F", action="store_true", help="List all files installed for all installed packages.")
	p.add_argument("--all-dirs", "-D", action="store_true", help="List top-level directories where files are installed for all installed packages.")
	p.add_argument("--info-dir", action="store", default="/var/lib/dpkg/info", help="Directory where package info is stored (default /var/lib/dpkg/info).")
	_options = p.parse_args()

	apt_pkg.init_config()
	apt_pkg.init_system()
	_cache = apt_pkg.Cache()

	if _options.installed_pkgs:
		for p in installed_packages():
			show_package(p)

	if _options.essential_pkgs:
		for p in essential_packages():
			show_package(p)

	if _options.important_pkgs:
		for p in important_packages():
			show_package(p)

	if _options.all_files:
		for f in all_installed_files():
			print(f)

	if _options.all_dirs:
		for d in all_installed_dirs():
			print(d)

	if _options.stand_alones:
		all_deps = []
		all_pkgs = []
		for pkg in installed_packages():
			all_pkgs.append(pkg.name)
			if 'Depends' in pkg.current_ver.depends_list_str:
				for deps in pkg.current_ver.depends_list_str['Depends']:
					all_deps.extend([d[0] for d in deps])
		for pkgname in sorted(set(all_pkgs) - set(all_deps)):
			try:
				show_package(pkgname)
			except KeyError:
				print(f' !!! Failed to retrive info for "{pkgname}" !!!')


if __name__ == '__main__':
	sys.exit(main() or 0)

