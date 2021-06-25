import pymysql
import pandas as pd
import datetime
import numpy as np
import xlrd
Creator = "10013783" #蘇佳敏

# 20200312 Init
# step 1. 同步  qmd_stopword from qs_stopword 
import pymysql  
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')

curQS = connQS.cursor()
curQS2 = connQS.cursor()

columnList = ''
varList = '' 
curQS.execute("SHOW COLUMNS FROM qs_stopword")
for r in curQS :
    columnList = columnList+'`'+r[0]+'`,'
    varList = varList+'%s,'
columnList = columnList[0:len(columnList)-1]
varList = varList[0:len(varList)-1]
curQS.execute("select count(1) from qs_stopword")
#print('qs_stopword 欄位數:',len(r),' , 來源QS 筆數:',curMQ.fetchone()[0],' , 目的QS 筆數:',curQS.fetchone()[0])
curQS.execute("delete from qmd_stopword")

curQS.execute("select "+columnList+" from qs_stopword")
for r in curQS :    
    curQS2.execute("insert into qmd_stopword("+columnList+")values("+varList+")",(r))
curQS2.execute("commit")
curQS.execute("select count(1) from qmd_stopword")
print('    完成 目的QMD 筆數:',curQS.fetchone()[0])

# 20200312 Init
# step 2. 將 "Sheet標準題" 解析到 standand_question
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQMD = connQS.cursor()

# step 2.1 qmd_standand_question 
path = "D:/曾行慶交接/IKnow_QS/QMD__系統問答資料庫_V2_0312.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('標準題')
print("QMD__系統問答資料庫 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols)
curQMD.execute("delete from qmd_standand_question")
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
    #Enabled = sheet_raw.cell(row,10).value
    Enabled = 'True'
    Creator = sheet_raw.cell(row,11).value
    Create_Date = sheet_raw.cell(row,12).value     
     
    curQMD.execute("insert into qmd_standand_question(Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,\
    SOP_chapter,SOP_No,URL,Enabled,Creator,Create_Date)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,SOP_chapter,SOP_No,URL,Enabled,Creator))
    curQMD.execute("commit")  

# 20200312 Init
# step 3. 將 "Sheet相似題" 解析到 sim_question
connQMD = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQMD = connQMD.cursor()
# step 3.1 qmd_sim_question
path = "D:/曾行慶交接/IKnow_QS/QMD__系統問答資料庫_V2_0312.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('相似題')
print("QMD各系統問答資料庫 相似題 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curQMD.execute("delete from qmd_sim_question")
for row in range(1, sheet_raw.nrows):
    Answer_NO = sheet_raw.cell(row,0).value
    Question = sheet_raw.cell(row,1).value
    print(row,' ',Answer_NO,' ',Question) 
    
    curQMD.execute("insert into qmd_sim_question(Answer_NO,Question,Creator,Create_Date)values(%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Answer_NO,Question,Creator))
curQMD.execute("commit")     
    
# 20200312 Init
# step 4. 將 "Sheet同義詞" 解析到 sim_question
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQS = connQS.cursor()
# step 4.1 qmd_sim_question
path = "D:/曾行慶交接/IKnow_QS/QMD__系統問答資料庫_V2_0312.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('同義詞')
print("QMD各系統問答資料庫 同義詞 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curQS.execute("delete from qmd_jieba_synon")
for row in range(1, sheet_raw.nrows):
    Word = sheet_raw.cell(row,2).value
    Synonymous = sheet_raw.cell(row,1).value
    print(row,' ',Word,' ',Synonymous) 
    
    curQS.execute("insert into qmd_jieba_synon(Word,Synonymous,Creator,Create_Date)values(%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Word,Synonymous,Creator))
curQS.execute("commit")     


# 20200312 Init
# step 5. 將 qs_standand_question裡的Keyword解析後，塞入qs_jiebadict
# step 5.1 QMD
import re 
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
curQS = connQS.cursor()
curQS2 = connQS.cursor()
# step 5.2 QMD
curQS.execute("delete from qmd_jiebadict")
curQS.execute("SELECT Keyword FROM qmd_standand_question")

for Key in curQS :
    KeywordList = re.split('，|；',Key[0])  
    for i in range(0,len(KeywordList)) :
        if len(KeywordList[i]) > 1 :
            curQS2.execute("insert ignore into qmd_jiebadict(jiebaword,Creator,Create_Date)values(%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",(KeywordList[i],Creator))
curQS2.execute("commit")     