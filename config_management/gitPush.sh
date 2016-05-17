#!/bin/bash

echo -e "\033[1;36m Invoking SSH agent as background process"
eval `ssh-agent`

echo -e "\033[1;36m Adding GIT key for user root"
ssh-add /root/.ssh/id_rsa.git

echo -e "\033[1;36m Verify key addition"
ssh-add -l

echo -e "\033[1;36m Pushing config to gitlab"
cd /var/config_data/
git add PE1
git commit -a -m "configs for PE1"
git push origin master
