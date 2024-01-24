# GitHub Set Up

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
docker run -e AWS_ACCESS_KEY_ID=AKIATEMAXBDJFNEYIZ63 \
           -e AWS_SECRET_ACCESS_KEY=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 \
           -e AWS_DEFAULT_REGION=us-east-1 \
           -p 8000:80 \
           solomonassistantsapp
```