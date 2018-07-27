import os
import fileinput

envVar = os.environ.get( "MYSQL_DATA_DIR" )
envVar =  str(envVar).rstrip('/') + '/'
if envVar in 'None':
    print 'MYSQL_DATA_DIR is null'
    exit()
for line in fileinput.input('./testRestore.py',inplace=1):
    if line.find('binlogDir =') != -1:
        print "binlogDir ='{}'".format(envVar)
    else:
        print line.rstrip()
 
