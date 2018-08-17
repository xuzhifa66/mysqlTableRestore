# mysqlTableRestore
This is a mysql table recovery tool (Caused by deletion error).

mysqlTableRestore是一个快速的恢复误删除表的工具。恢复过程是将指定的mydumer备份文件恢复到目标库中，再把备份之后产生的数据通过解析binlog文件恢复到目标库中。

使用mysqlTableRestore比原始手动恢复误删除表的做法会快很多，原因如下：

1、mysqlTableRestore使用了myloader，也就是说备份可以进行多线程的并行恢复某一张表。

2、mysqlTableRestore解析一个binlog日志文件的时候可以只解析出单个表的日志信息，不需要先通过mysqlbinlog解析出数据再使用脚本提取出指定表的日志信息。

3、mysqlTableRestore会自动帮你完成备份的恢复，日志找点，日志恢复，这只需要你的一个命令即可完成。大大提高了效率以及减少了失误的概率。

安装说明：
-
1、把下载好的安装包解压

2、安装依赖的python模块pymysql

3、进入解压后所生成的目录，并且设置“MYSQL_BINLOG_DIR”环境变量。

export MYSQL_DATA_DIR= mysql的binlog文件所在的目录

4、设置好环境变量之后在当前会话执行下面的命令

python install.py

使用说明：
-
1、要使用mysqlTableRestore恢复被误删除的表，需要提前使用mydumper进行备份。mydumper已经在mysqlTableRestore的压缩包内了，不需要额外的安装。

2、目前mysqlTableRestore只支持恢复被“drop table”命令所删除的表。

3、mysql的binlog参数要确认符合下面的值：

binlog_format=ROW

binlog_row_image=FULL

log_bin=ON

4、mysqlTableRestore的恢复表是通过mydumper备份加上binlog日志，如果数据不在备份或者日志当中存在那将无法恢复。


mysqlTableRestore.py的参数说明：
-

-h：数据要恢复到哪个数据库服务器就写上它的地址。

-u：数据库服务器的用户名（注意：这里的用户需要有alter，insert，update，delete，create权限）

-p：用户的密码

-P：端口号

-d：需要恢复到哪个库就写上它的名字。

-t：需要恢复的表名

-f：备份文件的位置（注意：这里的备份文件一定要是mydumper备份出来的文件）

-T：线程数量（注意：这里的线程数量越多，你恢复备份数据的时候越快。）

-n：这个参数后面不需要跟上其他内容，如果没有这个参数，他会在恢复的表名后面跟上“_Bu”后缀。


