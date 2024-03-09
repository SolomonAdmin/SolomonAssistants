vpc=vpc-0050cc7d
sb1=subnet-770f4328
sb2=subnet-2eedad48
sb3=subnet-6e733d4f
sb4=subnet-da4b5897
sb5=subnet-c38f18f2
sb6=subnet-1c81bb12
sg=sg-026d89dbac4f0729d
region=us-east-1
acc=215555180754

docker run -p 8080:80 \
-e AWS_ACCESS_KEY_ID=AKIATEMAXBDJFNEYIZ63 \
-e AWS_SECRET_ACCESS_KEY=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 \
-e AWS_DEFAULT_REGION=us-east-1 \
215555180754.dkr.ecr.us-east-1.amazonaws.com/solomonassistantsapp:f8d91e9f3efbd63144f8c91aa8ca17c873d163d5

# Create LB
aws elbv2 create-load-balancer \
     --name sap-alb \
     --subnets subnet-770f4328 subnet-2eedad48 subnet-6e733d4f subnet-da4b5897 subnet-c38f18f2 subnet-1c81bb12 \
     --security-groups sg-026d89dbac4f0729d \
     --region us-east-1
# LB=arn:aws:elasticloadbalancing:us-east-1:215555180754:loadbalancer/app/sap-alb/34f77eb563a575c4

#Create Target Group
aws elbv2 create-target-group \
     --name sap-target \
     --protocol HTTP \
     --port 80 8080 \
     --target-type ip \
     --vpc-id vpc-0050cc7d \
     --region us-east-1
# TG=arn:aws:elasticloadbalancing:us-east-1:215555180754:targetgroup/sap-target/d9f36238002f0997

aws elbv2 create-listener \
     --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:215555180754:loadbalancer/app/sap-alb/34f77eb563a575c4 \
     --protocol HTTP \
     --port 80 \
     --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:215555180754:targetgroup/sap-target/d9f36238002f0997 \
     --region us-east-1
# TG=arn:aws:elasticloadbalancing:us-east-1:215555180754:listener/app/sap-alb/34f77eb563a575c4/406686ab904e70b3

#Create ECS cluster
aws ecs create-cluster \
     --cluster-name sap \
     --region us-east-1
#CL=arn:aws:ecs:us-east-1:215555180754:cluster/sap

# Register Task Definition
aws ecs register-task-definition \
     --cli-input-json file://sap-taskdef.json \
     --region us-east-1
#TD=arn:aws:ecs:us-east-1:215555180754:task-definition/solomonassistantsapp:1

# Create AWS Service
aws ecs create-service \
     --cli-input-json file://sap-service.json \
     --region us-east-1
#S = arn:aws:ecs:us-east-1:215555180754:service/sap/solomonassistantsapp

# Update the AWS service
aws ecs update-service \
     --cluster sap \
     --service solomonassistantsapp \
     --task-definition solomonassistantsapp:2

# Blue/Green Deployment
# TEST target-group
aws elbv2 create-target-group \
     --name sap-target-test \
     --protocol HTTP \
     --port 8080 \   
     --target-type ip \
     --vpc-id vpc-0050cc7d \
     --region us-east-1
# arn:aws:elasticloadbalancing:us-east-1:215555180754:targetgroup/sap-target-test/be53d9deebf4a6e5

# Create a test Listener on the ALB
aws elbv2 create-listener \
     --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:215555180754:loadbalancer/app/sap-alb/34f77eb563a575c4 \
     --protocol HTTP \
     --port 8080 \
     --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:215555180754:targetgroup/sap-target-test/be53d9deebf4a6e5 \
     --region us-east-1