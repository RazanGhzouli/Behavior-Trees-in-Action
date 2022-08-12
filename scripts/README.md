# README #

The followings are presented in this folder:

- [2020-mining-notebooks](2020-mining-notebooks) contains the artifacts for our paper [Behavior Trees in Action](https://dl.acm.org/doi/pdf/10.1145/3426425.3426942);

- [2022-mining-and-filter-scripts](2022-mining-and-filter-scripts) contains artifacts for our paper [Behavior Trees and State Machines in Robotics Applications](https://arxiv.org/pdf/2208.04211.pdf).

## Folder Structure: ##


```bash
scripts
│
├───2020-mining-notebooks (contains jupyter notebooks and other python scripts for GitHub minning and automatic metric calculation)
│	├───2020-rawdata	 
│	│	├───behaviortreecpp (contains the XML files that were minned for BehaviorTree.CPP library using GitHub minning script)
│	│	└───pytreeros (contains the python scripts that were minned for py_tree_ros library using GitHub minning script)
│	│
│	├───BT-mining-script.ipynb (mine github repos using Ipython)
│	│ 
│	└───composite-node-counting.ipynb (count composite nodes in BT models)
│	│ 
│	└───BT_mining_script_for_testing.py (mine github repos using python)
│	│ 
│	└───test.py (test script with multiple unit tests)
│	│ 
│	└───README.txt
│ 
├───2020-artifacts-instructions (pdf containing instrcutions for running "Behavior Trees in Action" artifacts)
│ 
└───2022-mining-and-filter-scripts (scripts for mining and filtering repos for our paper "Behavior Trees and State Machines in Robotics Applications")
```
