from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
import language_tool_python
import docx2txt
import spacy
import re
from bs4 import BeautifulSoup
import requests
import re
import multiprocessing
import time
import nltk
from nltk.stem.snowball import SnowballStemmer
import numpy as np
import pandas as pd
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfVectorizer
from PyDictionary import PyDictionary
nltk.download('words')
nltk.download('stopwords')
nltk.download('punkt')
try: 
  from googlesearch import search 
except ImportError:  
  print("No module named 'google' found") 
import pyrebase
# Create your views here.
# from spellchecker import SpellChecker

nlp = spacy.load("en_core_web_md")

config = {
        "apiKey": "AIzaSyBYJJBXd5Fzfo3KOfOn_L6pC5gLk8cFir8",
        "authDomain": "vrite4u-aa22c.firebaseapp.com",
        "projectId": "vrite4u-aa22c",
        "storageBucket": "vrite4u-aa22c.appspot.com",
        "messagingSenderId": "887727054072",
        "appId": "1:887727054072:web:977987de4a5bdf561d6f0d",
        "measurementId": "G-FSTHP6N3DZ",
        "databaseURL":"https://vrite4u-aa22c-default-rtdb.firebaseio.com/"

    }
firebase=pyrebase.initialize_app(config) 
authe = firebase.auth() 
database=firebase.database() 

email = ""

def index(request):
    email  = database.child('users').child('0').child('email').get().val()
    phone = database.child('users').child('0').child('phone').get().val()
    return render(request,'main_page.html')

def profile(request):
    arr = range(0,12)
    # em = request.GET['email']
    email = request.GET['email']
    return render(request,'user_profile.html',{'arr': arr,'email':email })


def check(request):
    p = ""
    lis = []
    tool = language_tool_python.LanguageTool('en-US')
    p = request.GET['para']
    p=p.lstrip()
    p=p.rstrip()
    print(p)
    err_corr={}
    matches = tool.check(p)
    
    # score
    for i in range(len(matches)):
        rules=matches[i]
        d={}
        if len(rules.replacements)>0:
            d['start']=rules.offset
            d['end']=rules.errorLength+rules.offset
            d['error_text']=p[rules.offset:rules.errorLength+rules.offset]
            if((d['error_text']=='')or(d['error_text']==' ')):
                continue
            d['corr']=rules.replacements
            if((d['corr']==' ')or(len(d['corr'])==0)):
                continue
            d['cat']=rules.category
            d['first'] = rules.sentence[:rules.offset]
            d['last'] = p[rules.errorLength+rules.offset:len(rules.sentence)]
            err_corr[i+1]=d
            print(d)
    links = []
    import re
    n_words = len(re.findall(r'\w+', p))
    err_words=0
    for i in err_corr:
        err_txt=err_corr[i]['error_text']
    #print(err_txt)
        err_words += len(re.findall(r'\w+', err_txt))

    score=int(((n_words-err_words)/n_words)*100)
    # links = webScraper1(p)
    # import docx2txt
    # unseendocx = docx2txt.process(p)
    vocab_dict , arr = textProcessing(p)
    tf = computeTF(vocab_dict,arr)
    idf = computeIDF([vocab_dict])
    tfidf = computeTfidf(tf,idf)
    print("Finished TFIDF")
    NER = ner(p)
    print("Finished NER")
    #terms = clustering(p)
    #print("Finished Clustering")
    print(list(NER)+list(tfidf)) #theme NER-named entities TFIDF-freq TERMS-clustering
    queries = list(NER)+list(tfidf)
    for i in range(len(queries)):
        queries[i] = queries[i].lower() 
    queries = list(set(queries))#theme remove duplicates
    print("Score:",score)
    #v = scrape_queries(queries,unseen_document) #links %time print the time
    return render(request,'main_page.html',{'content': p,'matches':matches,'finals':err_corr,'num':len(err_corr),'themes':queries, 'themes_len':len(queries),'score':score})

def signIn(request): 
    return render(request,"login.html") 
def home(request): 
    return render(request,"main_page.html") 
  
def postsignIn(request): 
    email=request.POST.get('email') 
    pasw=request.POST.get('pass') 
    try: 
        # if there is no error then signin the user with given email and password 
        user=authe.sign_in_with_email_and_password(email,pasw) 
    except: 
        message="Invalid Credentials!!Please ChecK your Data"
        print(message)
        return render(request,"login.html",{"message":message}) 
    session_id=user['idToken'] 
    request.session['uid']=str(session_id) 
    return render(request,'main_page.html',{"email":email}) 
  
def logout(request): 
    try: 
        del request.session['uid'] 
    except: 
        pass
    return render(request,"login.html") 
  
def signUp(request): 
    return render(request,"register.html") 
  
def postsignUp(request): 
    email = request.POST.get('email') 
    passs = request.POST.get('pass') 
        #  name = request.POST.get('name') 
    try: 
            # creating a user with the given email and password 
        user=authe.create_user_with_email_and_password(email,passs) 
        uid = user['localId'] 
        idtoken = request.session['uid'] 
        print(uid) 
    except:
        # print('hello') 
        return render(request, "login.html") 
    return render(request,"login.html")

def about(request):
    return render(request,'about.html')

