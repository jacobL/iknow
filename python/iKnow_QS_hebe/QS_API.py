# -*- coding: utf-8 -*-
 
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
"""
Created on Thu Apr 22 15:08:05 2021

@author: jenny
"""


from flask_cors import CORS
from flask import Flask,jsonify,request
import requests
import sys
sys.path.append(r"/usr/src/iKnow_QS_new")
import datetime
import json
from QS_model_20210428 import *
from flask import Flask, Response, request
from flask import jsonify
from flask import  request
import requests
import pandas
import os
import pymysql
import math

QS_iKnow_model = QS_model()
app = Flask(__name__)
CORS(app)

#直接回答 (後端回應前端)
def Stand_Answer_Json(Q_Json,answerType,Q_AnsNO,Stand_Q_dict,ErrorCode=0,errorMessage=""):
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if ErrorCode==0:
        if answerType=="No_Answer" :
             Answer_Json= {
                    "Chat_ID": Q_Json["Chat_ID"],
                    "Session_ID": Q_Json["Session_ID"],
                    "user_ID": Q_Json["user_ID"],
                    "user_name": Q_Json["user_name"],
                    "Code": ErrorCode,
                    "errorMessage": errorMessage,
                    "answerType": answerType,
                    "user_question": Q_Json["user_question"],
                    "data":
                        [{
                            "answerNo": Q_AnsNO,
                            "answer": '資料庫未涵蓋後續新增，您若知道正確答案，請於建議欄填入喔，謝謝您的使用~',
                            "question": '',
                            "SOP": '',
                            "SOPNO": '',
                            "URL": ''
                        }],
                    "createDate": now_time,
                    "suggest": []
                    }          
        else :
            x = Stand_Q_dict.loc[Stand_Q_dict["Answer_NO"]==Q_AnsNO]['URL'].tolist()[0]
            Answer_Json= {
                    "Chat_ID": Q_Json["Chat_ID"],  #問題ID
                    "Session_ID": Q_Json["Session_ID"],  #同個Session ID表示同一次登入所問問題
                    "user_ID": Q_Json["user_ID"], #使用者工號
                    "user_name": Q_Json["user_name"], #使用者姓名
                    "Code": ErrorCode, #0正常 1錯誤
                    "errorMessage": errorMessage, #錯誤訊息
                    "answerType": answerType, #standard直接回答Lead引導回答
                    "user_question": Q_Json["user_question"], #使用者問題
                    "data":
                        [{
                            "answerNo": Q_AnsNO,   #對應答案編號
                            "answer": Stand_Q_dict.loc[Stand_Q_dict["Answer_NO"]==Q_AnsNO]['Answer'].tolist()[0], #對應答案
                            "question": Stand_Q_dict.loc[Stand_Q_dict["Answer_NO"]==Q_AnsNO]['Question'].tolist()[0], #對應標準問題
                            "SOP": "", #對應SOP章節
                            "SOPNO": "",  #對應SOP編號
                            "URL": "" if x != x else x #對應網址聯結
                        }],
                    "createDate": now_time
                    }                    

    else :
        Answer_Json= {
                "Chat_ID": Q_Json["Chat_ID"],
                "Session_ID": Q_Json["Session_ID"],
                "user_ID": Q_Json["user_ID"],
                "user_name": Q_Json["user_name"],
                "Code": ErrorCode,
                "errorMessage": Q_AnsNO,
                "answerType": answerType,
                "user_question": Q_Json["user_question"],
                "data":
                    [{
                        "answerNo": "",
                        "answer": "",
                        "question": "",
                        "SOP": "",
                        "SOPNO": "",
                        "URL": ""
                    }],
                "createDate": now_time,
                "suggest": []
                }
    return Answer_Json

#引導回答,推三個可能問題
def Lead_Answer_Json(Q_Json,Q_AnsNO_list,Stand_QS_dict):
    now_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Answer_Json= {
                "Chat_ID": Q_Json["Chat_ID"],
                "Session_ID": Q_Json["Session_ID"],
                "user_ID": Q_Json["user_ID"],
                "user_name": Q_Json["user_name"],
                "Code": 0,
                "errorMessage": "",
                "answerType": 'lead',
                "user_question": Q_Json["user_question"],
                }
   
    data=[]
    for A_NO in Q_AnsNO_list:
        x = Stand_QS_dict.loc[Stand_QS_dict["Answer_NO"]==A_NO]['URL'].tolist()[0]
        data_dict={"answerNo": A_NO,
                   "answer": Stand_QS_dict.loc[Stand_QS_dict["Answer_NO"]==A_NO]['Answer'].tolist()[0],
                   "question": Stand_QS_dict.loc[Stand_QS_dict["Answer_NO"]==A_NO]['Question'].tolist()[0],
                   "SOP": '',
                   "SOPNO": '',
                   'URL': "" if x != x else x
                   }
        data.append(data_dict)
       
    Answer_Json["data"]=data
    Answer_Json["createDate"]=now_time
    
    return Answer_Json

