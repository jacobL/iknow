from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS, cross_origin
from collections import OrderedDict
from werkzeug.serving import run_simple
import pymysql
import pyodbc
import datetime
import time
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = True
CORS(app)

@app.route("/toplist1", methods=['GET'])
def toplist1():    
    PERNR = request.args.get('PERNR');
    deptSystem = request.args.get('deptSystem').lower();
    returnData = OrderedDict();  
    TopN = 5
    if deptSystem == 'mq' : # deptSystem = 2
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'mq')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from mq_chat_log_new s join mq_standand_question t on s.answerNo=t.Answer_NO group by answerNo) a, (select count(1) total from mq_chat_log_new) b order by c desc limit %s",(TopN))
    elif deptSystem == 'qs' : # deptSystem = 4
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qs_chat_log_new s join qs_standand_question t on s.answerNo=t.Answer_NO group by answerNo) a, (select count(1) total from qs_chat_log_new) b order by c desc limit %s",(TopN))
    elif deptSystem == 'qmd' : # deptSystem = 5
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qmd_chat_log_new s join qmd_standand_question t on s.answerNo=t.Answer_NO group by answerNo) a, (select count(1) total from qmd_chat_log_new) b order by c desc limit %s",(TopN))
    elif deptSystem == 'rma' : # deptSystem = 6
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'rma')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from rma_chat_log_new s join rma_standand_question t on s.answerNo=t.Answer_NO group by answerNo) a, (select count(1) total from rma_chat_log_new) b order by c desc limit %s",(TopN))
    elif deptSystem == 'sqe' : # deptSystem = 7
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'sqe')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from sqe_chat_log_new s join sqe_standand_question t on s.answerNo=t.Answer_NO group by answerNo) a, (select count(1) total from sqe_chat_log_new) b order by c desc limit %s",(TopN))    
    else : # CoQ+  # deptSystem = 1
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')        
        cur = conn.cursor() 
        cur.execute("select answerNo,description,c,round(100*c/total,2) from (select s.answerNo,description,count(1) c from iknow.chatLog s join normalDescription t on s.answerNo=t.answerNo group by answerNo ) a,(select count(1) total from iknow.chatLog) b order by c desc limit %s",(TopN))
    c=0
    for r in cur : 
        returnData[c] = r[0]+'::'+r[1]+'::'+str(r[2])+'::'+str(r[3])
        c = c + 1    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/toplist2", methods=['GET'])
