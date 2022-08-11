import pandas as pd
from datetime import datetime

## a function to tag duplicate repos  that have same project name with either include or exclude

def exclude_projects(text):
    
    projects_to_exclude = ["alexandrosnic/DD2410_Introduction-to-Robotics",
                           "plhsu19/DD2410-Introduction-to-Robotics",
                           "Badi96/DD2410-Introduction-to-Robotics",
                           "callmeGoldenboy/DD2410-Introduction-to-robotics",
                           "RubiMonti/arquitectura_software",
                           "tapi1300/arquitectura_software",
                           "dstampfer/MOOD2Be",
                           "jhjune91/study",
                           "logivations/BehaviorTree.CPP",
                           "ryzhikovas/navigation2",
                           "ryzhikovas/navigation.ros.org",
                           "UoBFlightLab/drone_trees",
                            "arthurrichards77/drone_trees",
                            "happyOBO/leaderboard",
                            "varunjammula/leaderboard",
                            "xingyifei2016/scenario_runner",
                            "NaryeoH/scenario_runner",
                            "autofuzz2020/AutoFuzz",
                            "ptrckhmmr/Deep-Reinforcement-Learning",
                            "Keeganfn/infrastructure-packages",
                            "Jmz919/flexbe_behavior_engine",
                            "amsks/flexbe_behavior_engine",
                            "ITMO-lab/hrwros",
                            "abubakrsiddq/HRWROS",
                            "mertyureklli/ROS-Projects",
                            "MarzanShuvo/ROS",
                            "ahmtuguz/ROS",
                            "amancodeblast/Ros",
                            "tomdicke/assignment_industriele_robotica",
                            "FlexBE/generic_flexbe_states",
                            "amsks/generic_flexbe_states",
                            "Alperenlcr/ROS-Projects",
                            "Goose990/Fase2",
                            "PimKoole/assignment_industriele_robotica",
                            "jopkoopman/assignment_industriele_robotica",
                            "menno409/fase2",
                            "OPBrother/aliengo_delivery",
                            "ipa-rmb/autopnp",
                            "LoweDavince/catkin_ws",
                            "shydhryw/catkin_ws",
                            "kth-ros-pkg/CollaborativeBaxter",
                            "hubo/drc_hubo",
                            "DonghyunSung-MS/dyros_jet_avatar",
                            "DaegyuLim/dyros_jet_avatar",
                            "HappyYusuke/education",
                            "au1698/exp_assignment2",
                            "chiaraterrile/exp_assignment2",
                            "FraPorta/exp_assignment2",
                            "geraldo96/exp_assignment2",
                            "raghuveer-sid/exp_assignment2",
                            "riccardik/exp_assignment2",
                            "sararom15/exp_assignment2",
                            "andreatitti97/exp_assignment3",
                            "au1698/exp_assignment3",
                            "chiaraterrile/exp_assignment3",
                            "FraPorta/exp_assignment3",
                            "geraldo96/exp_assignment3",
                            "raghuveer-sid/exp_assignment3",
                            "riccardik/exp_assignment3",
                            "sararom15/exp_assignment3",
                            "laibazahid26/exp_rob_assignment_1",
                            "soundarya4807289/exp_rob_assignment_1",
                            "AlessioRoda/experimental_assignment1",
                            "Matt98x/Experimental_assignment1",
                            "CristinaNRR/ExperimentalRoboticsLab",
                            "EnzoUbaldoPetrocco/ExperimentalRoboticsLab",
                            "andreabradpitto/Experimental-robotics-laboratory",
                            "robertoalbanese/Experimental-Robotics-Laboratory",
                            "iidaissei/happymimi_apps",
                            "KIT-Happy-Robot/happymimi_apps",
                            "humanoid-path-planner/hpp_ros_interface",
                            "jmirabel/hpp_ros_interface",
                            "abubeck/ipa_seminar",
                            "jbohren-forks/linux_networking",
                            "iidaissei/mimi_common_pkg",
                            "pandora-auth-ros-pkg/pandora_ros_pkgs",
                            "apostoee/pandora_ros_pkgs",
                            "noamyogev84/qtcopter",
                            "qtcopter-technion/qtcopter",
                            "gripsCAR/rate_position_controller",
                            "pirobot/rbx2",
                            "mtbthebest/rbx2",
                            "Ewenwan/Ros",
                            "dtmoodie/ROS",
                            "tfinley/ROS",
                            "k-makihara/ROS",
                            "Jpub/ROS",
                            "is0392hr/ros_catkin_ws",
                            "beyondcn2008/ros_catkin_ws",
                            "huchunxu/ros_exploring",
                            "lhd-Sakura/ros_exploring",
                            "Hsin1987/smach_tutorial",
                            "HappyYusuke/smach_tutorial",
                            "jinglinjackychen/smach",
                            "reaverDK/SMACH",
                            "PROJ515/src",
                            "Jelledb03/turtlebot_arm",
                            "arebgun/ua-ros-pkg",
                            "Atom-machinerule/ua-ros-pkg",
                            "yoonssa/ua-ros-pkg",
                            "abishekh/ua-ros-pkg",
                            "gautam2410/ua-ros-pkg",
                            "Kenkoko/ua-ros-pkg",
                            "ua-sista/ua-ros-pkg",
## previous paper list                          
                            "ignaciotb/robi_final_project",
                            "ottocol/ejemplos_py_trees",
                            "benedictmulongo/robotics_stuffs",
                            "SemRoCo/giskardpy",
                            "naveedhd/nav2_trees",
                            "CARVE-ROBMOSYS/carve-scenarios-config",
                            "SherrySheng/BT",
                            "ros-planning/navigation2",
                            "airuchen/ROS_behavior_tree",
                            "alsora/ros2-code-examples",
                            "Adlink-ROS/BT_ros1",
                            "kuodehai/sw_pr",
                            "skylerpan/nav2_steps",
                            "mjeronimo/ros2_behavior_tree",
                            "zoubata/Stardust2020",
                            "shoufei403/navigation_learning",
                            "fmrico/software_arq_robots_course",
                            "ACTROS-Educational-Project/actros_essentials",
                            "IntelligentRoboticsLabs/ros2_planning_system_examples",
                            "YangWuuu/kunpeng_ai",
                            "Juancams/arq_sw_rob",
                            "SD-320808/behaviortree2",
                            "Mshivam2409/Behaviour-Trees",
                            "AlexanderSilvaB/btree",
                            "yashpatel1392/behavior_tree_tutorial",
                            "irvs/ros2_tms",
                            "curtkim/c-first",
                            "ehud101/robil4",
                            "msadowski/bt_logger_test",
                            "shirokunet/ros2_behavior_tree_ws",
                            "IntelligentRoboticsLabs/marathon_ros2",
                            "aayn/behavior-tree-witcher",
                            "rosindex-staging/hidmic",
                            "ros-infrastructure/index.ros.org",
                            
                         
### from old mining    
        
        "IntelligentRoboticsLabs/ros2_planning_system", "RazanGhzouli/Behavior-Trees-in-Action",

                            "RobeSafe-UAH/Techs4AgeCar-CARLA-Scenario-Runner", "mohdomama/carla_IL", "daeheepark/Carla_PathDataset_Generation",
                            "CaoZhong1992/carla-challenge-route", 
                            "hjanott/ceres_robot",
                            "thibs-sigma/CollaborativeBaxter",
                            "hdh7485/dr_navigation",
                            "Beomyeong/dyros_jet",

                            "humanoid-path-planner/hpp_ros_interface",
                            "RVSagar/hri_framework",
                            "abubeck/ipa_seminar",
                            "apostoee/pandora_ros_pkgs",
 

                            "huchunxu/ros_exploring",
                            "lhd-Sakura/ros_exploring",
    
                            "nfaction/ua-ros-pkg-nfaction",
                            "Aharobot/yale-ros-pkg",
                            "ros/executive_smach",
                            "ros-visualization/executive_smach_visualization",
                            "asr-ros/asr_state_machine",
                            "asr-ros/asr_flir_ptu_controller",

                            "FlexBE/flexbe_strands",
                            "amsks/flexbe_behavior_engine",
                            "MarzanShuvo/ROS",
                            "birlrobotics/birl_baxter_executive",
                            "Garyxud/melodic-all"]

    for i in projects_to_exclude:
        if i in text:
            return 'exclude'

    return 'include'


