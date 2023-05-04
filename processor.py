import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model=load_model('chatbot_model.h5')
import json
import random
import api

#intents = json.loads(open('job_intents.json', encoding='utf-8').read())
intents = json.loads(open('intents_haji.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
context={}

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    #print('bow',p)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.35
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def cek_param(sentence, model,userid):
    try:
        #print ('sentence',sentence)
        #print ('context['+userid+']',context[userid])
        if sentence.isdecimal():
            #print(context[userid])
            if context[userid]=="historydetails":
                return predict_class('ordernumber',model)
            elif context[userid]=="tanyaporsi":
                return predict_class('nomorporsi',model)
        else:
            try:
                if context[userid]=="tanyaporsi":
                    return predict_class('nomorporsi',model)
                elif context[userid]=="kotajadwalsholat":
                    #print ('predict_class context['+userid+']',context[userid])
                    return predict_class('jawabjadwalsholat',model)
            except:
                pass
    except:
        pass    
       
    return predict_class(sentence,model)
    
def getResponse(ints, intents_json,userid,msg):
    try:
        #print(intents_json)
        result=''
        if len(ints)==0:
            context[userid] = ''
            result='Mohon maaf, saya asisten AI PHLUT tidak bisa menemukan informasi yang ada minta !'                
            return result
        tag = ints[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            try:
                if(i['tag']== tag):
                    if 'set' in i and not 'filter' in i:
                        context[userid] = i['set']
                        #print('userID',context[userid])
                    #if the tag doesn't have any filter return response
                    if not 'filter' in i:
                        result = random.choice(i['responses'])
                    
                    if userid in context and 'filter' in i and i['filter']==context[userid]:
                        if 'set' in i:
                            context[userid] = i['set']
                        
                        #print("i[act]",i['act'])
                        if 'act' in i:
                            if i['act']=='cekPorsi':
                                nop=api.getPorsiHaji(msg)
                                #print(nop)
                                result=nop
                            elif i['act']=='cekdaftarnikah':
                                result='Pendaftaran nikah dengan nomor pendaftaran '+'....'
                            elif i['act']=='getjadwalsholat':
                                nop=api.getJadwalSholat(msg)
                                result=nop
                            
                            context[userid] = ''
                            break
                        else:
                            result=random.choice(i['responses'])
                            break
                    elif not 'filter' in i:
                        result = random.choice(i['responses'])
                    else:
                        context[userid] = ''#1101371276
                        result = "You must ask the right questions"
                        break
            except:
                pass
    except:
        context[userid] = ''
        result='Saya asisten AI PHLUT tidak mengerti komen anda, mohon diulangi !'

    return result

def chatbot_response(msg,userid='everyone'):
    #ints = predict_class(msg, model)
    ints=cek_param(msg, model,userid)
    #print((ints))
    res = getResponse(ints, intents,userid,msg)
    return res