def toplist2():
    PERNR = request.args.get('PERNR');
    deptSystem = request.args.get('deptSystem').lower();
    returnData = OrderedDict();  
    print(PERNR,' ',deptSystem)
    TopN = 5
    if deptSystem == 'mq' : # deptSystem = 2
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'mq')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from mq_chat_log_new s join mq_standand_question t on s.answerNo=t.Answer_NO where s.user_id=%s group by answerNo) a, (select count(1) total from mq_chat_log_new where user_id=%s) b order by c desc limit %s",(PERNR,PERNR,TopN))
    elif deptSystem == 'qs' : # deptSystem = 4
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qs_chat_log_new s join qs_standand_question t on s.answerNo=t.Answer_NO where s.user_id=%s group by answerNo) a, (select count(1) total from qs_chat_log_new where user_id=%s) b order by c desc limit %s",(PERNR,PERNR,TopN))
    elif deptSystem == 'qmd' : # deptSystem = 5
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qmd_chat_log_new s join qmd_standand_question t on s.answerNo=t.Answer_NO where s.user_id=%s group by answerNo) a, (select count(1) total from qmd_chat_log_new where user_id=%s) b order by c desc limit %s",(PERNR,PERNR,TopN))
    elif deptSystem == 'rma' : # deptSystem = 6
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'rma')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from rma_chat_log_new s join rma_standand_question t on s.answerNo=t.Answer_NO where s.user_id=%s group by answerNo) a, (select count(1) total from rma_chat_log_new where user_id=%s) b order by c desc limit %s",(PERNR,PERNR,TopN))
    elif deptSystem == 'sqe' : # deptSystem = 7
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'sqe')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from sqe_chat_log_new s join sqe_standand_question t on s.answerNo=t.Answer_NO where s.user_id=%s group by answerNo) a, (select count(1) total from sqe_chat_log_new where user_id=%s) b order by c desc limit %s",(PERNR,PERNR,TopN))    
    else : # CoQ+ # deptSystem = 1
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')        
        cur = conn.cursor() 
        cur.execute("select answerNo,description,c,round(100*c/total,2) from (select s.answerNo,description,count(1) c from iknow.chatLog s join normalDescription t on s.answerNo=t.answerNo where s.PERNR=%s group by answerNo ) a,(select count(1) total from iknow.chatLog where PERNR=%s) b order by c desc limit %s",(PERNR,PERNR,TopN))    
    c=0
    for r in cur : 
        returnData[c] = r[0]+'::'+r[1]+'::'+str(r[2])+'::'+str(r[3])
        c = c + 1
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/toplist3", methods=['GET'])
def toplist3(): 
    deptSystem = request.args.get('deptSystem').lower();
    returnData = OrderedDict();
    TopN = 5
    if deptSystem == 'mq' : # deptSystem = 2
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'mq')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from mq_chat_log_new s join mq_standand_question t on s.answerNo=t.Answer_NO where feedback=1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from mq_chat_log_new where feedback=1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'qs' : # deptSystem = 4
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qs_chat_log_new s join qs_standand_question t on s.answerNo=t.Answer_NO where feedback=1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from qs_chat_log_new where feedback=1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'qmd' : # deptSystem = 5
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qmd_chat_log_new s join qmd_standand_question t on s.answerNo=t.Answer_NO where feedback=1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from qmd_chat_log_new where feedback=1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'rma' : # deptSystem = 6
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'rma')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from rma_chat_log_new s join rma_standand_question t on s.answerNo=t.Answer_NO where feedback=1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from rma_chat_log_new where feedback=1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'sqe' : # deptSystem = 7
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'sqe')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from sqe_chat_log_new s join sqe_standand_question t on s.answerNo=t.Answer_NO where feedback=1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from sqe_chat_log_new where feedback=1 and answerNo is not NULL) b order by c desc limit %s",(TopN))    
    else : # CoQ+ # deptSystem = 1
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')        
        cur = conn.cursor() 
        cur.execute("select answerNo,description,c,round(100*c/total,2) from (select s.answerNo,description, count(1) c from iknow.chatLog s join normalDescription t on s.answerNo=t.answerNo where feedback=0 and s.answerNo is not NULL group by s.answerNo ) a,(select count(1) total from iknow.chatLog where feedback=0 and answerNo is not NULL) b limit 5" )
    #cur.execute("select answerNo,description,c,round(100*c/total,2) from (select s.answerNo,description,count(1) c from qm.chatLog s join normalDescription t on s.answerNo=t.answerNo where s.PERNR=%s group by answerNo ) a,(select count(1) total from qm.chatLog where PERNR=%s) b limit 5",(PERNR,PERNR))    
    c=0
    for r in cur : 
        returnData[c] = r[0]+'::'+r[1]+'::'+str(r[2])+'::'+str(r[3])
        c = c + 1
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/toplist4", methods=['GET'])
def toplist4():
     
    #PERNR = request.args.get('PERNR');
    deptSystem = request.args.get('deptSystem').lower();
    returnData = OrderedDict();
    TopN = 5
    if deptSystem == 'mq' : # deptSystem = 2
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'mq')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from mq_chat_log_new s join mq_standand_question t on s.answerNo=t.Answer_NO where feedback<>1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from mq_chat_log_new where feedback<>1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'qs' : # deptSystem = 4
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qs_chat_log_new s join qs_standand_question t on s.answerNo=t.Answer_NO where feedback<>1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from qs_chat_log_new where feedback<>1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'qmd' : # deptSystem = 5
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'qs')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from qmd_chat_log_new s join qmd_standand_question t on s.answerNo=t.Answer_NO where feedback<>1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from qmd_chat_log_new where feedback<>1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'rma' : # deptSystem = 6
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'rma')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from rma_chat_log_new s join rma_standand_question t on s.answerNo=t.Answer_NO where feedback<>1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from rma_chat_log_new where feedback<>1 and answerNo is not NULL) b order by c desc limit %s",(TopN))
    elif deptSystem == 'sqe' : # deptSystem = 7
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'sqe')        
        cur = conn.cursor() 
        cur.execute("select answerNo,Question,c,round(100*c/total,2) from (select answerNo,Question,count(1) c from sqe_chat_log_new s join sqe_standand_question t on s.answerNo=t.Answer_NO where feedback<>1 and s.answerNo is not NULL group by answerNo) a, (select count(1) total from sqe_chat_log_new where feedback<>1 and answerNo is not NULL) b order by c desc limit %s",(TopN))    
    else : # CoQ+ # deptSystem = 1
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')        
        cur = conn.cursor() 
        cur.execute("select answerNo,description,c,round(100*c/total,2) from (select s.answerNo,description, count(1) c from iknow.chatLog s join normalDescription t on s.answerNo=t.answerNo where feedback<>0 and s.answerNo is not NULL group by s.answerNo ) a,(select count(1) total from iknow.chatLog where feedback<>0 and answerNo is not NULL) b limit 5" )
    #cur.execute("select answerNo,description,c,round(100*c/total,2) from (select s.answerNo,description,count(1) c from qm.chatLog s join normalDescription t on s.answerNo=t.answerNo where s.PERNR=%s group by answerNo ) a,(select count(1) total from qm.chatLog where PERNR=%s) b limit 5",(PERNR,PERNR))    
    c=0
    for r in cur : 
        returnData[c] = r[0]+'::'+r[1]+'::'+str(r[2])+'::'+str(r[3])
        c = c + 1
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/feedback", methods=['GET'])
def feedback():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')     
    cur = conn.cursor() 
    Chat_ID = request.args.get('Chat_ID');
    result = request.args.get('result');
    feedbackText = request.args.get('comment');
    #print('Chat_ID:',Chat_ID,' result:',result,' feedbackText:',feedbackText)
    returnData = OrderedDict();  
    if feedbackText != '':
        cur.execute("update iknow.chatLog set feedback=%s,feedbackText=%s where id=%s",(result,feedbackText,Chat_ID))
    else :
        cur.execute("update iknow.chatLog set feedback=%s where id=%s",(result,Chat_ID))
    cur.execute("COMMIT")
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/leadUpdate", methods=['GET'])
def leadUpdate():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')     
    cur = conn.cursor() 
    app = request.args.get('app');
    yearmonth = request.args.get('yearmonth');
    lead1 = request.args.get('lead1');
    lead2 = request.args.get('lead2');
    lead3 = request.args.get('lead3');
    Chat_ID = request.args.get('Chat_ID');
    print(app,' ',yearmonth,' ',lead1,' ',lead2,' ',lead3,' ',Chat_ID)
    cur.execute("update iknow.chatLog set app=%s,yearmonth=%s,answerType=1,lead1=%s,lead2=%s,lead3=%s where id=%s",(app,yearmonth,lead1,lead2,lead3,Chat_ID))
    cur.execute("COMMIT")
    
    returnData = OrderedDict();
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 查詢談話紀錄
@app.route("/getChatLog", methods=['GET'])
def getChatLog():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')    
    cur = conn.cursor() 
    returnData = OrderedDict();  
    cur.execute("select id,PERNR,chat,checktime,status,sessionsId,answerType,app,yearmonth,answerNo,feedback,feedbackText,lead1,lead2,lead3,answerText,userChineseName from iknow.chatLog order by id desc")
    c = 0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['PERNR'] = r[1]
        tmp['chat'] = r[2]
        tmp['checktime'] = r[3]
        tmp['status'] = r[4]
        tmp['sessionsId'] = r[5]
        tmp['answerType'] = r[6]
        tmp['app'] = r[7]
        tmp['yearmonth'] = r[8]
        tmp['answerNo'] = r[9]
        tmp['feedback'] = r[10]
        tmp['feedbackText'] = r[11]
        tmp['lead1'] = r[12]
        tmp['lead2'] = r[13]
        tmp['lead3'] = r[14]
        tmp['answerText'] = r[15]
        tmp['userChineseName'] = r[16]
        returnData[c] = tmp 
        c = c + 1
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response   
# a. 談話紀錄
@app.route("/chatLog", methods=['GET'])
def chatLog():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')
    cnxn = pyodbc.connect('DRIVER={SQL Server}; Server=localhost\SQLEXPRESS;Database=coq;Trusted_Connection=True;')
    curMS = cnxn.cursor()    
    returnData = OrderedDict();    
    cur = conn.cursor() 
    PERNR = request.args.get('PERNR');
    chat = request.args.get('chat');
    sessionsId = request.args.get('sessionsId');
    curMS.execute("select NACHN,VORNA from emp01_hiring where PERNR=?",(PERNR))
    name = curMS.fetchone()
    NACHN = name[0]
    VORNA = name[1]
    
    checktime = datetime.datetime.fromtimestamp(round(time.time(), 0)).strftime('%Y-%m-%d %H:%M:%S')
    checktime1 = datetime.datetime.fromtimestamp(round(time.time(), 0)).strftime('%m-%d %H:%M:%S')
    cur.execute("insert into iknow.chatLog(PERNR,chat,sessionsId,checktime,userChineseName,feedback,answerType,status)values(%s,%s,%s,%s,%s,2,0,0)",(PERNR,chat,sessionsId,checktime,NACHN+VORNA))
    
    #print(conn.insert_id())
    #print(cur.lastrowid)
    returnData[0] = checktime1;
    returnData[1] = cur.lastrowid;
    cur.execute("COMMIT") 
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def updateChat(app,yearmonth,answerNo,answerText,Chat_ID):
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'iknow')
    cur = conn.cursor() 
    cur.execute("update iknow.chatLog set app=%s,yearmonth=%s,answerNo=%s,answerText=%s where id=%s",(app,yearmonth,answerNo,answerText,Chat_ID))
    cur.execute("COMMIT")

