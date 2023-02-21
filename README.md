# GitDeploy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

GitDeploy is a simple tool to deploy your python projects to a docker container or VPS from a git repository.

It has webhooks support for github and gitlab, the end goal is to have Heroku style functionality.

**Project is still in development, and may not work as intended.**

## Contributors wanted!

- Free to add your own ideas!
- Beginners are welcome and encouraged to join in!

### TODOs:

- [ ] Change the JavaScript to polling function to a websocket ( Flask-SocketIO )
  - ( app/theme/static/js/alpine:global:x-data.js )
- [ ] Add support for more git providers ( Bitbucket, Gitlab, etc. )
- [ ] Ability to add multiple repositories, and start/stop their commands
- [ ] Add support to spin up a nginx container / local install to serve the app
- [ ] Add support to manage nginx proxy
- [ ] Add support to manage certbot ( Let's Encrypt )

See more in the issues section!

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

or

```bash
chmod +x start
```

```bash
./start
```

**Windows:**

_**Run above in WSL**_

### Screenshots

![](https://raw.githubusercontent.com/Flask-Planet/GitDeploy/master/__assets__/screenshot_1.png)
