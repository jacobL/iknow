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
    SQL_Str='SELECT jiebaword FROM iknow.qm_jiebadict'
    dbCursor.execute(SQL_Str)
    results = dbCursor.fetchall()
    dict_List=[]
    for db_row in results:
        dict_List.append(db_row[0])
    userdict=pd.DataFrame(dict_List)
    userdict.to_csv('dict/userdict.txt', header=False,index=False,encoding='utf8')
    #同義字
    SQL_Str='SELECT WORD,SYNONYMOUS FROM iknow.qm_jieba_synon'
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

    SQL_Str='SELECT stopword FROM iknow.qm_stopword'
    dbCursor.execute(SQL_Str)
    results = dbCursor.fetchall()
    stop_words=[]
    for db_row in results:
        stop_words.append(db_row[0])
    with open("dict/stop_words.txt", "wb") as fp:   #Pickling
        pickle.dump(stop_words, fp)
        
    query='SELECT keyword,year_time FROM iknow.qm_year_kw'   
    year_kw = pd.read_sql(query, conn)
    year_key=year_kw['keyword'].tolist()
    year_Value=year_kw['year_time'].tolist()
    year_kw=dict(zip(year_key,year_Value))
    with open("dict/year_kw.txt", "wb") as fp:   #Pickling
        pickle.dump(year_kw, fp)

    query='SELECT keyword,month_time FROM iknow.qm_month_kw'   
    month_kw = pd.read_sql(query, conn)
    month_key=month_kw['keyword'].tolist()
    month_Value=month_kw['month_time'].tolist()
    month_kw=dict(zip(month_key,month_Value))
    with open("dict/month_kw.txt", "wb") as fp:   #Pickling
        pickle.dump(month_kw, fp)

    query='SELECT keyword,application FROM iknow.qm_app_kw'   
    app_kw = pd.read_sql(query, conn)
    app_key=app_kw['keyword'].tolist()
    app_Value=app_kw['application'].tolist()
    app_kw=dict(zip(app_key,app_Value))
    with open("dict/app_kw.txt", "wb") as fp:   #Pickling
        pickle.dump(app_kw, fp)
        
    query='SELECT keyword,OU FROM iknow.qm_ou_kw'   
    ou_kw = pd.read_sql(query, conn)
    ou_key=ou_kw['keyword'].tolist()
    ou_Value=ou_kw['OU'].tolist()
    ou_kw=dict(zip(ou_key,ou_Value))
    with open("dict/ou_kw.txt", "wb") as fp:   #Pickling
        pickle.dump(ou_kw, fp)
        
    query='SELECT keyword,fab FROM iknow.qm_fab_kw'   
    fab_kw = pd.read_sql(query, conn)
    fab_key=fab_kw['keyword'].tolist()
    fab_Value=fab_kw['fab'].tolist()
    fab_kw=dict(zip(fab_key,fab_Value))
    with open("dict/fab_kw.txt", "wb") as fp:   #Pickling
        pickle.dump(fab_kw, fp)
    
    query='SELECT keyword,customer FROM iknow.qm_customer_kw'   
    customer_kw = pd.read_sql(query, conn)
    customer_key=customer_kw['keyword'].tolist()
    customer_Value=customer_kw['customer'].tolist()
    customer_kw=dict(zip(customer_key,customer_Value))
    with open("dict/customer_kw.txt", "wb") as fp:   #Pickling
        pickle.dump(customer_kw, fp)  
        
    #conn.close()
    #print(stop_words)     
    return userdict,tongyici_dict,stop_words,year_kw,month_kw,app_kw,ou_kw,fab_kw,customer_kw

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
        datastr=' '.join(data_re)
        cut_word_List.append(datastr)
    return cut_word_List

def Build_BOW(conn,bc,stop_words,tongyici_dict):
    #標準問法題庫
    query="SELECT * FROM iknow.qm_standand_question Where Enabled='True'"   
    Stand_Q_df = pd.read_sql(query, conn)