# getAnswer 20200131    
@app.route("/getAnswer", methods=['GET'])
def getAnswer():
    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID');
    answerNo = request.args.get('answerNo');
    
    if answerNo == "Q001" : # Q001 CoQ現況
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        print(app,' ',yearmonth,' ',Chat_ID)    
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth = int(cur.fetchone()[0]);
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth

        returnData = OrderedDict(); 
        # CoQ總計(含供應商求償)(百萬元)  sorting = '10'
        cur.execute("SELECT cost FROM forboard where app=%s and yearmonth=%s and sorting = '10'",(app,yearmonth));
        returnData[' (1) '+str(yearmonth)+app+ 'CoQ總計(含供應商求償)'] = str(round(cur.fetchone()[0]/1000000, 2))+'M (NTD)';

        ############## 原本Q002 
        # CoQ總計佔營收比  sorting = '12'
        ans = '未達標'
        cur.execute("select GROUP_CONCAT(if(sorting = '12', cost , NULL))- GROUP_CONCAT(if(sorting = '', cost*1000000, NULL)) from forboard WHERE sorting in ('12','')  and app=%s and yearmonth=%s",(app,yearmonth));
        if int(cur.fetchone()[0]) <= 0 :
            ans = '達標';
        returnData[' (5) CoQ Rate 趨勢'] = ans;

        if yearmonth%100 == 1:
            yearmonth2 = yearmonth -100 +11
        else :
            yearmonth2 = yearmonth -1
        print(yearmonth,' ',yearmonth2)    
        cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
        r = cur.fetchone()
        print(r[0],' ',r[1])
        rate = round(float(r[0])/10000,2)
        rate2 = round( float(r[1]) /10000,2)
        ans = '改善'

        if rate < rate2 :
            ans = '改善'
        elif rate > rate2 :       
            ans = '惡化'
            if (rate - rate2)/rate2 <= 0.05 :
                ans = '持平'
        else :
            ans = '持平'
        returnData[' (6) 較上月'+ans] = str(abs(round(rate-rate2,2)))+'%'; 
        ############## 原本Q004
        if yearmonth%100 == 1:
            yearmonth2 = yearmonth -100 +11
        else :
            yearmonth2 = yearmonth -1
        cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
        r = cur.fetchone()
        rate = round(float(r[0])/10000,2)
        rate2 = round(float(r[1])/10000,2)
        returnData[' (2) '+str(yearmonth2)+' CoQ Rate'] = str(rate2)+'%';
        returnData[' (3) '+str(yearmonth)+' CoQ Rate'] = str(rate)+'%';

        ############## 原本Q009
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting=''",(yearmonth,app))
        returnData[' (4) CoQ Rate Target'] = str(round(float(cur.fetchone()[0])*100,2))+'%';

        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q001',answerText,Chat_ID) 
                
        response = jsonify(returnData)
        response.headers.add('Access-Control-Allow-Origin', '*') 
        return response

    elif answerNo == "Q002" : # 2. Q002 CoQ / CoQ Rate 是否超標
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')

        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        # CoQ總計佔營收比  sorting = '12'
        ans = '未達標'
        cur.execute("select GROUP_CONCAT(if(sorting = '12', cost , NULL))- GROUP_CONCAT(if(sorting = '', cost*1000000, NULL)) from forboard WHERE sorting in ('12','')  and app=%s and yearmonth=%s",(app,yearmonth));
        if int(cur.fetchone()[0]) <= 0 :
            ans = '達標';
        returnData[' '+str(yearmonth)+' '+app+' CoQ Rate'+'趨勢'] = ans;

        if yearmonth%100 == 1:
            yearmonth2 = yearmonth -100 +11
        else :
            yearmonth2 = yearmonth -1
        cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
        r = cur.fetchone()
        rate = round(float(r[0])/10000,2)
        rate2 = round(float(r[1])/10000,2)

        returnData['CoQ Rate'] = str(rate)+'%';
        ans = '改善'

        if rate < rate2 :
            ans = '改善'
        elif rate > rate2 :       
            ans = '惡化'
            if (rate - rate2)/rate2 <= 0.05 :
                ans = '持平'
        else :
            ans = '持平'
        returnData['較上月'+ans] = str(abs(round(rate-rate2,2)))+'%'; 
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q002',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    elif answerNo == "Q003" : # 3. Q003 CoQ 達標狀況(未達標應用別)
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 

        buList = ['ITI BU','AA BU','MD BU','TV BU']      
        appList = ['TV','SET_TV','AA-BD4','NB','MONITOR','IAVM','MP','CE','TABLET','AUTO-BD5']

        # get Below standard
        belowStandardApp = ''
        if app == '所有應用' :
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target' and app <> %s and app not in ('AII BU','MD BU')) b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000",(yearmonth,app,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+r[0]+","
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]   
            cur.execute("SELECT IFNULL(a4,0)+IFNULL(a5,0)+IFNULL(a6,0) FROM accumulation_new where app=%s and yearmonth=%s",(app,yearmonth))
            accumulationValue = cur.fetchone()[0];

        elif app == 'MD BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('MP','CE','Tablet')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+r[0]+","
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'ITI BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('NB','Monitor','IAVM')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+r[0]+","
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'AA BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('AA-BD4','AUTO-BD5')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+r[0]+","
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'TV BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('TV','SET_TV')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+r[0]+","
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]        
        else :
            belowStandardApp = "'"+app+"'"

        if belowStandardApp == '' : 
            belowStandardApp = '都有達標'

        returnData[str(yearmonth)+' '+app+' 未達標應用別'] = belowStandardApp;
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q003',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q004" : # Q004 CoQ Rate現況
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        #print(app,' ',yearmonth,' ',Chat_ID)
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 

        if yearmonth%100 == 1:
            yearmonth2 = yearmonth -100 +11
        else :
            yearmonth2 = yearmonth -1
        cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
        r = cur.fetchone()
        rate = round(float(r[0])/10000,2)
        rate2 = round(float(r[1])/10000,2)
        #print(rate,' ',rate2)
        #returnData['CoQ Rate'+str(yearmonth)+'現況'] = ' ';
        returnData[' '+str(yearmonth)+' '+app+' CoQ Rate 現況<br>(1)'+str(yearmonth2)] = str(rate2)+'%';
        returnData['(2)'+str(yearmonth)] = str(rate)+'%';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q004',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q005" : # 5. Q005 預防成本是多少?
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='01'",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' 預防成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q005',answerText,Chat_ID)             
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q006" : # 6. Q006 鑑定成本是多少?
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='02'",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' 鑑定成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q006',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q007" : # 7. Q007 外失成本是多少?
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select sum(cost) from forboard where yearmonth=%s and app=%s and sorting in ('04','05','06')",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' 外失成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q007',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q008" : # 8. Q008 內失成本是多少?
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='03'",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' 內失成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q008',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q009" : # 9. Q009 CoQ rate target(目標)是多少
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting=''",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' Target'] = str(round(float(cur.fetchone()[0])*100,2))+'%';

        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q009',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q010" : # 10. Q010 外失售保成本是多少? sorting='05'
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='05'",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' 外失售保成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q010',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q011" : # 11. Q011 AERB內失成本是多少?  sorting='07'
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select IFNULL(cost, 0) from forboard where yearmonth=%s and app=%s and sorting='07'",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' AERB內失成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q011',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q012" : # 12. Q012 外失Rebate成本是多少?  sorting='06'
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 
        cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='06'",(yearmonth,app))
        returnData[str(yearmonth)+' '+app+' 外失Rebate成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q012',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q013" : # 13. Q013 Top3 Model
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 

        buList = ['ITI BU','AA BU','MD BU','TV BU']      
        appList = ['TV','SET_TV','AA-BD4','NB','MONITOR','IAVM','MP','CE','TABLET','AUTO-BD5']

        # get Below standard
        belowStandardApp = ''
        if app == '所有應用' :
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target' and app <> %s and app not in ('AII BU','MD BU')) b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000",(yearmonth,app,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1] 

        elif app == 'MD BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('MP','CE','Tablet')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'ITI BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('NB','Monitor','IAVM')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'AA BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('AA-BD4','AUTO-BD5')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'TV BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('TV','SET_TV')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]        
        else :
            belowStandardApp = "'"+app+"'"

        # get top 3 model
        if (app == 'ITI BU' or app == 'AA BU' or app == 'MD BU' or app == 'TV BU') and belowStandardApp != '' :
            cur.execute("select bu,model,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,customer,cost_category,ROUND(BYMODELCUSTOMERCATE_COST/1000000,2) bymodelcustomercate_cost from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=26 and rank = 1 order by rank,cost limit 5",(yearmonth))
        elif app in appList and belowStandardApp != '' :
            cur.execute("select bu,model,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,customer,cost_category,ROUND(BYMODELCUSTOMERCATE_COST/1000000,2) bymodelcustomercate_cost from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=26 order by rank,cost limit 5",(yearmonth))
        elif belowStandardApp != '':
            cur.execute("select distinct bu,model,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,customer,cost_category,ROUND(BYMODELCUSTOMERCATE_COST/1000000,2) bymodelcustomercate_cost,rank from coq.mc where yearmonth=%s and length(board_title)=26 and bu in ("+belowStandardApp+") order by rank,cost limit 5",(yearmonth))        

        i = 1
        if cur.rowcount > 0 :                        
            for r in cur :            
                returnData['('+str(i)+')'] = r[1]+'外失成本'+str(r[2])+'(M NTD) 佔'+r[0]+'總外失比為'+str(r[3])+'%。該機種以客戶'+str(r[4])+'發生'+str(r[5])+'所佔最高，為'+str(r[6])+'(M NTD)';
                i = i + 1
        returnData[' '+str(yearmonth)+' '+app+' Top3 Model'] = ''
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q013',answerText,Chat_ID) 
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q014" : # 14. Q014 Top3 Customer
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    

        returnData = OrderedDict(); 

        buList = ['ITI BU','AA BU','MD BU','TV BU']      
        appList = ['TV','SET_TV','AA-BD4','NB','MONITOR','IAVM','MP','CE','TABLET','AUTO-BD5']

        # get Below standard
        belowStandardApp = ''
        if app == '所有應用' :
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target' and app <> %s and app not in ('AII BU','MD BU')) b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000",(yearmonth,app,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]   
        elif app == 'MD BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('MP','CE','Tablet')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'ITI BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('NB','Monitor','IAVM')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'AA BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('AA-BD4','AUTO-BD5')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
        elif app == 'TV BU':
            cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('TV','SET_TV')",(yearmonth,yearmonth))            
            if cur.rowcount > 0 :            
                for r in cur :
                    belowStandardApp = belowStandardApp+"'"+r[0]+"',"
                belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]                
        else :
            belowStandardApp = "'"+app+"'"

        # get top 3 customer
        if (app == 'ITI BU' or app == 'AA BU' or app == 'MD BU' or app == 'TV BU') and belowStandardApp != '' :
            cur.execute("select bu,customer,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=30 and rank = 1 order by rank,cost limit 5",(yearmonth )) 
        elif app in appList and belowStandardApp != '' :
            cur.execute("select bu,customer,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=30 order by rank,cost limit 5",(yearmonth ))                 
        elif belowStandardApp != '':    
            cur.execute("select distinct bu,customer,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,`rank` from coq.mc where yearmonth=%s and length(board_title)=30 and bu in ("+belowStandardApp+") order by rank,cost limit 5",(yearmonth))           

        i = 1
        if cur.rowcount > 0 :                        
            for r in cur :                
                returnData['('+str(i)+')'] = r[1]+'外失成本'+str(r[2])+' (M NTD) 佔'+r[0]+'總外失比為'+str(r[3])+'%。'
                i = i + 1

        returnData[' '+str(yearmonth)+' '+app+' Top3 Customer'] = ''
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q014',answerText,Chat_ID)
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q015" : # 15. Q015 預計損失圖
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    
        cur.execute("SELECT round(sum(total)/1000000,2) FROM aerb where yearmonth=%s",(yearmonth))
        AERB = cur.fetchone()[0];
        returnData = OrderedDict(); 
        returnData[str(yearmonth)+' '+app+' AERB預期未來損失'] = str(AERB)+'M (NTD)'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q015',answerText,Chat_ID)
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q016" : # 16. Q016 2018年度CoQ狀況
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        cur.execute("SELECT round(GROUP_CONCAT(if(sorting = '', cost, NULL))*100,2),round(GROUP_CONCAT(if(sorting = '10', cost, NULL))*12/1000000,2),round(GROUP_CONCAT(if(sorting = '13', cost, NULL))/10000,2)  FROM forboard where app=%s and yearmonth=201800 and sorting in ('','10','13')",(app))
        for r in cur :
            returnData['2018 '+app+'年度CoQ狀況']=''
            returnData['Target']=str(r[0])+'%'
            returnData['CoQ']=str(r[1])+'M (NTD)'
            returnData['CoQ Rate']=str(r[2])+'%'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,None,'Q016',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q017" : # 17. Q017 BU月圖    
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        yearmonth = cur.fetchone()[0];    

        returnData = OrderedDict(); 
        returnData['  '+str(yearmonth)+' '+app+'BU月圖']=''
        if app == '所有應用':    
            cur.execute("SELECT IFNULL(a5,0)+IFNULL(a6,0)+IFNULL(a7,0)+IFNULL(a8,0) FROM accumulation where app='所有應用' and yearmonth=%s",(yearmonth))        
        elif app == 'MD BU':
            cur.execute("SELECT IFNULL(a4,0)+IFNULL(a5,0)+IFNULL(a6,0) FROM accumulation where app='MD BU' and yearmonth=%s",(yearmonth))
        elif app == 'TV BU':    
            cur.execute("SELECT IFNULL(a3,0)+IFNULL(a4,0) FROM accumulation where app='TV BU' and yearmonth=%s",(yearmonth))
        elif app == 'ITI BU':
            cur.execute("SELECT IFNULL(a4,0)+IFNULL(a5,0)+IFNULL(a6,0) FROM accumulation where app='ITI BU' and yearmonth=%s",(yearmonth))
        elif app == 'AA BU':
            cur.execute("SELECT IFNULL(a3,0)+IFNULL(a4,0) FROM accumulation where app='AA BU' and yearmonth=%s",(yearmonth))
        else :
            cur.execute("SELECT IFNULL(a8,0)+IFNULL(a9,0)+IFNULL(a10,0)+IFNULL(a11,0) FROM accumulation where app=%s and yearmonth=%s",(app,yearmonth))
        accumulationValue = cur.fetchone()[0];
        returnData['1. 截至'+str(yearmonth)+'累計CoQ目標'] = str(round(accumulationValue/1000000,1))+'M (NTD)'
        cur.execute('SELECT output1,output2,output3,output4,output5,output6 FROM remainCoQ where yearmonth = %s and application = %s',(yearmonth,app))                    
        for r in cur : 
            returnData['2. 截至'+str(yearmonth)+'累計已支出CoQ'] = str(round(r[1]/1000000,1))+'M (NTD)'
            returnData['3. 年底達標預計可支出總CoQ'] = str(round(r[0]/1000000,1))+'M (NTD)'        
            returnData['4. 年剩餘額度'] = str(round(r[2]/1000000,1))+'M (NTD)'
            returnData['5. 年剩餘可控額度'] = str(round(r[4]/1000000,1))+'M (NTD)'
            returnData['6. 年平均CoQ Rate'] = str(round(r[3]*100,2))+'%'        
            returnData['7. 年供應商賠償總額'] = str(round(r[5]/1000000,1))+'M (NTD)'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q017',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q035" : # 35. CoQ是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['CoQ(Cost of Quality)']='指為了提高和保證產品品質而支出的一切費用，以及因產品品質未達到規定的要求而造成的一切損失的總和。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q035',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q036" : # 36. CoQ rate怎麼算
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['CoQ Rate']='Σ(預防+鑑定+內失+外失)成本 / 營收'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q036',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    elif answerNo == "Q037" : # 37. 預防成本是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['學術定義']='用於避免生產出不良品而投入的成本。'
        returnData['資料定義']='DQ/SQ/MQ/QS的十大費用(排除直接人事費用)。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q037',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    elif answerNo == "Q038" : # 38. 鑑定成本是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['學術定義']='檢驗產品是否符合標準的成本。'
        returnData['資料定義']='DQ/SQ/MQ/QS的十大費用(排除直接人事費用)。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q038',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    elif answerNo == "Q039" : # 39. 外失成本是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['學術定義']='產品運交至顧客後，因未能達到品質要求而造成的損失。'
        returnData['資料定義']='MQ/SQ的部份間接人事費用<br>產品於廠內執行報廢/重工/降等所產生的費用。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q039',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    elif answerNo == "Q040" : # 40. 內失成本是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['學術定義']='產品運交至顧客前，因未能達到品質要求而造成的損失。'
        returnData['資料定義']='1.RMA返品的維修、報廢、OBA/SORTING、賠償...等相關費用。<br>2.因品質問題導致營收減少的費用。<br>3.外失-其它：CQ/RMA的十大費用(排除營運費用)。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q040',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    elif answerNo == "Q041" : # 41. 外失售保是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['資料定義']='RMA管理帳的費用。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q041',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    elif answerNo == "Q042" : # 42. 內失AERB是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['資料定義']='廠內有標誌AERB，至降等或報廢的PANEL。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q042',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    elif answerNo == "Q043" : # 43. 外失Rebate是什麼
        Chat_ID = request.args.get('Chat_ID')
        returnData = OrderedDict(); 
        returnData['資料定義']='CQE 客戶要求rebate的費用。'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat('',None,'Q043',answerText,Chat_ID)    
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    elif answerNo == "Q048" : # 48. Q048 EXP 20200131
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    
        cur.execute('SELECT round(100*(IFNULL(GROUP_CONCAT(if(sorting = "01", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "02", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "03", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "04", cost, NULL)),0))/sum(cost),2) FROM forboard WHERE yearmonth = %s and app=%s and sorting in ("01","02","03","04","05","06","07") group by yearmonth',(yearmonth,app))
        EXPRate = cur.fetchone()[0];
        returnData = OrderedDict();
        if yearmonth % 100 == 0 :
            yearmonthTmp = str(yearmonth//100)+'全年'
        else :    
            yearmonthTmp = str(yearmonth)
        returnData[yearmonthTmp+' '+app+' EXP佔比'] = str(EXPRate)+'%'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q048',answerText,Chat_ID)
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    elif answerNo == "Q049" : # 49. Q049 CoPQ 20200131  
        conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
        cur = conn.cursor() 

        app = request.args.get('app');
        yearmonth = int(request.args.get('yearmonth'));
        Chat_ID = request.args.get('Chat_ID')
        cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
        maxYearmonth =  cur.fetchone()[0];    
        if yearmonth == '' or yearmonth > maxYearmonth:
            yearmonth = maxYearmonth    
        cur.execute('SELECT round(100*(IFNULL(GROUP_CONCAT(if(sorting = "05", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "06", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "07", cost, NULL)),0))/sum(cost),2) FROM forboard WHERE yearmonth = %s and app=%s and sorting in ("01","02","03","04","05","06","07") group by yearmonth',(yearmonth,app))
        CoPQRate = cur.fetchone()[0];
        returnData = OrderedDict(); 
        if yearmonth % 100 == 0 :
            yearmonthTmp = str(yearmonth//100)+'全年'
        else :    
            yearmonthTmp = str(yearmonth)    
        returnData[yearmonthTmp+' '+app+' CoPQ佔比'] = str(CoPQRate)+'%'
        answerText = json.dumps(returnData,ensure_ascii=False) 
        updateChat(app,yearmonth,'Q049',answerText,Chat_ID)
        response = jsonify(returnData)    
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
# 1. Q001 CoQ現況
@app.route("/Q001", methods=['GET'])
def Q001():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    print(app,' ',yearmonth,' ',Chat_ID)    
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth = int(cur.fetchone()[0]);
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth
    
    returnData = OrderedDict(); 
    # CoQ總計(含供應商求償)(百萬元)  sorting = '10'
    cur.execute("SELECT cost FROM forboard where app=%s and yearmonth=%s and sorting = '10'",(app,yearmonth));
    returnData[' (1) '+str(yearmonth)+app+ 'CoQ總計(含供應商求償)'] = str(round(cur.fetchone()[0]/1000000, 2))+'M (NTD)';
    
    ############## 原本Q002 
    # CoQ總計佔營收比  sorting = '12'
    ans = '未達標'
    cur.execute("select GROUP_CONCAT(if(sorting = '12', cost , NULL))- GROUP_CONCAT(if(sorting = '', cost*1000000, NULL)) from forboard WHERE sorting in ('12','')  and app=%s and yearmonth=%s",(app,yearmonth));
    if int(cur.fetchone()[0]) <= 0 :
        ans = '達標';
    returnData[' (5) CoQ Rate 趨勢'] = ans;
    
    if yearmonth%100 == 1:
        yearmonth2 = yearmonth -100 +11
    else :
        yearmonth2 = yearmonth -1
    print(yearmonth,' ',yearmonth2)    
    cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
    r = cur.fetchone()
    print(r[0],' ',r[1])
    rate = round(float(r[0])/10000,2)
    rate2 = round( float(r[1]) /10000,2)
    
    #returnData['CoQ Rate'] = str(rate)+'%';
    ans = '改善'
    
    if rate < rate2 :
        ans = '改善'
    elif rate > rate2 :       
        ans = '惡化'
        if (rate - rate2)/rate2 <= 0.05 :
            ans = '持平'
    else :
        ans = '持平'
    returnData[' (6) 較上月'+ans] = str(abs(round(rate-rate2,2)))+'%'; 
    ############## 原本Q004
    if yearmonth%100 == 1:
        yearmonth2 = yearmonth -100 +11
    else :
        yearmonth2 = yearmonth -1
    cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
    r = cur.fetchone()
    rate = round(float(r[0])/10000,2)
    rate2 = round(float(r[1])/10000,2)
    #print(rate,' ',rate2)
    #returnData['CoQ Rate'+str(yearmonth)+'現況'] = ' ';
    returnData[' (2) '+str(yearmonth2)+' CoQ Rate'] = str(rate2)+'%';
    returnData[' (3) '+str(yearmonth)+' CoQ Rate'] = str(rate)+'%';
    
    ############## 原本Q009
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting=''",(yearmonth,app))
    returnData[' (4) CoQ Rate Target'] = str(round(float(cur.fetchone()[0])*100,2))+'%';
    
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q001',answerText,Chat_ID) 
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*') 
    return response

# 2. Q002 CoQ / CoQ Rate 是否超標
@app.route("/Q002", methods=['GET'])
def Q002():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    
    
    returnData = OrderedDict(); 
    # CoQ總計佔營收比  sorting = '12'
    ans = '未達標'
    cur.execute("select GROUP_CONCAT(if(sorting = '12', cost , NULL))- GROUP_CONCAT(if(sorting = '', cost*1000000, NULL)) from forboard WHERE sorting in ('12','')  and app=%s and yearmonth=%s",(app,yearmonth));
    if int(cur.fetchone()[0]) <= 0 :
        ans = '達標';
    returnData[' '+str(yearmonth)+' '+app+' CoQ Rate'+'趨勢'] = ans;
    
    if yearmonth%100 == 1:
        yearmonth2 = yearmonth -100 +11
    else :
        yearmonth2 = yearmonth -1
    cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
    r = cur.fetchone()
    rate = round(float(r[0])/10000,2)
    rate2 = round(float(r[1])/10000,2)
    
    returnData['CoQ Rate'] = str(rate)+'%';
    ans = '改善'
    
    if rate < rate2 :
        ans = '改善'
    elif rate > rate2 :       
        ans = '惡化'
        if (rate - rate2)/rate2 <= 0.05 :
            ans = '持平'
    else :
        ans = '持平'
    returnData['較上月'+ans] = str(abs(round(rate-rate2,2)))+'%'; 
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q002',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 3. Q003 CoQ 達標狀況(未達標應用別)
@app.route("/Q003", methods=['GET'])
def Q003():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    
    buList = ['ITI BU','AA BU','MD BU','TV BU']      
    appList = ['TV','SET_TV','AA-BD4','NB','MONITOR','IAVM','MP','CE','TABLET','AUTO-BD5']
    
    # get Below standard
    belowStandardApp = ''
    if app == '所有應用' :
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target' and app <> %s and app not in ('AII BU','MD BU')) b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000",(yearmonth,app,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+r[0]+","
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]   
        cur.execute("SELECT IFNULL(a4,0)+IFNULL(a5,0)+IFNULL(a6,0) FROM accumulation_new where app=%s and yearmonth=%s",(app,yearmonth))
        accumulationValue = cur.fetchone()[0];

    elif app == 'MD BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('MP','CE','Tablet')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+r[0]+","
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'ITI BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('NB','Monitor','IAVM')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+r[0]+","
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'AA BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('AA-BD4','AUTO-BD5')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+r[0]+","
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'TV BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('TV','SET_TV')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+r[0]+","
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]        
    else :
        belowStandardApp = "'"+app+"'"
    
    if belowStandardApp == '' : 
        belowStandardApp = '都有達標'
    
    returnData[str(yearmonth)+' '+app+' 未達標應用別'] = belowStandardApp;
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q003',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
# 4. Q004 CoQ Rate現況
@app.route("/Q004", methods=['GET'])
def Q004():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    #print(app,' ',yearmonth,' ',Chat_ID)
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 

    if yearmonth%100 == 1:
        yearmonth2 = yearmonth -100 +11
    else :
        yearmonth2 = yearmonth -1
    cur.execute("select GROUP_CONCAT(if(yearmonth = %s, cost, NULL)),GROUP_CONCAT(if(yearmonth = %s, cost, NULL)) from forboard WHERE sorting ='12' and app=%s and yearmonth in (%s,%s)",(yearmonth,yearmonth2,app,yearmonth2,yearmonth));
    r = cur.fetchone()
    rate = round(float(r[0])/10000,2)
    rate2 = round(float(r[1])/10000,2)
    #print(rate,' ',rate2)
    #returnData['CoQ Rate'+str(yearmonth)+'現況'] = ' ';
    returnData[' '+str(yearmonth)+' '+app+' CoQ Rate 現況<br>(1)'+str(yearmonth2)] = str(rate2)+'%';
    returnData['(2)'+str(yearmonth)] = str(rate)+'%';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q004',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 5. Q005 預防成本是多少?
