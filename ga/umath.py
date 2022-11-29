
#    __  __       _   _             _   _ _ _ _   _           
#   |  \/  | __ _| |_| |__    _   _| |_(_) (_) |_(_) ___  ___ 
#   | |\/| |/ _` | __| '_ \  | | | | __| | | | __| |/ _ \/ __|
#   | |  | | (_| | |_| | | | | |_| | |_| | | | |_| |  __/\__ \
#   |_|  |_|\__,_|\__|_| |_|  \__,_|\__|_|_|_|\__|_|\___||___/
#                                                             

def clamp(minimum, value, maximum):
    '''Returns the bounded value between the given minimum and maximum. The bounds are inclusive.'''
    return max(minimum, min(value, maximum))


