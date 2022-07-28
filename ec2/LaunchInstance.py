import boto3
import json
from botocore.config import Config

# Read config file
with open("config.json") as file:
    configuration = json.load(file)

# Configure default region
aws_config = Config(
    region_name="us-east-1",
)
client = boto3.client("ec2", config=aws_config)
ec2_resource = boto3.resource("ec2", config=aws_config)

"""
    This is a simple class that creates an EC2 instance on AWS.
    It uses boto3 as the API for connecting to Amazon Web Sercvices Cloud.

    Please follow this link to configure your AWS credentials 
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
"""


class LaunchInstance:
    def __init__(self):
        self.instance_type = configuration["instance_type"]
        self.security_group_id = self.create_security_group()

    def create_security_group(self):
        security_group_name = configuration["security_group_name"]
        sec_groups = client.describe_security_groups()["SecurityGroups"]

        self.print_message("Creating security group")

        for sec_group in sec_groups:
            if sec_group.get("GroupName") == security_group_name:
                sec_group_id = sec_group['GroupId']
                print(f"The security group {security_group_name} exists. Group ID: {sec_group_id} ")
                return sec_group_id

        response = client.create_security_group(
            GroupName=configuration["security_group_name"],
            Description="Web service security group",
        )

        security_group_id = response["GroupId"]

        print("Created security group with ID: " + security_group_id)

        # Add a rule to the security group to allow HTTP ingress
        client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                }
            ],
        )
        return security_group_id

    """
        function to launch an ec2 instance
        @ return instance_id
    """
    def launch(self):
        self.print_message("Launching instance")
        instance = client.run_instances(
            ImageId=configuration["ami"],
            InstanceType=self.instance_type,
            SecurityGroupIds=[self.security_group_id],
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Tutorial", "Value": "ec2 tutorial"}],
                }
            ],
        )["Instances"][0]

        # Get instance created

        # Wait for instance to start running
        waiter = client.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance["InstanceId"]])

        # Fetch latest instance details
        instance = client.describe_instances(
            InstanceIds=[instance["InstanceId"]]
        )["Reservations"][0]["Instances"][0]

        print(
            "Launched instance with ID: "
            + instance["InstanceId"]
            + " and state: "
            + instance["State"]["Name"]
        )

        return instance
    
    def print_message(self, msg):
        print (("*" * 40) + "\n" + msg + "\n" + ("*" * 40))


if __name__ == "__main__":
    print("In main")
    launchInstance = LaunchInstance()

    launchInstance.launch()
