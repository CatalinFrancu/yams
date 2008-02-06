#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008 Catalin Francu <cata@francu.com>
#
# This file is part of Yams.
#
# Yams is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yams is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Yams.  If not, see <http://www.gnu.org/licenses/>.

import gnome
import gtk
import operator
import os
import os.path
import pango
import pygtk
import random
import time

import yamsData

VERSION = '1.0'
CONFIG_FILE = '~/.yams.conf'

MENU = '''<ui>
  <menubar name="MenuBar">
    <menu action="Game">
      <menuitem action="New"/>
      <menuitem action="Quit"/>
    </menu>
    <menu action="Settings">
      <menuitem action="Preferences"/>
    </menu>
    <menu action="Help">
      <menuitem action="Contents"/>
      <menuitem action="About"/>
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
MSG_GAME_OVER = 'Game over!'
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
MAX_PLAYERS = 6
MAX_TURNS = 6 * 12

def loadConfigFile():
    try:
        f = open(os.path.expanduser(CONFIG_FILE), 'r')
        for line in f:
            line = line.strip()
            parts = line.split('=', 2)
            if parts[0].strip() == 'playerNames':
                names = parts[1].split(',')
                playerNames = [x.strip() for x in names]
            #endif
        #endfor
        f.close()
    except IOError:
        playerNames = DEFAULT_PLAYERS
    #endtry
    return playerNames
#enddef

def saveConfigFile(playerNames):
    try:
        f = open(os.path.expanduser(CONFIG_FILE), 'w')
        f.write('playerNames = %s\n' % (', '.join(playerNames)))
        f.close()
    except IOError:
        pass
    #endtry
#enddef

class PreferencesWindow(gtk.Dialog):
    entries = None
    okButton = None

    def __init__(self, parent):
        gtk.Dialog.__init__(self, 'Yams Preferences', parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        playerNames = loadConfigFile()

        hbox = gtk.HBox(False, 2)
        self.vbox.pack_start(hbox, False, False, 10)
        hbox.show()

        label = gtk.Label('Number of players: ')
        hbox.pack_start(label, False, False, 10)
        label.show()

        adjustment = gtk.Adjustment(len(playerNames), 1, MAX_PLAYERS, 1)
        self.spinNumPlayers = gtk.SpinButton(adjustment)
        hbox.pack_start(self.spinNumPlayers, False, False, 10)
        self.spinNumPlayers.show()
        self.spinNumPlayers.connect('value-changed', self.onNumPlayersChanged)
        
        label = gtk.Label('Player names:')
        self.vbox.pack_start(label, False)
        label.show()

        table = gtk.Table(MAX_PLAYERS, 2)
        self.vbox.pack_start(table, False, False, 10)
        table.show()

        self.entries = []
        for i in range(MAX_PLAYERS):
            label = gtk.Label('%d:' % (i + 1))
            table.attach(label, 0, 1, i, i + 1)
            label.show()

            entry = gtk.Entry(40)
            table.attach(entry, 1, 2, i, i + 1, gtk.EXPAND | gtk.FILL, 0, 10)
            entry.show()
            entry.connect('changed', self.onEntryChanged)

            if i < len(playerNames):
                entry.set_text(playerNames[i])
            else:
                entry.set_sensitive(False)
            #endif
            self.entries += [entry]
        #endfor

        for c in self.action_area.get_children():
            if c.get_label() == 'gtk-ok':
              self.okButton = c
            #endif
        #endfor
    #enddef

    def onNumPlayersChanged(self, spinButton):
        for i in range(MAX_PLAYERS):
            self.entries[i].set_sensitive(i < spinButton.get_value())
        #endfor
        self.onEntryChanged(None)
    #enddef

    def onEntryChanged(self, entry):
        anyEmpty = 0
        for e in self.entries:
            if e.get_text().strip() == '' and e.state == gtk.STATE_NORMAL:
                anyEmpty = True
            #endif
        #endfor

        if self.okButton:
            self.okButton.set_sensitive(not anyEmpty)
        #endif
    #enddef

    def getPlayerNames(self):
        return [e.get_text() for e in self.entries \
                    if e.state == gtk.STATE_NORMAL]
    #enddef
#endclass


class ScoreWindow(gtk.Dialog):

    def __init__(self, parent):
        gtk.Dialog.__init__(self, 'Final Scores', parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.set_default_size(300, -1)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        matrix = []
        for i in range(yamsData.numPlayers):
            name = yamsData.playerNames[i]
            score = yamsData.scoreSheets[i].getTotal()
            matrix += [(name, score)]
        #endfor
        matrix.sort(key=operator.itemgetter(1))
        matrix.reverse()

        table = gtk.Table(yamsData.numPlayers, 3, False)
        self.vbox.pack_start(table, False, False, 10)

        for i in range(yamsData.numPlayers):
            label = gtk.Label('%d.' % (i + 1))
            table.attach(label, 0, 1, i, i + 1, gtk.FILL, 0, 20)

            label = gtk.Label(matrix[i][0])
            label.set_alignment(0.0, 0.0)
            table.attach(label, 1, 2, i, i + 1, gtk.EXPAND | gtk.FILL, 0, 0)

            label = gtk.Label(matrix[i][1])
            label.set_alignment(1.0, 0.0)
            table.attach(label, 2, 3, i, i + 1, gtk.FILL, 0, 20)
        #endfor

        self.show_all()
    #enddef
#endclass


class MainWindow:
    accelGroup = None
    diceButtons = None
    notebook = None
    rollButton = None
    statusBar = None
    window = None

    def doGameNew(self, action):
        yamsData.playerNames = loadConfigFile()
        yamsData.numPlayers = len(yamsData.playerNames)
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
        yamsData.turn = 0
        yamsData.gameOver = False
        self.advancePlayer()
    #enddef

    def doSettingsPreferences(self, action):
        pw = PreferencesWindow(self.window)
        response = pw.run()

        if response == gtk.RESPONSE_ACCEPT:
            saveConfigFile(pw.getPlayerNames())
        #endif

        pw.destroy()
    #enddef

    def doHelpContents(self, action):
        gnome.help_display('yams.xml', None)
    #enddef

    def doHelpAbout(self, action):
        ad = gtk.AboutDialog()

        ad.set_name('Yams')
        ad.set_version(VERSION)
        ad.set_copyright('Copyright 2008 Cătălin Frâncu')
        ad.set_comments('This game is dedicated to my father, '
                        'who taught me the game.')
        ad.set_license(
            'Yams is free software: you can redistribute it and/or modify '
            'it under the terms of the GNU General Public License as '
            'published by the Free Software Foundation, either version 3 of '
            'the License, or (at your option) any later version.\n\n'

            'Yams is distributed in the hope that it will be useful, '
            'but WITHOUT ANY WARRANTY; without even the implied warranty of '
            'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the '
            'GNU General Public License for more details.\n\n'

            'You should have received a copy of the GNU General Public '
            'License along with Yams.  If not, see '
            '<http://www.gnu.org/licenses/>.')
        ad.set_wrap_license(True)
        ad.set_website('http://catalin.francu.com')
        ad.run()
        ad.destroy()
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

    def onDieToggle(self, button):
        if yamsData.gameOver:
            button.set_active(False)
        elif yamsData.rolled == 0:
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

        if yamsData.gameOver:
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
            message = MSG_ANNOUNCE % ROW_PROPS[row][0]
            self.setStatusBarMessage(message, False)
            self.alert(message)
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
        if value > 0:
            model.set(model.get_iter(row), column, value)
        else:
            model.set(model.get_iter(row), column, u'\u2015')
        #endif

        ssCol = yamsData.scoreSheets[yamsData.currentPlayer].columns[ssColumn]
        model.set(model.get_iter(ROW_T1), column, ssCol.getT1())
        model.set(model.get_iter(ROW_T2), column, ssCol.getT2())
        model.set(model.get_iter(ROW_T3), column, ssCol.getT3())
        model.set(model.get_iter(ROW_TOTAL), column, ssCol.getTotal())        
        self.advancePlayer()
    #enddef

    def onNotebookSwitchPage(self, notebook, page, page_num):
        score = yamsData.scoreSheets[page_num].getTotal()
        self.grandTotalLabel.set_text(str(score))
    #enddef

    def onKeyPress(self, widget, event):
        key = event.keyval - ord('1')
        if key in range(5):
            die = self.diceButtons[key]
            die.set_active(not die.get_active())
            return True
        #endif
        return False
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
             ('Settings', None, '_Settings'),
             ('Preferences', gtk.STOCK_PREFERENCES, '_Preferences', '<Ctrl>P',
              None, self.doSettingsPreferences),
             ('Help', None, '_Help'),
             ('Contents', gtk.STOCK_HELP, '_Contents', 'F1', None,
              self.doHelpContents),
             ('About', gtk.STOCK_ABOUT, '_About', None, None, self.doHelpAbout),
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
            button.connect('toggled', self.onDieToggle)
            self.diceButtons += [button]
            toolbar.insert(button, i)
            self.setDiceImage(i, 0)
        #endfor

        self.rollButton = gtk.Button('')
        self.rollButton.add_accelerator('clicked', self.accelGroup, ord('R'),
                                        0, gtk.ACCEL_VISIBLE)
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
            self.rollButton.set_label('_Roll 3/3')
            self.rollButton.set_sensitive(False)
        else:
            self.rollButton.set_label('_Roll %d/3' % count)
            self.rollButton.set_sensitive(True)
        #endif
    #enddef

    def setStatusBarMessage(self, msg, bell = True):
        contextId = self.statusBar.get_context_id('unique')
        # Never stack messages up
        self.statusBar.pop(contextId)
        self.statusBar.push(contextId, msg)
        if bell:
            try:
                self.statusBar.error_bell()
            except AttributeError:
                pass
            #endtry
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
            yamsData.turn += 1
        #endif
        self.notebook.set_current_page(yamsData.currentPlayer)

        if yamsData.numPlayers == 1:
            # This doesn't happen automatically because the notebook page never
            # changes in single player mode.
            self.onNotebookSwitchPage(self.notebook, None, 0)
        #endif

        if yamsData.turn == MAX_TURNS:
            self.gameOver()
        else:
            name = yamsData.playerNames[yamsData.currentPlayer]
            self.setStatusBarMessage(MSG_TURN % name, False)
        #endif
    #enddef

    def gameOver(self):
        self.setStatusBarMessage(MSG_GAME_OVER)
        self.rollButton.set_sensitive(False)
        yamsData.gameOver = True

        # Show the final scores
        sw = ScoreWindow(self.window)
        sw.run()
        sw.destroy()
    #enddef

    def alert(self, message):
        dialog = gtk.Dialog("Message", self.window,
                            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK))
        label = gtk.Label(message)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.run()
        dialog.destroy()
    #enddef

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Yams')
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.connect('key_press_event', self.onKeyPress)

        vbox = gtk.VBox(False, 2)
        self.window.add(vbox)
        vbox.show()

        menuBar = self.makeMenu()
        vbox.pack_start(menuBar, False)

        hbox = gtk.HBox(False, 2)
        vbox.pack_start(hbox, False)
        hbox.show()

        self.statusBar = gtk.Statusbar()
        vbox.pack_start(self.statusBar, False)
        self.statusBar.show()

        hbox.pack_start(self.makeDiceBox(), False)

        vbox = gtk.VBox(False, 2)
        hbox.pack_start(vbox, False)
        vbox.show()

        self.notebook = gtk.Notebook()
        vbox.pack_start(self.notebook, False)
        self.notebook.show()
        self.notebook.connect('switch-page', self.onNotebookSwitchPage)

        hbox = gtk.HBox(False)
        vbox.pack_start(hbox, False)
        hbox.show()

        frame = gtk.Frame('Grand Total')
        hbox.pack_start(frame, True, False)
        frame.show()

        self.grandTotalLabel = gtk.Label("0")
        self.grandTotalLabel.set_width_chars(10)
        frame.add(self.grandTotalLabel)
        self.grandTotalLabel.modify_font(pango.FontDescription('times bold 20'))

        self.window.show_all()
    #enddef
#endclass

if __name__ == "__main__":
    appProperties = {'app-datadir': os.getcwd()}
    gnome.init('yams', '1.0', properties = appProperties)

    window = MainWindow()
    window.doGameNew(None)
    gtk.main()
#endif
