## The Admin-Bot Project
### Requirements

* poetry => 1.0.0
* git-flow => 1.12.3
* docker-ce => 20.10.17
* docker-compose => 1.29.2

### Install poetry
#### Ubuntu 20.04
```shell
  pc# curl -sSL https://install.python-poetry.org | python3 -
  pc# export PATH="/home/tech/.local/bin:$PATH"
```

### Install git-flow
#### Ubuntu 20.04
```shell
  pc# sudo apt install -y git-flow
```

### Install docker-compose
#### Ubuntu 20.04
```shell
  pc# sudo sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  pc# sudo chmod +x /usr/local/bin/docker-compose
  pc# sudo ln -svf /usr/local/bin/docker-compose /usr/bin/docker-compose
```

### Install Docker Community Edition
#### Ubuntu 20.04
```shell
  pc# apt update
  pc# sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
  pc# sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  pc# add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
  pc# apt update && apt install docker-ce
```

### Start & Develop project
* For local start code (From user bot from root)
```shell
  pc# git clone <repo_url>
  pc# cd /to/project/directory
  pc# git flow init
  pc# poetry shell
  pc# docker-compose -f admin-bot.local.yml up --build
```
* For stage deploy
```shell
  pc# git commit -am "<You change commit none>"
  pc# git push
```
* For production deploy

```shell
  pc# git tag -a v<Vesrion.Major.Minor> -m "BUMP <tag version>"
```
Example: git tag -a v0.0.1 -m "BUMP tag v0.0.1"
