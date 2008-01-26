# Yams die manipulation and counting

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
    if dice[1] == dice[2] and dice[2] == dice[3] and \
            (dice[0] == dice[1] or dice[3] == dice[4]):
        return dice[2]
    else:
        return 0
    #endif
#enddef

# Returns 1-6 for the yams type or 0 for no yams
def dl_getYamsType(dice):
    if dice[0] == dice[1] and dice[1] == dice[2] and \
            dice[2] == dice[3] and dice[3] == dice[4]:
        return dice[0]
    else:
        return 0
    #endif
#enddef