def run_filter(file_to_filter, output_file_included_excluded_path, output_file_included_only):
    repos = pd.read_csv(file_to_filter)

    repos['filter_exclude_projects'] = repos['name'].apply(exclude_projects)
    repos.to_csv(output_file_included_excluded_path, index=False)

    repos = repos[repos.filter_exclude_projects != "exclude"]
    repos.to_csv(output_file_included_only, index=False)


if __name__ == '__main__':
    
    ## change to input files location
    FILES_TO_FILTER = ["../filter_repo_forks/21012022_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                       "../filter_repo_forks/21012022_smach_RepoProjectNameHtmlCommitDates.csv",
                       "../filter_repo_forks/21012022_flexbe_RepoProjectNameHtmlCommitDates.csv",
                       "../filter_repo_forks/21012022_btcpp_RepoProjectNameHtmlCommitDates.csv"]

    date = datetime.today().strftime('%d%m%Y')
    
    ## change below to where you want to save the filtered files
        
    ### output files with the tag for included and excluded repos
    OUTPUT_FILES_PATHS_INCLUDED_EXCLUDED = [f"../filter_repo_duplicates/included_excluded/{date}_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_duplicates/included_excluded/{date}_smach_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_duplicates/included_excluded/{date}_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                            f"../filter_repo_duplicates/included_excluded/{date}_btcpp_RepoProjectNameHtmlCommitDates.csv"]
    
    
    ### output files with the excluded repos removed. Only included repos in these files
    OUTPUT_FILES_PATHS_INCLUDED_ONLY = [f"../filter_repo_duplicates/{date}_py_trees_ros_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_duplicates/{date}_smach_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_duplicates/{date}_flexbe_RepoProjectNameHtmlCommitDates.csv",
                                        f"../filter_repo_duplicates/{date}_btcpp_RepoProjectNameHtmlCommitDates.csv"]


    for i in range(len(FILES_TO_FILTER)):
        run_filter(FILES_TO_FILTER[i], OUTPUT_FILES_PATHS_INCLUDED_EXCLUDED[i], OUTPUT_FILES_PATHS_INCLUDED_ONLY[i])





