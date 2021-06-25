# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 13:24:59 2019

@author: sh.tseng
"""

import pandas as pd
import re
import jieba
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import copy
import datetime
from bert_serving.client import BertClient
import pymysql
from apyori import apriori

def Load_Jiebadict(conn):
    dbCursor  =  conn.cursor ()
    SQL_Str='SELECT jiebaword FROM qs.qs_jiebadict'
    dbCursor.execute(SQL_Str)
    results = dbCursor.fetchall()
    dict_List=[]
    for db_row in results:
        dict_List.append(db_row[0])
    userdict=pd.DataFrame(dict_List)
    userdict.to_csv('dict/userdict.txt', header=False,index=False,encoding='utf8')
    #同義字
    SQL_Str='SELECT WORD,SYNONYMOUS FROM qs.qs_jieba_synon'
    dbCursor.execute(SQL_Str)
    results = dbCursor.fetchall()
    dict_Name=[]
    dict_Value=[]
    for db_row in results:
        dict_Name.append(db_row[0])
        dict_Value.append(db_row[1])
    tongyici_dict=dict(zip(dict_Name,dict_Value))
    with open("dict/tongyici_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(tongyici_dict, fp)

    SQL_Str='SELECT stopword FROM qs.qs_stopword'
    dbCursor.execute(SQL_Str)
    results = dbCursor.fetchall()
    stop_words=[]
    for db_row in results:
        stop_words.append(db_row[0])
    with open("dict/stop_words.txt", "wb") as fp:   #Pickling
        pickle.dump(stop_words, fp)
        
    return userdict,tongyici_dict,stop_words
#多句斷詞 建BOW,斷詞完變list
def jiebacut(datalist,stop_words,tongyici_dict):
    datalist_S = []
    for i, text in enumerate(datalist):
        line = ''
        for w in jieba.cut(text, cut_all=False):
            if w.lower() not in stop_words:
                if w.lower() in tongyici_dict:
                    tongyici_w=tongyici_dict[w.lower()]
                else :
                    if not bool(re.match('[0-9]+', w.lower())):
                        tongyici_w=w.lower()
                    else :
                        tongyici_w=''
                    
                line=line+' '+ tongyici_w
           
        datalist_S.append(line)
    cut_word_List=[]
    for item in datalist_S:
        data=[]
        data=item.split(' ')
        data_re = sorted(set(data),key=data.index)
        while '' in data_re:
            data_re.remove('')
        cut_word_List.append(data_re)
    return cut_word_List
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
#多句斷詞,斷詞完變字串
def jiebacut_WF(datalist,stop_words,tongyici_dict):
    datalist_S = []
    for i, text in enumerate(datalist):
        line = ''
        for w in jieba.cut(text, cut_all=False):
            if w.lower() not in stop_words:
                if w.lower() in tongyici_dict:
                    tongyici_w=tongyici_dict[w.lower()]
                else :
#                     if not bool(re.match('[0-9]+', w.lower())):
                        tongyici_w=w.lower()
#                     else :
#                         tongyici_w=''
                line=line+' '+ tongyici_w
           
        datalist_S.append(line)
    cut_word_List=[]
    for item in datalist_S:
        data=[]
        data=item.split(' ')
        data_re = sorted(set(data),key=data.index)
        while '' in data_re:
            data_re.remove('')
        datastr=' '.join(data_re)
        cut_word_List.append(datastr)
    return cut_word_List
#單句斷詞,斷詞完變字串
def jiebacut_WF_word(Q_Word,stop_words,tongyici_dict):
    Word_list = ''
    for w in jieba.cut(Q_Word, cut_all=False):
        if w.lower() not in stop_words:
            if w.lower() in tongyici_dict:
                tongyici_w=tongyici_dict[w.lower()]
            else :
                tongyici_w=w.lower()
#                 if not bool(re.match('[0-9]+', w.lower())):
#                     tongyici_w=w.lower()
#                 else :
#                     tongyici_w=''
            Word_list=Word_list+' '+ tongyici_w
    cut_word=[]
    cut_word=Word_list.split(' ')
    while '' in cut_word:
        cut_word.remove('')
    cut_word_re = sorted(set(cut_word),key=cut_word.index)
    datastr=' '.join(cut_word_re)
    return datastr

def Build_BOW(conn,bc,stop_words,tongyici_dict):
    #標準問法題庫
    query="SELECT * FROM qs.qs_standand_question Where Enabled='True'"   
    Stand_Q_df = pd.read_sql(query, conn)
    #Stand_Q_df = pd.read_csv('DB/Stand_Q.txt',encoding='utf-8',delimiter="\t")
    Stand_Q=Stand_Q_df['Question'] #問題
    Stand_Q_AnsNO=Stand_Q_df['Answer_NO'].tolist() #對應答案編號
    Stand_Q_Ans=Stand_Q_df['Answer'].tolist() #對應答案編號
    Stand_Q_SOP=Stand_Q_df['SOP_chapter'].tolist() #對應答案編號
    Stand_Q_SOPNO=Stand_Q_df['SOP_No'].tolist() #對應答案編號
    Stand_Q_URL=Stand_Q_df['URL'].tolist() #對應答案編號
    Stand_Q_lower=Stand_Q.str.lower() #問題轉小寫
    Stand_Q_lower=Stand_Q_lower.tolist() #轉成陣列
    Stand_Q_list=Stand_Q.tolist()
    Stand_A_dict=dict(zip(Stand_Q_list,Stand_Q_AnsNO))
    with open("BOW/Stand_A_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(Stand_A_dict, fp)
#     print(Stand_Q_Ans)
#     print(Stand_A_dict)
    
    Stand_Q_dict={}
    i=0
    for AnsNO in Stand_Q_AnsNO :
        Stand_Q_Ans[i]=str(Stand_Q_Ans[i]).replace('\r\n','<br>')
        Stand_Q_SOP[i]=str(Stand_Q_SOP[i]).replace('\r\n','<br>')
        Stand_Q_SOPNO[i]=str(Stand_Q_SOPNO[i]).replace('','')
        Stand_Q_URL[i]=str(Stand_Q_URL[i]).replace('','')
        Stand_Q_dict[AnsNO]={'Question':Stand_Q_list[i],'Answer':Stand_Q_Ans[i]
                             ,'SOP':Stand_Q_SOP[i],'SOP_No':Stand_Q_SOPNO[i],'URL':Stand_Q_URL[i]}
        i+=1
    with open("BOW/Stand_Q_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(Stand_Q_dict, fp)    
    #print(Stand_Q_dict)
    
    #相似問題題庫
    query='SELECT * FROM qs.qs_sim_question'  
    Sim_Q_df = pd.read_sql(query, conn)
    #Sim_Q_df = pd.read_csv('DB/Sim_Q.txt',encoding='utf-8',delimiter="\t")
    Sim_Q=Sim_Q_df['Question']
    Sim_Q_AnsNO=Sim_Q_df['Answer_NO'].tolist()
    Sim_Q_lower=Sim_Q.str.lower()
    Sim_Q_lower=Sim_Q_lower.tolist()
    #關鍵字
    Stand_Q_KW=Stand_Q_df['Keyword'].str.lower()
    Stand_Q_KW=Stand_Q_KW.tolist()
    i=0
    kw_list=[] #每個問題的關鍵字
    Ans_list=[] #每個關鍵字組合對應的答案編號
    for qk in Stand_Q_KW:
        qk_list=[]
        qk_list=qk.split('；')
        for w in qk_list:
            w_list=[]
            w_list=w.split('，')
            w_list = [word.replace('\r\n', '') for word in w_list]
            w_list = [word.strip() for word in w_list]
            w_set=set(w_list)
            kw_list.append(w_set)
            Ans_list.append(Stand_Q_AnsNO[i])
        i+=1
    with open("BOW/kw_list.txt", "wb") as fp:   #Pickling
        pickle.dump(kw_list, fp)
    with open("BOW/Ans_list.txt", "wb") as fp:   #Pickling
        pickle.dump(Ans_list, fp)
    
    #建BOW
    All_Q=copy.copy(Stand_Q_lower)
    All_Q.extend(Sim_Q_lower)
      
    All_Q_WF=jiebacut_WF(All_Q,stop_words,tongyici_dict)
    vectorizer = CountVectorizer(token_pattern='\w+')
    X = vectorizer.fit_transform(All_Q_WF)
    feature_name = vectorizer.get_feature_names()
    with open("BOW/WordFreq_X.txt", "wb") as fp:   #Pickling
        pickle.dump(feature_name, fp)
    All_Q_df = pd.DataFrame(X.toarray(),columns=feature_name)
    #詞頻矩陣
    All_Q_BOW=All_Q_df.values
    with open("BOW/WordFreq_Array.txt", "wb") as fp:   #Pickling
        pickle.dump(All_Q_BOW, fp)
    #詞頻dataframe    
    with open("BOW/WordFreq_DF.txt", "wb") as fp:   #Pickling
        pickle.dump(All_Q_df, fp)
    All_Q_AnsNO=copy.copy(Stand_Q_AnsNO)
    All_Q_AnsNO.extend(Sim_Q_AnsNO)    
    with open("BOW/All_Q_AnsNO.txt", "wb") as fp:   #Pickling
        pickle.dump(All_Q_AnsNO, fp)
    #讀取BERT
    All_Q_BERT=bc.encode(All_Q)    
    with open("BOW/All_Q_BERT.txt", "wb") as fp:   #Pickling
        pickle.dump(All_Q_BERT, fp)
def Build_Association(conn):
    query = "select * from qs.qs_chat_log_new where answerNo is not null order by id desc"
    User_log_df = pd.read_sql(query, conn)
    Q_sessionsId=User_log_df['session_id'].tolist()
    Q_answerNo=User_log_df['answerNo'].tolist() 
    Q_dict={}
    i=0
    for qid in Q_sessionsId:
        if qid in Q_dict:
            Q_list=Q_dict[qid]
            Q_list.append(Q_answerNo[i])
            Q_dict[qid]=Q_list
        else :
            Q_dict[qid]=[Q_answerNo[i]]
        i+=1
    Q_basket=list(Q_dict.values())
    association_rules = apriori(Q_basket, min_lift=0.5, max_length=2)
    association_results = list(association_rules)
    #print(association_results)
    suggest_rules=[]
    for r in association_results:
        pair = r[0]
        #print(pair)
        rule = [x for x in pair]
        if len(rule)>=2:
            suggest_rules.append([rule[0],rule[1],str(r[1]),str(r[2][0][2]),str(r[2][0][3])])
    #print(suggest_rules)
    now_time=datetime.datetime.now().strftime("%Y%m%d%H%M")
    cur  =  conn.cursor ()
    for suggest in suggest_rules:
        #print(suggest)
        Q1=str(suggest[0])
        Q2=str(suggest[1])
        Support=suggest[2]
        Confidence=suggest[3]
        Lift=suggest[4]
        log_sql="INSERT INTO qs.qs_association_rule (DateNO,Question_X,Question_Y,Support,Confidence,Lift) \
            VALUES ('" + now_time + "','" + Q1 + "','"  + Q2 + "','" + Support + "','" + Confidence + "','" + Lift + "')"
#         log_sql="INSERT INTO qs.qs_association_rule VALUES ('" + now_time + "','" + Q1 + "', \
#                 '"  + Q2 + "','" + Support + "','" + Confidence + "','" + Lift + "')"
        #print(log_sql)
        cur.execute(log_sql)    
        s=cur.execute("COMMIT")
    
    return s
def Build_Top_Question(conn):
    DateNO=datetime.datetime.now().strftime("%Y%m%d%H%M")
    start_time=(datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
    end_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    query = "SELECT qs.qs_chat_log_new.answerNO,qs.qs_standand_question.category_main,\
    qs.qs_standand_question.category_sub,qs.qs_standand_question.Question \
    ,COUNT(qs.qs_chat_log_new.id) AS amount FROM qs.qs_chat_log_new inner join \
    qs.qs_standand_question on qs.qs_chat_log_new.answerNo=qs.qs_standand_question.Answer_NO \
    WHERE qs.qs_chat_log_new.checktime>='" + start_time + "' AND \
    qs.qs_chat_log_new.checktime<='" + end_time + "' AND \
    qs.qs_chat_log_new.answerNo IS NOT NULL AND qs.qs_chat_log_new.answerNo<>'' AND \
    qs.qs_chat_log_new.answerNo<>'AEXXXX' AND qs.qs_standand_question.system='QS' \
    GROUP BY qs.qs_chat_log_new.answerNO ORDER BY amount DESC Limit 5"
    User_log_df = pd.read_sql(query, conn)
    cur  =  conn.cursor ()
    for i in range(0,len(User_log_df)):
        insert_sql="INSERT INTO qs.qs_top_question (DateNO,System_NO,category_sub,Answer_NO,Question,amount) \
            VALUES ('" + DateNO + "','QS','All','"  + str(User_log_df.iloc[i,0]) + "'\
            ,'" + str(User_log_df.iloc[i,3]) + "'\
            ,'" + str(User_log_df.iloc[i,4]) +  "')"
        cur.execute(insert_sql)
        cur.execute("COMMIT")
    category_sub=['glossary','abnormal_handing','quality_system','specification_judge','process_production','quality_activity']
    for c in category_sub:
        query = "SELECT qs.qs_chat_log_new.answerNO,qs.qs_standand_question.category_main,\
        qs.qs_standand_question.category_sub,qs.qs_standand_question.Question \
        ,COUNT(qs.qs_chat_log_new.id) AS amount FROM qs.qs_chat_log_new inner join \
        qs.qs_standand_question on qs.qs_chat_log_new.answerNo=qs.qs_standand_question.Answer_NO \
        WHERE qs.qs_chat_log_new.checktime>='" + start_time + "' AND \
        qs.qs_chat_log_new.checktime<='" + end_time + "' AND \
        qs.qs_standand_question.category_sub='" + c + "' AND \
        qs.qs_chat_log_new.answerNo IS NOT NULL AND qs.qs_chat_log_new.answerNo<>'' AND \
        qs.qs_chat_log_new.answerNo<>'AEXXXX' AND qs.qs_standand_question.system='QS' \
        GROUP BY qs.qs_chat_log_new.answerNO ORDER BY amount DESC Limit 5"
        User_log_df = pd.read_sql(query, conn)
        for i in range(0,len(User_log_df)):
            insert_sql="INSERT INTO qs.qs_top_question (DateNO,System_NO,category_sub,Answer_NO,Question,amount) \
                VALUES ('" + DateNO + "','QS','" + str(User_log_df.iloc[i,2]) +"','"  + str(User_log_df.iloc[i,0]) + "'\
                ,'" + str(User_log_df.iloc[i,3]) + "'\
                ,'" + str(User_log_df.iloc[i,4]) +  "')"
            cur.execute(insert_sql)
            cur.execute("COMMIT")

def main():
    try:
        #conn  =  pymysql.connect ( host = '10.56.211.124' ,port=3306 ,  user = 'testuser' ,  passwd = "1688"  )
        conn  =  pymysql.connect ( host = '10.55.23.101' ,port=33060 ,  user = 'root' ,  passwd = "1234"  )
        userdict,tongyici_dict,stop_words=Load_Jiebadict(conn)
        #bc = BertClient("10.56.211.124")
        bc = BertClient("10.55.23.101")
        Build_BOW(conn,bc,stop_words,tongyici_dict)
        Build_Association(conn)
        Build_Top_Question(conn)
        conn.close()
        
    except Exception as e:
        now_time=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        f = open('error/'+ now_time +'_BuildModel.txt','w')
        f.write(str(e))
        
if __name__ == '__main__':
    main()
    print('main')