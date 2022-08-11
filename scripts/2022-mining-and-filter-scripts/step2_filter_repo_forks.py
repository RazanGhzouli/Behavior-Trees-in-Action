from github import Github
from github import UnknownObjectException
from datetime import datetime
import pandas as pd


## a function to filter out forked repos
def run_filter(file_to_filter, output_file_included_excluded_path, output_file_included_only, g):
    repos = pd.read_csv(file_to_filter)

    filter_fork = []
    num_rows = len(repos.index)

    for index, row in repos.iterrows():
        print(f'Progress: {index+1}/{num_rows} rows.')
        try:
            github_response = g.get_repo(row['name'])
            filter_fork.append("exclude" if github_response.fork else "include")
        except UnknownObjectException:
            filter_fork.append("404")

    repos['filter_fork'] = filter_fork

    repos.to_csv(output_file_included_excluded_path, index=False)

    repos = repos[repos.filter_fork != "exclude"]
    repos = repos[repos.filter_fork != "404"]
    repos.to_csv(output_file_included_only, index=False)


if __name__ == '__main__':
    
    ## change to input files location
    FILES_TO_FILTER = ["../commit_dates_extraction/20012022_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                       "../commit_dates_extraction/20012022_smach_RepoProjectNameHtmlCommitDates.csv",
                       "../commit_dates_extraction/20012022_flexbe_RepoProjectNameHtmlCommitDates.csv",
                       "../commit_dates_extraction/20012022_btcpp_RepoProjectNameHtmlCommitDates.csv"]

    date = datetime.today().strftime('%d%m%Y')
    
    ## change below to where you want to save the filtered files
        
    ### output files with the tag for included and excluded repos
    OUTPUT_FILES_PATHS_INCLUDED_EXCLUDED = [f"../filter_repo_forks/included_excluded/{date}_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_forks/included_excluded/{date}_smach_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_forks/included_excluded/{date}_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_forks/included_excluded/{date}_btcpp_RepoProjectNameHtmlCommitDates.csv"]

    ### output files with the excluded repos removed. Only included repos in these files
    OUTPUT_FILES_PATHS_INCLUDED_ONLY = [f"../filter_repo_forks/{date}_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_forks/{date}_smach_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_forks/{date}_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_forks/{date}_btcpp_RepoProjectNameHtmlCommitDates.csv"]

    token = open("token.txt", "r").readline()
    g = Github(token)

    
    for i in range(len(FILES_TO_FILTER)):
        run_filter(FILES_TO_FILTER[i], OUTPUT_FILES_PATHS_INCLUDED_EXCLUDED[i], OUTPUT_FILES_PATHS_INCLUDED_ONLY[i], g)
        
        
        
        


