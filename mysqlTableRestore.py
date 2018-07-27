#!/bin/env python
# coding: utf-8
# xuzhifa
# 2018-03-29

import sys
import getopt
import os
import shutil
import datetime
import pymysql
import fileinput

pwd = os.getcwd()
binlogDir ='/mysqldata/mysql/data/'
if binlogDir in '':
    print 'binlog The environment variable Is empty!'
    exit()
time = datetime.datetime.now()
time = time.strftime('%Y%m%d%H%M%S')

table = ''
host = ''
user = ''
passwd = ''
port = '3306'
database = ''
file = ''
noRename = True
thread = 4

options,args = getopt.getopt(sys.argv[1:],"h:u:p:P:d:t:f:T:n")

for opt in options:
    if '-t' in opt:
        table = opt[1]
    elif '-h' in opt:
        host = opt[1]
    elif '-u' in opt:
        user = opt[1]
    elif '-P' in opt:
        port = opt[1]
    elif '-d' in opt:
        database = opt[1]
    elif '-f' in opt:
        file = opt[1]
    elif '-p' in opt:
        passwd = opt[1]
    elif '-n' in opt:
        noRename = False
    elif '-T' in opt:
        thread = opt[1]

if user in '':
    print 'User names are not available without values.'
    exit()

try:
    conn = pymysql.connect(host=host, port=int(port), user=user, passwd=passwd, db=database, charset='utf8')
    conn.close()
except pymysql.err.OperationalError:
    print 'The connection to the database failed, please check if the parameters are correct.'
    exit()
except pymysql.err.InternalError:
    print 'This database does not exist.'
    exit()
    



judge = os.path.exists(file)
if judge == True:
    file = file.rstrip('/')
    newFile = file + '/' + database + '-' + table + '-' + time + '/'
    os.mkdir(newFile)
else:
    print "File does not exist"
    exit()

schemaBackup = file + '/' + database + '.' + table +  '-schema.sql.gz'
dataBackup = file + '/' + database + '.' + table +  '.sql.gz'
if not os.path.exists(schemaBackup):
    shutil.copy(file + '/metadata', newFile)
else:
    shutil.move(schemaBackup,newFile)
    shutil.move(dataBackup,newFile)
    shutil.copy(file + '/metadata', newFile)

#print 'user' + user
#print 'passwd' + passwd
#print 'host' + host
#print 'port' + port
#print 'database' + database
#print newFile
#print 'file' + file

#print ''' %s/mydumper-0.9.3/myloader -u %s -p %s -h %s -P %s -B %s -t %s -d %s  ''' %(pwd,user,passwd,host,port,database,thread,file)

    os.popen(''' %s/mydumper-0.9.3/myloader -u %s -p %s -h %s -P %s -B %s -t %s -d %s  ''' %(pwd,user,passwd,host,port,database,thread,newFile))


metadatFile = open(file + '/metadata','r')
startList = metadatFile.read()
startFile = startList.split('\t')[1].replace("\n",'').split(' ')[1]
startPos = startList.split('\t')[2].replace("\n",'').split(' ')[1]

for line in fileinput.input('{}/config.py'.format(pwd),inplace=1):
    if line.find('binlogFile') != -1:
        print "binlogFile = '{}".format(binlogDir) + startFile + "'".rstrip()
    elif line.find('schemaName') != -1:
        print "schemaName = '" + database + "'".rstrip()
    elif line.find('tableName') != -1:
        print "tableName = '" + table + "'".rstrip()
    elif line.find('startPos') != -1:
        print "startPos = '" + startPos + "'".rstrip()
    elif line.find('host') != -1:
        print "      'host':'" + host + "',".rstrip()
    elif line.find("'port'") != -1:
        print "      'port':" + port + ",".rstrip()
    elif line.find("'user'") != -1:
        print "      'user':'" + user + "',".rstrip()
    elif line.find('password') != -1:
        print "      'password':'" + passwd + "',".rstrip()
    else:
        print line.rstrip()


os.chdir(pwd)

while True:
    if os.path.exists('{}/config.pyc'.format(pwd)):
        os.remove('{}/config.pyc'.format(pwd))
    sql = os.system(''' python BinlogAnalyzer.py file''')

#    if sql == 39424 or sql == 0:
#        conn = pymysql.connect(host=host, port=int(port), user=user, passwd=passwd, db=database, charset='utf8')
#        cursor = conn.cursor()
#        sqlData = open("./result/redo.sql",'r')
#        for code in sqlData:
#            cursor.execute(code)connect
#        conn.commit()
#        cursor.close()
#        conn.close()
    if sql == 0:
        startFile = startFile.replace('.' + startFile.split(".")[1], '.' + str(int(startFile.split(".")[1]) + 1).zfill(6))
        startPos = ''
        if os.path.exists('{}'.format(binlogDir) + startFile):
            for line in fileinput.input('{}/config.py'.format(pwd),inplace=1):
                if line.find('binlogFile') != -1:
                    print "binlogFile = '{}".format(binlogDir) + startFile + "'".rstrip()
                elif line.find('startPos') != -1:
                    print "startPos = '" + startPos + "'".rstrip()
                else:
                    print line.rstrip()
        else:
            break
    if sql == 39424:
        break
    if sql != 0 and sql != 39424:
        break

if noRename == True:
    pass
else:
    try:
        conn = pymysql.connect(host=host, port=int(port), user=user, passwd=passwd, db=database, charset='utf8')
        cursor = conn.cursor()
        sqlData = 'alter table ' + table + '_Bu rename ' + table
        cursor.execute(sqlData)
    except pymysql.err.InternalError:
        print "The table name repetition , It can't be this {}.".format(table)

if not os.path.exists(newFile + database + '.' + table +  '-schema.sql.gz'):
    if os.path.exists(newFile):
        shutil.rmtree(newFile)
else:
    shutil.move(newFile + database + '.' + table +  '-schema.sql.gz',file + '/')
    if not os.path.exists(newFile + database + '.' + table +  '.sql.gz'):
        shutil.rmtree(newFile)
    else:
        shutil.move(newFile + database + '.' + table +  '.sql.gz',file + '/')
        shutil.rmtree(newFile)


