#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Script Description:
#-----------------------------------------------------------------------------------------------------
# The script is used to analyze MySQL binlog and generate rollback SQL
# Author: Young Chen
# Date: 2017/7/30
#-----------------------------------------------------------------------------------------------------

import sys
import os
from os import path
import time
import logging
import commands
import re
import pymysql
from pymysql.cursors import DictCursor
import subprocess
from multiprocessing import Process
import traceback
import config as myconf
reload(sys)  
sys.setdefaultencoding('utf8') 

colorTitle = "\x1B[{};{};{}m".format(4,31,1)
colorRed = "\x1B[{};{};{}m".format(0,31,1)
colorGray = "\x1B[{};{};{}m".format(0,32,1)
colorPurple = "\x1B[{};{};{}m".format(0,35,1)

if (len(sys.argv) != 2) or (str(sys.argv[1].lower()) not in ('db','file')):
  os.system("clear")
  print '\n{}{}\n\x1B[0m'.format(colorTitle,'Welcome to Binlog Analyzer')
  print '\n{}{}\n\x1B[0m'.format(colorPurple,'Instructions:')
  print 'Step 1: Copy your binlog file to folder ./binlog/'
  print 'Step 2: Modify parameters in ./config.py'
  print ' ' * 8 + 'If you want to generate results in local files, "LocalDatabase" in config.py is not required.'
  print 'Step 3: Run Binlog Analyzer'
  print ' ' * 8 + 'Usage 1 - generate results in files   : python ./BinlogAnalyzer.py file'
  print ' ' * 8 + 'Usage 2 - generate results in database: python ./BinlogAnalyzer.py db \n'
  print '\n{}{}\n\x1B[0m'.format(colorPurple,'Requirements:')
  print 'System  : Linux'
  print 'Python  : Python 2.7'
  print 'Database: MySQL 5.1 - 5.7\n\n'
  exit(0)

RunMode     = str(sys.argv[1])  
Basename      = os.path.basename(sys.argv[0]).split('.')[0]
v_time_now    = time.strftime("%Y%m%d_%H%M%S")
#scripts_path  = "/opt/ops/ops-db/scripts"
logs_path     = './logs/'
LogFile       = logs_path + Basename + ".log." + v_time_now
tmpBinlogDML  = "./logs/Tmp_Binlog_DML.log"
tmpBinlogUNDO = "./logs/Tmp_Binlog_UNDO.log"
FileDMLSQL    = "./result/redo.sql"
#FileUndoSQL   = "./result/undo.sql"

if os.path.exists(tmpBinlogDML):
  os.remove(tmpBinlogDML)
#if os.path.exists(tmpBinlogUNDO):
#  os.remove(tmpBinlogUNDO)

if RunMode =='db':
  try:
    StoreSQLConn  = pymysql.connect(**myconf.LocalDatabase)
    curStore      = StoreSQLConn.cursor(cursor=DictCursor)
  except Exception,e:
    print 'Parameter "LocalDatabase" in config.py incorrect!'
    print e
    logPrint.error('{}'.format(traceback.print_exc()))
    exit(9)

try:
  BinlogSrcConn = pymysql.connect(**myconf.BinlogSource)
  curSourceIns  = BinlogSrcConn.cursor(cursor=DictCursor)
except Exception,e:
  print 'Parameter "BinlogSource" in config.py incorrect!'
  print e
  logPrint.error('{}'.format(traceback.print_exc()))
  exit(9)

binlogFile = myconf.binlogFile.replace(' ', '').replace('\n','')
schemaName = myconf.schemaName.replace(' ', '').replace('\n','')
tableName  = myconf.tableName.replace(' ', '').replace('\n','')
startTime  = myconf.startTime.strip().replace('\n','')
endTime    = myconf.endTime.strip().replace('\n','')
startPos   = myconf.startPos.replace(' ', '').replace('\n','')
endPos     = myconf.endPos.replace(' ', '').replace('\n','')

startTimeStr = " "
endTimeStr   = " "
startPosStr  = " "
endPosStr    = " "
schemaStr    = " "
tableStr     = " "

if startTime != '':
  startTimeStr = " --start-datetime='{}' ".format(startTime)
if endTime != '':
  endTimeStr = " --stop-datetime='{}' ".format(endTime)
