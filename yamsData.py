# Yams global variables and data types

from yamsDieLogic import *

numPlayers = 1
scoreSheets = None

COLUMN_NORMAL = 0
COLUMN_CALLED = 1
COLUMN_SERVED = 2

UPPER_HALF_BONUS = 30
UPPER_HALF_LIMIT = 60

STRAIGHT_SCORES = [0, 15, 20]
FULL_SCORES = [0, 25, 30, 35, 40, 45, 50]
FK_SCORES = [0, 75, 80, 85, 90, 95, 100]
YAMS_SCORES = [0, 150, 160, 170, 180, 190, 200]

class Column:
    cells = None
    filled = None
    type = None

    def __init__(self, type):
        #self.cells = [0] * 12
        self.cells = [3, 6, 9, 12, 15, 17, 9, 10, 0, 15, 1, 3]
        self.filled = [False] * 12
        self.type = type
    #enddef

    def getT1(self):
        t1 = sum(self.cells[0:6])
        if t1 >= UPPER_HALF_LIMIT:
            if self.type == COLUMN_NORMAL:
                t1 += UPPER_HALF_BONUS
            elif self.type == COLUMN_SERVED:
                t1 += 2 * UPPER_HALF_BONUS
            #endif
        return t1
    #enddef

    def getT2(self):
        if self.filled[0] and self.filled[6] and self.filled[7]:
            return max(0, (self.cells[6] - self.cells[7]) * self.cells[0])
        else:
            return 0
        #endif
    #enddef

    def getT3(self):
        s = sum(self.cells[8:])
        if self.type == COLUMN_CALLED:
            return s  # No T3 bonuses on the called column
        #endif

        if s >= 300:
            bonus = 100
        elif s >= 150:
            bonus = 50
        else:
            bonus = 0
        #endif

        if self.type == COLUMN_SERVED:
            bonus *= 2
        #endif

        return s + bonus
    #enddef

    def getTotal(self):
        return self.getT1() + self.getT2() + self.getT3()
    #enddef

    def setCombo(self, pos, dice):
        # TODO: HANDLE THE ANNOUNCED COLUMN!
        self.filled[pos] = True;

        # Set the field's value according to the dice combo
        if pos <= 5:
            sum = dice.count(pos + 1) * (pos + 1)
            if pos == 0 and self.type == COLUMN_SERVED:
                # Double points for served aces
                self.cells[pos] = 2 * sum
            else:
                self.cells[pos] = sum
        elif pos <= 7:
            self.cells[pos] = sum(dice)
        elif pos == 8:
            self.cells[pos] = STRAIGHT_SCORES[dl_getStraightType(dice)]
        elif pos == 9:
            self.cells[pos] = FULL_SCORES[dl_getFullType(dice)]
        elif pos == 10:
            self.cells[pos] = FK_SCORES[dl_get4KType(dice)]
        elif pos == 11:
            self.cells[pos] = YAMS_SCORES[dl_getYamsType(dice)]
        #endif
    #enddef
#endclass

class ScoreSheet:
    columns = None

    def __init__(self):
        self.columns = []
        for i in range(4):
            self.columns.append(Column(COLUMN_NORMAL))
        #endfor
        self.columns.append(Column(COLUMN_CALLED))
        self.columns.append(Column(COLUMN_SERVED))
        self.columns[0].setCombo(11, [4, 4, 4, 4, 4])
        print self.columns[0].cells
    #enddef
#endclass
