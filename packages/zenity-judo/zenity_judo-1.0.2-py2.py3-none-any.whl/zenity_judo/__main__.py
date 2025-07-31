#  zenity/__main__.py
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
A command line test/demo for the python zenity wrapper.
"""
import argparse, sys, os, logging
from zenity_judo import (
	Calendar,
	Entry,
	Error,
	File_Selection,
	Info,
	List,
	Notification,
	Progress,
	Question,
	Text_Info,
	Warning,
	Scale,
	Color_Selection,
	Password,
	Forms
)

def main():
	p = argparse.ArgumentParser()
	p.epilog = """
	Wrapper for zenity dialogs. Usage at the command line is just for testing.
	"""
	group = p.add_mutually_exclusive_group(required = True)
	group.add_argument("--info", "-i", action = "store_true")
	group.add_argument("--warning", "-w", action = "store_true")
	group.add_argument("--error", "-r", action = "store_true")
	group.add_argument("--notification", "-n", action = "store_true")
	group.add_argument("--text-info", "-t", action = "store_true")
	group.add_argument("--entry", "-e", action = "store_true")
	group.add_argument("--password", "-P", action = "store_true")
	group.add_argument("--question", "-q", action = "store_true")
	group.add_argument("--list", "-l", action = "store_true")
	group.add_argument("--list-dict", "-d", action = "store_true")
	group.add_argument("--progress", "-p", action = "store_true")
	group.add_argument("--file-selection", "-f", action = "store_true")
	group.add_argument("--color-selection", "-c", action = "store_true")
	group.add_argument("--calendar", "-C", action = "store_true")
	group.add_argument("--scale", "-s", action = "store_true")
	group.add_argument("--forms", "-F", action = "store_true")
	p.add_argument("--multiple", "-M", action = "store_true",
		help = "Allow multiple selections when showing List")
	p.add_argument("--editable", "-E", action = "store_true",
		help = "Allow list items to be edited when showing List")
	p.add_argument("--verbose", "-v", action = "store_true")
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)3d] %(message)s"
	)

	if options.info:
		c = Info()
	elif options.warning:
		c = Warning()
	elif options.error:
		c = Error()
	elif options.notification:
		c = Notification()
	elif options.text_info:
		c = Text_Info()
		c.filename = os.path.join(os.path.dirname(__file__), 'man-zenity.txt')
		c.width = 600
		c.height = 800
	elif options.entry:
		c = Entry()
	elif options.password:
		c = Password()
	elif options.question:
		c = Question()
	elif options.list:
		c = List(['item 1', 'item 2', 'item 3'])
		c.column = 'selection'
		c.multiple = options.multiple
		c.editable = options.editable
	elif options.list_dict:
		c = List([
			{'name': 'Bob', 'grade': 11, 'department': 'Math'},
			{'name': 'Alice', 'grade': 10, 'department': 'Math'},
			{'name': 'Henry', 'grade': 12, 'department': 'Science'},
			{'name': 'George', 'grade': 5, 'department': 'Philosophy'}
		])
		c.width = 460
		c.height = 240
		c.multiple = options.multiple
		c.editable = options.editable
	elif options.progress:
		c = Progress()
	elif options.file_selection:
		c = File_Selection()
	elif options.color_selection:
		c = Color_Selection()
		c.show_palette = True
	elif options.calendar:
		c = Calendar()
	elif options.scale:
		c = Scale()
	elif options.forms:
		c = Forms()
		c.add_entry('data_type', 'Type of data')
		c.add_password('secret', 'Secret code')
		c.add_field(Forms.FIELD_CALENDAR, 'from_date', 'From date')
		c.add_calendar('to_date', 'To date')

	c.text = type(c).__name__ + " dialog"
	c.title = type(c).__name__

	print(c.show())


if __name__ == '__main__':
	main()