if startPos != '':
  startPosStr = " --start-position={} ".format(startPos)
if endPos != '':
  endPosStr = " --stop-position={} ".format(endPos)
if schemaName != '':
  schemaStr = " -d {} ".format(schemaName)

os.system("clear")
print '\n{}{}\n\x1B[0m'.format(colorTitle,'Welcome to Binlog Analyzer')
print '\nYou are running on {}{}\x1B[0m mode\n'.format(colorPurple,RunMode)



fileHandleDML = open(FileDMLSQL, 'w+')
#fileHandleUNDO = open(FileUndoSQL, 'w+')

class Logger:
    """
    Desc:
          Standard log print function with both screen print and log file print. 
    """
    def __init__(self, logfile, clevel, Flevel):
        self.logger = logging.getLogger(logfile)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

        #Console print
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)

        #Log file print
        fh = logging.FileHandler(logfile)
        fh.setFormatter(fmt)
        fh.setLevel(Flevel)
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    def debug(self,message):
        self.logger.debug(message)
    def info(self,message):
        self.logger.info(message)
    def war(self,message):
        self.logger.warn(message)
    def error(self,message):
        self.logger.error(message)

def usage():
  os.system("clear")
  print '\n{}{}\n\x1B[0m'.format(colorTitle,'Welcome to Binlog Analyzer')
  print '\n{}{}\n\x1B[0m'.format(colorPurple,'Usage:')
  print 'Step 1: Copy your binlog file to folder ./binlog/'
  print 'Step 2: Modify parameters in ./config.py'
  print ' ' * 8 + 'If you want to generate results in local files, "LocalDatabase" in config.py is not required.'
  print 'Step 3: Run Binlog Analyzer'
  print ' ' * 8 + 'Usage 1 - generate results in files   : python ./BinlogAnalyzer.py file'
  print ' ' * 8 + 'Usage 2 - generate results in database: python ./BinlogAnalyzer.py db \n\n'
  exit(0)

def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def works_multi_process(func, worknum):
    proc_record = []
    for i in range(worknum):
        p = Process(target = func, args = (i,))
        p.start()
        proc_record.append(p)
    for p in proc_record:
        p.join()

def getInfo(line):
  """
  Desc: Get information for every transaction as below:
        @ startTime
        @ dbNane
        @ tbName
        @ listField
        @ endLogPos
        @ DMLType
  """

  """
      indexTable = line.index('Table_map')
      db_name = line[indexTable::].split(' ')[1].replace('`', '').split('.')[0]
      tb_name = line[indexTable::].split(' ')[1].replace('`', '').split('.')[1]
      TabInfo = [db_name,tb_name]

      sql_desc = 'desc {}.{}'.format(schemaName,tableName)
      cur.execute(sql_desc)
      columnInfo = cur.fetchall()
      cur.close()
      i = 0
      for columnDic in columnInfo:
        listField.append('`' + columnDic['Field'] + '`')
      return TabInfo,listField
  """
  try:
    switcher = {'Write_rows:':'INSERT', 'Update_rows:':'UPDATE', 'Delete_rows:':'DELETE'}
    strTrxInfo = ''
    indexPos = line.index('end_log_pos')
    indexType = line.index('table id')
    indexTime = line.index('server')
    startTime = line[:indexTime:].rstrip(' ').replace('#', '20')
    startTime = startTime[0:4] + '-' + startTime[4:6] + '-' + startTime[6:]
    endLogPos = line[indexPos::].split(' ')[1]
    DMLType = line[:indexType].strip().split(' ')[-1].replace('\t','')
    DMLType = switcher.get(DMLType, DMLType)
    strTrxInfo = '/* {} | {} | {} _TRXINFO_ */'.format(DMLType,startTime,endLogPos)
    return strTrxInfo
  except Exception,e:
          logPrint.error('{} - {}'.format(Exception,e))
          logPrint.error('Failed to get transaction info at function getInfo() - {}'.format(line))
          logPrint.error('{}'.format(traceback.print_exc()))
          exit(9) 

