# README #


# Behavior Trees in Action: A Study of Robotics Applications artifacts evaluation README #
First go to "artifact-evaluation" folder in the online appendix: https://github.com/RazanGhzouli/Behavior-Trees-in-Action 
download it

This document presents an overview of the submitted artifacts. 
The following are presented:

1. Folder structure with an overview of folders content. 
2. Instruction on how to run the GitHub minning script and the automatic metric calculation script mentioned in Section 3.2 in the paper.

## Folder Structure: ##


```bash
artifact-evaluation
│
├───notebooks (contains jupyter notebooks for GitHub minning and automatic metric calculation)
│ 
└───rawdata	 
	├───behaviortreecpp (contains the XML files that were minned for BehaviorTree.CPP library using GitHub minning script)
	└───pytreeros (contains the python scripts that were minned for py_tree_ros library using GitHub minning script)
```

## Instruction for running GitHub minning script and the automatic metric calculation script
There are two way to run these scripts depending on the host machine settings:
1. If you have a running jupyter notebook on your machine then run the application and move the scripts (BT_mining_script.ipynb and composite_node_counting.ipynb) in notebooks folder to your jupyter working directory.	
2. If you do not have jupyter notebook on your machine, then follow the "Instruction for running docker image" section.
 
## Instruction for running docker image ##

## prerequisite ##

1. Docker (can be installed using the following link https://docs.docker.com/get-docker/)

## Running docker ##
1. After installing docker, open docker for desktop.
2. open your command line and test that docker is working by checking docker versio:
```
	docker --version
```
3. After making sure your docker is running, use your command line to pull the docker image that contains the jupyter notebooks:
```
	docker pull razangh/2020-beahviortree-script:latest
```
4. After pull complete, use your command line to run the docker image: 
```	
	docker run -p 8888:8888	 razangh/2020-beahviortree-script
```
5. You should get an output similar to the following
```
	Set username to: jovyan
	usermod: no changes
	Executing the command: jupyter notebook
	[I 18:31:05.907 NotebookApp] Writing notebook server cookie secret to /home/jovyan/.local/share/jupyter/runtime/notebook_cookie_secret
	[I 18:31:06.365 NotebookApp] JupyterLab extension loaded from /opt/conda/lib/python3.8/site-packages/jupyterlab
	[I 18:31:06.365 NotebookApp] JupyterLab application directory is /opt/conda/share/jupyter/lab
	[I 18:31:06.367 NotebookApp] Serving notebooks from local directory: /home/jovyan/src/notebooks
	[I 18:31:06.367 NotebookApp] Jupyter Notebook 6.1.3 is running at:
	[I 18:31:06.368 NotebookApp] http://xxxxxx:8888/?token=xxxxxx
	[I 18:31:06.368 NotebookApp]  or http://127.0.0.1:8888/?token=xxxxxx
	[I 18:31:06.368 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
	[C 18:31:06.371 NotebookApp]
	To access the notebook, open this file in a browser:
			file:///home/jovyan/.local/share/jupyter/runtime/nbserver-14-open.html
		Or copy and paste one of these URLs:
			http://xxxxxx:8888/?token=.xxxxxx
	or http://127.0.0.1:8888/?token=.xxxxxx
	
```	

6. Use the link the starts with "http://127.0.0.1:8888/..." to access jupyter.

7. Open the script "BT_mining_script.ipynb" to run the GitHub mine script. Comments are provided in the file to guide you how to run it.
If you get the error "BadCredentialsException: 401 " when running "BT_mining_script.ipynb", please change the GitHub token in the second cell.
8. Open the script "composite_node_counting.ipynb" to run the node count script. Comments are provided in the file to guide you how to run it.
