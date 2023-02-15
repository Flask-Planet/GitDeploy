# GitDeploy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

GitDeploy is a simple tool to deploy your python projects to a docker container or VPS from a git repository.

It has webhooks support for github and gitlab, the end goal is to have Heroku style functionality.

**Project is still in development, and may not work as intended.**

## Contributors wanted!

- Free to add your own ideas!
- Beginners are welcome and encouraged to join in!

### TODO:

- [x] Compatibility with macOS
- [x] Compatibility with Linux OS
- [ ] Compatibility with Windows OS
- [ ] Frontend styling (redesign or just make it look better)
- [ ] Parse errors in a neat way to the frontend
- [ ] Add command templates for some common commands
- [x] Ensure background task manager is working correctly
- [ ] Overall system testing

### Future features:

- [ ] Add support for oauth git login
- [ ] Add support to launch other tasks (not just deploy)

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

**GNU/Linux:**

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

**Windows** (powershell, with enabled scripts)

(Current state of the project will not work 'out of the box' on Windows due to the project requiring git cli, this needs more R&D time. Feel free to take on this task :) )

```powershell
python -m venv venv
```

```powershell
./venv/Scripts/activate
```

```powershell
pip install -r requirements.txt
```