def filterBinlog():
  logPrint.info('Purging binlog DML, it may take some minutes...')
  command_str = "./bin/mysqlbinlog --base64-output=decode-rows -v "  \
                + startTimeStr + endTimeStr + startPosStr + endPosStr + binlogFile + schemaStr + tableStr + " >> " + tmpBinlogDML
  (CMDStatus, CMDOutput) = commands.getstatusoutput(command_str)
  if CMDStatus != 0:
    #logPrint.info(command_str)
    logPrint.error("Failed while purging binlog DML!")
    logPrint.error(str(CMDStatus) + ' - ' + str(CMDOutput))
    exit(9)

  logPrint.info('Purging binlog UNDO, it may take some minutes...')
#  command_str = "./bin/mysqlbinlog -B --base64-output=decode-rows -v "  \
#                + startTimeStr + endTimeStr + startPosStr + endPosStr + binlogFile + schemaStr + tableStr +  " >> " + tmpBinlogUNDO
#  (CMDStatus, CMDOutput) = commands.getstatusoutput(command_str)
#  if CMDStatus != 0:
#    #logPrint.info(command_str)
#    logPrint.error("Failed while purging binlog UNDO!")
#    logPrint.error(str(CMDStatus) + ' - ' + str(CMDOutput))
#    exit(9)

def getColList(inputTable):
  """
  Desc:
      get all the fields for input table.
  """
  try:
    listResult = []
    getColSQL = 'desc {}_Bu'.format(inputTable)
    curSourceIns.execute(getColSQL)
    columnInfo = curSourceIns.fetchall()
    i = 0
    for columnDic in columnInfo:
      listResult.append('`' + columnDic['Field'] + '`')
    #print listResult
    return listResult
  except Exception,e:
          logPrint.error('{} - {}'.format(Exception,e))
          logPrint.error('Failed to get table columns for {}'.format(inputTable))
          logPrint.error('{}'.format(traceback.print_exc()))
          exit(9)   

def generateSQL(v_type, rawStr):
  """
  Desc:
      This function aims to transform from raw SQL string to standard SQL with all column names. 
      Only INSERT, UPDATE, DELETE will be processed.
  """

  global strSQL
  global sqlNumber
  strSQL = ''
  sqlNumber += 1

#-----------------------------------------------------------------------------------------------------
# Get input arguments
#-----------------------------------------------------------------------------------------------------
logPrint = Logger( LogFile, logging.INFO, logging.DEBUG)

if (len(binlogFile) == 0) :
  logPrint.error('Incorrect binlogFile !!!')
  exit(9)

logPrint.info("Started to analyze mysql binlog.")

logPrint.info("binlogFile: " + binlogFile)
logPrint.info("schemaName: " + schemaName )
logPrint.info("tableName: " + tableName )
logPrint.info("startTime: " + startTime )
logPrint.info("endTime: " + endTime )
logPrint.info("startPosition: " + startPos )
logPrint.info("endPosition: " + endPos )

#-----------------------------------------------------------------------------------------------------
# Step1. Purge binlog by mysqlbinlog
#-----------------------------------------------------------------------------------------------------
if not os.path.exists(binlogFile):
  logPrint.error('Binlog File {} not exists !!!'.format(binlogFile))
  exit(9)

if RunMode == 'db':
  create_tb_sql ='''
          CREATE TABLE IF NOT EXISTS binlog_sql_redo(
              id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
              dml_start_time DATETIME NOT NULL COMMENT 'when to start this transaction ',
              end_log_pos BIGINT NOT NULL COMMENT 'the log position for finish this transaction',
              db_name VARCHAR(100) NOT NULL COMMENT 'which database happened this transaction ',
              table_name VARCHAR(200) NOT NULL COMMENT 'which table happened this transaction ',
              sqltype VARCHAR(10) NOT NULL ,
              dml_sql LONGTEXT NULL  COMMENT 'what sql excuted',
              PRIMARY KEY (id),
              INDEX sqltype(sqltype),
              INDEX dml_start_time (dml_start_time),
              INDEX end_log_pos (end_log_pos)
          )
          COLLATE='utf8_general_ci' ENGINE=InnoDB;
          CREATE TABLE IF NOT EXISTS binlog_sql_undo(
              id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
              dml_start_time DATETIME NOT NULL COMMENT 'when to start this transaction ',
              end_log_pos BIGINT NOT NULL COMMENT 'the log position for finish this transaction',
              db_name VARCHAR(100) NOT NULL COMMENT 'which database happened this transaction ',
              table_name VARCHAR(200) NOT NULL COMMENT 'which table happened this transaction ',
              undo_sql LONGTEXT NULL  COMMENT 'undo sql',
              PRIMARY KEY (id),
              INDEX dml_start_time (dml_start_time),
              INDEX end_log_pos (end_log_pos)
          )
          COLLATE='utf8_general_ci' ENGINE=InnoDB;
          TRUNCATE TABLE binlog_sql_redo;
          TRUNCATE TABLE binlog_sql_undo;
          '''
  try:
    curStore.execute(create_tb_sql)
  except Exception,e:
    logPrint.error('Parameter "LocalDatabase" in config.py incorrect!')
    logPrint.error(e)
    logPrint.error('{}'.format(traceback.print_exc()))
    exit(9)  
  logPrint.info('Created table binlog_sql_redo and binlog_sql_undo for restoring results.')

