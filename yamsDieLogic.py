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

# Returns 1 for a low straight, 2 for a high straight, or 0 for no straight
def dl_getStraightType(dice):
    dice.sort()
    if dice == [2, 3, 4, 5, 6]:
        return 2
    elif dice == [1, 2, 3, 4, 5]:
        return 1
    else:
        return 0
    #endif
#enddef

# Returns 1-6 for the full house type or 0 for no full house
def dl_getFullType(dice):
    dice.sort()
    # Full houses look like A A B B B or A A A B B.
    # The die in the middle dictates the full house type
    if dice[0] == dice[1] and dice[3] == dice[4] and \
            (dice[2] == dice[1] or dice[2] == dice[3]):
        return dice[2]
    else:
        return 0
    #endif
#enddef

# Returns 1-6 for the 4K type or 0 for no 4K
def dl_get4KType(dice):
    dice.sort()
    # Four of a kinds look like A A A A B or A B B B B.
    # The die in the middle dictates the 4K type
    if (dice[1] == dice[3]) and (dice[0] == dice[1] or dice[3] == dice[4]):
        return dice[2]
    else:
        return 0
    #endif
#enddef

# Returns 1-6 for the yams type or 0 for no yams
def dl_getYamsType(dice):
    dice.sort()
    if dice[0] == dice[4]:
        return dice[0]
    else:
        return 0
    #endif
#enddef
