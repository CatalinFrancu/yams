#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gtk
import os
import os.path
import pango
import pygtk
import random

import yamsData

CONFIG_FILE = '~/.yams.conf'

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

ANNOUNCED_COLUMN = 5
SERVED_COLUMN = 6

MSG_ANNOUNCE = 'You announce %s.'
MSG_FILLED_CELL = 'That cell is already filled.'
MSG_FIRST_ROLL = 'Click Roll to roll all the dice.'
MSG_OBEY_ANNOUNCE = 'You announced %s and you must fill it.'
MSG_SELECT_DICE = 'Select some dice to roll or click a cell to fill it.'
MSG_RULE_DOWN = u'The \u21e9 Down \u21e9 column must be filled top-to-bottom.'
MSG_RULE_FDOWN = u'A \u21e9 Free \u21e9 cell can only be filled if the ' +\
    u'corresponding \u21e9 Down \u21e9 cell was filled.'
MSG_RULE_FUP = u'A \u21e7 Free \u21e7 cell can only be filled if the ' +\
    u'corresponding \u21e7 Up \u21e7 cell was filled.'
MSG_RULE_UP = u'The \u21e7 Up \u21e7 column must be filled bottom-to-top.'
MSG_THREE_ROLLS = 'You can only roll three times.'
MSG_TURN = "%s's turn."
MSG_WRONG_PLAYER = "It is %s's turn, please select the appropriate score sheet."

# Row name, corresponding row on the score sheet
ROW_PROPS = [ [ 'Ones', 0],
              [ 'Twos', 1],
              [ 'Threes', 2],
              [ 'Fours', 3],
              [ 'Fives', 4],
              [ 'Sixes', 5],
              [ '', -1],
              [ 'Max', 6],
              [ 'Min', 7],
              [ '', -1],
              [ 'Straight', 8],
              [ 'Full House', 9],
              [ '4 of a Kind', 10],
              [ 'Yams', 11],
              [ '', -1],
              [ 'T1', -1],
              [ 'T2', -1],
              [ 'T3', -1],
              [ 'Total', -1] ]
ROW_T1 = 15
ROW_T2 = 16
ROW_T3 = 17
ROW_TOTAL = 18

DIE_IMAGES = [ 'images/gnome-dice-none.svg',
               'images/gnome-dice-1.svg',
               'images/gnome-dice-2.svg',
               'images/gnome-dice-3.svg',
               'images/gnome-dice-4.svg',
               'images/gnome-dice-5.svg',
               'images/gnome-dice-6.svg' ]

DEFAULT_PLAYERS = [ 'Player 1' ]

