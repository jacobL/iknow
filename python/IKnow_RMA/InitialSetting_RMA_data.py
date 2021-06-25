import pymysql
import pandas as pd
import datetime
import numpy as np
import xlrd
Creator = "10126949"  #10126949 RMA 陳詩涵

# 20200511 Init
# step 1. 同步 rma_stopword 
import pymysql 
connQS = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'qs')
connRMA = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'rma')
curQS = connQS.cursor()
connRMA = connRMA.cursor()

columnList = ''
varList = '' 
curQS.execute("SHOW COLUMNS FROM qs_stopword")
for r in curQS :
    columnList = columnList+'`'+r[0]+'`,'
    varList = varList+'%s,'
columnList = columnList[0:len(columnList)-1]
varList = varList[0:len(varList)-1]
curQS.execute("select count(1) from qs_stopword")
connRMA.execute("select count(1) from rma_stopword")
print('qs_stopword 欄位數:',len(r),' , 來源QS 筆數:',curQS.fetchone()[0],' , 目的RMA 筆數:',connRMA.fetchone()[0])
connRMA.execute("delete from rma_stopword") 
selectStr = "select "+columnList+" from rma_stopword";
#print('selectStr:', selectStr)
curQS.execute("select "+columnList+" from qs_stopword")
for r in curQS :
    connRMA.execute("insert into rma_stopword("+columnList+")values("+varList+")",(r)) 
connRMA.execute("commit")
connRMA.execute("select count(1) from rma_stopword")
print('    完成 目的RMA 筆數:',connRMA.fetchone()[0])

# 20200512 Init
# step 2. 將 "Sheet標準題" 解析到 standand_question
connRMA = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'rma')
curRMA = connRMA.cursor()

# step 2.1 qs_standand_question
path = "D:/曾行慶交接/IKnow_RMA/系統問答資料庫template to 均銘_0531.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('標準題')
print("RMA各系統問答資料庫 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curRMA.execute("delete from rma_standand_question")
for row in range(0, sheet_raw.nrows):   
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
    Enabled = 'True' #  sheet_raw.cell(row,10).value
    Creator = sheet_raw.cell(row,11).value
    Create_Date = sheet_raw.cell(row,12).value     
    print(row,'. ',Answer_NO,' ',Keyword,',Enabled:',Enabled) 
    curRMA.execute("insert into rma_standand_question(Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,\
    SOP_chapter,SOP_No,URL,Enabled,Creator,Create_Date)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,SOP_chapter,SOP_No,URL,Enabled,Creator))
curRMA.execute("commit")  

# 20200604 Init
# step 3. 將 "Sheet相似題" 解析到 sim_question
connRMA = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'rma')
curRMA = connRMA.cursor()
# step 3.1 qs_sim_question
path = "D:/曾行慶交接/IKnow_RMA/系統問答資料庫template to 均銘_0531.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('相似題')
print("RMA各系統問答資料庫 相似題 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curRMA.execute("delete from rma_sim_question")
 
for row in range(1, sheet_raw.nrows):
    Answer_NO = sheet_raw.cell(row,0).value
    Question = sheet_raw.cell(row,1).value
    print(row,' ',Answer_NO,' ',Question) 
    
    curRMA.execute("insert into rma_sim_question(Answer_NO,Question,Creator,Create_Date)values(%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Answer_NO,Question,Creator))
curRMA.execute("commit") 

# 20200604 Init
# step 4. 將 "Sheet同義詞" 解析到 sim_question
connRMA = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'rma')
curRMA = connRMA.cursor()
# step 4.1 qs_sim_question
path = "D:/曾行慶交接/IKnow_RMA/系統問答資料庫template to 均銘_0531.xlsx" 
data = xlrd.open_workbook(path)
sheet_raw = data.sheet_by_name('同義詞')
print("RMA各系統問答資料庫 同義詞 row num:", sheet_raw.nrows,",col num:", sheet_raw.ncols) 
curRMA.execute("delete from rma_jieba_synon")
for row in range(1, sheet_raw.nrows):
    Word = sheet_raw.cell(row,2).value
    Synonymous = sheet_raw.cell(row,1).value
    print(row,' ',Word,' ',Synonymous) 
    
    curRMA.execute("insert ignore into rma_jieba_synon(Word,Synonymous,Creator,Create_Date)values(%s,%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",\
    (Word,Synonymous,Creator))
curRMA.execute("commit") 

# 20200604 Init
# step 5. 將 rma_standand_question裡的Keyword解析後，塞入rma_jiebadict

import re  
connRMA = pymysql.connect( host = '10.55.52.98' , port=33060 , user = 'root' , passwd = "1234" , db = 'rma')
curRMA = connRMA.cursor()
curRMA2 = connRMA.cursor()
curRMA.execute("delete from rma_jiebadict")
curRMA.execute("SELECT Keyword FROM rma_standand_question")

for Key in curRMA :
    KeywordList = re.split('，|；',Key[0])  
    for i in range(0,len(KeywordList)) :
        if len(KeywordList[i]) > 1 :
            curRMA2.execute("insert ignore into rma_jiebadict(jiebaword,Creator,Create_Date)values(%s,%s,CONVERT_TZ(NOW(),'+00:00','+8:00'))",(KeywordList[i],Creator))
curRMA2.execute("commit")       