@app.route("/Q005", methods=['GET'])
def Q005():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='01'",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' 預防成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q005',answerText,Chat_ID)             
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 6. Q006 鑑定成本是多少?
@app.route("/Q006", methods=['GET'])
def Q006():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='02'",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' 鑑定成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q006',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 7. Q007 外失成本是多少?
@app.route("/Q007", methods=['GET'])
def Q007():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select sum(cost) from forboard where yearmonth=%s and app=%s and sorting in ('04','05','06')",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' 外失成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q007',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 8. Q008 內失成本是多少?
@app.route("/Q008", methods=['GET'])
def Q008():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='03'",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' 內失成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q008',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 9. Q009 CoQ rate target(目標)是多少
@app.route("/Q009", methods=['GET'])
def Q009():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting=''",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' Target'] = str(round(float(cur.fetchone()[0])*100,2))+'%';
     
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q009',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# . Q010 外失售保成本是多少? sorting='05'
@app.route("/Q010", methods=['GET'])
def Q010():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='05'",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' 外失售保成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q010',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# . Q011 AERB內失成本是多少?  sorting='07'
@app.route("/Q011", methods=['GET'])
def Q011():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq')  
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select IFNULL(cost, 0) from forboard where yearmonth=%s and app=%s and sorting='07'",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' AERB內失成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q011',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# . Q012 外失Rebate成本是多少?  sorting='06'
@app.route("/Q012", methods=['GET'])
def Q012():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    cur.execute("select cost from forboard where yearmonth=%s and app=%s and sorting='06'",(yearmonth,app))
    returnData[str(yearmonth)+' '+app+' 外失Rebate成本'] = str(round(float(cur.fetchone()[0])/1000000,3))+'M (NTD)';
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q012',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 13. Q013 Top3 Model
@app.route("/Q013", methods=['GET'])
def Q013():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    
    buList = ['ITI BU','AA BU','MD BU','TV BU']      
    appList = ['TV','SET_TV','AA-BD4','NB','MONITOR','IAVM','MP','CE','TABLET','AUTO-BD5']
    
    # get Below standard
    belowStandardApp = ''
    if app == '所有應用' :
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target' and app <> %s and app not in ('AII BU','MD BU')) b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000",(yearmonth,app,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1] 

    elif app == 'MD BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('MP','CE','Tablet')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'ITI BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('NB','Monitor','IAVM')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'AA BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('AA-BD4','AUTO-BD5')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'TV BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('TV','SET_TV')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]        
    else :
        belowStandardApp = "'"+app+"'"
        
    # get top 3 model
    if (app == 'ITI BU' or app == 'AA BU' or app == 'MD BU' or app == 'TV BU') and belowStandardApp != '' :
        cur.execute("select bu,model,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,customer,cost_category,ROUND(BYMODELCUSTOMERCATE_COST/1000000,2) bymodelcustomercate_cost from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=26 and rank = 1 order by rank,cost limit 5",(yearmonth))
    elif app in appList and belowStandardApp != '' :
        cur.execute("select bu,model,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,customer,cost_category,ROUND(BYMODELCUSTOMERCATE_COST/1000000,2) bymodelcustomercate_cost from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=26 order by rank,cost limit 5",(yearmonth))
    elif belowStandardApp != '':
        cur.execute("select distinct bu,model,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,customer,cost_category,ROUND(BYMODELCUSTOMERCATE_COST/1000000,2) bymodelcustomercate_cost,rank from coq.mc where yearmonth=%s and length(board_title)=26 and bu in ("+belowStandardApp+") order by rank,cost limit 5",(yearmonth))        
    
    i = 1
    if cur.rowcount > 0 :                        
        for r in cur :            
            returnData['('+str(i)+')'] = r[1]+'外失成本'+str(r[2])+'(M NTD) 佔'+r[0]+'總外失比為'+str(r[3])+'%。該機種以客戶'+str(r[4])+'發生'+str(r[5])+'所佔最高，為'+str(r[6])+'(M NTD)';
            i = i + 1
    returnData[' '+str(yearmonth)+' '+app+' Top3 Model'] = ''
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q013',answerText,Chat_ID) 
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 14. Q014 Top3 Customer
@app.route("/Q014", methods=['GET'])
def Q014():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    

    returnData = OrderedDict(); 
    
    buList = ['ITI BU','AA BU','MD BU','TV BU']      
    appList = ['TV','SET_TV','AA-BD4','NB','MONITOR','IAVM','MP','CE','TABLET','AUTO-BD5']
    
    # get Below standard
    belowStandardApp = ''
    if app == '所有應用' :
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target' and app <> %s and app not in ('AII BU','MD BU')) b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000",(yearmonth,app,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]   
    elif app == 'MD BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('MP','CE','Tablet')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'ITI BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('NB','Monitor','IAVM')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'AA BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('AA-BD4','AUTO-BD5')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]
    elif app == 'TV BU':
        cur.execute("SELECT a.app FROM forboard a join (select app ,cost from forboard where yearmonth = %s and coq_type = 'Target') b on a.app = b.app WHERE a.yearmonth = %s and a.sorting=12 and a.cost > b.cost*1000000 and a.app in ('TV','SET_TV')",(yearmonth,yearmonth))            
        if cur.rowcount > 0 :            
            for r in cur :
                belowStandardApp = belowStandardApp+"'"+r[0]+"',"
            belowStandardApp = belowStandardApp[0:len(belowStandardApp)-1]                
    else :
        belowStandardApp = "'"+app+"'"
    
    # get top 3 customer
    if (app == 'ITI BU' or app == 'AA BU' or app == 'MD BU' or app == 'TV BU') and belowStandardApp != '' :
        cur.execute("select bu,customer,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=30 and rank = 1 order by rank,cost limit 5",(yearmonth )) 
    elif app in appList and belowStandardApp != '' :
        cur.execute("select bu,customer,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate from coq.mc where yearmonth=%s and bu in ("+belowStandardApp+") and length(board_title)=30 order by rank,cost limit 5",(yearmonth ))                 
    elif belowStandardApp != '':    
        cur.execute("select distinct bu,customer,ROUND(COST/1000000,2) cost,ROUND(rate,1) rate,`rank` from coq.mc where yearmonth=%s and length(board_title)=30 and bu in ("+belowStandardApp+") order by rank,cost limit 5",(yearmonth))           
    
    i = 1
    if cur.rowcount > 0 :                        
        for r in cur :                
            returnData['('+str(i)+')'] = r[1]+'外失成本'+str(r[2])+' (M NTD) 佔'+r[0]+'總外失比為'+str(r[3])+'%。'
            i = i + 1
    
    returnData[' '+str(yearmonth)+' '+app+' Top3 Customer'] = ''
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q014',answerText,Chat_ID)
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 15. Q015 預計損失圖
@app.route("/Q015", methods=['GET'])
def Q015():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    
    cur.execute("SELECT round(sum(total)/1000000,2) FROM aerb where yearmonth=%s",(yearmonth))
    AERB = cur.fetchone()[0];
    returnData = OrderedDict(); 
    returnData[str(yearmonth)+' '+app+' AERB預期未來損失'] = str(AERB)+'M (NTD)'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q015',answerText,Chat_ID)
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
# 16. Q016 2018年度CoQ狀況
@app.route("/Q016", methods=['GET'])
def Q016():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    cur.execute("SELECT round(GROUP_CONCAT(if(sorting = '', cost, NULL))*100,2),round(GROUP_CONCAT(if(sorting = '10', cost, NULL))*12/1000000,2),round(GROUP_CONCAT(if(sorting = '13', cost, NULL))/10000,2)  FROM forboard where app=%s and yearmonth=201800 and sorting in ('','10','13')",(app))
    for r in cur :
        returnData['2018 '+app+'年度CoQ狀況']=''
        returnData['Target']=str(r[0])+'%'
        returnData['CoQ']=str(r[1])+'M (NTD)'
        returnData['CoQ Rate']=str(r[2])+'%'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,None,'Q016',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
