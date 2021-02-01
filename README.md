# ml-code-dataset

Clones the github repositories from [paperswithcode-data](https://github.com/paperswithcode/paperswithcode-data), keeping only `.py`-files and converting any notebooks to scripts.

- [ml-code-dataset](#ml-code-dataset)
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

```
python download.py
```

The number of repositories to download can be limited by passing the flag `-n` or `--num_repos` followed by the number.