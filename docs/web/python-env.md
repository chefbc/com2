---
layout: post
title: Setup a Python Development Environment
image: img/david-clode-cxMJYcuCLEA-unsplash.jpg
author: [chefbc]
date: 2020-04-27
draft: false
tags:
  - python
excerpt: This is intended as a quick reference for setting up a Python development environment.
---

This is intended as a quick reference and explanation of how I setup environments to develop via Python on my Mac.

## Requirements
  - Develop/test on different versions of Python.
  - Isolate each project from each other.


## Isolate Python versions
[pyenv](https://github.com/pyenv/pyenv) a simple python version management tool that can be installed via [homebrew](https://docs.brew.sh/Homebrew-and-Python).

## Installalation
```bash
brew install pyenv
```

List installed python versions
```bash
pyenv install --list
```

Load python versions
```bash
pyenv install -v 3.8.2
```

List your loaded python versions
```bash
pyenv versions
```

Change your global python version
```bash
pyenv global 3.8.2
```

Set location specific python version
```bash
pyenv local 2.7.15
```

Uninstall any version
```bash
pyenv uninstall 2.7.15
```

Add to ~/.bash_profile
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
```

<!-- Create a virtual environment for python2
```bash
pyenv versions
pyenv shell 2.7.17
python -V
pip install virtualenv virtualenv env
source env/bin/activate
``` -->

<!-- #### Create for python3 with [venv] (https://docs.python.org/3/library/venv.html)a virtual environment  -->
Create a virtual environment
```bash
pyenv versions
pyenv shell 3.8.2
python -V
python -m venv env
source env/bin/activate
```

Leave virtual environment
```bash
deactivate
```
