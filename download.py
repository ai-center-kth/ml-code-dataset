import os
import sys
import glob
import json
import shutil

from tqdm import tqdm
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed


def clone_repo(repo_url):
    repo_name = repo_url.split('github.com/')[1]
    directory = f'./data/{repo_name}'

    os.system(f"git clone --depth=1 {repo_url} {directory} >/dev/null 2>&1")
    shutil.rmtree(f"{directory}/.git")

    # Remove any non python file
    folders = []
    for file in glob.glob(f"{directory}/**", recursive=True):

        if os.path.isdir(file):
            folders.append(file)
        if not os.path.isdir(file) and not (file.endswith('.py') or file.endswith('.ipynb')):
            os.remove(file)

        # Run command to convert notebooks into .py
        if file.endswith('.ipynb'):
            os.system(
                f"jupyter nbconvert --to script {file} >/dev/null 2>&1")
            os.remove(file)

    # Tidy up, removing empty folders
    for folder in folders:
        if len(os.listdir(folder)) == 0:
            os.removedirs(folder)


def start_async_download(repositories):
    with tqdm(total=len(repositories), unit=' Repositories', desc='Downloading repositories') as pbar:
        with ThreadPoolExecutor(max_workers=10) as executor:
            tasks = {executor.submit(
                clone_repo, url): url for url in repositories}

            for task in as_completed(tasks):
                pbar.update(1)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-n", "--num_repos", dest="num_repositories", type=int,
                        help="The maximum number of repositories to download", required=False)

    # Read repository urls from json file
    with open('links-between-papers-and-code.json', 'r') as file:
        repositories = json.load(file)

    # Filter out any eventual non-github repos
    repositories = list(set([repository['repo_url'] for repository in repositories if (
        'github.com/' in repository['repo_url'])]))

    args = parser.parse_args()

    if args.num_repositories is not None:
        repositories = repositories[:args.num_repositories]

    start_async_download(repositories)
    print("Done cloning.")
