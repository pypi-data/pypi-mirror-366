# zenity_judo

Python wrapper for zenity.

From the zenity manpage:

>   zenity is a program that will display GTK+ dialogs, and return (either in the
    return code, or on standard output) the users input. This allows you to present
    information, and ask for information from the user, from all manner of shell
    scripts.

>   For example, zenity --question will return either 0, 1 or 5, depending on
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

## Limitations

As of this moment, the "Progress" class is not finished. If you would like to contribute a solution, feel free to make a pull request!
