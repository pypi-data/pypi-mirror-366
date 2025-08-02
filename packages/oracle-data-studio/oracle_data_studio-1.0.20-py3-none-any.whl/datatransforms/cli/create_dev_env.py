'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Utility script to initialize the development environment. 

1. Get the current directory from where the script is executed (cli)
2. If the directory is given (--work-dir)  
3. if creation is successful, genenerate 
        - deploymnet.config 
        - set_env.sh 
'''

import logging
import os
import configparser

from datatransforms.cli import cli_common

parser=cli_common.parser

parser.add_argument("--work-dir", help="work directory for development environment",required=True)
parser.add_argument('--ip', nargs='?',  type=str, default="<data_transforms_ip>")
parser.add_argument('--user', nargs='?',  type=str, default="<data_transforms_user>")
parser.add_argument('--pswd', nargs='?',  type=str, default="<data_transforms_credential>")
parser.add_argument('--ide', nargs='?',
                    type=str,
                    default="shell",
                    help="supported ide vscode, Prepares settings\
                    file for vscode editor. Default is shell only env file will be created")
parser.add_argument('--deployment-name',
                    type=str,
                    default="an_active_deployment",
                    help="name that identifies the deployment. \
                        Must be unique within deployment.config")
parser.add_argument('--secure-config',
                    type=bool,
                    default=False,
                    help="Secures user and password in keyring store, \
                        Requires keyring to be installed")

args = cli_common.process_args(parser)

cli_common.set_log_level("INFO")
logging.info("Setting up development environment....")


def prepare_env_sh(work_dir):
    """
    Creates the shell script that sets the environment variables
    arguments 
     - work_dir - 
    """
    cwd = os.getcwd()
    python_path_suffix = cwd + (cwd+os.path.sep+"datatransforms")
    logging.debug("Current directory " + cwd )

    shell_code="""#!/bin/bash
export DATATRANSFORMS_HOME={cwd}
export PYTHONPATH=$PYTHONPATH:$DATATRANSFORMS_HOME:$DATATRANSFORMS_HOME/datatransforms
export PATH=$PATH:$DATATRANSFORMS_HOME:$DATATRANSFORMS_HOME/scripts
"""

    env_file_name = os.path.join(work_dir,"set_env.sh")
    logging.info("Preparing env file %s" , env_file_name)

    env_file = open(env_file_name,"w",encoding="utf-8")
    env_file.write(shell_code.format(cwd=cwd))
    env_file.close()
    logging.info("Change execution mode for %s" , env_file_name)
    os.chmod(env_file_name,0o755)

def prepare_work_dir(work_dir):
    """
    Creates the work directory for the projects.
     - arguments 
        - work_dir , directory to be initialised , wil be created 
        if it doesn't exist. 
     - Environment Error is thrown if the operation to initialise fails
     (mostly it could be due to write/create directory permissions on the given directory)
    """
    print("Preparing dev environment undr " + work_dir)
    if not os.path.isdir(work_dir):
        try:
            logging.info("Creating work directory %s" , work_dir)
            os.mkdir(work_dir)
        except OSError as error:
            print(error)
            print(
                "Provide valid work-dir %s, Failed to create work-dir!!",work_dir )
            raise EnvironmentError("Failed to create " + work_dir) from error

def prepare_deployment_config(work_dir,ip,user,pswd,deployment_name,secure_config):
    """
    Creates a deployment configuration file inside the given dev env directory 
    """
    config = configparser.ConfigParser()
    deployment_name = "an_active_deployment" if deployment_name == None else deployment_name
    config_dict ={'xforms_ip':ip,'xforms_user':user}

    config['ACTIVE']={'deployment':deployment_name}
    config[deployment_name]=config_dict 

    config_file_name = os.path.join(work_dir,"deployment.config")
    config.write(open(config_file_name,"w",encoding="utf-8"))

def prepare_about_py(dev_work_dir):
    """
    Generates the about.py in the given work directory. 
    """
    #optimize this code, load from examples or something rather than this large string dump.
    #may be bundle about.py as part of distribution ??

    about_code="""
#sample script to test the deployment connectiion. If it is valid , it will print the about string
from datatransforms.workbench import DataTransformsWorkbench,DataTransformsException,WorkbenchConfig
import logging

logging.getLogger().setLevel("INFO")
connect_params = WorkbenchConfig.get_workbench_config(getpass.getpass("Enter deployment password:"))
workbench = DataTransformsWorkbench()
workbench.connect_workbench(connect_params)


workbench.print_about_string()
"""
    about_file_name=os.path.join(dev_work_dir,"about.py")
    about_file = open(about_file_name,"w",encoding="utf-8")
    about_file.write(about_code)
    about_file.close()

def prepare_vscode_settings(dev_work_dir):
    """
    Prepare the necessary settings required to start using IDE Visual Studio Code 
    """
    cwd = os.getcwd()
    logging.debug("Current directory %s", cwd )

    settings_json_template = """{{
        "python.autoComplete.extraPaths": [
            "{cwd}",
        ],
        "python.envFile": "~/.env",
        "python.experiments.enabled": false,
        "python.terminal.launchArgs": [

        ],
        "python.analysis.extraPaths": [
            "{cwd}",
        ],
    }}"""

    vscode_dir = os.path.join(dev_work_dir,".vscode")
    os.mkdir(vscode_dir)
    print("Created .vscode directory for settings")
    settings_file_name = os.path.join(vscode_dir,"settings.json")
    logging.info("Preparing env file %s", settings_file_name)

    env_file = open(settings_file_name,"w",encoding="utf-8")
    env_file.write(settings_json_template.format_map(locals()))
    env_file.close()
    logging.info("VSCode settings created... %s" ,settings_file_name)

ip = args.ip
user = args.user
pswd = args.pswd
work_dir = args.work_dir
ide = args.ide

deployment_name = args.deployment_name
secure_config = args.secure_config

prepare_work_dir(work_dir)
prepare_env_sh(work_dir)
if ide.lower() == "vscode":
    prepare_vscode_settings(work_dir)
else:
    print("IDE Settings ignored, only vscode is supported")

prepare_deployment_config(work_dir,ip,user,pswd,deployment_name,secure_config)
prepare_about_py(work_dir)
print("\nDev environment preparattion complete")