class MainWindow:
    diceButtons = None
    notebook = None
    rollButton = None
    statusBar = None
    window = None

    def loadConfigFile(self):
        try:
            f = open(os.path.expanduser(CONFIG_FILE), 'r')
            for line in f:
                line = line.strip()
                parts = line.split('=', 2)
                if parts[0].strip() == 'playerNames':
                    names = parts[1].split(',')
                    yamsData.playerNames = [x.strip() for x in names]
                    yamsData.numPlayers = len(yamsData.playerNames)
                #endif
            #endfor
            f.close()
        except IOError:
            yamsData.numPlayers = len(DEFAULT_PLAYERS)
            yamsData.playerNames = DEFAULT_PLAYERS
        #endtry
    #enddef

    def doGameNew(self, action):
        self.loadConfigFile()
        yamsData.scoreSheets = []
        for i in range(yamsData.numPlayers):
            yamsData.scoreSheets.append(yamsData.ScoreSheet())
        #endfor

        while self.notebook.get_n_pages() > 0:
            self.notebook.remove_page(0)
        #endwhile
        for i in range(yamsData.numPlayers):
            tv = self.makeTreeView()
            tv.position = i
            self.notebook.append_page(tv, gtk.Label(yamsData.playerNames[i]))
            tv.show()
        #endfor

        yamsData.currentPlayer = -1
        self.advancePlayer()
    #enddef

    def onRollButtonClick(self, button):
        anyActive = sum(x.get_active() for x in self.diceButtons)
        if yamsData.rolled > 0 and not anyActive:
            self.setStatusBarMessage(MSG_SELECT_DICE)
            return
        #endif

        for i in range(5):
            if yamsData.rolled == 0 or self.diceButtons[i].get_active():
                yamsData.dice[i] = random.randint(1, 6)
                self.setDiceImage(i)
                self.diceButtons[i].set_active(False)
            #endif
        #endfor

        if yamsData.rolled == 0:
            yamsData.firstRollDice = yamsData.dice[:]
        #endif

        yamsData.rolled += 1
        self.setRollButtonCount(yamsData.rolled + 1)
    #enddef

    def onDieClick(self, button):
        if yamsData.rolled == 0:
            self.setStatusBarMessage(MSG_FIRST_ROLL)
            button.set_active(False)
        elif yamsData.rolled == 3:
            self.setStatusBarMessage(MSG_THREE_ROLLS)
            button.set_active(False)
        elif button.get_active():
            self.setDiceImage(button.position, 0)
        else:
            self.setDiceImage(button.position)
        #endif
    #enddef

    def onSheetClick(self, treeView):
        cursor = treeView.get_cursor()
        row = cursor[0][0]
        ssRow = ROW_PROPS[row][1]

        if cursor[1] == None:
            # First time we are displaying this tree. There was no click.
            return
        #endif

        column = cursor[1].position
        ssColumn = column - 1

        if yamsData.rolled == 0 or column == 0 or ssRow == -1:
            # Not rolled, clicked on a column header or clicked in an empty row
            return
        #endif

        if treeView.position != yamsData.currentPlayer:
            # Clicked in the wrong score sheet
            name = yamsData.playerNames[yamsData.currentPlayer]
            self.setStatusBarMessage(MSG_WRONG_PLAYER % name)
            return
        #endif

        if yamsData.isFilled(ssRow, ssColumn):
            # Clicked on a cell that's already filled
            self.setStatusBarMessage(MSG_FILLED_CELL)
            return
        #endif

        if not yamsData.canBeFilled(ssRow, ssColumn):
            # Clicked on a cell that cannot yet be filled
            if column == 1:
                self.setStatusBarMessage(MSG_RULE_DOWN)
            elif column == 2:
                self.setStatusBarMessage(MSG_RULE_FDOWN)
            elif column == 3:
                self.setStatusBarMessage(MSG_RULE_FUP)
            elif column == 4:
                self.setStatusBarMessage(MSG_RULE_UP)
            #endif
            return
        #endif
            
        if yamsData.rolled == 1 and column == ANNOUNCED_COLUMN \
                and yamsData.announced == None:
            # Announce something
            self.setStatusBarMessage(MSG_ANNOUNCE % ROW_PROPS[row][0], False)
            yamsData.announced = row
            #endif
            return
        #endif

        if yamsData.announced != None and \
                (column != ANNOUNCED_COLUMN or row != yamsData.announced):
            self.setStatusBarMessage(MSG_OBEY_ANNOUNCE %
                                     ROW_PROPS[yamsData.announced][0])
            return
        #endif

        value = yamsData.writeScore(ssRow, ssColumn)
        model = treeView.get_model()
        model.set(model.get_iter(row), column, value if value else u'\u2015')

        ssCol = yamsData.scoreSheets[yamsData.currentPlayer].columns[ssColumn]
        model.set(model.get_iter(ROW_T1), column, ssCol.getT1())
        model.set(model.get_iter(ROW_T2), column, ssCol.getT2())
        model.set(model.get_iter(ROW_T3), column, ssCol.getT3())
        model.set(model.get_iter(ROW_TOTAL), column, ssCol.getTotal())        
        self.advancePlayer()
    #enddef

    def makeMenu(self):
        uiManager = gtk.UIManager()
        accelGroup = uiManager.get_accel_group()
        self.window.add_accel_group(accelGroup)
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

        for (rowName, ignored) in ROW_PROPS:
            liststore.append([rowName] + [''] * 6)
        #endfor

        # create the TreeView using liststore
        treeView = gtk.TreeView(liststore)

        # create a CellRendererText to render the data
        cellHeaderCol = gtk.CellRendererText()
        cellNormalCol = gtk.CellRendererText()
        cellHeaderCol.set_property('weight', 550)

        # create the TreeViewColumns to display the data
        for i in range(7):
            tvColumn = gtk.TreeViewColumn(COLUMN_NAMES[i])
            treeView.append_column(tvColumn)

            if i == 0:
                cell = cellHeaderCol
            else:
                cell = cellNormalCol
            #endif

            tvColumn.pack_start(cell, True)
            tvColumn.add_attribute(cell, 'text', i)
            tvColumn.set_min_width(100)
            tvColumn.position = i
        #endfor

        treeView.get_selection().set_mode(gtk.SELECTION_NONE)
        treeView.set_rules_hint(True)
        treeView.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_VERTICAL)
        treeView.connect('cursor-changed', self.onSheetClick)
        return treeView
    #enddef

    def makeDiceBox(self):
        box = gtk.VBox(False, 2)

        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_VERTICAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_show_arrow(False)
        box.pack_start(toolbar, False)

        self.diceButtons = []

        for i in range(5):
            img = gtk.Image()
            button = gtk.ToggleToolButton()
            button.set_icon_widget(img)
            button.position = i
            button.connect('clicked', self.onDieClick)
            self.diceButtons += [button]
            toolbar.insert(button, i)
            self.setDiceImage(i, 0)
        #endfor

        self.rollButton = gtk.Button('')
        self.setRollButtonCount(1)
        self.rollButton.connect('clicked', self.onRollButtonClick)
        box.pack_end(self.rollButton, False)

        box.show()
        return box
    #endif

    def setDiceImage(self, count, value = None):
        if value == None:
            value = yamsData.dice[count]
        #endif
        image = self.diceButtons[count].get_icon_widget()
        image.set_from_file(DIE_IMAGES[value])
    #enddef

    def setRollButtonCount(self, count):
        if count > 3:
            self.rollButton.set_label('Roll 3/3')
            self.rollButton.set_sensitive(False)
        else:
            self.rollButton.set_label('Roll %d/3' % count)
            self.rollButton.set_sensitive(True)
        #endif
    #enddef

    def setStatusBarMessage(self, msg, bell = True):
        contextId = self.statusBar.get_context_id('unique')
        # Never stack messages up
        self.statusBar.pop(contextId)
        self.statusBar.push(contextId, msg)
        if bell:
            self.statusBar.error_bell()
        #endif
    #enddef

    def advancePlayer(self):
        for i in range(5):
            yamsData.dice[i] = 0
            self.setDiceImage(i)
            self.diceButtons[i].set_active(False)
        #endfor

        yamsData.rolled = 0
        self.setRollButtonCount(1)
        yamsData.announced = None
        yamsData.currentPlayer += 1
        if yamsData.currentPlayer == yamsData.numPlayers:
            yamsData.currentPlayer = 0
        #endif
        self.notebook.set_current_page(yamsData.currentPlayer)

        name = yamsData.playerNames[yamsData.currentPlayer]
        self.setStatusBarMessage(MSG_TURN % name, False)
    #enddef

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Yams')
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

        self.statusBar = gtk.Statusbar()
        vbox.pack_start(self.statusBar, False)
        self.statusBar.show()

        self.window.show_all()
    #enddef
#endclass

if __name__ == "__main__":
    window = MainWindow()
    window.doGameNew(None)
    gtk.main()
#endif
