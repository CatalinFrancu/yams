# Yams global variables and data types

from yamsDieLogic import *

announced = None
currentPlayer = 0
dice = [0, 0, 0, 0, 0]
firstRollDice = None
gameOver = False
numPlayers = None
playerNames = None
rolled = 0
scoreSheets = None
turn = 0

COLUMN_NORMAL = 0
COLUMN_ANNOUNCED = 1
COLUMN_SERVED = 2

UPPER_HALF_BONUS = 30
UPPER_HALF_LIMIT = 60
LOWER_HALF_BONUS1 = 50
LOWER_HALF_LIMIT1 = 150
LOWER_HALF_BONUS2 = 100
LOWER_HALF_LIMIT2 = 300

STRAIGHT_SCORES = [0, 15, 20]
FULL_SCORES = [0, 25, 30, 35, 40, 45, 50]
FK_SCORES = [0, 75, 80, 85, 90, 95, 100]
YAMS_SCORES = [0, 150, 160, 170, 180, 190, 200]

class Column:
    cells = None
    filled = None
    type = None

    def __init__(self, type):
        self.cells = [0] * 12
        self.filled = [False] * 12
        self.type = type
    #enddef

    def getT1(self):
        if sum(self.filled[0:6]) == 0:
            return None
        #endif

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
            if self.cells[6] == 0 or self.cells[7] == 0:
                # Rare case: one of the cells was cut, e.g. in the served column
                return 0
            #endif
            return max(0, (self.cells[6] - self.cells[7]) * self.cells[0])
        else:
            return None
        #endif
    #enddef

    def getT3(self):
        if sum(self.filled[8:]) == 0:
            return None
        #endif

        s = sum(self.cells[8:])
        if self.type == COLUMN_ANNOUNCED:
            return s  # No T3 bonuses on the announced column
        #endif

        if s >= LOWER_HALF_LIMIT2:
            bonus = LOWER_HALF_BONUS2
        elif s >= LOWER_HALF_LIMIT1:
            bonus = LOWER_HALF_BONUS1
        else:
            bonus = 0
        #endif

        if self.type == COLUMN_SERVED:
            bonus *= 2
        #endif

        return s + bonus
    #enddef

    def getTotal(self):
        t1 = self.getT1()
        t2 = self.getT2()
        t3 = self.getT3()
        if t1 == None and t2 == None and t3 == None:
            return None
        else:
            return (t1 if t1 else 0) + (t2 if t2 else 0) + (t3 if t3 else 0)
        #endif
    #enddef

    def setCombo(self, pos, dice):
        # TODO: HANDLE THE ANNOUNCED COLUMN!
        self.filled[pos] = True;

        if (self.type == COLUMN_SERVED and rolled > 1) or \
           (self.type == COLUMN_ANNOUNCED and rolled > 1 and announced == None):
            # Equivalent to a cut.
            self.cells[pos] = 0
            return
        #endif

        # Set the field's value according to the dice combo
        if pos < 6:
            origCount = firstRollDice.count(pos + 1)
            count = dice.count(pos + 1)
            digitSum = count * (pos + 1)
            if pos == 0 and self.type == COLUMN_SERVED:
                # Double points for served aces
                self.cells[pos] = 2 * digitSum
            elif self.type == COLUMN_ANNOUNCED:
                self.cells[pos] = digitSum * (2 if count > origCount else 1)
            else:
                self.cells[pos] = digitSum
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

        # Announced figures are doubled unless they are served.
        if pos >= 8 and self.type == COLUMN_ANNOUNCED and rolled > 1:
            self.cells[pos] *= 2
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
        self.columns.append(Column(COLUMN_ANNOUNCED))
        self.columns.append(Column(COLUMN_SERVED))
    #enddef

    def getTotal(self):
        total = 0
        for c in self.columns:
            colTotal = c.getTotal()
            if colTotal != None:
                total += colTotal
            #endif
        #endfor
        return total
    #enddef
#endclass

def writeScore(row, column):
    ssCol = scoreSheets[currentPlayer].columns[column]
    ssCol.setCombo(row, dice)
    return ssCol.cells[row]
#enddef

def isFilled(row, column):
    return scoreSheets[currentPlayer].columns[column].filled[row]
#enddef

def canBeFilled(row, column):
    if column == 0:
        ssCol = scoreSheets[currentPlayer].columns[0]
        return row == 0 or ssCol.filled[row - 1]
    elif column == 1:
        ssCol = scoreSheets[currentPlayer].columns[0]
        return ssCol.filled[row]
    elif column == 2:
        ssCol = scoreSheets[currentPlayer].columns[3]
        return ssCol.filled[row]
    elif column == 3:
        ssCol = scoreSheets[currentPlayer].columns[3]
        return row == 11 or ssCol.filled[row + 1]
    else:
        return True
    #endif
#enddef