# 17. Q017 BU月圖
@app.route("/Q017", methods=['GET'])
def Q017():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    yearmonth = cur.fetchone()[0];    
    
    returnData = OrderedDict(); 
    returnData['  '+str(yearmonth)+' '+app+'BU月圖']=''
    if app == '所有應用':    
        cur.execute("SELECT IFNULL(a5,0)+IFNULL(a6,0)+IFNULL(a7,0)+IFNULL(a8,0) FROM accumulation where app='所有應用' and yearmonth=%s",(yearmonth))        
    elif app == 'MD BU':
        cur.execute("SELECT IFNULL(a4,0)+IFNULL(a5,0)+IFNULL(a6,0) FROM accumulation where app='MD BU' and yearmonth=%s",(yearmonth))
    elif app == 'TV BU':    
        cur.execute("SELECT IFNULL(a3,0)+IFNULL(a4,0) FROM accumulation where app='TV BU' and yearmonth=%s",(yearmonth))
    elif app == 'ITI BU':
        cur.execute("SELECT IFNULL(a4,0)+IFNULL(a5,0)+IFNULL(a6,0) FROM accumulation where app='ITI BU' and yearmonth=%s",(yearmonth))
    elif app == 'AA BU':
        cur.execute("SELECT IFNULL(a3,0)+IFNULL(a4,0) FROM accumulation where app='AA BU' and yearmonth=%s",(yearmonth))
    else :
        cur.execute("SELECT IFNULL(a8,0)+IFNULL(a9,0)+IFNULL(a10,0)+IFNULL(a11,0) FROM accumulation where app=%s and yearmonth=%s",(app,yearmonth))
    accumulationValue = cur.fetchone()[0];
    returnData['1. 截至'+str(yearmonth)+'累計CoQ目標'] = str(round(accumulationValue/1000000,1))+'M (NTD)'
    cur.execute('SELECT output1,output2,output3,output4,output5,output6 FROM remainCoQ where yearmonth = %s and application = %s',(yearmonth,app))                    
    for r in cur : 
        returnData['2. 截至'+str(yearmonth)+'累計已支出CoQ'] = str(round(r[1]/1000000,1))+'M (NTD)'
        returnData['3. 年底達標預計可支出總CoQ'] = str(round(r[0]/1000000,1))+'M (NTD)'        
        returnData['4. 年剩餘額度'] = str(round(r[2]/1000000,1))+'M (NTD)'
        returnData['5. 年剩餘可控額度'] = str(round(r[4]/1000000,1))+'M (NTD)'
        returnData['6. 年平均CoQ Rate'] = str(round(r[3]*100,2))+'%'        
        returnData['7. 年供應商賠償總額'] = str(round(r[5]/1000000,1))+'M (NTD)'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q017',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response      

