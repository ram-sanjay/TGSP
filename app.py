import aws_cdk as cdk
import json
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
)

class TestTPGS(Stack):
 
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        region=config.get('region')
        vpcid = config.get('vpcid')
        role_arn = config.get('role_arn')
        key = config.get('key')
        ami_id = self.node.try_get_context("ami_id")
        security_group_id = config.get('security_group_id')
        InstanceType = config.get('instance_type')
        availability_zones=config.get('availability_zones')


        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id=vpcid)
        role = iam.Role.from_role_arn(
            self, "ExistingRole", role_arn=role_arn
        )
        existing_security_group = ec2.SecurityGroup.from_security_group_id(
            self, 'ImportedSecurityGroup',
            security_group_id=security_group_id,
        )


        ec2_instance = ec2.Instance(
            self,
            "TPGS-1",
            instance_type=ec2.InstanceType(InstanceType),
            machine_image=ec2.MachineImage.generic_linux(ami_map={region: ami_id}),
            vpc=vpc,
            availability_zone=availability_zones[0],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            associate_public_ip_address = True,
            security_group=existing_security_group,
            role= role,
            key_name=key
        )
        # ec2_instance.instance.add_property_override("DisableApiTermination",True)
        ec2_instance.apply_removal_policy(cdk.RemovalPolicy.RETAIN)

        ec2_instance1 = ec2.Instance(
            self,
            "TPGS-2",
            instance_type=ec2.InstanceType(InstanceType),
            machine_image=ec2.MachineImage.generic_linux(ami_map={region: ami_id}),
            vpc=vpc,
            availability_zone=availability_zones[1],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            associate_public_ip_address = True,
            security_group=existing_security_group,
            role= role,
            key_name=key
        )
        # ec2_instance1.instance.add_property_override("DisableApiTermination",True)
        ec2_instance1.apply_removal_policy(cdk.RemovalPolicy.RETAIN)


        ssm.StringParameter(self, "InstanceIdParameter",
            parameter_name="ec2instance1",
            string_value=ec2_instance.instance_id
        )
        ssm.StringParameter(self, "InstanceIdParameter1",
            parameter_name="ec2instance2",
            string_value=ec2_instance1.instance_id
        )

        ssm.StringParameter(self, "Instance1IP",
            parameter_name="EC2InstanceIP1",
            string_value=ec2_instance.instance_public_ip
        )
        ssm.StringParameter(self, "Instance2IP",
            parameter_name="EC2InstanceIP2",
            string_value=ec2_instance1.instance_public_ip
        )




class ProdTPGS(Stack):
 
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        instance1 = self.node.try_get_context("instance1")
        instance2 = self.node.try_get_context("instance2")
        EIP_AllocationID1 = config.get('EIP_AllocationID1')
        EIP_AllocationID2 = config.get('EIP_AllocationID2')


        ec2.CfnEIPAssociation(self, 'EIPAssociation1',
            allocation_id=EIP_AllocationID1,
            instance_id=instance1)
        
        ec2.CfnEIPAssociation(self, 'EIPAssociation2',
            allocation_id=EIP_AllocationID2,
            instance_id=instance2)




with open('config.json', 'r') as config_file:
    config = json.load(config_file)
env = cdk.Environment(account=config.get('AccountId'), region=config.get('region'))
app = cdk.App()
TestTPGS(app, "TestTPGS", env=env)
ProdTPGS(app, "ProdTPGS", env=env)


app.synth()




