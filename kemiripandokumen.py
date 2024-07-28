import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import numpy as np
import sys
import re
import string
import Sastrawi
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from functools import lru_cache
import time

stop_factory = StopWordRemoverFactory()
stopword = stop_factory.create_stop_word_remover()
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def preprocessing_data(data):
    data = data.lower()
    # remove tab, new line, ans back slice
    text = data.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"")
    # remove non ASCII (emoticon, chinese word, .etc)
    text = data.encode('ascii', 'replace').decode('ascii')
    # remove mention, link, hashtag
    text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
    text = text.replace("http://", " ").replace("https://", " ")
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("","",string.punctuation))
    text = text.strip()
    text = re.sub('\s+',' ',text)
    text = re.sub(r"\b[a-zA-Z]\b", "", text)
    text = stopword.remove(text)
    text = stemmer.stem(text)
    text = word_tokenize(text)

    kali=""

    for i in text:
      kali+=" "+i
    return kali

def to_dictionary():
    df = pd.read_csv('dictionary1.csv')
    kata_kamus = df['kata']
    sinonim = df['sinonim']
    pass
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    dif = distances[-1]
    cs = max(len(s1), len(s2))
    akurasi=str(((cs-dif)/cs)*100)[:5]
    return dif,cs,akurasi
def to1d(arr):
    sino=[]
    for i in arr:
        sino=sino+i
    return sino

def getidx(book):
    index=[]
    count=0
    for i in book.keys():
        for j in range (len(book[i])):
            index.append(count)
        count+=1
    return index
def aturbuku(buku):
    key=list(buku.keys())
    val=list(buku.values())

    sinom=to1d(val)
    idx=getidx(buku)

    return key, [sinom,idx]

def thesakurus(kalimat, dasar, sincro):
    sinom=sincro[0]
    idx=sincro[1]
    newdata=""
    lkt=[]
    lst=kalimat.split()

    daftar_deteksi=[]
    c=1
    for i in lst:
        if newdata == "":
            spc=""
        else:
            spc=" "

        if i in dasar:
            newdata=newdata+spc+str(i)
        elif i in sinom:
            ktdasar=dasar[idx[sinom.index(i)]]
            newdata=newdata+spc+str(ktdasar)
            daftar_deteksi.append(c)
            lkt.append(i+" > "+ktdasar)
        else:
            newdata=newdata+spc+str(i)
        c+=1
        #return 1kt,daftar_deteksi
    #st.text_area("Kata data pembanding yang diubah :", daftar_deteksi, height=100)
    return newdata
def baca_dikti(direk):
    book = pd.read_csv(direk)
    dasar=list(book["kata"])
    sinom=list(book["sinonim"].apply(lambda x: str(x).split("|")))
    book= dict(zip(dasar,sinom))
    return book

with open ('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html = True)

st.markdown(f'<h1 style="color:#0C81DE;font-size:36px;">{"Sistem Deteksi Kemiripan Teks"}</h1>', unsafe_allow_html=True)


st.sidebar.subheader("Sistem Deteksi Kemiripan Teks")

with st.sidebar:
    selected = option_menu (
        menu_title= "Menu",
        options=["Deteksi Kemiripan","Data Uji", "Data Pembanding"],
        icons=['list-task', 'list-task', 'list-task'],
        styles={
            "container": {"padding": "10px", "background-color": "#fafafa"},
            "icon": {"color": "black"}, 
            "nav-link": {"text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#0C81DE"},
        }
    )
if selected=="Data Uji":
    #st.text_input('Data Uji')
    df = pd.read_excel("data_uji.xlsx")
    st.dataframe(df,width=2000, height=1000)
dfUji = pd.read_excel("data_uji.xlsx")
dfBanding = pd.read_excel("Teks Berita_indra.xlsx")
du = [str(i) for i in dfUji['Judul']]
dp = [str(i) for i in dfBanding['Judul']]

if selected=="Data Pembanding":
    st.markdown('Data Pembanding')
    df = pd.read_excel("Teks Berita_indra.xlsx")
    st.dataframe(df,width=2000, height=1000)

if selected=="Deteksi Kemiripan":
    st.markdown('Similarity')
    with st.form("my_form"):
        dokumen1Input = st.selectbox("Masukkan Judul Data Uji: ",(du))
        dokumen2Input = st.selectbox("Masukkan Judul Data Pembanding: ", (dp))
        pakai_sinonim = st.checkbox('Pakai Sinonim')
        submitted = st.form_submit_button("Proses")
        if submitted:
            if pakai_sinonim:
                stime = time.time()
                df = pd.read_excel('Teks Berita_indra.xlsx')
                bok = baca_dikti('dictionary1.csv')
                dasar, sino = aturbuku(bok)
                berita = df['Berita']
                judul = df['Judul']
                akl=[]
                c=1
                dataUji=df.loc[df['Judul'] == dokumen1Input, 'Berita']
                dataBanding=df.loc[df['Judul'] == dokumen2Input, 'Berita']
                a=dataUji.iloc[0]
                b=dataBanding.iloc[0]
                dokumen1 = preprocessing_data(a) 
                dokumen2 = preprocessing_data(b)
                dasar1 = thesakurus(dokumen1, dasar,sino)
                dasar2 = thesakurus(dokumen2,dasar,sino)
                pd1=dasar1.split(" ")
                pd2=dasar2.split(" ")
                df,cs,ak=levenshteinDistance(pd1,pd2)
                etime = time.time()
                elapsedTime = etime-stime

                c+=1
                
                st.text_area("Dokumen Uji :", a, height=500)
                st.write('diubah ke dasar :', pd1)
                st.text_area("Dokumen Pembanding :", b, height=500)
                st.write('diubah ke dasar :', pd2)
                st.write('**Levenshtein Distance**')
                st.write('Distance: ', df)
                st.write('Similarity: ',ak)
                st.write ('Waktu Eksekusi: ', elapsedTime, ' detik.')
            else:
                stime = time.time()
                df = pd.read_excel('Teks Berita_indra.xlsx')
                
                berita = df['Berita']
                judul = df['Judul']
                dataUji=df.loc[df['Judul'] == dokumen1Input, 'Berita']
                dataBanding=df.loc[df['Judul'] == dokumen2Input, 'Berita']
                a=dataUji.iloc[0]
                b=dataBanding.iloc[0]
                akl=[]
                c=1
                dokumen1 = preprocessing_data(a) 
                dokumen2 = preprocessing_data(b)
                
                pd1=dokumen1.split(" ")
                pd2=dokumen2.split(" ")
                df,cs,ak=levenshteinDistance(pd1,pd2)
                etime = time.time()
                elapsedTime = etime-stime

                c+=1
                st.text_area("Dokumen Uji :",a, height=500)
                st.text_area("Dokumen Pembanding :", b, height=500)
                st.write('**Levenshtein Distance**')
                st.write('Distance: ', df)
                st.write('Similarity: ',ak)

                st.write ('Waktu Eksekusi: ', elapsedTime, ' detik.')
