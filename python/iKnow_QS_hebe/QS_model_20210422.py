# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:08:13 2021

@author: jenny
"""


import tensorflow_hub as hub
import tensorflow_text
import pandas
import monpa
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pickle
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics.pairwise import cosine_similarity
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class QS_model():

    def __init__(self):     
                
        def ReadPickle(file):
            data = pickle.load(file)    
            return data
        
        def tfidf(self,corpus):
            X = self.vectorizer.fit_transform(corpus)
            return X  
        monpa.load_userdict(r"/usr/src/iKnow_QS_new/load_dict.txt")
        self.Stand_QS_dict = pandas.read_excel(r"/usr/src/iKnow_QS_new/20210419_stan.xlsx")
        with open(r"/usr/src/iKnow_QS_new/SynonymData.pk","rb") as f:
            self.SynonymData = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/QS_all_data.pk","rb") as f:
            self.QS_all_data = ReadPickle(f)    
        with open(r"/usr/src/iKnow_QS_new/QS_corpus_monpa.pk","rb") as f:
            self.QS_corpus_monpa = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/QS_category.pk","rb") as f:
            self.QS_category = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/QS_answer.pk","rb") as f:
            self.QS_answer = ReadPickle(f)     
        with open(r"/usr/src/iKnow_QS_new/QS_system_svc.pk","rb") as f:
            self.QS_system_svc = ReadPickle(f)

        self.embed = hub.load(r"/usr/src/iKnow_QS_new/universal-sentence-encoder-multilingual-large_3")  

        with open(r"/usr/src/iKnow_QS_new/all_embed.pk","rb") as f:
            self.all_embed = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/DCC_embed.pk","rb") as f:
            self.DCC_embed = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/EC_embed.pk","rb") as f:
            self.EC_embed = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/IMP_embed.pk","rb") as f:
            self.IMP_embed = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/PCN_embed.pk","rb") as f:
            self.PCN_embed = ReadPickle(f)
        with open(r"/usr/src/iKnow_QS_new/PDS_embed.pk","rb") as f:
            self.PDS_embed = ReadPickle(f)
   
        self.vectorizer = TfidfVectorizer() 
        self.X = tfidf(self,self.QS_corpus_monpa)
    
    def Query_corpus(self,query):
        QueryList = []
        word = query.replace('?','').replace('？','').replace('】','').replace('【','').replace('「','').replace('」','').replace('”','').replace('“','').replace('，','').replace('(','').replace(')','').replace('。','').replace('"','').replace('、',' ').lower()#去除問號
        for r in range(len(list(self.SynonymData.get('Original')))): #同義詞轉換
                if list(self.SynonymData.get('Original'))[r].lower() in word:
                    word = word.replace( list(self.SynonymData.get('Original'))[r].lower() , ''.join(self.SynonymData.loc[self.SynonymData.Original == list(self.SynonymData.get('Original'))[r]].get("同義詞")).lower())               
        QueryList.append(' '.join(monpa.cut(word)))
        return word , QueryList
    
    def GetQuerySystemAnswer(self,query_corpus):
        query_vec = self.vectorizer.transform(query_corpus)
        pred_query = self.QS_system_svc.predict(query_vec)
        return pred_query[0]
            
    def GetQuerySimilarityAnswer_monpa(self,pred_query,query):
           try:  
                 query_vec_uni = self.embed(query)
                 cs = cosine_similarity(query_vec_uni , vars(self)[pred_query+"_embed"]).flatten() 
                 cs_sort = (cs > 0.5).astype(int) #(1,28)
                 idx = cs.argsort()[-1] #由小排到大
                 cs_all = cosine_similarity(query_vec_uni , self.all_embed).flatten()
                 idx_sim_1 = cs_all.argsort()[-1]
                 idx_sim_2 = cs_all.argsort()[-2]    
                 idx_sim_3 = cs_all.argsort()[-3]
                 ErrorCode = 0
                 if cs_sort[idx] == 1:
                     return  ErrorCode , "Have_Answer", self.QS_all_data.loc[self.QS_all_data.category == pred_query].get('Answer_NO').iloc[idx]
                 else:
                     answerOne = self.QS_all_data.get('Answer_NO').iloc[idx_sim_1]
                     answerTwo = self.QS_all_data.get('Answer_NO').iloc[idx_sim_2]
                     answerThree = self.QS_all_data.get('Answer_NO').iloc[idx_sim_3]
                     # answerOne = self.Stand_QS_dict.loc[self.Stand_QS_dict["Answer_NO"]==self.QS_all_data.get('Answer_NO').iloc[idx_sim_1]]['Question'].tolist()[0]
                     # answerTwo = self.Stand_QS_dict.loc[self.Stand_QS_dict["Answer_NO"]==self.QS_all_data.get('Answer_NO').iloc[idx_sim_2]]['Question'].tolist()[0]
                     # answerThree = self.Stand_QS_dict.loc[self.Stand_QS_dict["Answer_NO"]==self.QS_all_data.get('Answer_NO').iloc[idx_sim_3]]['Question'].tolist()[0]
                     return ErrorCode , "No_Answer" , [answerOne,answerTwo,answerThree]   
           except Exception as e:
             answerType = "Error"
             Q_AnsNO = e
             ErrorCode = 1           
             return ErrorCode , answerType , Q_AnsNO
    