# 35. CoQ是什麼
@app.route("/Q035", methods=['GET'])
def Q035():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['CoQ(Cost of Quality)']='指為了提高和保證產品品質而支出的一切費用，以及因產品品質未達到規定的要求而造成的一切損失的總和。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q035',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 36. CoQ rate怎麼算
@app.route("/Q036", methods=['GET'])
def Q036():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['CoQ Rate']='Σ(預防+鑑定+內失+外失)成本 / 營收'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q036',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 37. 預防成本是什麼
@app.route("/Q037", methods=['GET'])
def Q037():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['學術定義']='用於避免生產出不良品而投入的成本。'
    returnData['資料定義']='DQ/SQ/MQ/QS的十大費用(排除直接人事費用)。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q037',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 38. 鑑定成本是什麼
@app.route("/Q038", methods=['GET'])
def Q038():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['學術定義']='檢驗產品是否符合標準的成本。'
    returnData['資料定義']='DQ/SQ/MQ/QS的十大費用(排除直接人事費用)。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q038',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 39. 外失成本是什麼
@app.route("/Q039", methods=['GET'])
def Q039():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['學術定義']='產品運交至顧客後，因未能達到品質要求而造成的損失。'
    returnData['資料定義']='MQ/SQ的部份間接人事費用<br>產品於廠內執行報廢/重工/降等所產生的費用。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q039',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 40. 內失成本是什麼
