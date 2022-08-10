# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:27:47 2021

@author: Razan
"""

import github 
from github import Github
import pickle
import argparse
from datetime import datetime
import pandas as pd
import time


def access_token(token):
    ACCESS_TOKEN = token ## enter your githun token
    g = Github(login_or_token  = ACCESS_TOKEN)
    
    try:
        repo = g.get_repo("PyGithub/PyGithub")
        if repo.full_name == "PyGithub/PyGithub":
#         print(repo.full_name)#
            print("Access token works")
            return g
    except github.GithubException as e:
        
        if (e.data['message']=='Bad credentials'):
            print("Please provide a working access token")
        else:
            print (e)
 
        
#### a function to save mined library name
def library_name():
    library = input('Enter the desired library name to use as indication in files name. Do not use space in name use either _ or camel case schema: ')
    return library







### a function to query github by entering a specific string to search on files level
def query_github(g, keywords = None):
    g= g 
    if keywords is None:
        keywords = input('Enter keyword(s)[e.g py_trees_ros, main_tree_to_execute], file extension if needed, and size. Separate using comma: ')
    else:
        keywords = keywords
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    if len(keywords)>1:
         query = f'"{keywords[0]}" in:file extension:{keywords[1]} size:{keywords[2]}'
         
    else: 
        query = f'"{keywords}" in:file'
        
    
        
    rate_limit = g.get_rate_limit()
    rate = rate_limit.search
    if rate.remaining == 0:
        print(f'You have 0/{rate.limit} API calls remaining. Reset time: {rate.reset}.')      
        print("\nWaiting for an hour to restore rate limit.....")
        time.sleep(3600)
        
    else:
        print(f'You have {rate.remaining}/{rate.limit} API calls remaining')
        time.sleep(10)
    
    print("Start query." )    
    result = g.search_code(query, order='desc')
    time.sleep(10)
    print("Query finished.")
    print(f'Found {result.totalCount} file(s)')
    print("------------------------------------------------------------------------------")
    time.sleep(10)


    return result 


### a function to extract found files urls and repos names and save for later use in pickle format
def extract_url_repoName(result, library, date):
    new_repo = {}
    print("Start extracting found files URL and repos names." )
    for file in result:
        url = file.download_url 
        time.sleep(5)
        repo_name = file.repository.full_name
#        time.sleep(5)
    
        if repo_name in new_repo:
        ### append the new url to the existing array at this slot
            new_repo[repo_name].append(url)
        else:
        ### create a new array in this slot
            new_repo[repo_name] = [url]
            # time.sleep(5)
        print("moving to next result" )

  
    ### saving the found results 
    f = open( date+ "_" + library + "_repoName_plus_URL"+ ".pkl","wb")   
    pickle.dump(new_repo,f)
    f.close()  
    print("A file containing repos names and files URL was saved to your working directory")
    print("------------------------------------------------------------------------------")
    print("The number of repository: {}".format(len(new_repo)))
    print("The number of files: {}".format(sum(len(dct) for dct in new_repo.values() )))
    print("------------------------------------------------------------------------------")
    
    
    html = "https://github.com/"
    repo_html_df = pd.DataFrame( list(zip([key for key, value in new_repo.items()], [html+key for key, value in new_repo.items()])), columns= ['name','html_link'])

    ## create csv with names and found files url links

    repo_file_df = pd.concat({key: pd.Series(value) for key, value in new_repo.items()}).reset_index()
    repo_file_df = repo_file_df.drop(columns=["level_1"])

    repo_file_df.columns = ['name' , 'file_url' ]


    
    ### Save the extracted info to excel
    
    repo_html_df.to_csv(date + "_"+ library +"_RepoProjectNameHtml.csv")
    repo_file_df.to_csv(date + "_"+ library +"_RepoProjectNameURL.csv")

    print("A CSV containing repos name and found file URL was saved to your working directory")
    print("------------------------------------------------------------------------------")
    
    
    
    return new_repo

# #### uncomment this part and related part in main if you want to limit number of returned results
# def limit_result_size(result, desired_size):    
#     max_size = desired_size  
#     if result.totalCount >= max_size:
#         print(f'The number of mined GitHub files is {result.totalCount} and it was limmited to {max_size} ')
#         return result[:max_size]




# #### a function to specify save path location for downloaded files
# def save_path():
#     savePath = input('Enter the desired save path for downloading the found files: ')
#     return savePath

# ### a function to download found files content   
# def download_models(savePath, url_repo_name_dict,repoName_html_sha, token,username ):
#     file_count = 0
    
#     print("Start downloading found files." )
#     for key,value in url_repo_name_dict.items():
        
#         ###getting the sha number for the specific commit point in repo where the mining was done earlier
#         sha_index = repoName_html_sha.index[repoName_html_sha['name'] == key]
#         sha = {'tree' : repoName_html_sha.sha[sha_index][0] }
        
#         ####download the file content at specific point in the repo
#         for i in range(len(value)):
#             r = requests.get(value[i],sha, auth=HTTPBasicAuth(username, token))
#             ### if you want to change the path where files are saved change  "/home/jovyan/src/notebooks/downloads/pytreeros" to where you want, also for XML fromat files change the re.search to xml instead of py 
#             # open(os.path.join(savePath, os.path.basename(key.replace('/','_')+'_'+(re.search('/(\w*((%20\w)*)?.py)', value[i]).group(1)))) , "wb").write(r.content)
#             open(os.path.join(savePath, os.path.basename(key.replace('/','_')+'_'+value.split("/")[-1])) , "wb").write(r.content)

#             file_count += 1
#     print("Finished downloading found files." )
#     print("------------------------------------------------------------------------------")
#     print("Download complete for {} files".format(file_count))
#     print("------------------------------------------------------------------------------")
    
    


def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(

        description="pass arguments for access token,  query string and library name "


    )

    parser.add_argument(

        "-ac", "--accesstoken", required=False

    )
    
    parser.add_argument(

        "-q", "--query", required=False

    )
    
    
    
    parser.add_argument(

        "-l", "--library", required=False
        

    )
    
    parser.add_argument(

        "-p", "--savePath", required=False
        

    )

    return parser

    

def main(accesstoken =None , query = None, library = None ,savePath = None):
    
    
    
    ### access token and query Github 
    if accesstoken != None:
        token = accesstoken
        g = access_token(token)
    
        result = query_github(g, keywords = query)
    else:
#        token = open("token.txt", "r").readline()
        token = input("Enter your Github access token: ")
        g = access_token(token)
           
        result = query_github(g,keywords= None)
        
        
    
    
    ### today's date for later saved file formating
    date = datetime.today().strftime('%d%m%Y') 
    ### change here depending on number of files that you want to download. GitHub API has a limit of maximum 1000 files
    # desired_size = 1000
    # result = limit_result_size(result, desired_size) 
    
    
    ### for later file naming enter the mined library name
    
    if library != None:
        ### extract found files url and repos names
        url_repo_name_dict= extract_url_repoName(result,library,date)
    else:
        ### enter save path
        # library = "ADDNAME"
        library = library_name()
        ### extract found files url and repos names
        url_repo_name_dict= extract_url_repoName(result,library,date)
    

    
    # ### extract found repos name, sha and html link 
    # repoName_html_sha = extract_repolink_name_sha(g,result,library,date)
    
    # ### save found files path
    # if savePath != None:
    #     ### download the found files
    #     download_models(savePath, url_repo_name_dict, repoName_html_sha, token, username)
    # else:
    #     ### enter save path
    #     # savePath = "C:/Users/Razan/Behavior-Trees-in-Action/scripts/notebooks/models/"
    #     savePath = save_path()
    #      ### download the found files
    #     download_models(savePath, url_repo_name_dict, repoName_html_sha ,token, username )
        
    
    
    

if __name__ == '__main__':
    parser = init_argparse()

    args = parser.parse_args()
    
    main(accesstoken = args.accesstoken , query= args.query, library=args.library,savePath = args.savePath)

    



