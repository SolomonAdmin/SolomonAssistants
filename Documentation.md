# GitHub Set Up
test comment 
## SSH Keys
Steps to creating and using the SSH keys
- Open terminal
- ```ls -al ~/.ssh```
- ```ssh-keygen -t ed25519 -C "your_email@example.com"``` add a passphrase
- ```eval "$(ssh-agent -s)"```
- ```open ~/.ssh/config```
- If the file does not exist, ```touch ~/.ssh/config```
-      

Here is my solomon config for reference
```nano ~/.ssh/config```                                                              
Config for SolomonAdmin GitHub, note the name of the key we created is called "solomonkey", located in "~/.ssh/solomonkey"
```
Host github-SolomonAdmin
  HostName github.com
  User git
  AddKeysToAgent yes
  IdentityFile ~/.ssh/solomonkey
```
Add the SSH private key to the ssh-agent
```
ssh-add -K ~/.ssh/solomonkey
```
Copy the .pub key for the key you created. In my case its 
```
nano ~/.ssh/solomonkey.pub
```
It looks like this 
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDbEahW/yLYX1QrR8pXtTRIGB1A9RQpV9EruL4jmPwZI/Padx+Q2u4BwM6fZsdzNNKd1UmG8r/GLi7tLEq/m3mOjelx4C9dayjbaCwPJEqJjsn2lsnqyUW+wSxQNDhg>
```
- Go to GitHub.com and log into https://github.com/SolomonAdmin.
- Click on your profile photo, top right corner, then click Settings.
- In the user settings sidebar, click SSH and GPG keys.
- Click New SSH key or Add SSH key.
- In the "Title" field, add a descriptive label for the new key, like "MacBook Pro".
- Paste your `.pub` key into the "Key" field (it should already be copied to your clipboard).
- Click Add SSH key.
- Test your connection, ```ssh -T git@github.com```

Check the SSH Configuration
```
ssh-add -l
```
If it is not added
```
ssh-add ~/.ssh/solomonkey
```

Test the connection
```
ssh -T git@github-SolomonAdmin
```
Ensure correct remote URL
```
git remote -v
```
If it's not using github with solomon ley
```
git remote set-url origin github-SolomonAdmin:SolomonAdmin/SolomonAssistants.git
```

## Install brew

## Clone the repo
Once you have the SSH key set up, you can clone the repo.
```
git clone git@github.com:SolomonAdmin/SolomonAssistants.git
```

Install requirements in the rooy directory (solomonassistants)
```
pip install -r requirements.txt
```

# Testing the Application
## Testing locally
```
# Make sure to change into the app directory as shown here. This will open the application on local host, http://localhost:8000, switch to http://localhost:8000/docs#/
cd app
uvicorn main:app --reload  
```
# Docker
First, change to the root directory 
```cd ~/SolomonAssistants
```
Build the docker image called "solomonassistantsapp"
docker build -t solomonassistantsapp .
```
```
You can see if the image built successfully now
docker images
```
```
# The application is exposed on Port 80. We also pass in the AWS credentials to access our other API keys stored in AWS Secrets
docker run -e AWS_ACCESS_KEY_ID=AKIATEMAXBDJLDYV4P67 \
           -e AWS_SECRET_ACCESS_KEY=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 \
           -e AWS_DEFAULT_REGION=us-east-1 \
           -p 8000:80 \
           solomonassistantsapp
```

```
sudo yum install java
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum upgrade
# Add required dependencies for the jenkins package
sudo yum install fontconfig java-17-openjdk
sudo yum install jenkins
sudo systemctl daemon-reload

sudo systemctl enable jenkins
sudo systemctl status jenkins
sudo systemctl start jenkins

sudo systemctl status jenkins
# copy
/var/lib/jenkins/secrets/initialAdminPassword

sudo cat /var/lib/jenkins/secrets/initialAdminPassword
# Password: 776900b3c82646fba0882d629bb2091a

curl -fsSL https://get.docker.com -o install-docker.sh

sudo yum install docker
sudo service docker start
sudo usermod -a -G docker jenkins

sudo -su jenkins
whoami # jenkins

cd /var/lib/jenkins/
mkdir .aws

sudo -su jenkins
cd /var/lib/jenkins/
aws configure
exit
newgrp

connect to ec2
sudo -su jenkins
id -nG jenkins

sudo systemctl restart jenkins
sudo systemctl status jenkins

```

```
Create EC2 instance (t2.medium)
OS - Ubuntu
Solomon2023*

#1
sudo apt install default-jre

#2 install docker 
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

#3 download java runtime env and check install
sudo apt install openjdk-17-jre-headless
java -version

#4 install jenkins (addsto apt sources)
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins

#5 
sudo groupadd docker
sudo usermod -aG docker $USER
sudo usermod -aG docker jenkins

#6 
sudo -su jenkins 
docker run hello-world

#7 
exit
sudo systemctl start jenkins

#8 
Update inbound rules on security group with Custom CPT (0000:0 on port 8080)

#9
sudo systemctl status jenkins
/var/lib/jenkins/secrets/initialAdminPassword
q
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
Password - 6890b069fcf5400f942f0263c5392eee

#10 open the public port on 8080
http://52.202.206.221:8080
install suggested plugins

#11 
sudo apt install unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

http://52.202.206.221/docs#/
```