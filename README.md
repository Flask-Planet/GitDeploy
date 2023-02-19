# GitDeploy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

GitDeploy is a simple tool to deploy your python projects to a docker container or VPS from a git repository.

It has webhooks support for github and gitlab, the end goal is to have Heroku style functionality.

**Project is still in development, and may not work as intended.**

![](https://raw.githubusercontent.com/Flask-Planet/GitDeploy/master/__assets__/screenshot_0.png)

## Contributors wanted!

- Free to add your own ideas!
- Beginners are welcome and encouraged to join in!

### Project Board:

[Click here](https://github.com/orgs/Flask-Planet/projects/1/views/1?layout=table) to see what needs done.

### How to contribute

- Fork the repository
- Make your changes
- Create a pull request
- Wait for review

If you are a beginner, you can also check out
[this guide](https://opensource.com/article/19/7/create-pull-request-github)

You can also join the [discord server](https://discord.gg/nZkQECDU) to discuss the project.

## Local setup

Clone the repository and install the requirements:

```bash
git clone https://github.com/Flask-Planet/GitDeploy.git
```

```bash
cd GitDeploy
```

**GNU/Linux / macOS:**

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python3 gitdeployflask
```

**Windows:**

_**Run above in WSL**_