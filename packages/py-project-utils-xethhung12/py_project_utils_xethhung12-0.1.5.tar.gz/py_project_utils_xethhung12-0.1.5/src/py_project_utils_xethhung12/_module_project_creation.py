import sys
import shutil
import os
import stat
import importlib.resources as resources
import py_project_utils_xethhung12 as py_project
import platform
def create_project(project_name):
    resourcePath=resources.files("py_project_utils_xethhung12.data")
    base = str(resourcePath._paths[0])
    data = list(resourcePath.iterdir())
    for i in data:
        print("base: ", base)
        pr = str(i)
        print("pr: ",pr)

        if os.path.isdir(pr):
            print(pr, "is directory, skipping")
            continue

        project_name_for_replacing = project_name.replace("-","_")
        fp = pr[len(base)+1:]\
            .replace("$","/")\
            .replace("___project_name___",project_name_for_replacing)
        print("fp: ",fp)
        hasSubPath = True if len(fp.split("/")) > 1 else False
        if hasSubPath:
            os.makedirs("/".join(fp.split("/")[:-1]), exist_ok=True)
        shutil.copy(pr, fp)
        with open(fp, "rt") as fin:
            with open(f"{fp}__", "wt") as fout:
                for line in fin:
                    fout.write(line\
                        .replace("___project_name___", project_name_for_replacing)\
                        .replace("___project_cmd_name___", project_name_for_replacing.replace("_","-"))
                        )
        if os.path.exists(fp):
            os.remove(fp)
        shutil.move(f"{fp}__", fp)

        if fp.endswith(".sh"):
            if platform.system() == 'Windows':
                pass
            else:  # Linux/Unix-like systems
                current_permissions = os.stat(fp).st_mode
                new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                # Apply the new permissions
                os.chmod(fp, new_permissions)
                print(f"File '{fp}' made executable (chmod +x).")

    print("Project initializing complete")