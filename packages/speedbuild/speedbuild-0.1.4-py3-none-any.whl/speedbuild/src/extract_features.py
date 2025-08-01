import os
import yaml
import shutil

from pathlib import Path
from ..utils.compare_templates import compare_zip_code_folders
from ..utils.utils import findFilePath, get_template_output_path
from ..utils.venv_utils import get_activated_venv
from ..utils.django_utils import ManageDjangoSettings
from ..utils.feature_dependencies import arrangeChunks
from ..utils.extract import clear_folder, extract_feature_code_and_dependencies, getTemplateFileNames, getURLForFeature
import re

# remove comments from code before splitting blocks
def create_temp_from_feature(project_path,project_name,feature_name,feature_file_path,template_django_apps):

    venv = get_activated_venv()
    

    # get settings conf from django.conf.settings TODO
    relative_path = feature_file_path.replace(project_path,"").split("/")
    relative_path.pop()
    app_name = relative_path.pop()


    findFilePath(project_path, "urls.py")

    # use conditional statement to check if file is found
    project_name = findFilePath(project_path, "asgi.py")

    if len(project_name) == 0:
        raise(ValueError("Cannot find django project settings file"))
    
    template_dep = set()
    installed_apps = set()
    project_name = project_name[0].split("/")[0]
    settings_path = f"{project_name}/settings.py"
    settings_path = os.path.join(project_path, settings_path)

    project_dir = [folder for folder in os.listdir(project_path) if os.path.isdir(f"{project_path}/{folder}")]
    
    # here
    # template_django_apps = getDjangoAppsPackage(settings_path,venv)

    settings = ManageDjangoSettings(settings_path,venv)

    processed = set()


    # start; make recursive

    output_folder_name = "sb_output_"+feature_name

    template_settings_import,template_confs,template_dep = extract_feature_code_and_dependencies(
        feature_file_path,
        feature_name,
        project_path,
        project_dir,
        app_name,
        template_django_apps,
        settings,
        project_name,
        installed_apps,
        template_dep,
        processed,
        [],
        None,
        output_folder_name
    )

    # end recursion

    output_dir = "./output/"+output_folder_name

    # Create template yaml file

    template_confs = arrangeChunks(template_confs,[],[])
    
    data = {
        "feature" : feature_name,
        "feature_file_path" : feature_file_path.replace(project_path,""),
        "source_project":project_name,
        "dependencies" : list(template_dep),
        "settings" : {
            "imports" : list(sorted(set(template_settings_import))),
            "installed_apps" : list(installed_apps),
            "middlewares" : settings.getTemplateMiddleWare(list(installed_apps)),
            "configurations" : template_confs#list(set(template_confs))
        }
    }

    # print("template configurations ",template_confs)

    with open(f'{output_dir}/sb_{feature_name}.yaml', 'w') as file:
        yaml.dump(data, file, default_flow_style=False,sort_keys=False)


    if os.path.exists(f"{output_dir}/sb_app/views.py"):
        # if views.py in models, generate url for feature
        getURLForFeature(feature_name,feature_file_path,app_name,project_path,output_folder_name)

    # create template documentations here
    tem_files = getTemplateFileNames(output_dir)
    tem_files = sorted(tem_files, key=lambda x: not x.startswith('.sb_utils')) #process dependencies first
    # Exclude the yaml file

    # for file in tem_files:
    #     file_name = file.split("/")
    #     main_file = file_name.pop().split(".")[0] #remove extention from file name
    #     file_name.append(main_file)
    #     file_name = "_".join(file_name)
  
    #     main_dir = "./output/documentation"
    #     if not os.path.exists(main_dir):
    #         os.makedirs(main_dir)

    #     # write to file  TODO : leave commented for now
    #     with open(f"{main_dir}/{file_name}.md","w") as new_file:
    #         # get and write doc to file
    #         pass
    #         # doc = documentationAgent(file)
    #         # new_file.write(doc)

    # Save template to user main dir in the .sb_zip folder
    user_dir = str(Path.home())
    user_dir += "/.sb_zip"

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    # print("Saving to ", user_dir)

    # output_zip = f"{user_dir}/speed_build_{feature_name}"  # No .zip extension needed
    template_path = get_template_output_path(feature_name)

    shutil.make_archive(template_path, 'zip', output_dir)


    # delete output folder
    clear_folder(output_dir)
    
    # structure templates to include versions

    if os.path.exists(template_path):
        # print("Template already exist")
        templateIsSame = compare_zip_code_folders(f"{template_path}.zip",os.path.join(template_path, "lts.zip"))

        if templateIsSame:
            os.remove(f"{template_path}.zip") #template did not change, so delete extracted feature
        else:
            next_version = get_next_version_file(template_path)

            #rename old lts version
            last_version_name = template_path + "/" + next_version #new name for last version (current lts version)
            os.rename(os.path.join(template_path, "lts.zip"),last_version_name)

            #move update template to folder
            shutil.move(f"{template_path}.zip", os.path.join(template_path, "lts.zip"))

    else:
        # print("Fresh template")
        # make template base folder
        os.makedirs(template_path, exist_ok=True)

        # move extracted to new folder and rename to lts.zip
        shutil.move(f"{template_path}.zip", os.path.join(template_path, "lts.zip"))

    print(f"Template `{template_path}` Created")


def get_next_version_file(folder_path):

    version_pattern = re.compile(r'^(\d+(?:\.\d+)?)\.zip$')
    versions = []

    for fname in os.listdir(folder_path):
        if fname == "lts.zip":
            continue
        match = version_pattern.match(fname)
        if match:
            ver_str = match.group(1)
            parts = ver_str.split('.')
            if len(parts) == 1:
                major = int(parts[0])
                minor = 0
            else:
                major = int(parts[0])
                minor = int(parts[1])
            versions.append((major, minor))

    if not versions:
        return "0.1.zip"

    # Find highest version
    versions.sort()
    major, minor = versions[-1]

    # Calculate next version
    if minor < 9:
        next_major = major
        next_minor = minor + 1
    else:
        next_major = major + 1
        next_minor = 0

    next_version = f"{next_major}.{next_minor}.zip" if next_minor > 0 else f"{next_major}.zip"
    return next_version
