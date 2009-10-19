#!/usr/bin/python
import dbus

# These are defined incorrectly in dbus.dbus_bindings
DBUS_START_REPLY_SUCCESS = 1
DBUS_START_REPLY_ALREADY_RUNNING = 2

# Get the current session bus
bus = dbus.SessionBus()

# Explicitly try to start Rhythmbox.
#(success, status) = bus.start_service_by_name('org.gnome.Rhythmbox')

# If we started it, make sure we explicitly show it
#force_visible = (status == DBUS_START_REPLY_SUCCESS)
force_visible = True

# Open the Rhythmbox shell object and get its properties
rbshellobj = bus.get_object('org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Shell')
rbprops = dbus.Interface(rbshellobj, 'org.freedesktop.DBus.Properties')

# Toggle the visibility value from its current setting
is_visible = rbprops.Get('org.gnome.Rhythmbox.Shell', 'visibility')
rbprops.Set('org.gnome.Rhythmbox.Shell', 'visibility', force_visible or (not is_visible))


import gtk
q = gtk.TextView()
b = gtk.TextBuffer()
b.set_text("hi")
q.set_buffer(b)
q.show_all()
shell.add_widget(q, rb.SHELL_UI_LOCATION_MAIN_NOTEBOOK)
shell.notebook_set_page(q)

