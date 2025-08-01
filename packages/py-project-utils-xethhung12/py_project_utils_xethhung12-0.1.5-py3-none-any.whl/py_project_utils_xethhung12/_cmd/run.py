import sys
import shutil
import os
import importlib.resources as resources
import py_project_utils_xethhung12 as py_project
import argparse
from j_vault_http_client_xethhung12 import client
def main():
    client.load_to_env()
    parser = argparse.ArgumentParser(
        prog = "PyProjectUtils",
        description="The PyProjectUtils is a tools to help create and manage py project. (Consider it as a automation to create python packaging tool)",
        epilog="Enjoy the tool"
    )

    parser.add_argument("-n", "--name", type=str, help="the project name")
    args = parser.parse_args()
    if args.name is None:
        print("Name is missing.")
        return
    
    py_project.create_project(args.name)
