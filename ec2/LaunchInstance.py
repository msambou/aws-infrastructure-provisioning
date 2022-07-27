import boto3

client = boto3.client("ec2")


class LaunchInstance:
    def __init__(self, instance_type, image_id, key_name, security_group_id):
        self.instance_type = instance_type
        self.image_id = image_id
        self.key_name = key_name
        self.security_group_id = security_group_id

    """
        function to launch an ec2 instance
        @ return instance_id
    """
    def launch(self):
        response = client.run_instances(
            ImageId=self.image_id,
            InstanceType=self.instance_type,
            KeyName=self.key_name,
            SecurityGroupIds=[self.security_group_id],
        )

        # Wait for instance to start running
        waiter = client.get_waiter(
            "instance_running",
            {"InstanceIds": [response["Instances"][0]["InstanceId"]]},
        )
        waiter.wait()

        instance_state = client.describe_instance_status(
            InstanceIds=[response["Instances"][0]["InstanceId"]]
        )

        print(
            "Launched instance with ID: "
            + response["Instances"][0]["InstanceId"]
            + " and state: "
            + instance_state["InstanceStatuses"][0]["InstanceState"]["Name"]
        )
        return response["Instances"][0]["InstanceId"]
