#TechVidvan ChatBot project
import os
import nltk, random, json , pickle
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
nltk.download('punkt');nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import flatten
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Activation,Dropout
from tensorflow.keras.optimizers import SGD

documents=None
words=None
classes=None

def process_data():
    global documents,words,classes
    #fetch patterns and tokenize them into words
    pattern=list(map(lambda x:x["patterns"],intents))
    words=list(map(word_tokenize,flatten(pattern)))
    #fetch classes i.e. tags and store in documents along with tokenized patterns 
    classes= flatten( [[x["tag"]]*len(y) for x,y in zip(intents,pattern)])
    documents=list(map(lambda x,y:(x,y),words,classes))
    #lower case and filter all the symbols from words
    words=list(map(str.lower,flatten(words)))
    words=list(filter(lambda x:x not in ignore_words,words))
    
    #lemmatize the words and sort the class and word lists                    
    words=list(map(stemmer.stem,words))
    words=sorted(list(set(words)))
    classes=sorted(list(set(classes)))
    pickle.dump(words, open('words.pkl','wb'))
    pickle.dump(classes, open('classes.pkl','wb'))
def train_data():
    #initialize and set analyzer=word as we want to vectorize words not characters
    cv=CountVectorizer(tokenizer=lambda txt: txt.split(),analyzer="word",stop_words=None)
    #create the training sets for model
    training=[]
    for doc in documents:
        #lower case and lemmatize the pattern words
        pattern_words=list(map(str.lower,doc[0]))
        pattern_words=' '.join(list(map(stemmer.stem,pattern_words)))

        #train or fit the vectorizer with all words
        #and transform into one-hot encoded vector
        vectorize=cv.fit([' '.join(words)])
        word_vector=vectorize.transform([pattern_words]).toarray().tolist()[0]

        #create output for the respective input
        #output size will be equal to total numbers of classes
        output_row=[0]*len(classes)

        #if the pattern is from current class put 1 in list else 0
        output_row[classes.index(doc[1])]=1
        cvop=cv.fit([' '.join(classes)])
        out_p=cvop.transform([doc[1]]).toarray().tolist()[0]

        #store vectorized word list long with its class
        training.append([word_vector,output_row])

    #shuffle training sets to avoid model to train on same data again
    random.shuffle(training)
    training=np.array(training,dtype=object)
    train_x=list(training[:,0])#patterns
    train_y=list(training[:,1])#classes
    print(train_y)
    return train_x,train_y 

def build():
    #load the data from train_data function
    train_x,train_y = train_data()
    
    ##Create a Sequential model with 3 layers. 
    model=Sequential()
    #input layer with latent dimension of 128 neurons and ReLU activation function 
    model.add(Dense(128,input_shape=(len(train_x[0]),),activation='relu'))
    model.add(Dropout(0.5)) #Dropout to avoid overfitting
    #second layer with the latent dimension of 64 neurons
    model.add(Dense(64,activation='relu')) 
    model.add(Dropout(0.5))
    #fully connected output layer with softmax activation function
    model.add(Dense(len(train_y[0]),activation='softmax')) 
    '''Compile model with Stochastic Gradient Descent with learning rate  and
       nesterov accelerated gradient descent'''
    sgd=SGD(lr=1e-2,momentum=0.9,nesterov=True)
    model.compile(loss='categorical_crossentropy',optimizer=sgd,metrics=['accuracy'])
    #fit the model with training input and output sets
    hist=model.fit(np.array(train_x),np.array(train_y),epochs=200,batch_size=10,verbose=1)
    #save model and words,classes which can be used for prediction.
    #model.save('chatbot_model.h5',hist)
    model.save(f'{os.getcwd()}\\chatbot_model.h5',hist)
    pickle.dump({'words':words,'classes':classes,'train_x':train_x,'train_y':train_y},
                open(f'{os.getcwd()}\\training_data.file',"wb"))


lemmatizer=WordNetLemmatizer()
factory = StemmerFactory()
stemmer = factory.create_stemmer()

#read and load the intent file
#data_file=open('intents.json').read()
data_file=open('job_intents.json').read()
intents=json.loads(data_file)['intents']
ignore_words=list("!@#$%^&*?")
process_data()
build()