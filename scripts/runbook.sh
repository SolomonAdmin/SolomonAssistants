#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
echo "Starting script"

# AWS Configuration
vpc="vpc-0050cc7d"
sb1="subnet-770f4328"
sb2="subnet-da4b5897"
sg="sg-0e17a4185f1832374"
region="us-east-1"
acc="215555180754"
lb_name="client1-alb"
cluster_name="client1"
tg_name="client1alb-target1"
service_name="client1"
ecr_image="215555180754.dkr.ecr.us-east-1.amazonaws.com/solomonassistantsapp:latest"

# Check if Load Balancer exists
if ! aws elbv2 describe-load-balancers --names $lb_name --region $region 2>/dev/null; then
    echo "Creating Load Balancer: $lb_name"
    aws elbv2 create-load-balancer --name $lb_name --subnets $sb1 $sb2 --security-groups $sg --region $region
else
    echo "Load Balancer $lb_name already exists."
fi

# Check if Target Group exists
if ! aws elbv2 describe-target-groups --names $tg_name --region $region 2>/dev/null; then
    echo "Creating Target Group: $tg_name"
    aws elbv2 create-target-group --name $tg_name --protocol HTTP --port 80 --target-type ip --vpc-id $vpc --region $region
else
    echo "Target Group $tg_name already exists."
fi

# Create Listener
aws elbv2 create-listener \
     --load-balancer-arn arn:aws:elasticloadbalancing:$region:$acc:loadbalancer/app/client1-alb/05e3ab6be983d171 \
     --protocol HTTP \
     --port 80 \
     --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:$region:$acc:targetgroup/$tg_name/e6033c1d13e45278 \
     --region $region

# Check if ECS Cluster exists
if ! aws ecs describe-clusters --clusters $cluster_name --region $region | grep -q "ACTIVE"; then
    echo "Creating ECS Cluster: $cluster_name"
    aws ecs create-cluster --cluster-name $cluster_name --region $region
else
    echo "ECS Cluster $cluster_name already exists."
fi

# Register Task Definition using the latest ECR image
echo "Registering Task Definition using image: $ecr_image"
sed "s|<ECR_IMAGE>|$ecr_image|g" client1-task-def.json > tmp_task_def.json
aws ecs register-task-definition --cli-input-json file://tmp_task_def.json --region $region
rm tmp_task_def.json

# Update or create ECS Service
if aws ecs describe-services --services $service_name --cluster $cluster_name --region $region | grep -q "ACTIVE"; then
    echo "Updating ECS Service: $service_name"
    # Update ECS service logic here
else
    echo "Creating ECS Service: $service_name"
    # Create ECS service logic here
fi
