import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # List of regions you want to check CloudFormation stacks in
    regions = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    for region in regions:
        print(f"Checking stacks in region: {region}")
        cf = boto3.client('cloudformation', region_name=region)
        
        # Initialize paginator for the describe_stacks operation in the current region
        paginator = cf.get_paginator('list_stacks')
        
        # Filter for stacks in a completed state (adjust as needed)
        stack_statuses = ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE']
        
        # Iterate through pages of stacks in the current region
        for page in paginator.paginate(StackStatusFilter=stack_statuses):
            for summary in page['StackSummaries']:
                stack_name = summary['StackName']
                stack_status = summary['StackStatus']
                
                # Describe the stack to get its tags
                stack_description = cf.describe_stacks(StackName=stack_name)
                stack_tags = stack_description['Stacks'][0]['Tags']
                
                # Convert tags into a dictionary for easier access
                tags_dict = {tag['Key']: tag['Value'] for tag in stack_tags}
                
                # Check for the 'CleanupDate' tag and delete stack if criteria met
                cleanup_date_str = tags_dict.get('CleanupDate')
                if cleanup_date_str:
                    cleanup_date = datetime.strptime(cleanup_date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    
                    if cleanup_date < now:
                        try:
                            print(f"Deleting stack: {stack_name} in region: {region}")
                            cf.delete_stack(StackName=stack_name)
                        except ClientError as e:
                            print(f"Error deleting stack {stack_name} in region: {region}: {e}")