#紀錄使用者紀錄
def QS_Insert_log(Answer_Json) :
    Chat_ID=Answer_Json['Chat_ID']
    conn  =  pymysql.connect ( host = '10.55.23.168' ,port=33060 ,  user = 'root' ,  passwd = "1234" , db='qs')  
    select_sql="SELECT * FROM qs.qs_chat_log_new Where chat_id='" + Chat_ID + "'"
    
    cur  =  conn.cursor ()
    cur.execute(select_sql)
    e=cur.fetchone()
    if e is None:
        if Answer_Json['answerType']=="Have_Answer" :
            log_sql="INSERT INTO qs.qs_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
            ,answerNo,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "', \
            '" + Answer_Json['user_ID'] + "','" + Answer_Json['user_name'] + "',\
            '" + Answer_Json['createDate'] + "','" + Answer_Json['user_question'] + "', \
            '" + Answer_Json['answerType'] + "','" + Answer_Json['data'][0]['answerNo'] + "',2)"
        elif Answer_Json['answerType']=="No_Answer" :
            log_sql="INSERT INTO qs.qs_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
            ,answerNo,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "', \
            '" + Answer_Json['user_ID'] + "','" + Answer_Json['user_name'] + "',\
            '" + Answer_Json['createDate'] + "','" + Answer_Json['user_question'] + "', \
            '" + Answer_Json['answerType'] + "','" + Answer_Json['data'][0]['answerNo'] + "',0)"
            
        else :
            if len(Answer_Json['data'])==2:
                log_sql="INSERT INTO qs.qs_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
                ,lead1,lead2,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "',\
                '" +Answer_Json['user_ID'] + "',\
                '" + Answer_Json['user_name'] + "','" + Answer_Json['createDate'] + "',\
                '" + Answer_Json['user_question'] + "','" + Answer_Json['answerType'] + "',\
                '" + Answer_Json['data'][0]['answerNo'] + "','" + Answer_Json['data'][1]['answerNo'] + "',2)"
            else :
                log_sql="INSERT INTO qs.qs_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
                ,lead1,lead2,lead3,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "',\
                '" +Answer_Json['user_ID'] + "',\
                '" + Answer_Json['user_name'] + "','" + Answer_Json['createDate'] + "',\
                '" + Answer_Json['user_question'] + "','" + Answer_Json['answerType'] + "',\
                '" + Answer_Json['data'][0]['answerNo'] + "','" + Answer_Json['data'][1]['answerNo']  + "',\
                '" + Answer_Json['data'][2]['answerNo'] + "',2)"
    else :
        log_sql="UPDATE qs.qs_chat_log_new SET answerNO='" + Answer_Json['data'][0]['answerNo'] + "' \
        Where chat_id = '" + Chat_ID + "'"
    
    print(log_sql)
    cur.execute(log_sql)    
    cur.execute("COMMIT")
    cur.close()
	
def Iknow_QS(QS_Json,Stand_QS_dict) :
    queryNew , query_corpus = QS_iKnow_model.Query_corpus(QS_Json["user_question"])
    pred_category = QS_iKnow_model.GetQuerySystemAnswer(query_corpus)
    ErrorCode , answerType , QS_AnsNO = QS_iKnow_model.GetQuerySimilarityAnswer_monpa(pred_category,queryNew)
    if answerType == 'No_Answer':
        Answer_Json = Lead_Answer_Json(QS_Json,QS_AnsNO,Stand_QS_dict)      
    else:
        Answer_Json = Stand_Answer_Json(QS_Json,answerType,QS_AnsNO,Stand_QS_dict,ErrorCode)
    return Answer_Json 

def QS_feedback(QS_FB) :
    Chat_ID=str(QS_FB['Chat_ID'])
    feedback=str(QS_FB['feedback'])
    suggest=str(QS_FB['user_suggest'])
    update_sql="UPDATE qs.qs_chat_log_new SET feedback='" + feedback + "',suggest='" + suggest + "' \
        Where chat_id = '" + Chat_ID + "'"
    conn  =  pymysql.connect ( host = '10.55.23.168' ,port=33060 ,  user = 'root' ,  passwd = "1234" , db='qs') 
    cur  =  conn.cursor ()
    cur.execute(update_sql)
    s=cur.execute("COMMIT")
    cur.close()
    conn.close()
    return s
#前端呼叫後端    
@app.route('/I_Know_QS', methods = ['GET','POST'])
def I_Know_QS():
    try:
        QS_Json=json.loads(request.get_data(),encoding='utf8')  #USER回傳的問題題目
        Answer_Json=Iknow_QS(QS_Json,QS_iKnow_model.Stand_QS_dict)
        s=QS_Insert_log(Answer_Json)
        response = Response(json.dumps(Answer_Json).encode('utf8')
                            , status=200, mimetype="application/json")
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        now_time=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        f = open('./error/'+ now_time +'_Predict.txt','w')
        f.write(str(e))
        Answer_Json={}
        Answer_Json['error']=str(e)
        response = Response(json.dumps(Answer_Json).encode('utf8')
                            , status=400, mimetype="application/json")
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        response.headers.add('Access-Control-Allow-Origin', '*')  
        return response
    
@app.route('/I_Know_QS_FB', methods = ['POST'])
def I_Know_QS_FB():
    QS_FB=json.loads(request.get_data(),encoding='utf8')
    fb=str(QS_feedback(QS_FB))
    return fb    
    
if __name__ == '__main__':          
    #Define the IP and port used in the service URL
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=92)
