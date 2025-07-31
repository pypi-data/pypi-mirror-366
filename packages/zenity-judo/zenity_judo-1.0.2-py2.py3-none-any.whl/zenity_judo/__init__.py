#  zenity/__init__.py
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
Python wrapper for zenity.

From the zenity manpage:

    zenity is a program that will display GTK+ dialogs, and return (either in the
    return code, or on standard output) the users input. This allows you to present
    information, and ask for information from the user, from all manner of shell
    scripts.

    For example, zenity --question will return either 0, 1 or 5, depending on
    whether the user pressed OK, Cancel or timeout has been reached.  zenity
    --entry  will output on standard output what the user typed into the text entry
    field.

Examples:

Show a message:
    from zenity import Info
    dlg = Info(text = 'This is the message text', title = 'Some info')
    dlg.show()

Ask a question:
    dlg = Question(text = 'Are you really <b>sure</b> you want to do that?',
        ok_label = 'Sure', cancel_label = 'No, not ever')
    if dlg.show():
        print('Okay, you asked for it!')

(The above example illustrates the use of "Pango" markup. See:
https://docs.gtk.org/Pango/pango_markup.html)

Choose one out of a list:
    dlg = List(['Tom', 'Dick', 'Harry'])
    res = dlg.show()
    if res:
        print(f'Sending this off to {res} ...')

Pick a color:
    dlg = Color_Selection(color = "#00FF00")
    res = dlg.show()
    if res:
        print(f'Color me {res}')

"""
from subprocess import run, CalledProcessError
from os import linesep as ls

__version__ = "1.0.2"
TR = {ord("_"): ord("-")}

class _ZenityCommand:
	"""
    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	title 		= None
	window_icon = None
	icon_name 	= None
	width 		= None
	height 		= None
	timeout 	= None
	_stdin		= None

	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			if key in dir(self):
				setattr(self, key, value)
			else:
				raise AttributeError(f'Class "{type(self).__name__}" has no "{key}" attribute')

	def show(self):
		args = ['zenity', "--" + type(self).__name__.lower().translate(TR)] \
			+ self.args()
		try:
			res = run(
				args,
				input = self._stdin,
				capture_output = True,
				text = True,
				check = True
			)
		except CalledProcessError as err:
			if err.stderr:
				# Skip error generated when cancel is pressed in --list:
				if not 'giounix.c:410Error' in err.stderr:
					raise err
		else:
			return res.stdout.strip()

	def args(self):
		a = []
		for key in self.__dict__.keys():
			val = getattr(self, key)
			if key[0] != '_' and not val is None and not (isinstance(val, bool) and not val):
				a.append("--" + key.translate(TR))
				if not isinstance(val, bool):
					a.append(str(val))
		return a


class _ZenityTextCommand(_ZenityCommand):

	text 		= None
	no_wrap 	= None
	no_markup 	= None


class Info(_ZenityTextCommand):
	"""
    Info attributes:
        text (str):          Set the dialog text
        no_wrap (bool):      Do not enable text wrapping
        no_markup (bool):    Do not enable pango markup

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""


class Warning(_ZenityTextCommand):
	"""
    Warning attributes:
        text (str):          Set the dialog text
        no_wrap (bool):      Do not enable text wrapping
        no_markup (bool):    Do not enable pango markup

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""


class Error(_ZenityTextCommand):
	"""
    Error attributes:
        text (str):          Set the dialog text
        no_wrap (bool):      Do not enable text wrapping
        no_markup (bool):    Do not enable pango markup

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""


class Question(_ZenityTextCommand):
	"""
    Question attributes:
        text (str):          Set the dialog text
        no_wrap (bool):      Do not enable text wrapping
        no_markup (bool):    Do not enable pango markup
        ok_label (str):      Set the text of the OK button
        cancel_label (str):  Set the text of the cancel button

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	ok_label		= None
	cancel_label	= None

	def show(self):
		return super().show() is not None


class Calendar(_ZenityCommand):
	"""
    Calendar attributes:
        text (str):          Set the dialog text
        day (int):           Set the calendar day
        month (int):         Set the calendar month
        year (int):          Set the calendar year
        date_format (str):   Set the format for the returned date. The
                             default depends on the user locale or be set with
                             the strftime style. For example: %A %d/%m/%y

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text 		= None
	day			= None
	month		= None
	year		= None
	date_format	= None


class Entry(_ZenityCommand):
	"""
    Text entry attributes:
        text (str):          Set the dialog text
        entry_text (str):    Set the entry text
        hide_text (bool):    Hide the entry text

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text		= None
	entry_text	= None
	hide_text	= None


class File_Selection(_ZenityCommand):
	"""
    File selection attributes:
        filename (str):      Set the file or directory to be selected by default
        multiple (bool):     Allow selection of multiple filenames in file selection dialog
        directory (bool):    Activate directory-only selection
        save (bool):         Activate save mode
        separator (str):     Specify separator character when returning multiple filenames
        confirm_overwrite (bool):
                             Confirm file selection if filename already exists
        file_filter (str):   Sets a filename filter. The format is:
                                "<displayed name> | <pattern> [ .. <pattern> ]".
                             For example: "Text files | *.txt *.py *.md"

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	filename			= None
	multiple			= None
	directory			= None
	save				= None
	separator			= None
	confirm_overwrite	= None
	file_filter			= None


class List(_ZenityCommand):
	"""
	Displays a dialog which allows the user to select an item from a list.

	You may pass a list of options to the constructor, like so:
        dialog = List(['item 1', 'item 2', 'item 3'])
    ... in which case, the List will display a each list item on a
    single line, with no headers. The return value will be a list
    of items selected, if "multiple" is true, else the value of the
    selected item.

    List attributes:
        text (str):          Set the dialog text
        column (str):        Set the column header. Only valid when
                             constructing with a list.
        checklist (bool):    Use check boxes for first column
        radiolist (bool):    Use radio buttons for first column
        separator (str):     Set output separator character
        multiple (bool):     Allow multiple rows to be selected
        editable (bool):     Allow changes to text
        print_column (int):  Specify what column to print to standard
                             output. The default is to return the first column.
                             'ALL' may be used to print all columns.
        hide_column (int):   Hide a specific column
        hide_header (bool):  Hides the column headers

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text			= None
	column			= None
	checklist		= None
	radiolist		= None
	separator		= None
	multiple		= None
	editable		= None
	hide_column		= None
	hide_header		= None

	KEY_COLUMN		= 'key'

	def __init__(self, items, **kwargs):
		assert isinstance(items, list)
		self._items = items
		self._list_dicts = isinstance(self._items[0], dict)
		if self._list_dicts:
			self._keys = self._items[0].keys()
			for item in self._items[1:]:
				if item.keys() != self._keys:
					raise RuntimeError('All list items must have the same keys')

	def show(self):
		if not self._items:
			raise RuntimeError('No items in list')
		if self._list_dicts:
			self._stdin = ls.join(ls.join(str(val) for val in (i, *d.values())) \
				for i, d in enumerate(self._items))
		else:
			self._stdin = ls.join(self._items) + ls
		res = super().show()
		if res is None:
			return None
		if self._list_dicts or self.multiple:
			res = res.split('|' if self.separator is None else self.separator)
		if self._list_dicts:
			size = len(self._keys) + 1
			a = []
			for list_ in [ res[i:i+size] for i in range(0, len(res), size) ]:
				old_item = self._items[int(list_[0])]
				a.append({ key: type(old_value)(new_value) \
					for key, old_value, new_value in \
					zip(self._keys, old_item.values(), list_[1:]) })
			return a
			#return [ self._arg_to_dict(item) \
				#for item in res ] \
				#if self.multiple else self._arg_to_dict(res)
		return res

	def _arg_to_dict(self, item):
		return { key:val for key, val in zip(self._keys, item) }

	def args(self):
		a = super().args()
		if self._list_dicts:
			a.append('--column')
			a.append(self.KEY_COLUMN)
			for field_name in self._keys:
				a.append('--column')
				a.append(field_name)
			a.append('--hide-column')
			a.append(self.KEY_COLUMN)
			a.append('--print-column')
			a.append('ALL')
		elif self.column is None:
			a.append('--column')
			a.append(self.KEY_COLUMN)
			a.append('--hide-header')
		return a


class Notification(_ZenityCommand):
	"""
    Notification attributes:
        text (str):          Set the notification text
        listen (bool):       Listen for commands on stdin. Commands
                             include 'message', 'tooltip', 'icon', and
                             'visible' separated by a colon. For example,
                             'message: Hello world', 'visible: false', or
                             'icon: /path/to/icon'. The icon command also
                             accepts the four stock icon: 'error', 'info',
                             'question', and 'warning'

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text		= None
	listen		= None


class Progress(_ZenityCommand):
	"""
    Progress attributes:
        text (str):          Set the dialog text
        percentage (int):    Set initial percentage
        auto_close (bool):   Close dialog when 100% has been reached
        auto_kill (bool):    Kill parent process if cancel button is pressed
        pulsate (bool):      Pulsate progress bar
        no_cancel (bool):    Hides the cancel button

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text		= None
	percentage	= None
	auto_close	= None
	auto_kill	= None
	pulsate		= None
	no_cancel	= None


class Text_Info(_ZenityCommand):
	"""
    Text attributes:
        filename (str):      Open file
        editable (bool):     Allow changes to text
        checkbox (str):      Enable a checkbox for use like a 'I read and accept the terms.'
        ok_label (str):      Set the text of the OK button
        cancel_label (str):  Set the text of the cancel button

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	filename		= None
	editable		= None
	checkbox		= None
	ok_label		= None
	cancel_label	= None


class Scale(_ZenityCommand):
	"""
    Scale attributes:
        text (str):          Set the dialog text
        value (int):         Set initial value
        min_value (int):     Set minimum value
        max_value (int):     Set maximum value
        step (int):          Set step size
        print_partial (bool):
                             Print partial values
        hide_value (bool):   Hide value

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text			= None
	value			= None
	min_value		= None
	max_value		= None
	step			= None
	print_partial	= None
	hide_value		= None


class Color_Selection(_ZenityCommand):
	"""
    Color selection attributes:
        color (str):         Set the initial color. Should be either a
                             hexadecimal color value, a string in the format
                             "rgb(N, N, N)", or a string in the format
                             "rgba(N, N, N)".
        show_palette (bool): Show the palette

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	color			= None
	show_palette	= None


class Password(_ZenityCommand):
	"""
    Password dialog attributes:
        username (bool):     Also display the username field

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	username	= None


class Forms(_ZenityCommand):
	"""
	Returns a dict whose keys are the given form fields and values are the
    values provided by the user.

    Call one of the three "add_<field type>" methods to add a field.
    Fields will appear in the order in which they are added.

    Forms dialog attributes:
        text (str):          Set the dialog text
        separator (str):     Set output separator character
        forms_date_format (str):
                             Set the format for the returned date(s). The
                             default depends on the user locale or be set with
                             the strftime style. For example: %A %d/%m/%y

    General attributes:
        title (str):         Set the dialog title
        window_icon (str):   Set the window icon with the path to an
                             image. Alternatively, one of the four stock icons
                             can be used: 'error', 'info', 'question' or 'warning'
        icon_name (str):     The name of the icon to display on the
                             dialog to override the default stock icons
        width (int):         Set the dialog width
        height (int):        Set the dialog height
        timeout (int):       Set the dialog timeout in seconds
	"""
	text				= None
	separator			= None
	forms_date_format	= None

	_fields				= []

	FIELD_ENTRY			= "--add-entry"
	FIELD_PASSWORD		= "--add-password"
	FIELD_CALENDAR		= "--add-calendar"

	def add_field(self, field_type, field_name, label):
		"""
		Add a new field. The "field_type" argument may be one of:
		    FIELD_ENTRY   FIELD_PASSWORD   FIELD_CALENDAR
		Alternately, call one of the other "add_<field type>" methods.
		"""
		self._fields.append((field_type, field_name, label))

	def add_entry(self, field_name, label):
		"""
		Add a new standard field to the forms dialog.
		"""
		self._fields.append((self.FIELD_ENTRY, field_name, label))

	def add_password(self, field_name, label):
		"""
		Add a new password field to the dialog.
		"""
		self._fields.append((self.FIELD_PASSWORD, field_name, label))

	def add_calendar(self, field_name, label):
		"""
		Add a new calendar field to the dialog.
		"""
		self._fields.append((self.FIELD_CALENDAR, field_name, label))

	def args(self):
		a = super().args()
		for field_arg, field_name, label in self._fields:
			a.append(field_arg)
			a.append(label.translate(TR))
		return a

	def show(self):
		res = super().show()
		if res is None:
			return None
		return { field[1]:value for field, value in zip(self._fields, res.split('|')) }


#  end zenity/__init__.py
