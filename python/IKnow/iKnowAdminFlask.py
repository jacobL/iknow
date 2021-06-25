from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS, cross_origin
from collections import OrderedDict
from werkzeug.serving import run_simple
import pymysql
import datetime
import time
import json 

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

@app.route('/uploadStandandQuestion', methods = ['GET'])
def uploadStandandQuestion():
    PERNR = request.args.get('PERNR')
    db = request.args.get('db') 
    print(' PERNR:',PERNR,' db:',db) 

    List = json.loads(request.args.get('List'))  
    
    print(len(List),' PERNR:',PERNR,' db:',db) 
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = db )          
    cur = conn.cursor() 
    returnData = OrderedDict();
    
    for i in range(0,len(List)) : 
        Answer_NO = List[i]["Answer_NO"]
        Question = List[i]["Question"]
        Answer = List[i]["Answer"]
        Keyword = List[i]["Keyword"]
        SOP_chapter = List[i]["SOP chapter"] if "SOP chapter" in List[i] else '' 
        SOP_No = List[i]["SOP No"] if "SOP No" in List[i] else ''
        URL = List[i]["URL"] if "URL" in List[i] else ''
        # x = 10 if a > b else 11
    
            
        Action = List[i]["異動"]
        #print(i,' Answer_NO:',Answer_NO,' Question:',Question,' Answer:',Answer,' Keyword:',Keyword,' SOP_chapter:',SOP_chapter,' SOP_No:',SOP_No,' URL:',URL,' Action:',Action)
        print(i,' Answer_NO:',Answer_NO)
        if Action == '修訂' :
            result = cur.execute('update '+db+'_standand_question set Question=%s,Answer=%s,Keyword=%s,SOP_chapter=%s,SOP_No=%s,URL=%s where Answer_NO=%s',(Question,Answer,Keyword,SOP_chapter,SOP_No,URL, Answer_NO))
        elif Action == '新增' :
            result = cur.execute('insert ignore into '+db+'_standand_question (Answer_NO,Question,Answer,Keyword,SOP_chapter,SOP_No,URL)values(%s,%s,%s,%s,%s,%s,%s)',(Answer_NO,Question,Answer,Keyword,SOP_chapter,SOP_No,URL))
        elif Action == '刪除' :
            result = cur.execute('update '+db+'_standand_question set Enabled="FALSE" where Answer_NO=%s',(Answer_NO))
        print('  result:',result)
        tmp = {}
        tmp['異動'] = Action
        tmp['result'] = result
        returnData[Answer_NO] = tmp
    #cur.execute('commit')    
    #Sample_Json=json.loads(request.get_data(),encoding='utf8')
    
      
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getAdminAuth", methods=['GET'])
def getAdminAuth():
    PERNR = request.args.get('PERNR')
    #print(PERNR)
    
    returnData = OrderedDict();
    
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = 'iknow' )          
    cur = conn.cursor() 
    
    cur.execute('select department,auth from adminAuth where PERNR=%s and status=0',(PERNR))
    if cur.rowcount > 0 : 
        for r in cur :
            department = r[0]
            auth = r[1]
            returnData['department'] = department
            returnData['auth'] = auth
    else :
        returnData['department'] = 'na'
        
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
@app.route("/getStandandQuestion", methods=['GET'])
def getStandandQuestion():
    db = request.args.get('db')
    tab = db
    if db == 'all' :
        db = 'mq'
    elif db == 'qmd' :    
        tab = db
        db = 'qs'
        
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = db )          
    cur = conn.cursor() 
        
    returnData = OrderedDict();
     
    cur.execute('SELECT Answer_NO,System,Question,category_main,category_sub,Answer,Keyword,SOP_chapter,SOP_No,URL,Enabled,Creator,DATE_FORMAT(Create_Date,"%Y%m%d %H:%i:%s") from '+tab+'_standand_question where Enabled="True" order by Answer_NO')
    #print(cur.rowcount)
    if cur.rowcount > 0 : 
        for r in cur :
            tmp = OrderedDict()
            Answer_NO = r[0]
            tmp['System'] = r[1]
            tmp['Question'] = r[2]
            tmp['category_main'] = r[3]
            tmp['category_sub'] = r[4]
            tmp['Answer'] = r[5]
            tmp['Keyword'] = r[6]
            tmp['SOP_chapter'] = r[7]
            tmp['SOP_No'] = r[8]
            tmp['URL'] = r[9]
            tmp['Enabled'] = r[10]
            tmp['Creator'] = r[11]
            tmp['Create_Date'] = r[12]
            returnData[Answer_NO] = tmp
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response      

@app.route("/getSimQuestion", methods=['GET'])
def getSimQuestion():
    db = request.args.get('db')
    tab = db
    if db == 'all' :
        db = 'mq'
    elif db == 'qmd' :    
        tab = db
        db = 'qs'
        
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = db )          
    cur = conn.cursor() 
        
    returnData = OrderedDict();
    cur.execute('SELECT Answer_NO,Question,Creator,DATE_FORMAT(Create_Date,"%Y%m%d %H:%i:%s") FROM '+tab+'_sim_question order by Answer_NO')
    #print(cur.rowcount)
    if cur.rowcount > 0 : 
        for r in cur :
            tmp = OrderedDict()
            Answer_NO = r[0]
            tmp['Question'] = r[1]
            tmp['Creator'] = r[2]
            tmp['Create_Date'] = r[3]
            returnData[Answer_NO] = tmp
     
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response      

@app.route("/getJiebaSynon", methods=['GET'])
def getJiebaSynon():
    db = request.args.get('db')
    tab = db
    if db == 'all' :
        db = 'mq'
    elif db == 'qmd' :    
        tab = db
        db = 'qs'
        
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = db )          
    cur = conn.cursor() 
        
    returnData = OrderedDict();
    cur.execute('SELECT Word,Synonymous,Creator,DATE_FORMAT(Create_Date,"%Y%m%d %H:%i:%s") FROM '+tab+'_jieba_synon order by Create_Date desc')
    #print(cur.rowcount)
    if cur.rowcount > 0 : 
        c=0
        for r in cur :
            tmp = OrderedDict()
            tmp['Word'] = r[0]
            tmp['Synonymous'] = r[1]
            tmp['Creator'] = r[2]
            tmp['Create_Date'] = r[3]
            returnData[c] = tmp
            c=c+1
     
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response  

if __name__ == '__main__':    
    host = '10.55.52.98' 
    port=33060 
    user = 'root' 
    passwd = "1234"
    
    app.run(host='0.0.0.0', port=81)
    #run_simple('127.0.0.1', 81, app)        
        
        