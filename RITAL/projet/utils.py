import re
import unicodedata
import string
import nltk
import spacy
import os.path

def preprocess(text, lemma = False):
    """
    Transforms text to remove unwanted bits.
    """
    
    # Characters suppression 
    
    # Non normalized char suppression 
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    
    # Lowercase transformation
    text = text.lower()

    # Punctuation suppression
    translation_table = str.maketrans("", "", string.punctuation + '\n\r\t')
    text = text.translate(translation_table)
    
    # Digits suppression
    text = re.sub(r'\d', '', text)
    # Use the sub function to replace double spaces with single spaces
    text = re.sub(r'\s+', ' ', text)
 
    if lemma:
        nlp = spacy.load("en_core_web_sm")
        lemmatised_text = nlp(text)
        text = [str(word.lemma_) for word in lemmatised_text]
        text = ' '.join(text)
    
    return text

def load_movies(path2data): # 1 classe par répertoire
    alltxts = [] # init vide
    labs = []
    cpt = 0
    for cl in os.listdir(path2data): # parcours des fichiers d'un répertoire
        for f in os.listdir(path2data+cl):
            txt = open(path2data+cl+'/'+f).read()
            alltxts.append(txt)
            labs.append(cpt)
        cpt+=1 # chg répertoire = cht classe
        
    return alltxts,labs
