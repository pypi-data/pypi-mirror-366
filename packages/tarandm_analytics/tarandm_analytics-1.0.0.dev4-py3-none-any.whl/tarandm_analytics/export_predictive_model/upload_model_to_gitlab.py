import os
import shutil
import stat
import urllib
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Any

import gitlab
import structlog
from furl import furl
from git import Repo

from tarandm_analytics.predictive_models.builder import PredictiveModelBuilder

logger = structlog.get_logger(__name__)


def remove_readonly(func: Callable[[str | Path], None], path: str | Path, _: Any) -> None:
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def delete_folder(folder: str | Path) -> None:
    # Check if the folder exists and delete it if it does
    if os.path.exists(folder):
        logger.info(f"Folder {folder} already exists, deleting.")
        shutil.rmtree(folder, onerror=remove_readonly)


def create_folder(folder: str | Path) -> None:
    os.makedirs(folder)
    logger.info(f'Creating folder"{folder}".')


def create_merge_request(
    gitlab_url: str,
    repository_url: str,
    environment: str,
    git_user_name: str,
    git_user_token: str,
    cloned_repo_dir: str,
    model_kwargs: Dict[str, Any],
) -> None:
    # Get the current time
    current_time = datetime.now()

    # Format the time as a string
    time_str = current_time.strftime("%Y%m%d%H%M%S")

    new_model_name = model_kwargs["model_name"]
    if new_model_name is None:
        raise ValueError("Model name is required.")

    teambox_branch_name = f"{environment}-teambox"
    new_branch_name = f"{environment}-feature/{git_user_name}/upload_new_model_{time_str}"
    path_to_models = Path("repository/strategies/models")
    repo_full_path = "tarandm/strategies"

    # Prepare the folder
    delete_folder(cloned_repo_dir)
    create_folder(cloned_repo_dir)

    # prepare furl url
    repo_url = furl(repository_url)
    repo_url.username = "__token__"
    repo_url.password = git_user_token

    # clone strategies repo
    repo = Repo.clone_from(
        urllib.parse.unquote(str(repo_url)),
        cloned_repo_dir,
        branch=teambox_branch_name,
    )
    logger.info(f"Cloned strategies repository into {cloned_repo_dir}")

    # Create a new branch from the current branch
    repo.create_head(new_branch_name)
    logger.info(f"New branch '{new_branch_name}' created.")

    # Switch to the new branch (optional)
    repo.git.checkout(new_branch_name)
    logger.info(f"Switched to branch '{new_branch_name}'")

    # get necessary files
    model = PredictiveModelBuilder().build(**model_kwargs)
    model_content = model.get_content()

    # prepare new model folder
    new_model_folder = Path(cloned_repo_dir) / path_to_models / Path(new_model_name)

    if os.path.exists(new_model_folder):
        model_already_existed = True
    else:
        model_already_existed = False

    delete_folder(new_model_folder)
    create_folder(new_model_folder)

    # Write extended_model_yaml to file
    if model_content.extended_predictive_model_yaml:
        model_content.extended_predictive_model_yaml.seek(0)
        filepath = new_model_folder / Path("extended_model.yaml")
        with open(filepath, "w") as outfile:
            outfile.write(model_content.extended_predictive_model_yaml.getvalue())
        logger.info(f"Wrote extended_model_yaml to {filepath}")

    # Write external_model_json to file
    if model_content.external_model_json:
        model_content.external_model_json.seek(0)
        filepath = new_model_folder / Path("external_model.json")
        with open(filepath, "w") as outfile:
            outfile.write(model_content.external_model_json.getvalue())
        logger.info(f"Wrote external_model_json to {filepath}")

    # Write external_model_pmml to file
    if model_content.external_model_pmml:
        model_content.external_model_pmml.seek(0)
        filepath = new_model_folder / Path("external_model.pmml")
        with open(filepath, "w") as outfile:
            outfile.write(model_content.external_model_pmml.getvalue())
        logger.info(f"Wrote external_model_pmml to {filepath}")

    # Write images to files
    for filename, image_content in model_content.attached_images.items():
        image_content.seek(0)
        filepath = new_model_folder / Path(filename)
        with open(filepath, "wb") as outfile:
            outfile.write(image_content.read())
        logger.info(f"Wrote image content to {filepath}")

    logger.info(f"All files have been written to the folder '{new_model_folder}'.")

    # Git add, commit and push
    subfolder_path = path_to_models / Path(new_model_name)
    repo.git.add(subfolder_path)

    if model_already_existed:
        message = f"Update model {new_model_name}."
    else:
        message = f"Create model {new_model_name}"

    repo.index.commit(message=message)
    repo.git.push("origin", new_branch_name)
    logger.info("Changes commited and pushed to GitLab")

    # initialize GitLab
    gl = gitlab.Gitlab(gitlab_url, private_token=git_user_token)
    # Get the project
    project = gl.projects.get(repo_full_path)

    # Create the merge request
    merge_request = project.mergerequests.create(
        {
            "source_branch": new_branch_name,
            "target_branch": teambox_branch_name,
            "title": message,
            "description": message,
        }
    )

    logger.info(f"Merge request created: {merge_request.web_url}")

    delete_folder(cloned_repo_dir)
