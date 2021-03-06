# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:51:26 2020

@author: sh.tseng
"""

from apscheduler.schedulers.background import BackgroundScheduler
import i_know_mq_buildmodel
sched = BackgroundScheduler(daemon=True)
@sched.scheduled_job('interval', id='my_job_id',start_date='2020-2-3 01:59:00',days=1)
def timed_job_one():
    print('build model')
    i_know_mq_buildmodel.main()
sched.start()

import json
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
from flask import Flask, request
from flask import Response
from flask_cors import CORS, cross_origin

# app = Flask(__name__)
app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'test'
app.secret_key = 'Your Key'  
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
SESSION_PROTECTION = 'strong'
CORS(app)

def CheckAD(UserID,password):
    data = {"UserID": UserID, "password": password}
    response = requests.post('http://jnb2bws01/InxSSOAuth/api/Auth/CheckAD', json=data)
    json_data = json.loads(response.text)
    return json_data    
    
class User(UserMixin):  
    pass

@login_manager.user_loader  
def user_loader(ID):  
    user = User()  
    user.id = ID
    return user
@app.route('/IKnow/login', methods=['GET', 'POST'])  
def login():  
    conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688",db='iknow'  ) 
    cur = conn.cursor();
    errMsg = ''
    if request.method == 'GET':  
        return render_template('login.htm',errMsg=errMsg)  
    UserID = request.form['UserID']
    password = request.form['password']
    #print(UserID,' ',password)
    json_data = CheckAD(UserID,password)    
    errMsg = json_data['errMsg']
    if errMsg == '' : # ????????????
        ID = json_data['ID']
        user = User()
        user.id = ID
        login_user(user)
        
        json_data1 = json.loads(json_data['Properties'])
        employeeid = json_data1['employeeid'][0]
        userChineseName = json_data1['displayname'][0].replace(ID,'').replace(' ','')
        department = json_data1['department'][0] 
        OU = json_data1['adspath'][0].split(",")[3].split("=")[1]
        DC = json_data1['adspath'][0].split(",")[5].split("=")[1]
        cur.execute('insert into mq_login_log (UserID,loginTime)values(%s,CURRENT_TIMESTAMP())',(UserID))
        cur.execute('insert ignore into mq_user_loader(UserID,employeeid,userChineseName,OU,DC,department,STATUS)values(%s,%s,%s,%s,%s,%s,%s)',(UserID,employeeid,userChineseName,OU,DC,department,0))
        cur.execute('commit')        
        #print('????????????')
        return redirect(url_for('IKnow')) 
    else : # ????????????
        cur.execute('insert into mq_login_log (UserID,loginTime,errMsg)values(%s,CURRENT_TIMESTAMP(),%s)',(UserID,errMsg))
        cur.execute('commit')
        #print('????????????')
        return render_template('login.htm',errMsg=errMsg)
@app.route('/MQ8118/IKnow')
@login_required  
def IKnow():
    if current_user.is_active: 
        conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688",db='iknow'  )        
        cur = conn.cursor();
        returnData = OrderedDict();
        #user = mq_user_loader()
        UserID = current_user.id
        cur.execute('select employeeid,userChineseName,OU,DC,department from mq_user_loader where UserID=%s and STATUS=0',(UserID))
        if cur.rowcount > 0 :
            #print(UserID,' ??????mq_user_loader??????')
            r = cur.fetchone()
            employeeid = r[0]
            userChineseName = r[1]
            OU = r[2]
            DC = r[3]
            department = r[4]
            userDict = {'UserID':UserID, 'employeeid':employeeid, 'userChineseName':userChineseName, 'OU':OU,'DC':DC,'department':department}           
            return render_template('iknow_MQ_newIP.htm',userDict=userDict)
        else:
            #print(UserID,' ????????????mq_user_loader??????')
            return render_template('login.htm',errMsg='')

@app.route('/IKnow')
@login_required  
def IKnow2():
    if current_user.is_active: 
        conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688",db='iknow'  )        
        cur = conn.cursor();
        returnData = OrderedDict();
        #user = mq_user_loader()
        UserID = current_user.id
        cur.execute('select employeeid,userChineseName,OU,DC,department from mq_user_loader where UserID=%s and STATUS=0',(UserID))
        if cur.rowcount > 0 :
            #print(UserID,' ??????mq_user_loader??????')
            r = cur.fetchone()
            employeeid = r[0]
            userChineseName = r[1]
            OU = r[2]
            DC = r[3]
            department = r[4]
            userDict = {'UserID':UserID, 'employeeid':employeeid, 'userChineseName':userChineseName, 'OU':OU,'DC':DC,'department':department}           
            return render_template('iknow_MQ_newIP.htm',userDict=userDict)
        else:
            #print(UserID,' ????????????mq_user_loader??????')
            return render_template('login.htm',errMsg='')        
 
@app.route('/IKnow/logout')  
def logout():   
    logout_user()   
    return  redirect(url_for('login'))

import pymysql
conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688",db='iknow'  )       
cur = conn.cursor();
cur.execute('select employeeid,userChineseName,OU,DC,department from mq_user_loader where UserID=%s and STATUS=0',('s'))
if cur.rowcount > 0 :
    r = cur.fetchone()
    employeeid = r[0]
    userChineseName = r[1]
    OU = r[2]
    DC = r[3]
    department = r[4]  

import pandas as pd
import re
import jieba
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import copy
import math
from scipy import stats
import datetime
import json
from bert_serving.client import BertClient
import pymysql
from i_know_mq_buildmodel import jiebacut_word_num
from i_know_mq_buildmodel import jiebacut_WF_word
import opencc

#?????????????????????????????????????????????,???????????????????????????
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
#????????????????????????????????? by Word Freq
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
#??????????????????????????????
def mq_associstion(conn,answerNo):
    #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
    cur  =  conn.cursor ()
    sql_dateno="Select distinct DateNo from iknow.mq_association_rule Order By DateNo desc"
    cur.execute(sql_dateno)
    result = cur.fetchone()
    dateno=str(result[0])
    sql="Select Question_Y from iknow.mq_association_rule Where Question_X='" + answerNo + "' \
    AND DateNO='" + dateno + "' Order By Confidence,Lift desc LIMIT 3" 
    cur.execute(sql)
    suggest_items = [x for x in cur]
    #print(suggest_items)
    cur.close
    
    return suggest_items  
#????????????
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
                            "answer": '?????????????????????????????????????????????????????????????????????????????????????????????????????????~',
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
                    "Chat_ID": Q_Json["Chat_ID"],  #??????ID
                    "Session_ID": Q_Json["Session_ID"],  #??????Session ID?????????????????????????????????
                    "user_ID": Q_Json["user_ID"], #???????????????
                    "user_name": Q_Json["user_name"], #???????????????
                    "Code": ErrorCode, #0??????1??????
                    "errorMessage": errorMessage, #????????????
                    "answerType": answerType, #standard????????????Lead????????????
                    "user_question": Q_Json["user_question"], #???????????????
                    "data":
                        [{
                            "answerNo": Q_AnsNO,   #??????????????????
                            "answer": Stand_Q_dict[Q_AnsNO]['Answer'], #????????????
                            "question": Stand_Q_dict[Q_AnsNO]['Question'], #??????????????????
                            "SOP": Stand_Q_dict[Q_AnsNO]['SOP'], #??????SOP??????
                            "SOPNO": Stand_Q_dict[Q_AnsNO]['SOP_No'],  #??????SOP??????
                            "URL": Stand_Q_dict[Q_AnsNO]['URL'] #??????????????????
                        }],
                    "createDate": now_time
                    }
            #??????????????????
            suggest_items=mq_associstion(conn,Q_AnsNO)
            suggest=[]
            
            for item in suggest_items:
                suggest_dict={"answerNo": item[0],"question": Stand_Q_dict[item[0]]['Question']}
                #print(Stand_Q_dict[item[0]])
                suggest.append(suggest_dict)
            Answer_Json["suggest"]=suggest
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
#????????????,?????????????????????
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
#?????????????????????
def MQ_Insert_log(conn,Answer_Json) :
    Chat_ID=Answer_Json['Chat_ID']
    select_sql="SELECT * FROM iknow.mq_chat_log_new Where chat_id='" + Chat_ID + "'"
    #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
    cur  =  conn.cursor ()
    cur.execute(select_sql)
    e=cur.fetchone()
    
    if e is None:
        if Answer_Json['answerType']=="standard" :
            log_sql="INSERT INTO iknow.mq_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
            ,answerNo,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "', \
            '" + Answer_Json['user_ID'] + "','" + Answer_Json['user_name'] + "',\
            '" + Answer_Json['createDate'] + "','" + Answer_Json['user_question'] + "', \
            '" + Answer_Json['answerType'] + "','" + Answer_Json['data'][0]['answerNo'] + "',2)"
        elif Answer_Json['answerType']=="No_Answer" :
            log_sql="INSERT INTO iknow.mq_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
            ,answerNo,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "', \
            '" + Answer_Json['user_ID'] + "','" + Answer_Json['user_name'] + "',\
            '" + Answer_Json['createDate'] + "','" + Answer_Json['user_question'] + "', \
            '" + Answer_Json['answerType'] + "','" + Answer_Json['data'][0]['answerNo'] + "',0)"
            
        else :
            if len(Answer_Json['data'])==2:
                log_sql="INSERT INTO iknow.mq_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
                ,lead1,lead2,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "',\
                '" +Answer_Json['user_ID'] + "',\
                '" + Answer_Json['user_name'] + "','" + Answer_Json['createDate'] + "',\
                '" + Answer_Json['user_question'] + "','" + Answer_Json['answerType'] + "',\
                '" + Answer_Json['data'][0]['answerNo'] + "','" + Answer_Json['data'][1]['answerNo'] + "',2)"
            else :
                log_sql="INSERT INTO iknow.mq_chat_log_new (chat_id,session_id,user_id,user_name,checktime,chat,answerType \
                ,lead1,lead2,lead3,feedback) VALUES ('" + Chat_ID + "','" + Answer_Json['Session_ID'] + "',\
                '" +Answer_Json['user_ID'] + "',\
                '" + Answer_Json['user_name'] + "','" + Answer_Json['createDate'] + "',\
                '" + Answer_Json['user_question'] + "','" + Answer_Json['answerType'] + "',\
                '" + Answer_Json['data'][0]['answerNo'] + "','" + Answer_Json['data'][1]['answerNo']  + "',\
                '" + Answer_Json['data'][2]['answerNo'] + "',2)"
                                
        
        
    else :
        log_sql="UPDATE iknow.mq_chat_log_new SET answerNO='" + Answer_Json['data'][0]['answerNo'] + "' \
        Where chat_id = '" + Chat_ID + "'"
    
    
    #print(log_sql)
    cur.execute(log_sql)    
    cur.execute("COMMIT")
    cur.close()
#???????????????????????????
def MQ_feedback(Q_FB) :
    #print('Q_FB:',Q_FB)
    Chat_ID=str(Q_FB['Chat_ID'])
    #print('Chat_ID:',Chat_ID)
    feedback=str(Q_FB['feedback'])
    suggest=str(Q_FB['user_suggest'])
    #print('feedback:',feedback)
    update_sql="UPDATE iknow.mq_chat_log_new SET feedback='" + feedback + "',suggest='" + suggest + "' \
        Where chat_id = '" + Chat_ID + "'"
    conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
    cur  =  conn.cursor ()
    #print(update_sql)
    cur.execute(update_sql)
    s=cur.execute("COMMIT")
    cur.close()
    conn.close()
    return s
#??????????????????Top 5??????
def Select_TopQ(Q_System) :
    original_question={}
    MQ_original_question={}
    MQ_original_question['All']=["AERB ?????????????????????","AERB TAT??????????????????","????????????DCC??????","??????????????????Site??????","????????????????????????"]
    MQ_original_question['glossary']=["?????????EOL","?????????ND Filter","?????????API","?????????8D","?????????ECRS","?????????ECRSAA"]
    MQ_original_question['abnormal_handing']=["AERB ?????????????????????","AERB TAT??????????????????","?????????CAERB??????????????????(RPN)","CAERB???????????????????????????????????????QBQ??????","IMP ??????????????????"]
    MQ_original_question['quality_system']=["????????????DCC??????","????????????VLRR","?????????VLRR","???????????????KY2??????","??????????????????"]
    MQ_original_question['specification_judge']=["??????IIS","?????????????????????????????????","Mura??????????????????????????????","?????????????????????","???????????????(?????????)??????"]
    MQ_original_question['process_production']=["????????????????????????","?????????CT1/CT2","?????????C???","LCD ?????????????????????","??????LCM ??????"]
    MQ_original_question['quality_activity']=["??????????????????Site??????","????????????????????????","????????????????????????","??????CRN ","???????????????"]
    original_question['MQ']=MQ_original_question
    
    System=str(Q_System['System'])
    conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
    cur  =  conn.cursor ()
    sql_dateno="Select distinct DateNo from iknow.mq_top_question Where System_NO='" + System + "' \
    Order By DateNo desc"
    cur.execute(sql_dateno)
    result = cur.fetchone()
    dateno=str(result[0])
    category_sub=['All','glossary','abnormal_handing','quality_system','specification_judge','process_production','quality_activity']
    TopQ_dict={}
    for c in category_sub:
        sql="Select Question from iknow.mq_top_question Where DateNO='" + dateno + "' \
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
#IKnow_MQ??????????????????
def Iknow_MQ_QA(Q_Json,bc,TopN=10,KNN_N=1) :
    try:
        with open("dict/tongyici_dict.txt", "rb") as fp:   #???????????????
            tongyici_dict=pickle.load(fp)
        with open("dict/stop_words.txt", "rb") as fp:   #???????????????
            stop_words=pickle.load(fp)
        with open("BOW/kw_list.txt", "rb") as fp:   #???????????????????????????
            kw_list=pickle.load(fp)
        with open("BOW/Ans_list.txt", "rb") as fp:   #Pickling
            Ans_list=pickle.load(fp)
        with open("BOW/All_Q_AnsNO.txt", "rb") as fp:   #????????????(????????????????????????)???????????????
            All_Q_AnsNO=pickle.load(fp)   
        with open("BOW/All_Q_BERT.txt", "rb") as fp:   #????????????(????????????????????????)???BERT??????
            All_Q_BERT=pickle.load(fp)
        with open("BOW/Stand_Q_dict.txt", "rb") as fp:   #???????????????????????????,??????,????????????
            Stand_Q_dict=pickle.load(fp)
        with open("BOW/Stand_A_dict.txt", "rb") as fp:   #???????????????????????????
            Stand_A_dict=pickle.load(fp)
        jieba.load_userdict('dict/userdict.txt') #????????????
        cc = opencc.OpenCC('s2t')
        Q_Word=cc.convert(Q_Json["user_question"])
        Q_Word_lower=Q_Word.lower()
        #user_Q=jiebacut_word(Q_Word_lower,stop_words,tongyici_dict) # ????????????????????????
        user_Q=jiebacut_word_num(Q_Word_lower,stop_words,tongyici_dict) # ????????????????????????
        #print('user_Q:',user_Q)
        #user_Q_num=jiebacut_word_num(Q_Word_lower,stop_words,tongyici_dict) #????????????
        
        conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
        if Q_Word in Stand_A_dict: #????????????????????????
            AnsNO=Stand_A_dict[Q_Word]
            answerType="standard"
            Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict,conn)
            s=MQ_Insert_log(conn,Answer_Json)
            
        else :
            #user_Q_WF=jiebacut_WF_word(Q_Word_lower,stop_words,tongyici_dict) # ????????????????????????
            #user_Q_WF_List=[user_Q_WF]
            #print('user_Q_WF:',user_Q_WF)
            user_Q_set=set(user_Q)
            #print('user_Q_set:',user_Q_set)
            #????????????????????????????????????
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
            if len(match_AnsNO)>0 : #???????????????
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
                sim_p=0.95
      
            else : #??????????????????
      
                #??????BERT??????
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
            if -user_Ans_sim[0]>sim_p: #???????????????
                if KNN_N>len(user_Ans_Index):
                    KNN_N=len(user_Ans_Index)
                #print(AnsNO_Array)
                AnsNO_KNN=AnsNO_Array[:KNN_N]
                #????????????
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

            else : #???3?????????
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
            s=MQ_Insert_log(conn,Answer_Json)
        
        
        conn.close()
                
    except Exception as e:
        answerType="Error"
        Q_AnsNO=''
        conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  ) 
        Answer_Json=Stand_Answer_Json(Q_Json,answerType,Q_AnsNO,Stand_Q_dict,conn,
                                      ErrorCode=1,errorMessage=str(e))
        now_time2=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        with open('error/'+now_time2+'.txt', 'w') as outfile:  
            json.dump(Answer_Json, outfile)
        conn.close()
    
    return Answer_Json 


@app.route('/I_Know_MQ', methods = ['POST'])
def I_Know_MQ():
    try:
        Q_Json=json.loads(request.get_data(),encoding='utf8')
        #print(Q_Json)
        bc = BertClient("10.56.211.124")
        Answer_Json=Iknow_MQ_QA(Q_Json,bc)
        #print(Answer_Json)
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

@app.route('/I_Know_MQ_FB', methods = ['POST'])
def I_Know_MQ_FB():
    Q_FB=json.loads(request.get_data(),encoding='utf8')
    #print('Q_FB:',Q_FB)
    fb=str(MQ_feedback(Q_FB))
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
    #app.run(host='0.0.0.0', port=8000)
    #app.run(host='10.56.211.24', port=8100)
    hpcip = '0.0.0.0' 
    run_simple(hpcip, 8000, app)