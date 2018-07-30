# mysqlTableRestore
This is a mysql table recovery tool (Caused by deletion error).

-h：数据要恢复到哪个数据库服务器就写上它的地址。
-u：数据库服务器的用户名（注意：这里的用户需要有alter，insert，update，delete，create权限）
-p：用户的密码
-P：端口号
-d：需要恢复到哪个库就写上它的名字。
-t：需要恢复的表名
-f：备份文件的位置（注意：这里的备份文件一定要是mydumper备份出来的文件）
-T：线程数量（注意：这里的线程数量越多，你恢复备份数据的时候越快。）
-n：这个参数后面不需要跟上其他内容，如果没有这个参数，他会在恢复的表名后面跟上“_Bu”后缀。
