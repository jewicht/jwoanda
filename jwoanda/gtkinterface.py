import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import threading
import logging

from jwoanda.baseinterface import BaseInterface

class InstrWindow(Gtk.Window):

    def __init__(self, instruments):
        Gtk.Window.__init__(self, title="Trading window")
        
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.ninstruments = len(instruments)
        
        self.store = Gtk.ListStore(str, float, float, float)
        for instrument in instruments:
            self.store.append([instrument, 0., 0., 0.])

        treeview = Gtk.TreeView.new_with_model(self.store)
        for i, column_title in enumerate(["instrument", "bid", "ask", "spread"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            treeview.append_column(column)
        self.grid.add(treeview)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        
        self.textbuffer = self.textview.get_buffer()

        self.grid.attach_next_to(self.textview, treeview, Gtk.PositionType.RIGHT, 2, 1)


    def clear(self):
        self.textbuffer.set_text("")        


class GTKInterface(threading.Thread, BaseInterface):

    def __init__(self, instruments, **kwargs):
        super(GTKInterface, self).__init__(**kwargs)
        self.win = InstrWindow(instruments)
        #win2 = LogWindow()
        self.win.connect("delete-event", Gtk.main_quit)
        self.win.show_all()
    
        
    def run(self):
        Gtk.main()

    def disconnect(self):
        self.win.close()
        Gtk.main_quit()

    def setprice(self, name, b, a):
        for i in range(0, self.win.ninstruments):
            if self.win.store[i][0] == name:
                self.win.store[i][1] = b
                self.win.store[i][2] = a
                self.win.store[i][3] = a - b
                #logging.error("updated")
                return
            #logging.error("not understood {}" % name)

    def addtext(self, t):
        self.win.textbuffer.insert(self.win.textbuffer.get_iter_at_line(0), t + "\n")
