import pandas as pd
import requests
import os
from time import sleep

def df_to_dict(df):
    rv_dict = {}
    for index, row in df.iterrows():
        if row["name"] not in rv_dict:
            rv_dict[row["name"]] = [row["file_url"]]
        else:
            rv_dict[row["name"]].append(row["file_url"])
    return rv_dict

url_csv_df = pd.read_csv("../repo_file_URL/14012022_btcpp_RepoProjectNameURL.csv")
btcpp_url_dict_array = [df_to_dict(url_csv_df)]

url_csv_df = pd.read_csv("../repo_file_URL/13012022_flexbe_RepoProjectNameURL.csv")
flexbee_url_dict_array = [df_to_dict(url_csv_df)]

url_csv_df = pd.read_csv("../repo_file_URL/12012022_py_trees_ros_RepoProjectNameURL.csv")
pytreesros_url_dict_array = [df_to_dict(url_csv_df)]

url_csv_df = pd.read_csv("../repo_file_URL/12012022_smach_RepoProjectNameURL.csv")
smach_url_dict_array = [df_to_dict(url_csv_df)]


filtered_repos_btcpp = pd.read_csv("../5-filter_readme_completed/btcpp_RepoProjectNameHtmlCommitDate_29012022_readme.csv")
filtered_repos_flexbe = pd.read_csv("../5-filter_readme_completed/flexbe_RepoProjectNameHtmlCommitDate_29012022_readme.csv")
filtered_repos_pytrees_ros = pd.read_csv("../5-filter_readme_completed/py_trees_ros_RepoProjectNameHtmlCommitDate_29012022_readme.csv")
filtered_repos_smach = pd.read_csv("../5-filter_readme_completed/smach_RepoProjectNameHtmlCommitDate_29012022_readme.csv")

def replace_slashes(text):
    # return text.replace("/", "_")
    return text

filteredReposList = []
filteredReposList.extend(list(filtered_repos_btcpp["name"].apply(replace_slashes)))
filteredReposList.extend(list(filtered_repos_flexbe["name"].apply(replace_slashes)))
filteredReposList.extend(list(filtered_repos_pytrees_ros["name"].apply(replace_slashes)))
filteredReposList.extend(list(filtered_repos_smach["name"].apply(replace_slashes)))

def filter_dicts(unfiltered_url_dict_array, filtered_repos_list):
    rv = []
    for unfiltered_dict in unfiltered_url_dict_array:
        for key in unfiltered_dict:
            if key in filtered_repos_list:
                # key has not been filtered away, so needs to be added
                rv.extend(unfiltered_dict[key])
    return rv

btcpp_to_download = filter_dicts(btcpp_url_dict_array, filteredReposList)
flexbe_to_download = filter_dicts(flexbee_url_dict_array, filteredReposList)
pytreesros_to_download = filter_dicts(pytreesros_url_dict_array, filteredReposList)
smach_to_download = filter_dicts(smach_url_dict_array, filteredReposList)


def download_models(directory, model_urls):
    counter = 0
    max_counter = len(model_urls)
    for url in model_urls:

        while True:
            r = requests.get(url)
            if r.status_code == 200:
                print("Successfully retrieved: " + url)
                break
            elif r.status_code == 429:
                # too many requests
                retry_after = int(r.raw.headers._container['retry-after'][1]) + 10
                print("429 (too many requests): " + url + " retrying after " + str(retry_after))
                sleep(retry_after)
            elif r.status_code == 404:
                print("404 (not found): " + url)
                r = None
                break
            else:
                raise Exception("[ERROR] UNHANDLED STATUS CODE: " + str(r.status_code) + " (" + url + ")")
                #print("[ERROR] UNHANDLED STATUS CODE: " + str(r.status_code) + " (" + url + ")")

        if r is None:
            continue

        c = r.content
        split_url = url.split("/")
        split_url.pop(0)
        split_url.pop(0)
        split_url.pop(0)
        split_url.pop(2)
        save_path = split_url[0]

        for i in range(1, len(split_url)):
            save_path = save_path + "_" + split_url[i]

        if os.path.isfile(directory + save_path):
            # check if file has already been downloaded
            counter += 1
            print("Progress: " + str(round(counter / max_counter, 2)))
            continue

        try:
            open(directory + save_path, "wb").write(c)
        except OSError:
            # weird paths e.g. :
            # skm-wwry_orange_%E6%97%A0%E9%94%A1%E6%8D%B7%E6%99%AE-%E8%93%9D%E7%B2%BE%E7%81%B5%EF%BC%882%E3%80%819%E3%80%8110%E3%80%8111%E3%80%8114%E3%80%8115%E3%80%8116%E3%80%8117%E3%80%8118%E3%80%8119%EF%BC%89_%E8%93%9D%E7%B2%BE%E7%81%B510%E3%80%8111%E3%80%8114%E3%80%8115_src_agv_flexbe_behaviors_do_backward1m_sm.py
            save_path = split_url[0] + "_" + split_url[1] + "_" + split_url[-1]
            open(directory + save_path, "wb").write(c)

        counter += 1
        print("Progress: " + str(round(counter/max_counter,2)))

download_models("../6-downloaded_models/btcpp/", btcpp_to_download)
download_models("../6-downloaded_models/flexbe/", flexbe_to_download)
download_models("../6-downloaded_models/pytreesros/", pytreesros_to_download)
download_models("../6-downloaded_models/smach/", smach_to_download)

import winsound
winsound.Beep(2500, 1500)