def ner(unseen_document): #named entity
  nlp = spacy.load("en_core_web_md")
  doc = nlp(unseen_document)
  queries = set({}) #search keywords
  for ent in doc.ents: 
    if(ent.label_ in ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE']):
      queries.add(ent.text)
  return queries #txt of named entities

def scrape_helper(url,text):
  page = requests.get(url)
  soup = BeautifulSoup(page.content, 'html.parser') #DOM retrieval
  page_body = soup.body
  regex = "<(\"[^\"]*\"|'[^']*'|[^'\">])*>"
  words = set(nltk.corpus.words.words())
  page_body = " ".join(w for w in nltk.wordpunct_tokenize(str(page_body)) \
           if w.lower() in words or not w.isalpha()) #extraxting meaningful words
  page_body = re.sub(regex,'',str(page_body)).replace('\n','') #rem HTML tags
  page_body = page_body.replace('\t',' ')

  # print(page_body)
  text[url] = page_body #entire scrape helper

def scrape(url):
  manager = multiprocessing.Manager()
  return_dict = manager.dict()
  # text = multiprocessing.Value(c_char_p, "".encode(), lock=False)
  p = multiprocessing.Process(target=scrape_helper, args=(url,return_dict,))
  p.start()

  p.join(10)

  if p.is_alive():
    p.terminate()
    p.join()
  return return_dict[url]

def scrape_queries(q,unseen_document):
  to_ret = {}
  doc=nlp(unseen_document)
  links = search(q, tld="co.in", num=1, stop=5, pause=2)
  visited = []
  for j in links:
    if j in visited:
        break
    visited.append(j)
    try:
        print(j)
        scrape_nlp = nlp(str(scrape(j)))
        # print(scrape_nlp)
        sim = scrape_nlp.similarity(doc)
        print(sim,j)
        if (sim>0.7):
            to_ret[sim]=j
            #print(to_ret[sim])
        else:
            break
    except:
        continue
  print(to_ret)
  return to_ret

def textProcessing(doc):
    # Reference: https://github.com/AjayJohnAlex/Keyword-Extraction/blob/master/model.py
    '''Prepocessing of input text with 
    1. tokenisation and Lemmatisation
    2. Removing stop words 

    3. Creating and removing custom stop words.
    4. Generating required Vocabulary from input
    5. Preprocessing the input 
    '''
    Nouns = []
    Noun_set = []
    trimmed_noun_set = []
    removing_duplicates = []
    arr = []
    vocab = []
    vocab_dict = {}

    doc = nlp(doc.upper())

    for possible_nouns in doc:
        if possible_nouns.pos_ in ["NOUN","PROPN"] :
            Nouns.append([possible_nouns , [child for child in possible_nouns.children]])
       
    
    for i,j in Nouns:
        for k in j:
            Noun_set.append([k,i])

    
    for i , j in Noun_set:
        if i.pos_ in ['PROPN','NOUN','ADJ']:
            trimmed_noun_set.append([i ,j])
            
    
    for word in trimmed_noun_set:
        if word not in removing_duplicates:
            removing_duplicates.append(word)
    
    
    for i in removing_duplicates:
        strs = ''
        for j in i:
            strs += str(j)+" "
        arr.append(strs.strip())

    
    for word in Noun_set:
        string = ''
        for j in word:
            string+= str(j)+ " "
        vocab.append(string.strip())

    
    for word in vocab:
        vocab_dict[word]= 0
        
    for word in arr:
        vocab_dict[word]+= 1

    return vocab_dict , arr

def computeTF(wordDict,bow):
    '''Computing TF(Term Frequency of the vocab) '''
    tfDict = {}
    bowCount = len(bow)
    for word, count in wordDict.items():
        tfDict[word] = count/float(bowCount)
    return tfDict


def computeIDF(doclist):
    '''Computing IDF for the vocab '''
    import math 
    count = 0
    idfDict = {}
    for element in doclist:
        for j in element:
            count+=1
    N = count

    # count no of documents that contain the word w
    idfDict = dict.fromkeys(doclist[0].keys(),0)

    for doc in doclist:
        for word,val in doc.items():
            if val>0:
                idfDict[word]+= 1

    # divide N by denominator above
    for word,val in idfDict.items():
        if val == 0:
            idfDict[word] = 0.0
        else:
            idfDict[word] = math.log(N / float(val))

    return idfDict

def computeTfidf(tf,idf):
    '''Computing TF-IDF for the words in text '''
    tfidf = {}
    sorted_list = []
    for word , val in tf.items():
        tfidf[word] = val * idf[word]

    ranking_list  = sorted(tfidf.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))[:10]
    for i, _ in ranking_list:
        sorted_list.append(i)

    return sorted_list

def synlinks(request):
    query=request.GET.get('keyword')
    p=request.GET.get('para')
    ldict = scrape_queries(query,p)
    links=[]
    
    for i in sorted(ldict.keys()):
        links.append(ldict[i])
    if(len(links)==0):
        links.append("No relevant links found")
    elif(len(links)>5):
        links=links[:5]
    ql=query.split()
    s=[]
    for q in ql:
        s+=getsyn(q)
    print(links)
    res={'links':links,'synonyms':s}
    print(res)
    return JsonResponse({'Result':res})

def getsyn(word):
    dictionary=PyDictionary()
    l=list(dictionary.synonym(word))
    if(len(l)>5):
        l=l[:5]
    return l

def upload_files(request):
    p=""
    if(request.method == "POST"):
        n = request.FILES['notesfile']
        p=n.read().decode('utf-8')
        p=p.strip('\n')
    #p = Notes()
    #p.notesfile = n
    return render(request,'main_page.html',{'content':p})
