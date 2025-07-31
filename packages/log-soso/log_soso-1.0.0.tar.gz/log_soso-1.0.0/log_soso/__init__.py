#  log_soso/__init__.py
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
Some logging enhancements, such as log error with traceback, redirect STDOUT,
STDERR to log, and more.
"""
import os, logging, sys

__version__ = "1.0.0"


sys_stdout = sys.stdout
sys_stderr = sys.stderr


def log_error(e):
	"""
	Sends nicely formatted error message to logging.error
	"""
	tb = e.__traceback__
	logging.error('%s: %s "%s" in %s, line %s',
		tb.tb_frame.f_code.co_name,
		type(e).__name__,
		str(e),
		os.path.basename(tb.tb_frame.f_code.co_filename),
		tb.tb_lineno
	)


def log_stdout(level = logging.INFO):
	"""
	Redirect STDOUT to log
	"""
	sys.stdout = StreamToLogger(level)


def log_stderr(level = logging.ERROR):
	"""
	Redirect STDOUT to log
	"""
	sys.stderr = StreamToLogger(level)


class StreamToLogger:
	"""
	File-like stream object that redirects writes to a logger instance.
	Use like:
		with StreamToLogger(logging.getLogger(), logging.DEBUG) as sob:
			pprint(object, stream=sob)
	"""

	def __init__(self, level = logging.DEBUG):
		self.level = level
		self.linebuf = ''

	def write(self, buf):
		for line in buf.rstrip().splitlines():
			logging.getLogger().log(self.level, line)

	def flush(self):
		pass

	def __enter__(self):
		return self

	def __exit__(self, *_):
		pass


class PrintPassthru:
	"""
	A context manager which temporarily directs output to real stdout.
	"""

	def __init__(self):
		self.logger = sys.stdout

	def __enter__(self):
		sys.stdout = sys_stdout

	def __exit__(self, *_):
		sys.stdout = self.logger


#  end log_soso/__init__.py
