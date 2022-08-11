# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 10:30:45 2021

@author: Razan
"""


from github import Github
import pandas as pd
import requests
import argparse
import os.path
import re
from datetime import datetime
import time
from nltk.corpus import stopwords
from nltk import word_tokenize
import string  


# # extract deafult branch so we can access readme file for the main branch
def extract_branch(repos, ACCESS_TOKEN):

    print("------start extracting default branch-----")
    default_branch = []
    for i in range(len(repos)):
        repo = 'https://api.github.com/repos/' + repos.name.iloc[i]
        try: 
        
            response = requests.get(repo, headers={'Authorization': 'TOK: ACCESS_TOKEN'})
            default_branch.append(response.json()['default_branch'])
        except:

            print('Rate limited. Waiting to retry…')
            time.sleep(10)
            print('-------finished waiting-----')
            response = requests.get(repo,  headers={'Authorization': 'TOK: ACCESS_TOKEN'})
            default_branch.append(response.json()['default_branch'])

            
    ## add the  deafult branch name to dataframe as column
    repos['default_branch'] = default_branch  
    print("------finished extracting default branch-----")
    return repos
    

def download_readme(repos, g,library):    

    print("------start downloading readme-----")
    count = 0
    for i in range(len(repos)):
        repo = repos.name.iloc[i]     
        try:
            url = g.get_repo(repo).get_contents("README.md").download_url 
            
            r = requests.get(url)
            filename = 'readme.txt'
            ### change dir according to where to save. In the current style it is assumed to have a folder for each library files.
            open(os.path.join("../filter_repo_name/{library}_readme", os.path.basename(repo.replace('/','_')+'_'+ filename )) , "wb").write(r.content)
        except:
            filename = 'readme.txt'
            content = b"no readme file or other naming schema used"
            ### change dir according to where to save
            open(os.path.join("../filter_repo_name/{library}_readme", os.path.basename(repo.replace('/','_')+'_'+ filename )) , "wb").write(content)
            count += 1

    print("------number of files with no readme or using different naming schema than README.md is: {}".format(count))
    print("------finished downloading readme-----")





### defining a pre-processing function to clean description text
def clean(text = '', stopwords = []):
    
    #remove https links
    pattern=r"http\S+"
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


### filter repo by finding the ones with course/assignment in their readme
    
def match_word(text):
    
    desired_words = ['assignment', 'course', 'tutorial', 'introduction']   
    for i in desired_words:
        
        if i in text:
            
            return 'exclude'
        else:
            return 'include'



def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(


        description="pass arguments for access token and file name that include the repo names to extract their readme"

    )

    parser.add_argument(

        "-ac", "--accesstoken", required=False

    )
    
    parser.add_argument(

        "-f", "--file", required=True

    )

    return parser

    

def main(accesstoken =None , file=None):
    date = datetime.today().strftime('%d%m%Y')
    
    #### if you don't have the files with readme then uncomment below part and comment the other files names with readme
    # files = ["../filter_repo_name/py_trees_ros_RepoProjectNameHtmlCommitDate_21012022.csv",
    #          "../filter_repo_name/btcpp_RepoProjectNameHtmlCommitDate_21012022.csv",
    #          "../filter_repo_name/flexbe_RepoProjectNameHtmlCommitDate_21012022.csv",
    #          "../filter_repo_name/smach_RepoProjectNameHtmlCommitDate_21012022.csv"]
    
    
    #### if you don't have the files with readme then uncomment upper part and comment this part. These files should have the readme already for each file in a column
    files = ["../filter_repo_name/py_trees_ros_RepoProjectNameHtmlCommitDate_21012022_readme.csv",
             "../filter_repo_name/btcpp_RepoProjectNameHtmlCommitDate_21012022_readme.csv",
             "../filter_repo_name/flexbe_RepoProjectNameHtmlCommitDate_21012022_readme.csv",
             "../filter_repo_name/smach_RepoProjectNameHtmlCommitDate_21012022_readme.csv"]

    output_included_exclude = [f"../5-filter_readme_completed/included_excluded/py_trees_ros_RepoProjectNameHtmlCommitDate_{date}_readme.csv",
                               f"../5-filter_readme_completed/included_excluded/btcpp_RepoProjectNameHtmlCommitDate_{date}_readme.csv",
                               f"../5-filter_readme_completed/included_excluded/flexbe_RepoProjectNameHtmlCommitDate_{date}_readme.csv",
                               f"../5-filter_readme_completed/included_excluded/smach_RepoProjectNameHtmlCommitDate_{date}_readme.csv"]

    output_included_only = [f"../5-filter_readme_completed/py_trees_ros_RepoProjectNameHtmlCommitDate_{date}_readme.csv",
                               f"../5-filter_readme_completed/btcpp_RepoProjectNameHtmlCommitDate_{date}_readme.csv",
                               f"../5-filter_readme_completed/flexbe_RepoProjectNameHtmlCommitDate_{date}_readme.csv",
                               f"../5-filter_readme_completed/smach_RepoProjectNameHtmlCommitDate_{date}_readme.csv"]
    
    
    
    for i in range(len(files)):

        file = files[i]
        output_included_exclude_file = output_included_exclude[i]
        output_included_only_file = output_included_only[i]

        repos = pd.read_csv(file, encoding="windows-1252")
        print("------successfully read file-----") 
        
        ### uncomment below part to extract readme. If you have the files with readme then no need. Don't forget to uncomment the arguments in the main    
        # if accesstoken != None:
        #     ACCESS_TOKEN = accesstoken
        
        # else:
        #     ACCESS_TOKEN = input("Enter your Github access token: ")
        
        #### extract default branch to use for constructing the readme URL   
        # repos = extract_branch(repos,ACCESS_TOKEN)
        
        #### extract readme content
        # g = Github(ACCESS_TOKEN)
        # library = re.search("(py_trees_ros|btcpp|flexbe|smach)",file).group(0)
        # repos = download_readme(repos,g,library)
        
        ### save the result to file
        #### formating the file name to desired format
        # date = datetime.today().strftime('%d%m%Y')
        # file = file.strip('csv')
        # file = re.sub(r'\d+', '', file)
        # # repos.to_csv( file+ '_'+ date+ '_default_branch.csv')
        # repos.to_csv( file+  date+ '_default_branch.csv')
        # print("------saved extracted data to a csv file in current working directory-----")

        ####clean the readme
        print("----start cleaning readme text-----")
        repos['clean_readme'] = repos['readme'].apply(str) #make sure description is a string
        repos['clean_readme'] = repos['clean_readme'].apply(lambda x: clean(text = x, stopwords = stopwords.words('english')))
        print("----finished cleaning readme text-----")
        # add include/exclude column when desired exclusion words are found in readme
        print("-----start matching inclusion/exclusion words-----")
        repos['filter_readme'] = repos['clean_readme'].apply(match_word)
        print("-----finished matching inclusion/exclusion words-----")
        
        #### save the result to file
        repos.to_csv(output_included_exclude_file, index=False)   
        repos = repos[repos.filter_readme != "exclude"]
        repos.to_csv(output_included_only_file, index=False)
    
        print("------saved extracted data to a csv file in current working directory-----")
        
            
            
   

           
   
    
if __name__ == '__main__':
    
    #### uncomment arguments parser below part if you need to extract readme. If you have the files with readme then no need. Just change th input files to their location

    #parser = init_argparse()

    #args = parser.parse_args()
    
    #main(accesstoken = args.accesstoken , file= args.file)
    
    main()

