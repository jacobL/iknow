# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:51:26 2020

@author: sh.tseng
"""
import os
os.chdir("/usr/src/IKnow_QMD")

import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from apscheduler.schedulers.background import BackgroundScheduler
import i_know_qmd_buildmodel
sched = BackgroundScheduler(daemon=True)
@sched.scheduled_job('interval', id='my_job_id',start_date='2020-2-3 01:59:00',days=1)
def timed_job_one():
    print('build model')
    i_know_qmd_buildmodel.main()
sched.start()

 
import pandas as pd
import numpy as np
from werkzeug.serving import run_simple
from flask import Flask, Response, request, render_template, url_for,flash, make_response
from flask import jsonify
from flask import url_for, request, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask import send_file, send_from_directory, safe_join, abort
import requests
import json 
import pymysql
from collections import OrderedDict 
from flask_cors import CORS, cross_origin
app = Flask(__name__) 
CORS(app)
     
import re
import jieba
import pickle 
from sklearn.feature_extraction.text import CountVectorizer
import copy
import math
from scipy import stats
import datetime 
from bert_serving.client import BertClient
 
from i_know_qmd_buildmodel import jiebacut_word_num
from i_know_qmd_buildmodel import jiebacut_WF_word
import opencc

#新問題的詞彙可能不存在於舊詞庫,於是需重建詞頻矩陣
def Add_WF_Array(user_Q_WF,feature_name,All_Q_BOW):
    cut_word=user_Q_WF.split(' ')
    New_feature=[]
    for word in cut_word:
        if word not in feature_name:
            New_feature.append(word)
    
    New_feature_List=copy.deepcopy(feature_name)
    New_feature_List.extend(New_feature)
    Zero_A=np.zeros((len(New_feature),All_Q_BOW.shape[0]))
    All_Q_BOW_Add= np.c_[All_Q_BOW,Zero_A.T]
    
    return New_feature_List,All_Q_BOW_Add
#計算與問題庫之餘弦距離 by Word Freq
def Cal_UserQ_CosSim(UserQ_V,All_Q_Vector,TopN):
    if TopN>len(All_Q_Vector):
        TopN=len(All_Q_Vector)
    Cos_D=np.zeros(len(All_Q_Vector))
    for i in range(0,len(All_Q_Vector)):
        cos_u=np.dot(UserQ_V, All_Q_Vector[i]) 
        cos_dl=math.sqrt(np.dot(UserQ_V, UserQ_V)) 
        cos_du=math.sqrt(np.dot(All_Q_Vector[i], All_Q_Vector[i]))
        if cos_dl==0 or cos_du==0:
            Cos_D[i]=0
        else :
            Cos_D[i]=round(cos_u/(cos_dl*cos_du),5)
 
    TopArray_Value=np.sort(-Cos_D)
    TopArray_Index=np.argsort(-Cos_D)
    ValueN=TopArray_Value[0:TopN]
    IndexN=TopArray_Index[0:TopN]
    return IndexN,ValueN
#取得關聯規則對應題目
def qmd_associstion(conn,answerNo):
    #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
    
    cur  =  conn.cursor ()
    sql_dateno="Select distinct DateNo from qs.qmd_association_rule Order By DateNo desc"
    cur.execute(sql_dateno)
    result = cur.fetchone()
    dateno=str(result[0])
    sql="Select Question_Y from qs.qmd_association_rule Where Question_X='" + answerNo + "' \
    AND DateNO='" + dateno + "' Order By Confidence,Lift desc LIMIT 3" 
    cur.execute(sql)
    suggest_items = [x for x in cur]
    #print(suggest_items)
    cur.close
    
    return suggest_items  
#直接回答
def Stand_Answer_Json(Q_Json,answerType,Q_AnsNO,Stand_Q_dict,conn,ErrorCode=0,errorMessage=""):
    now_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                            "question": 'nan',
                            "SOP": 'nan',
                            "SOPNO": 'nan',
                            "URL": 'nan'
                        }],
                    "createDate": now_time,
                    "suggest": []
                    }
            
        else :
            
            #print(Stand_Q_dict[Q_AnsNO])
            Answer_Json= {
                    "Chat_ID": Q_Json["Chat_ID"],  #問題ID
                    "Session_ID": Q_Json["Session_ID"],  #同個Session ID表示同一次登入所問問題
                    "user_ID": Q_Json["user_ID"], #使用者工號
                    "user_name": Q_Json["user_name"], #使用者姓名
                    "Code": ErrorCode, #0正常1錯誤
                    "errorMessage": errorMessage, #錯誤訊息
                    "answerType": answerType, #standard直接回答Lead引導回答
                    "user_question": Q_Json["user_question"], #使用者問題
                    "data":
                        [{
                            "answerNo": Q_AnsNO,   #對應答案編號
                            "answer": Stand_Q_dict[Q_AnsNO]['Answer'], #對應答案
                            "question": Stand_Q_dict[Q_AnsNO]['Question'], #對應標準問題
                            "SOP": Stand_Q_dict[Q_AnsNO]['SOP'], #對應SOP章節
                            "SOPNO": Stand_Q_dict[Q_AnsNO]['SOP_No'],  #對應SOP編號
                            "URL": Stand_Q_dict[Q_AnsNO]['URL'] #對應網址聯結
                        }],
                    "createDate": now_time
                    }
            #取得關聯題目
            """
            suggest_items=qmd_associstion(conn,Q_AnsNO)
            suggest=[]
            
            for item in suggest_items:
                suggest_dict={"answerNo": item[0],"question": Stand_Q_dict[item[0]]['Question']}
                #print(Stand_Q_dict[item[0]])
                suggest.append(suggest_dict)
                
            Answer_Json["suggest"]=suggest
            """
    else :
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
def Lead_Answer_Json(Q_Json,Q_AnsNO_list,Stand_Q_dict):
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
        data_dict={"answerNo": A_NO,"answer": Stand_Q_dict[A_NO]['Answer'],
                   "question": Stand_Q_dict[A_NO]['Question'],
                   "SOP": Stand_Q_dict[A_NO]['SOP'],
                   "SOPNO": Stand_Q_dict[A_NO]['SOP_No'],
                   "URL": Stand_Q_dict[A_NO]['URL']}
        data.append(data_dict)
       
    Answer_Json["data"]=data
    Answer_Json["createDate"]=now_time
    
    return Answer_Json
#紀錄使用者紀錄
def QMD_Insert_log(conn,Answer_Json) :
    Chat_ID=Answer_Json['Chat_ID']
    select_sql="SELECT * FROM qs.qmd_chat_log_new Where chat_id='" + Chat_ID + "'"
    #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
    cur  =  conn.cursor ()
    cur.execute(select_sql)
    e=cur.fetchone()
    
    if e is None:
        if Answer_Json['answerType']=="standard" :
            log_sql="INSERT INTO qs.qmd_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
            ,answerNo,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "', \
            '" + Answer_Json['user_ID'] + "','" + Answer_Json['user_name'] + "',\
            '" + Answer_Json['createDate'] + "','" + Answer_Json['user_question'] + "', \
            '" + Answer_Json['answerType'] + "','" + Answer_Json['data'][0]['answerNo'] + "',2)"
        elif Answer_Json['answerType']=="No_Answer" :
            log_sql="INSERT INTO qs.qmd_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
            ,answerNo,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "', \
            '" + Answer_Json['user_ID'] + "','" + Answer_Json['user_name'] + "',\
            '" + Answer_Json['createDate'] + "','" + Answer_Json['user_question'] + "', \
            '" + Answer_Json['answerType'] + "','" + Answer_Json['data'][0]['answerNo'] + "',0)"
            
        else :
            if len(Answer_Json['data'])==2:
                log_sql="INSERT INTO qs.qmd_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
                ,lead1,lead2,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "',\
                '" +Answer_Json['user_ID'] + "',\
                '" + Answer_Json['user_name'] + "','" + Answer_Json['createDate'] + "',\
                '" + Answer_Json['user_question'] + "','" + Answer_Json['answerType'] + "',\
                '" + Answer_Json['data'][0]['answerNo'] + "','" + Answer_Json['data'][1]['answerNo'] + "',2)"
            else :
                log_sql="INSERT INTO qs.qmd_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
                ,lead1,lead2,lead3,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "',\
                '" +Answer_Json['user_ID'] + "',\
                '" + Answer_Json['user_name'] + "','" + Answer_Json['createDate'] + "',\
                '" + Answer_Json['user_question'] + "','" + Answer_Json['answerType'] + "',\
                '" + Answer_Json['data'][0]['answerNo'] + "','" + Answer_Json['data'][1]['answerNo']  + "',\
                '" + Answer_Json['data'][2]['answerNo'] + "',2)"
                                
        
        
    else :
        log_sql="UPDATE qs.qmd_chat_log_new SET answerNO='" + Answer_Json['data'][0]['answerNo'] + "' \
        Where chat_id = '" + Chat_ID + "'"
    
    
    #print(log_sql)
    cur.execute(log_sql)    
    cur.execute("COMMIT")
    cur.close()
#使用者回饋是否答對
def QMD_feedback(Q_FB) :
    #print('Q_FB:',Q_FB)
    Chat_ID=str(Q_FB['Chat_ID'])
    #print('Chat_ID:',Chat_ID)
    feedback=str(Q_FB['feedback'])
    suggest=str(Q_FB['user_suggest'])
    #print('feedback:',feedback)
    update_sql="UPDATE qs.qmd_chat_log_new SET feedback='" + feedback + "',suggest='" + suggest + "' \
        Where chat_id = '" + Chat_ID + "'"
    
    conn  =  pymysql.connect ( host = '10.55.23.168' ,port=33060 ,  user = 'root' ,  passwd = "1234" , db='qs') 
    cur  =  conn.cursor ()
    #print(update_sql)
    cur.execute(update_sql)
    s=cur.execute("COMMIT")
    cur.close()
    conn.close()
    return s
#找出每個類別Top 5問題
def Select_TopQ(Q_System) :
    original_question={}
    QMD_original_question={}
    QMD_original_question['All']=["AERB 涵蓋類型有哪些","AERB TAT的規範是什麼","如何查詢DCC文件","台灣撥打其他Site短號","如何查詢生產良率"]
    QMD_original_question['glossary']=["什麼是EOL","什麼是ND Filter","什麼是API","什麼是8D","什麼是ECRS","什麼是ECRSAA"]
    QMD_original_question['abnormal_handing']=["AERB 涵蓋類型有哪些","AERB TAT的規範是什麼","什麼是CAERB的風險度評分(RPN)","CAERB結案時，如何確認是否需啟動QBQ會議","IMP 系統如何進入"]
    QMD_original_question['quality_system']=["如何查詢DCC文件","如何查詢VLRR","什麼是VLRR","白血球倉別KY2為何","什麼是白血球"]
    QMD_original_question['specification_judge']=["何謂IIS","動態規格調整是包含什麼","Mura應該在什麼畫面下判定","什麼是紅燈右轉","何謂表面能(達因值)測試"]
    QMD_original_question['process_production']=["如何查詢生產良率","什麼是CT1/CT2","什麼是C檢","LCD 製程主要有哪些","何謂LCM 製程"]
    QMD_original_question['quality_activity']=["台灣撥打其他Site短號","如何預約電話會議","如何加入電話會議","何謂CRN ","如何補打卡"]
    original_question['QMD']=QMD_original_question
    
    System=str(Q_System['System'])
    #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  )
    conn  =  pymysql.connect ( host = '10.55.23.168' ,port=33060 ,  user = 'root' ,  passwd = "1234" , db='qs') 
    cur  =  conn.cursor ()
    sql_dateno="Select distinct DateNo from qs.qmd_top_question Where System_NO='" + System + "' \
    Order By DateNo desc"
    cur.execute(sql_dateno)
    result = cur.fetchone()
    dateno=str(result[0])
    category_sub=['All','glossary','abnormal_handing','quality_system','specification_judge','process_production','quality_activity']
    TopQ_dict={}
    for c in category_sub:
        sql="Select Question from qs.qmd_top_question Where DateNO='" + dateno + "' \
        AND category_sub='" + c + "' Order By amount desc LIMIT 5" 
        cur.execute(sql)
        question_items = [x[0] for x in cur]
        
        if len(question_items)<5:
            original_q=original_question[System][c]
            for q in original_q:
                
                if q not in question_items:
                    question_items.append(q)
                    
                if len(question_items)==5:
                    exit
        TopQ_dict[c]=question_items
    cur.close()
    conn.close()
    return TopQ_dict
#IKnow_QMD主程式
def Iknow_QMD_QA(Q_Json,bc,TopN=10,KNN_N=1) :
    try:
        with open("dict/tongyici_dict.txt", "rb") as fp:   #同義詞詞典
            tongyici_dict=pickle.load(fp)
        with open("dict/stop_words.txt", "rb") as fp:   #停用詞詞典
            stop_words=pickle.load(fp)
        with open("BOW/kw_list.txt", "rb") as fp:   #每個標準題之關鍵字
            kw_list=pickle.load(fp)
        with open("BOW/Ans_list.txt", "rb") as fp:   #Pickling
            Ans_list=pickle.load(fp)
        with open("BOW/All_Q_AnsNO.txt", "rb") as fp:   #每個問題(含標準題與相似題)之答案編號
            All_Q_AnsNO=pickle.load(fp)   
        with open("BOW/All_Q_BERT.txt", "rb") as fp:   #每個問題(含標準題與相似題)之BERT向量
            All_Q_BERT=pickle.load(fp)
        with open("BOW/Stand_Q_dict.txt", "rb") as fp:   #答案編號與對應問題,答案,連結詞典
            Stand_Q_dict=pickle.load(fp)
        with open("BOW/Stand_A_dict.txt", "rb") as fp:   #問題與答案對照辭典
            Stand_A_dict=pickle.load(fp)
        jieba.load_userdict('dict/userdict.txt') #斷詞詞典
        cc = opencc.OpenCC('s2t')
        Q_Word=cc.convert(Q_Json["user_question"])
        Q_Word_lower=Q_Word.lower()
        #user_Q=jiebacut_word(Q_Word_lower,stop_words,tongyici_dict) # 斷詞後為陣列型式
        user_Q=jiebacut_word_num(Q_Word_lower,stop_words,tongyici_dict) # 斷詞後為陣列型式
        print('user_Q:',user_Q)
        #user_Q_num=jiebacut_word_num(Q_Word_lower,stop_words,tongyici_dict) #保留數字
        
        #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
        conn  =  pymysql.connect ( host = '10.55.23.168' ,port=33060 ,  user = 'root' ,  passwd = "1234") 
        if Q_Word in Stand_A_dict: #標準問法直接回答
            AnsNO=Stand_A_dict[Q_Word]
            answerType="standard"
            Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict,conn)
            s=QMD_Insert_log(conn,Answer_Json)
            
        else :
            #user_Q_WF=jiebacut_WF_word(Q_Word_lower,stop_words,tongyici_dict) # 斷詞後為字串型式
            #user_Q_WF_List=[user_Q_WF]
            #print('user_Q_WF:',user_Q_WF)
            user_Q_set=set(user_Q)
            #print('user_Q_set:',user_Q_set)
            #將使用者問題轉成詞頻矩陣
#             New_feature_List,New_BOW=Add_WF_Array(user_Q_WF,feature_name,All_Q_BOW)
#             loaded_vec = CountVectorizer(vocabulary=New_feature_List)
#             user_Q_WF_count = loaded_vec.fit_transform(user_Q_WF_List)
#             user_Q_df = pd.DataFrame(user_Q_WF_count.toarray(),columns=New_feature_List)
#             user_Q_BOW=user_Q_df.values.flatten().T
            match_AnsNO=[]
            i=0
            for kw in kw_list:
                if user_Q_set & kw==kw:
                    match_AnsNO.append(Ans_list[i])
                i+=1
            #print('match_AnsNO:',match_AnsNO)
            AnsNO_Array=np.array([])
            if len(match_AnsNO)>0 : #關鍵字符合
                match_AnsNO_set=set(match_AnsNO)
                match_NO=[]
                i=0
                for Q in All_Q_AnsNO:
                    for AnsNO in match_AnsNO_set:
                        if Q==AnsNO :
                            match_NO.append(i)
                    i+=1
                    
                user_Q_BERT=bc.encode([Q_Word_lower])
                user_Q_BERT=user_Q_BERT.reshape(-1)
                #print(user_Q_BERT)
                #print('match_NO:',match_NO)
                match_BERT=All_Q_BERT[match_NO]
                user_Ans_Index,user_Ans_sim=Cal_UserQ_CosSim(user_Q_BERT,match_BERT,TopN)
                #print(user_Ans_sim)
                for i in user_Ans_Index:
                    AnsNO_Array=np.append(AnsNO_Array,All_Q_AnsNO[match_NO[i]])
                sim_p=0.9
      
            else : #關鍵字不符合
      
                #取得BERT向量
                user_Q_BERT=bc.encode([Q_Word_lower])
                user_Q_BERT=user_Q_BERT.reshape(-1)
                #print(user_Q_BERT)
                user_Ans_Index,user_Ans_sim=Cal_UserQ_CosSim(user_Q_BERT,All_Q_BERT,TopN)
                #print(user_Ans_sim)
                for i in user_Ans_Index:
                    AnsNO_Array=np.append(AnsNO_Array,All_Q_AnsNO[i])
                sim_p=0.95
       
                
            #print('sim_p:',sim_p)
            #print('user_Ans_sim:',-user_Ans_sim[0])
            if -user_Ans_sim[0]>sim_p: #推一個答案
                if KNN_N>len(user_Ans_Index):
                    KNN_N=len(user_Ans_Index)
                #print(AnsNO_Array)
                AnsNO_KNN=AnsNO_Array[:KNN_N]
                #取得眾數
                AnsNO_mode=stats.mode(AnsNO_KNN)
                AnsNO_C_dict={}
                for i in range(0,KNN_N):
                    if AnsNO_KNN[i] not in AnsNO_C_dict:
                        AnsNO_C_dict[AnsNO_KNN[i]]=1
                    else :
                        AnsNO_C_dict[AnsNO_KNN[i]]+=1
                if  AnsNO_C_dict[AnsNO_KNN[0]]>= AnsNO_mode[1][0]:
                    AnsNO=AnsNO_KNN[0]
                else :
                    AnsNO=AnsNO_mode[0][0]
                answerType="standard"    
                Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict,conn)

            else : #推3個答案
                AnsNO_All=[]
                for AnsNO in AnsNO_Array:
                    if AnsNO not in AnsNO_All:
                        AnsNO_All.append(AnsNO)
                if len(AnsNO_All)>3:
                    AnsNO_list=AnsNO_All[:3]
                else :
                    AnsNO_list=AnsNO_All
                if len(AnsNO_list)==1:
                    AnsNO=AnsNO_list[0]
                    answerType="standard"
                    Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict,conn)

                else :
                    Answer_Json=Lead_Answer_Json(Q_Json,AnsNO_list,Stand_Q_dict)
            #print(Answer_Json)
            s=QMD_Insert_log(conn,Answer_Json)
        
        
        conn.close()
                
    except Exception as e:
        answerType="Error"
        Q_AnsNO=''
        #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
        conn  =  pymysql.connect ( host = '10.55.23.168' ,port=33060 ,  user = 'root' ,  passwd = "1234") 
        Answer_Json=Stand_Answer_Json(Q_Json,answerType,Q_AnsNO,Stand_Q_dict,conn,
                                      ErrorCode=1,errorMessage=str(e))
        now_time2=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        with open('error/'+now_time2+'.txt', 'w') as outfile:  
            json.dump(Answer_Json, outfile)
        conn.close()
    
    return Answer_Json 


@app.route('/I_Know_QMD', methods = ['POST'])
def I_Know_QMD():
    try:
        Q_Json=json.loads(request.get_data(),encoding='utf8')
        print(Q_Json)
        #bc = BertClient("10.55.23.101")
        bc = BertClient(ip="10.55.23.168",port=34090,port_out=34091)
        Answer_Json=Iknow_QMD_QA(Q_Json,bc)
        print(Answer_Json)
        response = Response(json.dumps(Answer_Json).encode('utf8')
                            , status=200, mimetype="application/json")
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        response.headers.add('Access-Control-Allow-Origin', '*')
        
        return response
    
    except Exception as e:
        now_time=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        f = open('error/'+ now_time +'_Predict.txt','w')
        f.write(str(e))
        Answer_Json={}
        Answer_Json['error']=str(e)
        response = Response(json.dumps(Answer_Json).encode('utf8')
                            , status=400, mimetype="application/json")
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        response.headers.add('Access-Control-Allow-Origin', '*')  
        return response

@app.route('/I_Know_QMD_FB', methods = ['POST'])
def I_Know_QMD_FB():
    Q_FB=json.loads(request.get_data(),encoding='utf8')
    #print('Q_FB:',Q_FB)
    fb=str(QMD_feedback(Q_FB))
    #print(fb)
    return fb

@app.route('/I_Know_Top5', methods = ['POST'])
def I_Know_Top5():
    Q_System=json.loads(request.get_data(),encoding='utf8')
    #print('Q_System:',type(Q_System))
    TopQ=Select_TopQ(Q_System)
   
    response = Response(json.dumps(TopQ).encode('utf8')
                            , status=200, mimetype="application/json")
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers.add('Access-Control-Allow-Origin', '*')
       
    return response 

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=85)
    #app.run(host='127.0.0.1', port=35085) #本機 
