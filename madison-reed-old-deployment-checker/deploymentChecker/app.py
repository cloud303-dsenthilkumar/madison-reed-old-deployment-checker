import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    cf = boto3.client('cloudformation')
    stacks = cf.describe_stacks()['Stacks']
    
    # Define static states
    static_states = ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE']
    
    for stack in stacks:
        # Proceed only if the stack is in a static state
        if stack['StackStatus'] in static_states:
            # Extract tags into a dictionary for easier access
            tags = {tag['Key']: tag['Value'] for tag in stack.get('Tags', [])}
            cleanup_date_str = tags.get('CleanupDate')
            
            # Proceed if the 'CleanupDate' tag exists
            if cleanup_date_str:
                cleanup_date = datetime.strptime(cleanup_date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                
                # Check if the cleanup date is in the past
                if cleanup_date < now:
                    stack_name = stack['StackName']
                    try:
                        print(f"Deleting stack: {stack_name}")
                        cf.delete_stack(StackName=stack_name)
                    except ClientError as e:
                        print(f"Error deleting stack {stack_name}: {e}")
