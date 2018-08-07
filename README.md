# mysqlTableRestore
This is a mysql table recovery tool (Caused by deletion error).

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


