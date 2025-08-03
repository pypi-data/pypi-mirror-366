# TASKER: cli based task manager #

### Installation

```sh
pipx install tasker-tasks-cli
pipx ensurepath
```

### Description

*tasker* is a cli-based task manager.

Tasker tasks and config file will be saved to $HOME/tasker/

Consider converting $HOME/tasker into a repository post install.

### Usage

Type ```tasker``` to launch.

### Tips

 - Running ```tasker``` for the first time will create all necessary files in ```~/tasker/```, otherwise tasker will use existing files from any previous installs.

 - Config file location is set to ```~/tasker/conf/tasker.conf```

 - When executing ```tasker```, it has its own menu system. However you can incorporate tasker into your own scripts using command line options if you wish. EG: ```tasker -n get milk personal 2```

### Dependencies

Dependencies will be installed as part of pipx installation above.

 - configparser
 - iterfzf
 - python-dateutil
