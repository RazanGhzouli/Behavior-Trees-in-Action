# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 15:45:38 2021

@author: Razan
"""
from github import Github
import pandas as pd
import argparse

import os.path
import re

from datetime import datetime


from nltk.corpus import stopwords
from nltk import word_tokenize
import string  


## a funcation to extract a repo description
def extract_desc(repos, ACCESS_TOKEN):
    print("------start extracting description-----")
    g = Github(ACCESS_TOKEN)
    descriptions = []
    for i in range(len(repos)):
        descrip = g.get_repo(repos.name[i]).description 
        if descrip == None:
            descriptions.append('no description')
        else:
            descriptions.append(descrip)
       
    repos['description'] = descriptions
    
    print("------finished extracting description-----")
    return repos
        
            
            
# ## defining a pre-processing function to clean description text
def clean(text = '', stopwords = []):
    
    #remove https links
    pattern=r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    #tokenize    
    tokens = word_tokenize(text.strip())
    
    #lowercase    
    clean = [i.lower() for i in tokens]
  
    #remove punctuation  
    punctuations = list(string.punctuation)
      
    ## exclusing +  # so langauges names don't get excluded like c++ or c#  
    clean = [i.strip(''.join(punctuations)) for i in clean if i not in punctuations] 
    clean = [re.sub(r'\W+', ' ', i) for i in clean]
    
    #remove stopwords    
    clean = [i for i in clean if i not in stopwords]
        
    return " ".join(clean)


## filter repo by finding the ones with course/assignment in their description
       
def match_word(text):
    
    desired_words = ['assignment', 'course', 'tutorial', 'introduction']    
    for i in desired_words:
        
        if i in text:
            
            return 'exclude'
        else:
            return 'include'            
            



def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(


        description="pass arguments for access token and file name that include the repo names to extract their description"

    )

    parser.add_argument(

        "-ac", "--accesstoken", required=False

    )
    
    parser.add_argument(

        "-f", "--file", required=True

    )

    return parser


def main(accesstoken =None , file=None):
    
    if accesstoken != None:
        ACCESS_TOKEN = accesstoken
    
    else:
        ACCESS_TOKEN = input("Enter your Github access token: ")

     
    ## read file
    cwd = os.getcwd()
    file_path = cwd + "\\" + file+ ".csv"
    repos = pd.read_csv(file_path, encoding = "utf-8")
    print("------successfully read file-----")
    
    # ### extract description   
    repos = extract_desc(repos,ACCESS_TOKEN)
    
    # #clean the description
    print("----start cleaning  text-----")
    repos['clean_desc'] = repos['description'].apply(str) #make sure description is a string
    repos['clean_desc'] = repos['clean_desc'].apply(lambda x: clean(text = x, stopwords = stopwords.words('english')))
    print("----finished cleaning  text-----")
    ## add include/exclude column when desired exclusion words are found in description
    print("-----start matching inclusion/exclusion words-----")
    repos['filter_desc'] = repos['clean_desc'].apply(match_word)
    print("-----finished matching inclusion/exclusion words-----")

    
    ## save result file
    ## formating the file name to desired format
    date = datetime.today().strftime('%d%m%Y')
    file = file.strip('csv')
    file = re.sub(r'\d+', '', file)
    repos.to_csv( file+ '_' +date+ '_description.csv')

    print("------saved extracted data to a csv file in current working directory-----")


if __name__ == '__main__':
    parser = init_argparse()

    args = parser.parse_args()
    
    main(accesstoken = args.accesstoken , file= args.file)