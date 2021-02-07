Clones the github repositories from [paperswithcode-data](https://github.com/paperswithcode/paperswithcode-data), keeping only `.py`-files and converting any notebooks to scripts.

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)

# Getting Started

## Prerequisites

- python3.6+
- git

## Installation

Activate any virtualization environment and install the python packages.

Ex.
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

Use the crawler to retrieve a set of github repositories by their topic.
Create a [personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) and store it in `apikey.txt`.
View the optional arguments by passing `--help`

```
python crawler.py
```

To clone the repositories listed in the json-file simply run, 

```
python downloader.py -f <path to json>
```
