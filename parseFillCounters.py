#!/usr/bin/python
import re
from re import match
import os
import os.path

# input = {{line} + dateTime + pcfillcountS2 + {line}}

# input = {command}
# command = {line} + dateTime + [pcfillcountS2 | pcfillcountS3 | pcobtmeas]
# dateTimeLine = "Date/Time" + whitepaces + dateTime
# pcfillcountS2 = "PC_FILLCOUNT_S2" + line + counterLine
# pcfillcountS3 = "PC_FILLCOUNT_S3" + line + counterLine
# pcobtmeas = "PC_OBT_MEAS_R2" + line + counterLine
# counterline = {char} + decrement + {char} + level
# decrement = {digit}
# level =  {digit}
class Parser:
    SEPARATOR=','
    def __init__ (self, filepath):
        print ("Opening file: " + filepath)
        self.filepath = filepath
        self.fh = open(filepath, "r") #overwrite existing file
        filename, file_extension = os.path.splitext(filepath)
        self.outputFilename = filename + ".csv-input"
        self.fo = open(self.outputFilename, "w")
        self.printf("Date/Time,PC_FILLCOUNT_S2,FC_LFB,FC_LFC,FC_NA_COND,FC_O2_ZERO,FC_CLEAN,FC_KCL_BG,FC_KCL_ISE,FC_RINSE,FC_WASTE or")
        self.printf("Date/Time,PC_FILLCOUNT_S3,FC_D,FC_C1,FC_C2,FC_C3,FC_C4,FC_KCL_MSS,FC_RINSE,FC_WASTE")
        self.firstDateTime = "unset"
        self.dateTime = "unset"
        self.commandLine = "unset"
        self.S2FillCounts = []
        self.S3FillCounts = []
        self.S1 = "unset"
        self.S0 = "unset"
    
    def __del__(self):
        print ("Closing files ..")
        self.fo.close()
        self.fh.close()

    def printf(self, line, end="\n"):
        'prints to file and stdout'
        with open(self.outputFilename, "a") as fo: fo.write(line+end)  # to do
        print(line, end=end) 
        return

    def command(self):
        'skips preceding lines until PC_FILLCOUNT_S2 or PC_FILLCOUNT_S3 or PC_OBT_MEAS_R2 is found'
        'remembers last date time before in self.dateTime'
        line = self.fh.readline()
        match = None
        while (match==None and line!=''):
            match = re.match(r'(PC_FILLCOUNT_S2|PC_FILLCOUNT_S3|PC_OBT_MEAS_R2)', line)
            dateMatch=re.match("Date/Time\s+", line)
            if dateMatch!=None: 
                dateTimeLine=re.split(r'\n', line)
                dateTimeTimeOnly = re.split(r'Date/Time ', dateTimeLine[0])
                self.dateTime =  dateTimeTimeOnly[1]
            if match!=None:
                self.commandLine = line
            line = self.fh.readline()
        return line
    
    def pcFillCountS2(self, line):
        'scans the "PC_FILLCOUNT_S2" block and prints counters on one line csv delimited'
        self.printf(self.dateTime, end=Parser.SEPARATOR)
        self.printf("PC_FILLCOUNT_S2", end=Parser.SEPARATOR)
        for i in range(9):
            line=self.fh.readline()   #skip header
            lineItems=re.split('\s+', line)
            if i<8: 
                self.printf(lineItems[3], end=Parser.SEPARATOR)  #FC_COUNTER
            else: 
                self.printf(lineItems[3])
        return
    
    def pcFillCountS3(self, line):
        'scans the "PC_FILLCOUNT_S3" block and prints counters on one line csv delimited'
        self.printf(self.dateTime, end=Parser.SEPARATOR)
        self.printf("PC_FILLCOUNT_S3", end=Parser.SEPARATOR)
        for i in range(8):
            line=self.fh.readline()    #skip header
            lineItems=re.split('\s+', line)
            if i<7: 
                self.printf(lineItems[3], end=Parser.SEPARATOR)  #FC_COUNTER
            else: 
                self.printf(lineItems[3])
        return

    def pcobtmeas(self, line):
        'scans the "PC_OBT_MEAS_R2" block and prints new mean consumption counters on one line csv delimited'
        self.printf(self.dateTime, end=Parser.SEPARATOR)
        self.printf("PC_OBT_MEAS_R2", end=Parser.SEPARATOR)
        for i in range(1,5):
            line=self.fh.readline()
            lineItems=re.split('\s+', line)
            if i<4: 
                self.printf(lineItems[3], end=Parser.SEPARATOR)  #New mean
            else: 
                self.printf(lineItems[3])
        return

    def getFillCounts(self):
        line = self.fh.readline()
        match2 = None
        match3 = None
        while ((match2==None or match3==None) and line!=''):
            dateMatch=re.match("Date/Time\s+", line)
            if dateMatch!=None: 
                dateTimeLine=re.split(r'\n', line)
                dateTimeTimeOnly = re.split(r'Date/Time ', dateTimeLine[0])
                if self.firstDateTime == "unset":
                    self.firstDateTime = dateTimeTimeOnly[1]
            if match2==None:    #only first one
                match2 = re.match('PC_FILLCOUNT_S2', line)
                if match2!=None:
                    line=self.fh.readline()  #skip header
                    line=self.fh.readline()  #get first line
                    for i in range(9):
                        lineItems=re.split('\s+', line)
                        if i<7:
                            self.S2FillCounts.append (int(lineItems[3])+int(lineItems[2]))
                        else:
                            if i<8:
                                if self.S1=="unset":
                                    self.S1=str(int(lineItems[3])+int(lineItems[2]))  # S1
                            else:
                                if self.S0=="unset":
                                    self.S0=str(int(lineItems[3])-int(lineItems[2]))  # waste
                        line=self.fh.readline()
            if match3==None:    #only first one
                match3 = re.match('PC_FILLCOUNT_S3', line)
                if match3!=None:
                    line=self.fh.readline()  #skip header
                    line=self.fh.readline()  #get first line
                    for i in range(8):
                        lineItems=re.split('\s+', line)
                        if i<6:
                            self.S3FillCounts.append (int(lineItems[3])+int(lineItems[2]))
                        else:
                            if i<7:
                                if self.S1=="unset":
                                    self.S1=str(int(lineItems[3])+int(lineItems[2]))  # S1
                            else:
                                if self.S0=="unset":
                                    self.S0=str(int(lineItems[3])-int(lineItems[2]))  # waste
                        line=self.fh.readline()
            line = self.fh.readline()
        return 
    
    def prepare(self):  #print the first 3 lines       
        self.getFillCounts()
        self.printf(self.firstDateTime + ",INIT", end=Parser.SEPARATOR)
        self.printf(self.S0, end=Parser.SEPARATOR)
        self.printf(self.S1, end=Parser.SEPARATOR)
        for x in self.S2FillCounts:
            self.printf(str(x), end=Parser.SEPARATOR)
        for x in self.S3FillCounts:
            self.printf(str(x), end=Parser.SEPARATOR)
        self.printf('')
        # print("S0 Counts")
        # print(self.S0)
        # print("S1 Counts")
        # print(self.S1)      
        # print("S2 Counts")
        # for x in self.S2FillCounts:
        #     print(x)
        # print("S3 Counts")
        # for x in self.S3FillCounts:
        #     print(x)
        self.fh.seek(0, 0)
        return

    def start(self):
        self.prepare()
        line = self.command()
        while (line):
            if re.match("PC_FILLCOUNT_S2", self.commandLine)!=None:
                self.pcFillCountS2(line)
            if re.match("PC_FILLCOUNT_S3", self.commandLine)!=None:
                self.pcFillCountS3(line)
            if re.match("PC_OBT_MEAS_R2", self.commandLine)!=None:
                self.pcobtmeas(line)

            line = self.command()

#main: parses input
print ("Starting ..")

#test
with open("foo.txt", "w") as ft: ft.write( "Python is a great language.\nYeah its great!!\n")
with open("foo.txt", "a") as ft: ft.write( "Second!\n")

data_folder = os.path.join("")

# file_to_open = os.path.join(data_folder, "input.dat")
# p=Parser(file_to_open)
# p.start()

# file_to_open = os.path.join(data_folder, "iu_190923_sn_19375.dat")
# p=Parser(file_to_open)
# p.start()

file_to_open = os.path.join(data_folder, "iu_191212_sn_9524.dat")
p=Parser(file_to_open)
p.start()

print ("End!")

