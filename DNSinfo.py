#!/usr/bin/env python

import os.path
import sys
import csv
import re
import string
import socket

class App:
    def __init__(self, argv):
        if len(argv) < 2:
            sys.exit('Usage: %s csvFileName' % argv[0])
        self.csvfile = argv[1]
        self.usage_name = os.path.basename(argv[0])
        self.setDefaults()

    def setDefaults(self):
        # regex for characters allowed in FQDN
        self.allowed = re.compile("[^a-zA-Z\d\-]")

        # output file name with invalid FQDNs 
        self.invNameFile = "invalid-fqdn"

        # current 11 header fields in Google doc
        # update this entry when there are changes  in number of columns.
        self.header=["Allocation","IP/Mask","VLAN","Description","Subnet","CIDR","","","","","DNS"]

        # few first lines in csv file are empty or a title, or a header line 
        self.SKIP = 5

    def readCsvFile(self):
        if not os.path.isfile(self.csvfile):
            sys.exit('ERROR: %s is not a file' % self.csvfile)
        name,ext = os.path.splitext(self.csvfile)
        if ext == '.csv':
            delimiter = ','
        elif ext == '.txt':
            delimiter = '\t'
        else:
            sys.exit('ERROR: %s must be .csv or .txt Excel format' % self.csvfile)

        self.csvReader = csv.reader(open(self.csvfile, 'rU'), delimiter=delimiter, quotechar='"')
    
    
    def isValid(self, row):
        # check FQDN
        checkFQDN = self.isValidHostname(row[0])
        # check IP
        checkIP = self.isValidIP(row[1])
        
        return checkFQDN and checkIP


    def isValidHostname(self, hostname):
        havedot = string.find(hostname, ".")
        return all(x and not self.allowed.search(x) for x in hostname.split(".")) and havedot > 0


    def isValidIP(self, ip):
        try:
            socket.inet_aton(ip)
            result = True
        except socket.error:
            result = False
        return result


    def writeInvalid(self):
        f = open(self.invNameFile, 'w')
        for line in self.invalid:
            f.write ("%s\n" % line)
        f.close()


    def checkEntries(self):
        lines = list(self.csvReader)
        pos = None
        for i in range(self.SKIP):
            if lines[i] == self.header:
                pos = i+1
                break
        if pos == None:
            print "Error in csv header, Check input file"
            sys.exit(0)
           
        self.vals = lines[pos:]

    def getHostInfo(self):
        self.invalid = []
        self.valid = []
        for row in self.vals:
            if "DNS" not in row: 
                continue
            if row[0] == "": continue
            if row[1] == "": continue
            if self.isValid(row):
                self.valid.append([row[0], row[1]])
            else: 
                self.invalid.append(row[0])
        self.writeInvalid()
    
    def writeHostInfo(self):
        for i in self.valid:
            print "%s\t%s" % (i[0], i[1])

    def run(self):
        self.readCsvFile()
        self.checkEntries()
        self.getHostInfo()
        self.writeHostInfo()


if __name__ == "__main__":
        app=App(sys.argv)
        app.run()

