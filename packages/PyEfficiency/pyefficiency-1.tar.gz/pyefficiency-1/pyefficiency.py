# PyEfficiency: omg silly functions like binary searches and algorithmic functions!! :D
# NOTE the commenting/variables are admittedly a bit all over the place so use no-annotation if it's too distracting

def flute(num, place): # an ACTUAL working function that correctly rounds floats
    # checker thing to make sure we dont have to do so much work =w=
    checked = str() # converted to string
    if type(num) == float: # is a float (but is it really?)
        while True:
            if checked[-1] == 0:
                checked = checked[:-1] # zero detected!
            if checked[-1] == ".":
                checked = checked[:-1]
                checked = int(checked) # hello integer
                verified = int(checked)
            else: # you passed the float test :3
                verified = float(checked)
    elif isinstance(num, int): # already an integer?!?!?!
        verified = int(num)
    if isinstance(verified, int):
        return verified # simple silly integer
    if place == 0:
        return int(verified)        
    verified = str(verified).split(".")  # HECK YEA SPLIT THAT CLIP!! more difficult to edit decimal when it stays attached to int
    clipped = verified[0]  # the whole integer form of the original number
    following = list(verified[1])  # the rest of the number that comes after the decimal
    quirk = place - 1 # minus one because we will use it for zero-based indexing
    if place > len(following): # four or less, let it rest 
        return verified
    rounder = int(following[place]) if place < len(following) else 0
    if rounder >= 5:  # five or more, raise the score
        following[quirk] = str(int(following[quirk]) + 1)
    following = following[:place] # trimming everything before the place we rounded
    finalflute = float(clipped + "." + "".join(following)) # putting the number back together
    return finalflute # FLUTE DETECTED???

# this is a binary search
def binarysearch(target, list):
    low = list[0]
    high = list[-1]
    middle = (high+low)/2
    while middle != target:
        middle = (high+low)/2
        if middle > target:
            high = middle - 1
        elif middle < target:
            low = middle + 1
    print(middle)
# very easy to understand

# recursion thing for stuff like Tower Of Hanoi. this has to be one of my favorite functions in this whole project!
def solvehanoi(discamount: int, source: int, dest: int, aux: int):
    if discamount == 1:
        print ("move disk 1 from:", source, "to:", dest)
        return

    solvehanoi(discamount -1, source, aux, dest)
    print("move disc:", discamount, "from:", source, "to:", dest)
    solvehanoi(discamount -1, aux, dest, source)

# do factorials!
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n-1)