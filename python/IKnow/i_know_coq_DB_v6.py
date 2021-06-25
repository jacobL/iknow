# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:21:56 2020

@author: sh.tseng
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 16:26:00 2020

@author: sh.tseng
"""
import os
from apscheduler.schedulers.background import BackgroundScheduler
import i_know_coq_buildmodel_v4

sched = BackgroundScheduler(daemon=True)
#@sched.scheduled_job('cron', hour=10, minute=15)
#@sched.scheduled_job('date', run_date='2019-08-19 16:10:05')
@sched.scheduled_job('interval', id='my_job_id',start_date='2020-1-16 23:59:00',days=1)
def timed_job_one():
    print('build model')
    i_know_coq_buildmodel_v4.main()
sched.start()

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
import opencc

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
def Get_YMA(Q_Json,user_Q_num,year_kw,month_kw,app_kw,ou_kw,fab_kw,customer_kw):
    for word in user_Q_num:
        if word in year_kw:
            Q_Json['year']=str(year_kw[word])
        if word in month_kw:
            Q_Json['month']=str(month_kw[word])
        if word in app_kw:
            Q_Json['application']=app_kw[word]
        if word in ou_kw:
            Q_Json['ou']=ou_kw[word]
        if word in fab_kw:
            Q_Json['fab']=fab_kw[word]
        if word in customer_kw:
            Q_Json['customer']=customer_kw[word]
    now = datetime.datetime.now()
    if Q_Json['month']=="" :
        now_word={'最近','最新','這個月','現在','上個月','前個月','目前','現況'}
        inte = list(set(now_word).intersection(set(user_Q_num)))
        if len(inte)>0:
            if now.month==1:
                Q_Json['month']="12"
                if Q_Json['year']=="" :
                    Q_Json['year']=str(now.year-1)
            else : 
                Q_Json['month']=str(now.month-1)
                if Q_Json['year']=="" :
                    Q_Json['year']=str(now.year)
        else :
            Q_Json['month']="00"
            if Q_Json['year']=="" :
                Q_Json['year']=str(now.year-1)
            
    else :
        if Q_Json['year']=="" :
            Q_Json['year']=str(now.year)
        
    if len(Q_Json['month'])==1:
        Q_Json['month']="0"+ Q_Json['month']    
    if Q_Json['application']=="" :
        Q_Json['application']='所有應用'
        
    return  Q_Json

def Coq_associstion(answerNo,application):
    conn  =  pymysql.connect ( host = '10.55.52.98' ,port=33060 ,  user = 'root' ,  passwd = "1234"  ) 
    cur  =  conn.cursor ()
    sql_dateno="Select distinct DateNo from iknow.coq_association_rule Order By DateNo desc"
    cur.execute(sql_dateno)
    result = cur.fetchone()
    dateno=str(result[0])
    sql="Select Question_Y,App_Y from iknow.coq_association_rule Where Question_X='" + answerNo + "' \
    AND App_X='" + application + "' AND DateNO='" + dateno + "' Order By Confidence,Lift desc LIMIT 3" 
    cur.execute(sql)
    suggest_items = [x for x in cur]
    
    return suggest_items    

def Stand_Answer_Json(Q_Json,answerType,Q_AnsNO,Stand_Q_dict,ErrorCode=0,errorMessage=""):
    now_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if ErrorCode==0:
        if answerType=="No_Answer" :
            Answer_Json= {
            "Chat_ID": Q_Json["Chat_ID"],
            "user_ID": Q_Json["user_ID"],
            "Code": ErrorCode,
            "errorMessage": errorMessage,
            "answerType": answerType,
            "user_question": Q_Json["user_question"],
            "application": "",
            "ou": "",
            "fab": "",
            "customer": "",
            "year": "",
            "month": "",
            "category_main": "",
            "category_sub": "",
            "data":
                [{
                    "answerNo": Q_AnsNO,
                    "category": "",
                    "question": "",
                    "answer": "無法回答您喔,我只能回答CoQ與AIOK的問題",
                    "URL": ""
                }],
            "createDate": now_time,
            "suggest": []
            }
        else :
            Answer_Json= {
                "Chat_ID": Q_Json["Chat_ID"],
                "user_ID": Q_Json["user_ID"],
                "Code": ErrorCode,
                "errorMessage": errorMessage,
                "answerType": answerType,
                "user_question": Q_Json["user_question"],
                "application": Q_Json["application"],
                "ou": Q_Json["ou"],
                "fab": Q_Json["fab"],
                "customer": Q_Json["customer"],
                "year": Q_Json["year"],
                "month": Q_Json["month"],
                "category_main": Stand_Q_dict[Q_AnsNO]['Main'],
                "category_sub": Stand_Q_dict[Q_AnsNO]['Sub'],
                "data":
                    [{
                        "answerNo": Q_AnsNO,
                        "category": Stand_Q_dict[Q_AnsNO]['System'],
                        "question": Stand_Q_dict[Q_AnsNO]['Question'],
                        "answer": Stand_Q_dict[Q_AnsNO]['Answer'],
                        "URL": Stand_Q_dict[Q_AnsNO]['URL']
                    }],
                "createDate": now_time
                }
            suggest_items=Coq_associstion(Q_AnsNO,Q_Json["application"])
            #suggest_items=[]
            suggest=[]
            for item in suggest_items:
                suggest_dict={"answerNo": item[0],"question": Stand_Q_dict[item[0]],"application": item[1]
                       ,"year": Q_Json["year"],"month": Q_Json["month"]}
                suggest.append(suggest_dict)
            Answer_Json["suggest"]=suggest
    else :
        Answer_Json= {
            "Chat_ID": Q_Json["Chat_ID"],
            "user_ID": Q_Json["user_ID"],
            "Code": ErrorCode,
            "errorMessage": errorMessage,
            "answerType": answerType,
            "user_question": Q_Json["user_question"],
            "application": Q_Json["application"],
            "ou": Q_Json["ou"],
            "fab": Q_Json["fab"],
            "customer": Q_Json["customer"],
            "year": Q_Json["year"],
            "month": Q_Json["month"],
            "category_main": "",
            "category_sub": "",
            "data":
                [{
                    "answerNo": Q_AnsNO,
                    "category": "",
                    "question": "",
                    "answer": "系統異常",
                    "URL": ""
                }],
            "createDate": now_time,
            "suggest": []
            }
        
        
    
    return Answer_Json
def Lead_Answer_Json(Q_Json,Q_AnsNO_list,Stand_Q_dict,Q_category='COQ'):
    now_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Answer_Json= {
                "Chat_ID": Q_Json["Chat_ID"],
                "user_ID": Q_Json["user_ID"],
                "Code": 0,
                "errorMessage": "",
                "answerType": 'lead',
                "user_question": Q_Json["user_question"],
                "application": Q_Json["application"],
                "ou": Q_Json["ou"],
                "fab": Q_Json["fab"],
                "customer": Q_Json["customer"],
                "year": Q_Json["year"],
                "month": Q_Json["month"]
                }
   
    data=[]
    for A_NO in Q_AnsNO_list:
        data_dict={"answerNo": A_NO,"category": Stand_Q_dict[A_NO]['System'],"question": Stand_Q_dict[A_NO]['Question']
                   ,"URL": Stand_Q_dict[A_NO]['URL']}
        data.append(data_dict)
#     data.append({"answerNo": "","category": "","question": "以上都不是,我換個問法"
#                    ,"URL": ""})
       
    Answer_Json["data"]=data
    Answer_Json["createDate"]=now_time
    
    return Answer_Json

#單句斷詞不保留數字
def jiebacut_word(Q_Word,stop_words,tongyici_dict):
    Word_list = ''
    for w in jieba.cut(Q_Word, cut_all=False):
        if w.lower() not in stop_words:
            if w.lower() in tongyici_dict:
                tongyici_w=tongyici_dict[w.lower()]
            else :
                if not bool(re.match('[0-9]+', w.lower())):
                    tongyici_w=w.lower()
                else :
                    tongyici_w=''
            Word_list=Word_list+' '+ tongyici_w
    cut_word=[]
    cut_word=Word_list.split(' ')
    while '' in cut_word:
        cut_word.remove('')
    cut_word_re = sorted(set(cut_word),key=cut_word.index)
    return cut_word_re
#單句斷詞保留數字
def jiebacut_word_num(Q_Word,stop_words,tongyici_dict):
    Word_list = ''
    for w in jieba.cut(Q_Word, cut_all=False):
        if w.lower() not in stop_words:
            if w.lower() in tongyici_dict:
                tongyici_w=tongyici_dict[w.lower()]
            else :
                tongyici_w=w.lower()
            Word_list=Word_list+' '+ tongyici_w
    cut_word=[]
    cut_word=Word_list.split(' ')
    while '' in cut_word:
        cut_word.remove('')
    cut_word_re = sorted(set(cut_word),key=cut_word.index)
    return cut_word_re
#單句斷詞,斷詞完變字串
def jiebacut_WF_word(Q_Word,stop_words,tongyici_dict):
    Word_list = ''
    for w in jieba.cut(Q_Word, cut_all=False):
        if w.lower() not in stop_words:
            if w.lower() in tongyici_dict:
                tongyici_w=tongyici_dict[w.lower()]
            else :
                tongyici_w=w.lower()

            Word_list=Word_list+' '+ tongyici_w
    cut_word=[]
    cut_word=Word_list.split(' ')
    while '' in cut_word:
        cut_word.remove('')
    cut_word_re = sorted(set(cut_word),key=cut_word.index)
    datastr=' '.join(cut_word_re)
    return datastr

def QM_QA(Q_Json,bc,TopN=10,KNN_N=3) :
    try:
        with open("dict/tongyici_dict.txt", "rb") as fp:   #Pickling
            tongyici_dict=pickle.load(fp)
        with open("dict/stop_words.txt", "rb") as fp:   #Pickling
            stop_words=pickle.load(fp)
        with open("dict/year_kw.txt", "rb") as fp:   #Pickling
            year_kw=pickle.load(fp)
        with open("dict/month_kw.txt", "rb") as fp:   #Pickling
            month_kw=pickle.load(fp)  
        with open("dict/app_kw.txt", "rb") as fp:   #Pickling
            app_kw=pickle.load(fp)
        with open("dict/ou_kw.txt", "rb") as fp:   #Pickling
            ou_kw=pickle.load(fp)
        with open("dict/fab_kw.txt", "rb") as fp:   #Pickling
            fab_kw=pickle.load(fp)
        with open("dict/customer_kw.txt", "rb") as fp:   #Pickling
            customer_kw=pickle.load(fp)  

        with open("BOW/WordFreq_X.txt", "rb") as fp:   #Pickling
            feature_name=pickle.load(fp)
        with open("BOW/WordFreq_Array.txt", "rb") as fp:   #Pickling
            All_Q_BOW=pickle.load(fp)
        with open("BOW/All_Q_AnsNO.txt", "rb") as fp:   #Pickling
            All_Q_AnsNO=pickle.load(fp)   
        with open("BOW/All_Q_BERT.txt", "rb") as fp:   #Pickling
            All_Q_BERT=pickle.load(fp)
        with open("BOW/Stand_Q_dict.txt", "rb") as fp:   #Pickling
            Stand_Q_dict=pickle.load(fp)
        with open("BOW/Stand_A_dict.txt", "rb") as fp:   #Pickling
            Stand_A_dict=pickle.load(fp)

        with open("BOW/Stand_Q_df.txt", "rb") as fp:   #Pickling
            Stand_Q_df=pickle.load(fp)
        with open("BOW/main_kw_dict.txt", "rb") as fp:   #Pickling
            main_kw_dict=pickle.load(fp)
        with open("BOW/sub_kw_dict.txt", "rb") as fp:   #Pickling
            sub_kw_dict=pickle.load(fp)
      
           
        jieba.load_userdict('dict/userdict.txt')
        cc = opencc.OpenCC('s2t')
        Q_Word=cc.convert(Q_Json["user_question"])
        Q_Word_lower=Q_Word.lower()
        user_Q=jiebacut_word(Q_Word_lower,stop_words,tongyici_dict) # 斷詞後為陣列型式
        user_Q_num=jiebacut_word_num(Q_Word_lower,stop_words,tongyici_dict) #保留數字
        if Q_Word in Stand_A_dict: #標準問法直接回答
            AnsNO=Stand_A_dict[Q_Word]
            if Q_Json["year"]=="":
                Q_Json=Get_YMA(Q_Json,user_Q_num,year_kw,month_kw,app_kw,ou_kw,fab_kw,customer_kw)
            answerType='standard'
            
            Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict)
        else :
            Q_Json=Get_YMA(Q_Json,user_Q_num,year_kw,month_kw,app_kw,ou_kw,fab_kw,customer_kw)
            user_Q_WF=jiebacut_WF_word(Q_Word_lower,stop_words,tongyici_dict) # 斷詞後為字串型式
            user_Q_WF_List=[user_Q_WF]
            #print('user_Q_WF:',user_Q_WF)
            user_Q_set=set(user_Q)
            #將使用者問題轉成詞頻矩陣
            New_feature_List,New_BOW=Add_WF_Array(user_Q_WF,feature_name,All_Q_BOW)
            loaded_vec = CountVectorizer(vocabulary=New_feature_List)
            user_Q_WF_count = loaded_vec.fit_transform(user_Q_WF_List)
            user_Q_df = pd.DataFrame(user_Q_WF_count.toarray(),columns=New_feature_List)
            user_Q_BOW=user_Q_df.values.flatten().T
            #找出符合關鍵字之主類別
            match_main=[]
            for c in main_kw_dict:
                for kw in main_kw_dict[c]:
                    if user_Q_set & kw==kw:
                        match_main.append(c)
            match_main=list(set(match_main))
            #print('match_main:',match_main)
            #找出符合關鍵字之副類別
            match_sub=[]
            for c in sub_kw_dict:
                for kw in sub_kw_dict[c]:
                    if user_Q_set & kw==kw:
                        match_sub.append(c)
            match_sub=list(set(match_sub))
            #print('match_sub:',match_sub)
            
            
            if len(match_main)==0 :
                answerType='No_Answer'
                Answer_Json=Stand_Answer_Json(Q_Json,answerType,"QXXX",Stand_Q_dict)
        
            else :
                match_AnsNO=[]
                if len(match_sub)==0 :
                    for c1 in match_main:
                        df_match=Stand_Q_df.loc[Stand_Q_df['category_main'] == c1[1]]
                        match=df_match['Answer_NO'].tolist()
                        match_AnsNO.extend(match)
                else :
                    for c1 in match_main:
                        for c2 in match_sub:
                            df_match=Stand_Q_df.loc[(Stand_Q_df['category_main'] == c1[1]) 
                                                    & (Stand_Q_df['category_sub'] == c2[1])]
                            match=df_match['Answer_NO'].tolist()
                            match_AnsNO.extend(match)
                    
                #print('match_AnsNO:',match_AnsNO)
                #print('All_Q_AnsNO:',All_Q_AnsNO)
                AnsNO_Array=np.array([])
                if len(match_AnsNO)>0:
                    match_NO=[]
                    i=0
                    for Q in All_Q_AnsNO:
                        for AnsNO in match_AnsNO:
                            if Q==AnsNO :
                                match_NO.append(i)
                        i+=1
                    #print('match_NO:',match_NO)
                    match_BOW=New_BOW[match_NO]
                    user_Ans_Index,user_Ans_sim=Cal_UserQ_CosSim(user_Q_BOW,match_BOW,TopN)
                    for i in user_Ans_Index:
                        AnsNO_Array=np.append(AnsNO_Array,All_Q_AnsNO[match_NO[i]])
                    sim_p=0.6
                else:
                    #print('Q_Word:',Q_Word)
                    #取得BERT向量
                    user_Q_BERT=bc.encode([Q_Word])
                    user_Q_BERT=user_Q_BERT.reshape(-1)
                    #print(user_Q_BERT)
                    user_Ans_Index,user_Ans_sim=Cal_UserQ_CosSim(user_Q_BERT,All_Q_BERT,TopN)
                    #print(user_Ans_sim)
                    for i in user_Ans_Index:
                        AnsNO_Array=np.append(AnsNO_Array,All_Q_AnsNO[i])
                    sim_p=0.94

                #print('user_Ans_sim:',-user_Ans_sim)
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

                    answerType='standard'
                  
                    Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict)

                else : #推3個答案
                    AnsNO_All=[]
                    for AnsNO in AnsNO_Array:
                        if AnsNO not in AnsNO_All:
                            AnsNO_All.append(AnsNO)
                    if len(AnsNO_All)>3:
                        AnsNO_list=AnsNO_All[:3]
                    else :
                        AnsNO_list=AnsNO_All
                    #print(AnsNO_list)
                    if len(AnsNO_list)==1:
                        AnsNO=AnsNO_list[0]
                        answerType='standard'
                     
                      
                        Answer_Json=Stand_Answer_Json(Q_Json,answerType,AnsNO,Stand_Q_dict)

                    else :
                        Answer_Json=Lead_Answer_Json(Q_Json,AnsNO_list,Stand_Q_dict)
                
    except Exception as e:
        Answer_Json=Stand_Answer_Json(Q_Json,"Error",'Q999',Stand_Q_dict,1,str(e))
        now_time2=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        with open('error/'+now_time2+'.txt', 'w') as outfile:  
            json.dump(Answer_Json, outfile)
    
    return Answer_Json

from flask import Flask, request
from flask import Response
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
#app.config['JSON_AS_ASCII'] = False
@app.route('/I_Know', methods = ['POST'])
   
def I_Know():
    try:
        Q_Json=json.loads(request.get_data(),encoding='utf8')
        bc = BertClient("10.55.52.98")
        Answer_Json=QM_QA(Q_Json,bc)
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
if __name__ == '__main__':
    os.chdir("/usr/src/i_know_coq")
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8000)
    #app.run(host='10.56.211.24', port=4996)
