import os
import fileinput

envVar = os.environ.get( "MYSQL_BINLOG_DIR" )
envVar =  str(envVar).rstrip('/') + '/'
if envVar in 'None':
    print 'MYSQL_BINLOG_DIR is null'
    exit()
for line in fileinput.input('./mysqlTableRestore.py',inplace=1):
    if line.find('binlogDir =') != -1:
        print "binlogDir ='{}'".format(envVar)
    else:
        print line.rstrip()
 
