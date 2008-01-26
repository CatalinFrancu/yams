#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gtk
import pango
import pygtk

from yamsData import *

CONFIG_FILE = '~/.yams'

MENU = '''<ui>
  <menubar name="MenuBar">
    <menu action="Game">
      <menuitem action="New"/>
      <menuitem action="Quit"/>
    </menu>
  </menubar>
</ui>'''

COLUMN_NAMES = [ '', u'\u21e9 Down \u21e9', u'\u21e9 Free \u21e9',
                 u'\u21e7 Free \u21e7', u'\u21e7 Up \u21e7',
                 'Announced', 'Served' ]

ROW_NAMES = [ 'Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes',
              'Max', 'Min', 'Straight', 'Full House', '4 of a Kind', 'Yams' ]

DIE_IMAGES = [ 'images/gnome-dice-none.svg',
               'images/gnome-dice-1.svg',
               'images/gnome-dice-2.svg',
               'images/gnome-dice-3.svg',
               'images/gnome-dice-4.svg',
               'images/gnome-dice-5.svg',
               'images/gnome-dice-6.svg' ]

class MainWindow:
    accelGroup = None
    diceBox = None
    notebook = None
    window = None

    def doGameNew(self, action):
        scoreSheets = []
        for i in range(numPlayers):
            scoreSheets.append(ScoreSheet())
        #endfor
    #enddef
    
    def makeMenu(self):
        uiManager = gtk.UIManager()
        self.accelGroup = uiManager.get_accel_group()
        self.window.add_accel_group(self.accelGroup)
        actionGroup = gtk.ActionGroup('UIManager')
        actionGroup.add_actions(
            [('Game', None, '_Game'),
             ('New', gtk.STOCK_NEW, '_New Game', None, None, self.doGameNew),
             ('Quit', gtk.STOCK_QUIT, None, None, None,
              lambda w: gtk.main_quit()),
             ])
        uiManager.insert_action_group(actionGroup, 0)
        uiManager.add_ui_from_string(MENU)
        return uiManager.get_widget('/MenuBar')
    #enddef

    def makeTreeView(self):
        liststore = gtk.ListStore(str, str, str, str, str, str, str)

        for row in range(12):
            liststore.append([ROW_NAMES[row]] + [''] * 6)
        #endfor

        # create the TreeView using liststore
        treeview = gtk.TreeView(liststore)

        # create a CellRendererText to render the data
        cellHeaderCol = gtk.CellRendererText()
        cellNormalCol = gtk.CellRendererText()
        cellHeaderCol.set_property('weight', 550)

        # create the TreeViewColumns to display the data
        for i in range(7):
            tvcolumn = gtk.TreeViewColumn(COLUMN_NAMES[i])
            treeview.append_column(tvcolumn)

            if i == 0:
                cell = cellHeaderCol
            else:
                cell = cellNormalCol
            #endif

            tvcolumn.pack_start(cell, True)
            tvcolumn.add_attribute(cell, 'text', i)
            tvcolumn.set_min_width(100)
        #endfor

        liststore.set(liststore.get_iter(2), 4, "qqqqq")
        treeview.get_selection().set_mode(gtk.SELECTION_NONE)
        treeview.set_rules_hint(True)
        #treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_VERTICAL)
        return treeview
    #enddef

    def makeDiceBox(self):
        box = gtk.VBox(False, 2)
        self.diceImages = []

        for i in range(5):
            img = gtk.Image()
            self.diceImages += [img]
            box.pack_start(img, False)
            self.setDiceImage(i, 0)
        #endfor


        box.show()
        return box
    #endif

    def setDiceImage(self, count, value):
        self.diceImages[count].set_from_file(DIE_IMAGES[value])
    #enddef

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Yams")
        self.window.connect('destroy', lambda w: gtk.main_quit())

        vbox = gtk.VBox(False, 2)
        self.window.add(vbox)
        vbox.show()

        menuBar = self.makeMenu()
        vbox.pack_start(menuBar, False)

        hbox = gtk.HBox(False, 2)
        vbox.pack_start(hbox, False)
        hbox.show()

        hbox.pack_start(self.makeDiceBox(), False);

        self.notebook = gtk.Notebook()
        hbox.pack_start(self.notebook, False);
        self.notebook.show()

        for i in range(3):
            tv = self.makeTreeView()
            self.notebook.append_page(tv, gtk.Label("Player %d" % (i + 1)))
            tv.show()
        #endfor

        self.window.show_all()
    #enddef
#endclass

if __name__ == "__main__":
    MainWindow()
    gtk.main()
#endif
