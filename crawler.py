#!/usr/bin/env python
import sys
import json
import math
import time
import datetime
import requests

from tqdm import tqdm
from types import SimpleNamespace
from argparse import ArgumentParser


repositoryCollection = []
BASE_URL = "https://api.github.com/search/repositories"


def cooldown(headers):
    threshold = 100
    try:
        limit = headers['X-RateLimit-Limit']
        remaining = headers['X-RateLimit-Remaining']
        reset = headers['X-RateLimit-Reset']
        if remaining >= remainingthreshold:
            return
        else:
            time_to_sleep = math.ceil(math.abs(reset - time.time()) / 1000)
            print("Cooling down for %s seconds until: %s" & (time_to_sleep, datetime.datetime.fromtimestamp(
                reset).strftime('%c')))
            time.sleep(time_to_sleep)
    except:
        time.sleep(10)


def fetch_repos(headers, query, page, args):
    # cut off
    maxnewprojects = args.maxprojects - \
        len(repositoryCollection) if args.maxprojects else 0
    if maxnewprojects < 0:
        return 0

    response = requests.get("%s?page=%s&q=%s" % (
        BASE_URL, page, query), headers=headers)

    cooldown(response.headers)

    response = json.loads(
        response.text, object_hook=lambda d: SimpleNamespace(**d))

    newRepos = None
    while newRepos == None:
        try:
            newRepos = []
            newcount = 0
            for idx, repo in enumerate(response.items):
                if args.maxsize > 0 and repo.size > args.maxsize:
                    print("Skipping oversized project",
                          repo.full_name, ":", repo.size, "kb")
                    continue

                license = ""
                try:
                    license = repo.license.key
                except:
                    pass

                newRepos.append({
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'topics': repo.topics,
                    'repo_url': repo.git_url,
                    'stars': repo.stargazers_count,
                    'watchers': repo.watchers_count,
                    'forks': repo.forks,
                    'created': repo.created_at,
                    'size': repo.size,
                    'license': license,
                    'language': repo.language,
                    'last_updated': repo.updated_at,
                })

                newcount += 1
                if maxnewprojects and newcount >= maxnewprojects:
                    break

            repositoryCollection.extend(newRepos)
            time.sleep(5)
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                print("Aborting.")
                sys.exit(1)
            print(f"Exception thrown: {e}\nRetrying BLOCK")
            newRepos = None
            time.sleep(30)

    return newcount


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", dest="basedir", type=str, default=".",
                        help="The directory to download to", required=False)
    parser.add_argument("-l", "--lang", dest="language", type=str, default="python",
                        help="The language of source code to filter by", required=False)
    parser.add_argument("-m", "--max", dest="maxprojects", type=int, default=1000,
                        help="The maximum number of projects", required=False)
    parser.add_argument("--min_stars", dest="minstars", type=int, default=10,
                        help="The minimum number of stars for the repository", required=False)
    parser.add_argument("--max_stars", dest="maxstars", type=int, default=1000000,
                        help="The maximum number of stars for the repository", required=False)
    parser.add_argument("--max_size", dest="maxsize", type=int, default=0,
                        help="The maximum number size of the repository", required=False)
    parser.add_argument("--topics", dest="topics", type=lambda s: [str(item) for item in s.split(',')], default="machine-learning",
                        help="The repository topics to filter by", required=False)

    args = parser.parse_args()

    with open('apikey.txt', 'r') as fd:
        APIKEY = fd.read().rstrip()

    if not APIKEY:
        print("Please first paste your API key in file apikey.txt!")
        sys.exit(1)

    headers = {'Accept': 'application/vnd.github.mercy-preview+json',
               'Authorization': 'token %s' % APIKEY}
    query = 'language:%s+topic:%s+stars:%d..%d' % (
        args.language, "+".join(args.topics), args.minstars, args.maxstars)

    page = 1
    num_fetched_repositories = 0
    pbar = tqdm(total=args.maxprojects, desc="Fetching repositories")
    while num_fetched_repositories <= args.maxprojects:
        newcount = fetch_repos(headers, query, page, args)
        pbar.update(newcount)

        num_fetched_repositories += newcount
        page += 1

        # cut off
        if args.maxprojects and len(repositoryCollection) >= args.maxprojects:
            repositoryCollection = repositoryCollection[:args.maxprojects]
            break

        # Save intermediate results for every 5th page
        if page % 5 == 0:
            with open(f"{args.basedir}/githubRepositories.json", 'wt') as fd:
                fd.write(json.dumps(repositoryCollection))

    # Write final results
    pbar.close()
    print("Done fetching repositories.")
    with open(f"{args.basedir}/githubRepositories.json", 'wt') as fd:
        fd.write(json.dumps(repositoryCollection))
