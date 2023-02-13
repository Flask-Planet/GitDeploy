#!/bin/bash

sudo apt update
sudo apt install -y git
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y python3-venv

sudo mkdir /gitdeploy
sudo mkdir /gitdeploy/logs
sudo mkdir /gitdeploy/supervisor
sudo mkdir /gitdeploy/supervisor/logs
sudo mkdir /gitdeploy/supervisor/ini

sudo chown -R "$USER":"$USER" /gitdeploy

