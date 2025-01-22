# pylint: disable=unused-argument

"""
===================
sword_fargate.py
===================
Lambda function for launching fargate task
"""
import os
import boto3

AWS_REGION = os.environ['REGION']
TASK = os.environ['TASK_NAME']
CLUSTER = os.environ['FARGATE_CLUSTER']
SUBNET_ID = os.environ['FARGATE_SUBNET_ID']
SECURITY_GROUP = os.environ['FARGATE_SECURITY_GROUP']


def run_fargate_task(event, context):
    """function for launching a fargate task"""
    client = boto3.client('ecs', region_name=AWS_REGION)
    response = client.run_task(
        cluster=CLUSTER,
        launchType='FARGATE',
        taskDefinition=TASK,
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    SUBNET_ID,
                ],
                'securityGroups': [
                    SECURITY_GROUP,
                ],
                'assignPublicIp': 'DISABLED'
            }
        }
    )
    return str(response)
