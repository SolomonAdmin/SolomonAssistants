vpc=vpc-0050cc7d
sb1=subnet-770f4328
sb2=subnet-da4b5897
sg=sg-0e17a4185f1832374
region=us-east-1
acc=215555180754
lb_name=client1-alb

echo "VPC: $vpc"
echo "Subnet 1: $sb1"
echo "Subnet 2: $sb2"
echo "Security Group: $sg"
echo "Region: $region"
echo "Account: $acc"
echo "Load Balancer Name: $lb_name"

# Create LB
aws elbv2 create-load-balancer \
  --name "$lb_name" \
  --subnets "$sb1" "$sb2" \
  --security-groups "$sg" \
  --region "$region"
# # LB=arn:aws:elasticloadbalancing:$region:$acc:loadbalancer/app/client1-alb/05e3ab6be983d171

#Create Target Group
aws elbv2 create-target-group \
     --name client1alb-target1 \
     --protocol HTTP \
     --port 80 \
     --target-type ip \
     --vpc-id vpc-0050cc7d \
     --region us-east-1
# TG=arn:aws:elasticloadbalancing:$region:$acc:targetgroup/client1alb-target1/e6033c1d13e45278

aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:215555180754:loadbalancer/app/client1-alb/64c5d0c99cebb93d \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:215555180754:targetgroup/client1alb-target1/89664e725a08e7d1 \
  --region us-east-1
# # TG=arn:aws:elasticloadbalancing:$region:$acc:listener/app/client1-alb/05e3ab6be983d171/3b60711da724165f

#Create ECS cluster
aws ecs create-cluster \
  --cluster-name client1 \
  --region us-east-1
#CL=arn:aws:ecs:$region:$acc:cluster/client1

# Register Task Definition
aws ecs register-task-definition \
    --cli-input-json file://aws_configs/client1-task-def.json \
    --region us-east-1
#TD=arn:aws:ecs:$region:$acc:task-definition/client1-task-def:1

# Create AWS Service
aws ecs create-service \
     --cli-input-json file://aws_configs/service.json \ 
     --region us-east-1