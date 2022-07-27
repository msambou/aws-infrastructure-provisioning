import boto3
import json

# Read config file
with open("config.json") as file:
    configuration = json.load(file)

client = boto3.client("ec2")


class LaunchInstance:
    def __init__(self):
        self.instance_type = configuration.instance_type
        self.security_group_id = self.create_security_group()

    def create_security_group(self):
        security_group_name = "web-security-group"
        sec_groups = client.describe_security_groups()["SecurityGroups"]
        for sec_group in sec_groups:
            if sec_group.get("GroupName") == security_group_name:
                return sec_group["GroupId"]

        response = client.create_security_group(
            GroupName="web-security-group",
            Description="Launch a web server",
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
        response = client.run_instances(
            InstanceType=self.instance_type,
            SecurityGroupIds=[self.security_group_id],
        )

        instance = response["Instances"][0]

        # Wait for instance to start running
        waiter = client.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance["InstanceId"]])

        # Reload instance data
        instance.load()

        print(
            "Launched instance with ID: "
            + response["Instances"][0]["InstanceId"]
            + " and state: "
            + instance["State"]["Name"]
        )

        return instance


if __name__ == "__main__":
    pass
    # main()