if tableName == '':
  filterBinlog()
else:
  for singalTable in  tableName.split(','):
    tableStr = " -T {} ".format(singalTable)
    filterBinlog()
(CMDStatus,rowCountDML) = commands.getstatusoutput('wc -l ' + tmpBinlogDML)
rowCountDML = rowCountDML.split()[0]
#(CMDStatus,rowCountUNDO) = commands.getstatusoutput('wc -l ' + tmpBinlogUNDO)
#rowCountUNDO = rowCountUNDO.split()[0]



#-----------------------------------------------------------------------------------------------------
# Step2. Analyze and transform to standard SQLs
#-----------------------------------------------------------------------------------------------------
"""
analyze DML SQLs in binlog file 
"""
try:
  with open(tmpBinlogDML,'r') as tmpBinlog:
    logPrint.info('Part 1: Start to analyze binlog file for DML...')
    rowNumber = 0
    sqlNumber = 0
    trxNumber = 0
    ddllist = []
    ddlrow = 0
    ddladd = ''
    strSQL = ''
    TrxInfo = ''
    isNull = 0
    valuesOne = 0
    newStrSQL = ''
    setON = 0
    updateWhere = ''
    updateWhereOn = 0
    fieldNum = 0
    updateSet = ''
    updateSetOn = 0
    updatePrefix = ''
#    listField = getColList(schemaName + '.' + tableName)
    for line in tmpBinlog:
      rowNumber += 1
      if rowNumber % 100000 == 0 :
        logPrint.info('{}% has been processed.'.format(int(round(float(rowNumber) / float(rowCountDML),2) * 100) ))
      if (line.find('###') == -1) and (line.find('STMT_END_F') == -1) and (not line.startswith('COMMIT')):
        if re.findall(r'^DROP TABLE `{}`'.format(tableName),line) or re.findall(r'^ALTER TABLE `{}` RENAME'.format(tableName),line) or re.findall(r'^TRUNCATE `{}`'.format(tableName),line):
          exit(666)
        if re.findall(r'^ALTER TABLE `{}`'.format(tableName),line) or ddlrow == 1 or re.findall(r'^CREATE TABLE `{}`'.format(tableName),line):
          ddllist.append(line.strip('\n').strip('\r'))
          ddlrow = 1
          if re.findall(r'^/\*!\*/;$',line):
            ddlrow = 0
            for ddl in ddllist:
              ddl = str(ddl)
              ddl = ddl.strip('[').strip(']')
              if not re.findall(r'^/\*!\*/;$',ddl):
                ddladd = ddladd + ' ' + ddl
              else:
                ddladd = ddladd + ';'
                print ddladd
                print '--------------ddladd-----------------------'
                if re.findall(r'^ALTER TABLE `{}`'.format(tableName),ddladd.strip()) or re.findall(r'^CREATE TABLE `{}`'.format(tableName),ddladd.strip()):
                  ddladd = ddladd.replace('`' + tableName, '`' + tableName + '_Bu',1)
