import pymysql
import pandas as pd
import datetime
import numpy as np
import xlrd
Creator = "10013783" #蘇佳敏

# 20200312 Init
# step 1. 同步 qs_stopword & qmd_stopword from mq_stopword 
import pymysql 
connMQ = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'mq')
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curMQ = connMQ.cursor()
curQS = connQS.cursor()

columnList = ''
varList = '' 
curMQ.execute("SHOW COLUMNS FROM mq_stopword")
for r in curMQ :
    columnList = columnList+'`'+r[0]+'`,'
    varList = varList+'%s,'
columnList = columnList[0:len(columnList)-1]
varList = varList[0:len(varList)-1]
curMQ.execute("select count(1) from mq_stopword")
curQS.execute("select count(1) from qs_stopword")
print('mq_stopword 欄位數:',len(r),' , 來源MQ 筆數:',curMQ.fetchone()[0],' , 目的QS 筆數:',curQS.fetchone()[0])
curQS.execute("delete from qs_stopword")
curQS.execute("delete from qmd_stopword")

selectStr = "select "+columnList+" from qs_stopword";
print('selectStr:', selectStr)
curMQ.execute("select "+columnList+" from mq_stopword")
for r in curMQ :
    curQS.execute("insert into qs_stopword("+columnList+")values("+varList+")",(r))
    curQS.execute("insert into qmd_stopword("+columnList+")values("+varList+")",(r))
curQS.execute("commit")
curQS.execute("select count(1) from qs_stopword")
print('    完成 目的QS 筆數:',curQS.fetchone()[0])

# 20200312 Init
# step 2. 將 "Sheet標準題" 解析到 standand_question
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQS = connQS.cursor()

# step 2.1 qs_standand_question
path = "D:/曾行慶交接/IKnow_QS/QS各系統問答資料庫_V2_0312.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('標準題')
print("QS各系統問答資料庫 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curQS.execute("delete from qs_standand_question")
for row in range(1, sheet_raw.nrows):   
    Answer_NO = sheet_raw.cell(row,0).value
    System = sheet_raw.cell(row,1).value
    Question = sheet_raw.cell(row,2).value
    category_main = sheet_raw.cell(row,3).value
    category_sub = sheet_raw.cell(row,4).value
    Answer = sheet_raw.cell(row,5).value
    Keyword = sheet_raw.cell(row,6).value
    SOP_chapter = sheet_raw.cell(row,7).value
    SOP_No = sheet_raw.cell(row,8).value
    URL = sheet_raw.cell(row,9).value
    Enabled = sheet_raw.cell(row,10).value
    Creator = sheet_raw.cell(row,11).value
    Create_Date = sheet_raw.cell(row,12).value     
     
    curQS.execute("insert into qs_standand_question(Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,\
    SOP_chapter,SOP_No,URL,Enabled,Creator,Create_Date)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,SOP_chapter,SOP_No,URL,Enabled,Creator))
    curQS.execute("commit")  

# 20200312 Init
# step 3. 將 "Sheet相似題" 解析到 sim_question
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQS = connQS.cursor() 
path = "D:/曾行慶交接/IKnow_QS/QS各系統問答資料庫_V2_0312.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('相似題')
print("QS各系統問答資料庫 相似題 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curQS.execute("delete from qs_sim_question")
for row in range(1, sheet_raw.nrows):
    Answer_NO = sheet_raw.cell(row,0).value
    Question = sheet_raw.cell(row,1).value
    print(row,' ',Answer_NO,' ',Question) 
    
    curQS.execute("insert into qs_sim_question(Answer_NO,Question,Creator,Create_Date)values(%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Answer_NO,Question,Creator))
curQS.execute("commit") 

# 20200312 Init
# step 4. 將 "Sheet同義詞" 解析到 sim_question
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQS = connQS.cursor()
path = "D:/曾行慶交接/IKnow_QS/QS各系統問答資料庫_V2_0312.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('同義詞')
print("QS各系統問答資料庫 同義詞 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curQS.execute("delete from qs_jieba_synon")

for row in range(1, sheet_raw.nrows):
    Word = sheet_raw.cell(row,2).value
    Synonymous = sheet_raw.cell(row,1).value
    print(row,' ',Word,' ',Synonymous) 
    
    curQS.execute("insert ignore into qs_jieba_synon(Word,Synonymous,Creator,Create_Date)values(%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Word,Synonymous,Creator))
curQS.execute("commit") 

# 20200312 Init
# step 5. 將 qs_standand_question裡的Keyword解析後，塞入qs_jiebadict
# step 5.1 QS
import re  
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQS = connQS.cursor()
curQS2 = connQS.cursor()
curQS.execute("delete from qs_jiebadict")
curQS.execute("SELECT Keyword FROM qs_standand_question")

for Key in curQS :
    KeywordList = re.split('，|；',Key[0])  
    for i in range(0,len(KeywordList)) :
        if len(KeywordList[i]) > 1 :
            curQS2.execute("insert ignore into qs_jiebadict(jiebaword,Creator,Create_Date)values(%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",(KeywordList[i],Creator))
curQS2.execute("commit")     