#     Stand_Q_df = pd.read_csv('DB/Stand_Q.txt',encoding='utf-8',delimiter="\t")
    Stand_Q=Stand_Q_df['Question'] #問題
    Stand_Q_list=Stand_Q.tolist()
    Stand_Q_AnsNO=Stand_Q_df['Answer_NO'].tolist() #對應答案編號
    Stand_A_dict=dict(zip(Stand_Q_list,Stand_Q_AnsNO))
    with open("BOW/Stand_A_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(Stand_A_dict, fp)
    with open("BOW/Stand_Q_df.txt", "wb") as fp:   #Pickling
        pickle.dump(Stand_Q_df, fp)
       
    Stand_Q_lower=Stand_Q.str.lower() #問題轉小寫
    Stand_Q_lower=Stand_Q_lower.tolist() #轉成陣列
    Stand_Q_Main_C=Stand_Q_df['category_main'].tolist()
    Stand_Q_Sub_C=Stand_Q_df['category_sub'].tolist()
    Stand_Q_Ans=Stand_Q_df['Answer'].tolist()
    Stand_Q_url=Stand_Q_df['URL'].tolist() #問題
    Stand_Q_Sys=Stand_Q_df['QM_System'].tolist() #問題
    
    i=0
    Stand_Q_dict={}
    for ANO in Stand_Q_AnsNO:
        Stand_Q_dict[ANO]={}
        Stand_Q_dict[ANO]['Question']=Stand_Q_list[i]
        Stand_Q_dict[ANO]['System']=Stand_Q_Sys[i]
        Stand_Q_dict[ANO]['Main']=Stand_Q_Main_C[i]
        Stand_Q_dict[ANO]['Sub']=Stand_Q_Sub_C[i]
        if Stand_Q_Ans[i] is None:
            Stand_Q_dict[ANO]['Answer']=''
        else :
            Stand_Q_dict[ANO]['Answer']=Stand_Q_Ans[i]
        if Stand_Q_url[i] is None:
            Stand_Q_dict[ANO]['URL']=''
        else :
            Stand_Q_dict[ANO]['URL']=Stand_Q_url[i]
        
        i+=1
    
    with open("BOW/Stand_Q_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(Stand_Q_dict, fp)    
    #print(Stand_Q_dict)
   
   
    #相似問題題庫
    query='SELECT * FROM iknow.qm_sim_question'  
    Sim_Q_df = pd.read_sql(query, conn)
#     Sim_Q_df = pd.read_csv('DB/Sim_Q.txt',encoding='utf-8',delimiter="\t")
    Sim_Q=Sim_Q_df['Question']
    Sim_Q_AnsNO=Sim_Q_df['Answer_NO'].tolist()
    Sim_Q_lower=Sim_Q.str.lower()
    Sim_Q_lower=Sim_Q_lower.tolist()

        
    #主分類關鍵字
    query='SELECT * FROM iknow.qm_category_main_kw'  
    category_main_df = pd.read_sql(query, conn)
    category_main=category_main_df['category_main'].tolist()
    #關鍵字
    keyword_main=category_main_df['keyword'].str.lower()
    keyword_main=keyword_main.tolist()
    system_main=category_main_df['QM_System'].tolist()
    i=0
    main_kw_dict={} #每個類別的關鍵字
    for kw in keyword_main:
        main_kw=[]
        kw_list=[]
        #print('kw_main:',kw)
        kw_list=kw.split('；')
        for w in kw_list:
            w_list=[]
            w_list=w.split('，')
            w_list_strip=[x.strip() for x in w_list]
            w_set=set(w_list_strip)
            main_kw.append(w_set)
        main_kw_dict[(system_main[i],category_main[i])]=main_kw
        i+=1
    #print(main_kw_dict)
    with open("BOW/main_kw_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(main_kw_dict, fp)
        
    #副分類關鍵字
    query='SELECT * FROM iknow.qm_category_sub_kw'  
    category_sub_df = pd.read_sql(query, conn)
    category_sub=category_sub_df['category_sub'].tolist()
    #關鍵字
    keyword_sub=category_sub_df['keyword'].str.lower()
    keyword_sub=keyword_sub.tolist()
    system_sub=category_sub_df['QM_System'].tolist()
    i=0
    sub_kw_dict={} #每個類別的關鍵字
    for kw in keyword_sub:
        sub_kw=[]
        kw_list=[]
        #print('kw_sub:',kw)
        kw_list=kw.split('；')
        for w in kw_list:
            w_list=[]
            w_list=w.split('，')
            w_list_strip=[x.strip() for x in w_list]
            w_set=set(w_list_strip)
            sub_kw.append(w_set)
        sub_kw_dict[(system_sub[i],category_sub[i])]=sub_kw
        i+=1
    #print(sub_kw_dict)
    with open("BOW/sub_kw_dict.txt", "wb") as fp:   #Pickling
        pickle.dump(sub_kw_dict, fp)
    
     
    
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
    query="SELECT Answer_NO FROM iknow.qm_standand_question Where Enabled='False'"   
    answerNo_df = pd.read_sql(query, conn)
    answerNo=answerNo_df['Answer_NO'].tolist()
    if len(answerNo)==0:
        Filter_NO="('')"
    else :
        Filter_NO="(''"
        for ano in answerNo:
            Filter_NO=Filter_NO + ",'" + ano + "'"
        Filter_NO=Filter_NO + ")"
    #print(Filter_NO)
    conn_coq = pymysql.connect( host = '10.55.52.98' ,port=33060 ,  user = 'root' ,  passwd = "1234" ,  db = 'iknow' ) 
    #query = "select * from qm.chatLog where answerNo is not null and feedback=0 order by id desc"
    query = "select * from iknow.chatLog where answerNo is not null and answerNo not in " + Filter_NO + "order by id desc"
    #print(query)
    User_log_df = pd.read_sql(query, conn_coq)
    #print(User_log_df)
    Q_sessionsId=User_log_df['sessionsId'].tolist()
    Q_answerNo=User_log_df['answerNo'].tolist() 
    Q_app=User_log_df['app'].tolist()
    Q_dict={}
    i=0
    for qid in Q_sessionsId:
        Q_log=str(Q_answerNo[i]) + '_' + str(Q_app[i])
        if qid in Q_dict:
            Q_list=Q_dict[qid]
            Q_list.append(Q_log)
            Q_dict[qid]=Q_list
        else :
            Q_dict[qid]=[Q_log]
        i+=1
    Q_basket=list(Q_dict.values())
    conn_coq.close()
    association_rules = apriori(Q_basket, min_lift=1, max_length=2)
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
        Q1=str(suggest[0]).split('_')
        Q2=str(suggest[1]).split('_')
        Support=suggest[2]
        Confidence=suggest[3]
        Lift=suggest[4]
        log_sql="INSERT INTO iknow.coq_association_rule (DateNO,Question_X,App_X,Question_Y,App_Y, \
        Support,Confidence,Lift) VALUES ('" + now_time + "','" + Q1[0] + "', \
                '" + Q1[1] + "','" + Q2[0] + "','" + Q2[1] + "','" + Support + "', \
                '" + Confidence + "','" + Lift + "')"
        cur.execute(log_sql)    
        cur.execute("COMMIT")
        

def main():
    try:
        
        conn  =  pymysql.connect ( host = '10.55.52.98' ,port=33060 ,  user = 'root' ,  passwd = "1234"  )
        print('1.Load_Jiebadict')
        userdict,tongyici_dict,stop_words,year_kw,month_kw,app_kw,ou_kw,fab_kw,customer_kw=Load_Jiebadict(conn)
        print('2.BertClient')
        bc = BertClient("10.56.211.124")
        print('3.Build_BOW')
        Build_BOW(conn,bc,stop_words,tongyici_dict)
        print('4.Build_Association')
        Build_Association(conn)
        conn.close()
        
    except Exception as e:
        now_time=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        f = open('error/'+ now_time +'_BuildModel.txt','w')
        f.write(str(e))
        
if __name__ == '__main__':
    main()
