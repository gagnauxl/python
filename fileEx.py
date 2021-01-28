#!/usr/bin/python
print ("File IO")
# Open a file
fo = open("foo.txt", "r+")
s = fo.read(10)
print ("Read String is : "+ s)

# Check current position
position = fo.tell()
print ("Current file position : " + str(position))

# Reposition pointer at the beginning once again
position = fo.seek(0, 0);
str = fo.read(10)
print ("Again read String is : " + str)
# Close opend file
fo.close()