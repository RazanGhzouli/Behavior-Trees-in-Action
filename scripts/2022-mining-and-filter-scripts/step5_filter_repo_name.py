import pandas as pd
import string
import re
from datetime import datetime


## a function to clean repo name from specific characters and digits

def clean(text):
    rv = re.split('['+string.punctuation+string.digits+']', text)
    rv = [element.lower() for element in rv]
    return rv


## a function to tag repos with desired words with either include or exclude

def match_word(text):
    desired_words = ["course", "introduction", "tutorial", "assignment", "intro",
                     "courses", "introductions", "tutorials", "assignments", "intros"]

    for i in desired_words:
        if i in text:
            return 'exclude'

    return 'include'

## a function to apply filter

def run_filter(file_to_filter, output_file_included_excluded_path, output_file_included_only):
    repos = pd.read_csv(file_to_filter)

    repos['clean_name'] = repos['name'].apply(clean)
    repos['filter_name'] = repos['clean_name'].apply(match_word)

    repos = repos.drop(columns='clean_name')
    repos.to_csv(output_file_included_excluded_path, index=False)

    repos = repos[repos.filter_name != "exclude"]
    repos.to_csv(output_file_included_only, index=False)


if __name__ == '__main__':
    
    ## change to input files location
    FILES_TO_FILTER = ["../filter_repo_tool/21012022_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                        "../filter_repo_tool/21012022_smach_RepoProjectNameHtmlCommitDates.csv",
                                        "../filter_repo_tool/21012022_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                        "../filter_repo_tool/21012022_btcpp_RepoProjectNameHtmlCommitDates.csv"]

    date = datetime.today().strftime('%d%m%Y')
    
    
    ## change below to where you want to save the filtered files
        
    ### output files with the tag for included and excluded repos
    OUTPUT_FILES_PATHS_INCLUDED_EXCLUDED = [f"../filter_repo_name/included_excluded/{date}_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_name/included_excluded/{date}_smach_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_name/included_excluded/{date}_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_name/included_excluded/{date}_btcpp_RepoProjectNameHtmlCommitDates.csv"]
    
    ### output files with the excluded repos removed. Only included repos in these files

    OUTPUT_FILES_PATHS_INCLUDED_ONLY = [f"../filter_repo_name/{date}_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_name/{date}_smach_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_name/{date}_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_name/{date}_btcpp_RepoProjectNameHtmlCommitDates.csv"]

    for i in range(len(FILES_TO_FILTER)):
        run_filter(FILES_TO_FILTER[i], OUTPUT_FILES_PATHS_INCLUDED_EXCLUDED[i], OUTPUT_FILES_PATHS_INCLUDED_ONLY[i])






