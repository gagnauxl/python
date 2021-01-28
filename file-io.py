#!/usr/bin/python
import re

# input = {{line} + dateTime + pcfillcountS2 + {line}}
# dateTimeLine = "Date/Time" + whitepaces + dateTime
# pcfillcountS2 = "PC_FILLCOUNT_S2" + line + counterLine
# counterline = {char} + decrement + {char} + level
# decrement = {digit}
# level =  {digit}

#function definitions

#prints to file
def printf(line, end="\n"):
    with open("inc.csv", "a") as fo: fo.write(line+end) 
    print(line, end=end) 
    return

#skips preceding lines
def getLine():
    line = fh.readline()
    match = None
    while match==None:
        match = re.match("PC_FILLCOUNT_S2", line)
        dateMatch=re.match("Date/Time\s+", line)
        if dateMatch!=None:
            dateTimeLine=re.split(r'\n', line)
            global dateTime
            dateTime =  dateTimeLine[0]
        line = fh.readline()
    return line

#scans the "PC_FILLCOUNT_S2" block and prints increment on one line csv delimited
def pcFillCountS2(line):
    printf(dateTime, end=SEPARATOR)
    for i in range(1,10):
        line=fh.readline()
        lineItems=re.split(r'\W+', line)
        if i<9: 
            printf(lineItems[2], end=SEPARATOR)
        else: 
            printf(lineItems[2])
    return

#global vars
SEPARATOR=','
dateTime = "unset"


#main: parses input
print ("Starting ..")
print ("Opening file: input.dat")
with open("inc.csv", "w") as fo: fo.write("") #overwrite existing file
fh = open("input.dat", "r")
#fh = open("./Documents/repos/python/input.dat", "r")

#test
with open("foo.txt", "w") as ft: ft.write( "Python is a great language.\nYeah its great!!\n")
with open("foo.txt", "a") as ft: ft.write( "Second!\n")

line = getLine()
while line:
    pcFillCountS2(line)
    line = getLine()

fh.close()
fo.close()
ft.close()