@app.route("/Q040", methods=['GET'])
def Q040():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['學術定義']='產品運交至顧客前，因未能達到品質要求而造成的損失。'
    returnData['資料定義']='1.RMA返品的維修、報廢、OBA/SORTING、賠償...等相關費用。<br>2.因品質問題導致營收減少的費用。<br>3.外失-其它：CQ/RMA的十大費用(排除營運費用)。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q040',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 41. 外失售保是什麼
@app.route("/Q041", methods=['GET'])
def Q041():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['資料定義']='RMA管理帳的費用。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q041',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 42. 內失AERB是什麼
@app.route("/Q042", methods=['GET'])
def Q042():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['資料定義']='廠內有標誌AERB，至降等或報廢的PANEL。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q042',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 43. 外失Rebate是什麼
@app.route("/Q043", methods=['GET'])
def Q043():   
    Chat_ID = request.args.get('Chat_ID')
    returnData = OrderedDict(); 
    returnData['資料定義']='CQE 客戶要求rebate的費用。'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat('',None,'Q043',answerText,Chat_ID)    
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 48. Q048 EXP 20200131
@app.route("/Q048", methods=['GET'])
def Q048():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    
    cur.execute('SELECT round(100*(IFNULL(GROUP_CONCAT(if(sorting = "01", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "02", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "03", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "04", cost, NULL)),0))/sum(cost),2) FROM forboard WHERE yearmonth = %s and app=%s and sorting in ("01","02","03","04","05","06","07") group by yearmonth',(yearmonth,app))
    EXPRate = cur.fetchone()[0];
    returnData = OrderedDict();
    if yearmonth % 100 == 0 :
        yearmonthTmp = str(yearmonth//100)+'全年'
    else :    
        yearmonthTmp = str(yearmonth)
    returnData[yearmonthTmp+' '+app+' EXP佔比'] = str(EXPRate)+'%'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q048',answerText,Chat_ID)
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 49. Q049 CoPQ 20200131
@app.route("/Q049", methods=['GET'])
def Q049():
    conn = pymysql.connect(host = host,port = port,user = 'root',passwd = "1234",db = 'coq') 
    cur = conn.cursor() 

    app = request.args.get('app');
    yearmonth = int(request.args.get('yearmonth'));
    Chat_ID = request.args.get('Chat_ID')
    cur.execute("select max(yearmonth) from (SELECT yearmonth,count(1) c FROM forboard group by yearmonth ORDER by yearmonth) a where c>300")
    maxYearmonth =  cur.fetchone()[0];    
    if yearmonth == '' or yearmonth > maxYearmonth:
        yearmonth = maxYearmonth    
    cur.execute('SELECT round(100*(IFNULL(GROUP_CONCAT(if(sorting = "05", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "06", cost, NULL)),0)+IFNULL(GROUP_CONCAT(if(sorting = "07", cost, NULL)),0))/sum(cost),2) FROM forboard WHERE yearmonth = %s and app=%s and sorting in ("01","02","03","04","05","06","07") group by yearmonth',(yearmonth,app))
    CoPQRate = cur.fetchone()[0];
    returnData = OrderedDict(); 
    if yearmonth % 100 == 0 :
        yearmonthTmp = str(yearmonth//100)+'全年'
    else :    
        yearmonthTmp = str(yearmonth)    
    returnData[yearmonthTmp+' '+app+' CoPQ佔比'] = str(CoPQRate)+'%'
    answerText = json.dumps(returnData,ensure_ascii=False) 
    updateChat(app,yearmonth,'Q049',answerText,Chat_ID)
    response = jsonify(returnData)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':    
    localDB = False #False #True  
    if localDB == True :
        host = '127.0.0.1'
        port=3306
    else :
        #conn = pymysql.connect( host = '10.55.52.98' ,port=33060 ,  user = 'root' ,  passwd = "1234" ,  db = 'coq' )
        #host = '10.56.211.124'
        host = '10.55.52.98'
        port=33060 
    #run_simple('10.55.8.201', 84, app) 
    app.run(host='0.0.0.0', port=83)
    #run_simple('10.56.244.8', 84, app) 
