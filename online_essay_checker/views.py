from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
import language_tool_python
import pyrebase
# Create your views here.
# from spellchecker import SpellChecker

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
            d['corr']=rules.replacements
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

    score=((n_words-err_words)/n_words)*100
    # links = webScraper1(p)
    # import docx2txt
    # unseendocx = docx2txt.process(p)
    import spacy
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(p)
    # print(doc)
    queries = set({})
    queries_dict = {}
    for ent in list(doc.ents): 
        queries.add(ent.text)
        queries_dict[ent.text] = ent.label_
    print(queries)
    print(queries_dict)
    try: 
        from googlesearch import search 
    except ImportError:  
        print("No module named 'google' found") 
    
    # to search 

    from PyDictionary import PyDictionary
    dictionary=PyDictionary()

    query = ''
    to_ret = []
    syn=[]
    for i in queries:
        if(queries_dict[i] in ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE']):
            query = i
            syn.append(dictionary.synonym(query))
            for j in search(query, tld="co.in", num=1, stop=1, pause=2):
                print(j)
                to_ret.append(j)
            print()
    print(to_ret)
    print ()
    return render(request,'main_page.html',{'content': p,'matches':matches,'finals':err_corr,'num':len(err_corr),'links':to_ret,'syn':syn,'score':score})

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