#                  fileHandleDML.write('{}\n'.format(ddladd))
                  curSourceIns.execute('use {}'.format(schemaName))
                  curSourceIns.execute(ddladd)
                  listField = getColList(schemaName + '.' + tableName)
                ddladd = ''
            ddllist = []          
        continue
      if line.replace('\n','').replace(' ','') == 'BEGIN':
        TrxInfo = ''
      elif line.find('STMT_END_F') != -1:
        TrxInfo = getInfo(line)
        trxNumber += 1
      elif line.startswith('### INSERT'):
        if strSQL != '':
          pass
          #logPrint.error('Find insert!!' + strSQL)
        #  generateSQL('redo',strSQL)
        typeSQL = 'i'
        strSQL += TrxInfo + line.strip('###').strip().replace('`' + schemaName + '`.`' + tableName + '`','`' + schemaName + '`.`' + tableName + '_Bu`')
      elif line.startswith('### UPDATE'):
        if strSQL != '':
          pass
          #generateSQL('redo',strSQL)
        typeSQL = 'u'
        strSQL += TrxInfo + line.strip('###').strip()
        updatePrefix = TrxInfo + line.strip('###').strip().replace('`' + schemaName + '`.`' + tableName + '`','`' + schemaName + '`.`' + tableName + '_Bu`')
      elif line.startswith('### DELETE'):
        if strSQL != '':
          pass
          #generateSQL('redo',strSQL)
        typeSQL = 'd'
          #strSQL = strSQL.strip('###').strip().replace('`' + schemaName + '`.`' + tableName + '`','`' + schemaName + '`.`' + tableName + '_Bu`')
        strSQL += TrxInfo + line.strip('###').strip()
        if re.findall(r'`{}`.`{}`$'.format(schemaName,tableName),line.strip()):
          strSQL = strSQL.strip('###').strip().replace('`' + schemaName + '`.`' + tableName + '`','`' + schemaName + '`.`' + tableName + '_Bu`')
          print strSQL
          print '&&&&&&&&&&strSQL&&&&&&&&&&&&&&'
      elif line.startswith('### ') and typeSQL != '':
        #if line.find('=-') != -1 and line.find('(') != -1:
          # Process signed int
        #  strSQL += ' ' + line.strip('### ').strip().split()[0]
        if 1 > 2:
          pass
        else:
          if re.findall(r'^-.*\)$',re.sub("\@[0-9]{1,}\=","",line.strip('### ').strip(),1)):
            line = line[:line.index('(')]
          if typeSQL == 'i':
            if re.findall(r'^SET$',line.strip('### ').strip()):
              line = line.replace('SET','VALUES (')
            if re.findall(r'VALUES \($',strSQL):
              line = re.sub("\@[0-9]{1,}\=","",line,1)
              valuesOne = 1
            if valuesOne == 1:
              line = re.sub("\@[0-9]{1,}\=",",",line,1)
          if typeSQL == 'u':
            listField = getColList(schemaName + '.' + tableName)
            if re.findall(r'WHERE$',line.strip('### ').strip()):
              updateWhereOn = 1
            if updateWhereOn == 1:
              if re.findall(r'^SET$',line.strip('### ').strip()):
                updateWhereOn = 0
                fieldNum = 0
                updateSetOn = 1
              else:
                if re.findall(r'^WHERE$',line.strip('### ').strip()):
                  updateWhere += ' ' + line.strip('### ').strip()
                #print updateWhere
                #print '===========updateWhere=================='
                if fieldNum < len(listField) and not re.findall(r'WHERE$',line.strip('### ').strip()):
                  if re.findall(r'^NULL$',re.sub("\@[0-9]{1,}\=","",line.strip('### ').strip(),1)):
                    line.strip('### ').strip()
                  if re.findall(r'WHERE$',updateWhere):
                    if re.findall(r'^NULL$',re.sub("\@[0-9]{1,}\=","",line.strip('### ').strip(),1)):
                      re.sub("\=NULL"," is NULL",line,1)
                    updateWhere += re.sub("\@[0-9]{1,}",' ' + listField[fieldNum],line.strip('### ').strip(),1)
                  else:
                    if re.findall(r'^NULL$',re.sub("\@[0-9]{1,}\=","",line.strip('### ').strip(),1)):
                      line = re.sub("\=NULL"," is NULL",line,1)
                    updateWhere += re.sub("\@[0-9]{1,}",' AND ' + listField[fieldNum],line.strip('### ').strip(),1)
                  fieldNum += 1
                  print updateWhere
                  print '------------updateWhere------------------'
            if updateSetOn == 1:
              if re.findall(r'^SET$',line.strip('### ').strip()):
                updateSet += ' ' + line.strip('### ').strip()
              if fieldNum < len(listField) and not re.findall(r'SET$',line.strip('### ').strip()):
                if re.findall(r'SET$',updateSet):
                  updateSet += re.sub("\@[0-9]{1,}\=",' ' + listField[fieldNum] + '=',line.strip('### ').strip(),1)
                else:
                  updateSet += re.sub("\@[0-9]{1,}\=",' ' + ',' + listField[fieldNum] + '=',line.strip('### ').strip(),1)
                fieldNum += 1

          if typeSQL == 'd':
            listField = getColList(schemaName + '.' + tableName)
            if re.findall(r'^NULL$',re.sub("\@[0-9]{1,}\=","",line.strip('### ').strip(),1)):
              line = re.sub("\=NULL"," is NULL",line,1)
            if fieldNum < len(listField) and not re.findall(r'WHERE$',line.strip('### ').strip()):
              if re.findall(r'WHERE$',strSQL.strip('### ').strip()):
                line = re.sub("\@[0-9]{1,}",' ' + listField[fieldNum],line.strip('### ').strip(),1)
              else:
                line = re.sub("\@[0-9]{1,}",' AND ' + listField[fieldNum],line.strip('### ').strip(),1)
              fieldNum += 1

          
          #if line.find('\'') == -1 and line.find('=NULL') != -1 and isNull == 0:
          #  line = line.replace('=',' is ')
          #if re.findall(r'^SET$',line):
          #  isNull = 1
          strSQL += ' ' + line.strip('### ').strip()
      elif line.startswith('COMMIT'):
        isNull = 0
        valuesOne = 0
        fieldNum = 0
        if strSQL.startswith('/* INSERT'):
          strSQL += ' );'
          #fileHandleDML.write('{}\n'.format(strSQL))
          print strSQL
          print '-------------strSQL------------------'
          curSourceIns.execute(strSQL)
          BinlogSrcConn.commit()
          strSQL = ''
        if strSQL.startswith('/* UPDATE'):
          #fieldNum = 0
          updatePrefix = updatePrefix + updateSet + updateWhere
          #fileHandleDML.write('{};\n'.format(updatePrefix))
          curSourceIns.execute(updatePrefix)
          BinlogSrcConn.commit()
          print updatePrefix
          print '**************updatePrefix************'
          updatePrefix = ''
          updateWhere = ''
          updateSet = ''
          updateSetOn = 0
          strSQL = ''
        if strSQL.startswith('/* DELETE'):
          print strSQL
          print '-----------strSQL---------------'
          #fileHandleDML.write('{};\n'.format(strSQL))
          curSourceIns.execute(strSQL)
          BinlogSrcConn.commit()
          strSQL = ''
        newStrSQL = ''
        if strSQL != '':
          pass
          #generateSQL('redo',strSQL)
      elif not line.startswith('###'):
        typeSQL = ''
  logPrint.info('Total SQLs: {}'.format(sqlNumber))
  logPrint.info('Total Tranactions: {}'.format(trxNumber))
except Exception,e:
  logPrint.error('Error while processing line: ' + line.strip('\n'))
  logPrint.error(e)
  logPrint.error('{}'.format(traceback.print_exc()))
  exit(9) 

fileHandleDML.close()
curSourceIns.close()
if RunMode =='db':
  StoreSQLConn.commit()
  curStore.close()
  StoreSQLConn.close()

logPrint.info('All done...')
logPrint.info('Results are restored as below:')
logPrint.info('-' * 50 )
if RunMode == 'db':
  logPrint.info('REDO SQLs: SELECT * FROM binlog_sql_redo; ')
  logPrint.info('Undo SQLs: SELECT * FROM binlog_sql_undo;')
  logPrint.info('IP: {}'.format(myconf.LocalDatabase['host']))
  logPrint.info('Port: {}'.format(myconf.LocalDatabase['port']))
  logPrint.info('User: {}'.format(myconf.LocalDatabase['user']))
  logPrint.info('Password: {}'.format(myconf.LocalDatabase['password']))
else:
  logPrint.info('./result/redo.sql')
  logPrint.info('./result/undo.sql')
logPrint.info('-' * 50)
exit(0)





