from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, S3Backend
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws import (
    lightsail_container_service,
    lightsail_database,
    lightsail_instance,
    lightsail_key_pair,
    lightsail_domain,
    cloudfront_distribution,
    iam_user,
    iam_access_key,
    iam_user_policy,
    s3_bucket
)
# Correct Random imports
from cdktf_cdktf_provider_random.provider import RandomProvider
from cdktf_cdktf_provider_random import password
from cdktf_cdktf_provider_aws.secretsmanager_secret import SecretsmanagerSecret
from cdktf_cdktf_provider_aws.secretsmanager_secret_version import SecretsmanagerSecretVersion
from cdktf_cdktf_provider_aws.wafv2_web_acl import Wafv2WebAcl, Wafv2WebAclDefaultAction, Wafv2WebAclRule, Wafv2WebAclVisibilityConfig, Wafv2WebAclDefaultActionAllow, Wafv2WebAclRuleOverrideAction, Wafv2WebAclRuleOverrideActionNone, Wafv2WebAclRuleOverrideActionCount, Wafv2WebAclRuleVisibilityConfig
from cdktf_cdktf_provider_aws.wafv2_web_acl_association import Wafv2WebAclAssociation
from cdktf_cdktf_provider_aws.wafv2_rule_group import Wafv2RuleGroupRuleVisibilityConfig


import os, json

#create an enum for different flags
from enum import Enum
class ArchitectureFlags(Enum):
    SKIP_DATABASE = "skip_database"


class BBAWSLightsailMiniV1a(TerraformStack):

    @staticmethod
    def get_architecture_flags():
        """
        Returns the ArchitectureFlags enum.
        """
        return ArchitectureFlags

    @staticmethod
    def get_archetype(product, app, tier, organization, region):
        """
        Returns the BuzzerboyArchetype instance.
        """
        from BuzzerboyArchetypeStack import BuzzerboyArchetype
        return BuzzerboyArchetype(product=product, app=app, tier=tier, organization=organization, region=region)

    resources = {}

    @staticmethod
    def properize_s3_bucketname(string):
        """
        Converts a string to a valid S3 bucket name.
        """
        return string.lower().replace(" ", "-").replace("_", "-").replace(".", "-").replace(":", "-").replace("/", "-").replace("\\", "-")[:63]


    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id)

        # Stack configuration

        self.region = kwargs.get("region", "us-east-1")
        self.environment = kwargs.get("environment", "dev")
        self.project_name = kwargs.get("project_name", "bb-aws-lightsail-mini-v1a-app")
        self.domain_name = kwargs.get("domain_name", "bb-aws-lightsail-mini-v1a-app.buzzerboy.com")
        self.secret_name = kwargs.get("secret_name", f"{self.project_name}/{self.environment}/database-credentials")
        self.profile = kwargs.get("profile", "default")
        self.default_db_name = kwargs.get("default_db_name", self.project_name)
        self.default_db_username = kwargs.get("default_db_username", "dbadmin")
        self.default_signature_version = kwargs.get("default_signature_version", "s3v4")
        self.default_extra_secret_env = kwargs.get("default_extra_secret_env", "SECRET_STRING")
        self.flags = kwargs.get("flags", [])

        self.secrets = {}

        # Create Terraform backend
        self.create_terraform_backend()

        # Initialize providers
        aws = AwsProvider(self, "aws", region=self.region, profile=self.profile)
        self.resources["aws"] = aws

        RandomProvider(self, "random")
        self.resources["random"] = RandomProvider

        self.post_terraform_messages = []
        self._post_plan_guidance: list[str] = []




        # Create IAM resources
        self.create_iam_resources()

        # Create Lightsail resources
        self.create_lightsail_resources()
        self.create_lightsail_database()

        # Create Lightsail domain
        # Commented out as per Fahad's request to create manually
        self.create_lightsail_domain()

        # Create Bastion host
        # Commented out as per Fahad's request to create manually
        self.create_bastion_host()

        # Create cloudfront distribution
        # Commented out as per Fahad's request to create manually
        self.create_networking_resources()

        # Create security resources
        self.create_security_resources()

        # Create S3 bucket
        self.create_s3_bucket()

        # Outputs
        self.create_outputs()

    def create_iam_policy_from_file(self, file_path="iam_policy.json"):

        file_to_open = os.path.join(os.path.dirname(__file__), file_path)


        with open(file_to_open, "r") as f:
            policy = f.read()
        return iam_user_policy.IamUserPolicy(
            self, f"{self.project_name}-{self.environment}-service-policy",
            name=f"{self.project_name}-{self.environment}-service-policy",
            user=self.container_service_user.name,
            policy=policy
        )


    def clean_hypens(self, string):
        """
        Cleans hyphens from a string.
        """
        return string.replace("-", "_").replace(" ", "_").lower()

    def create_state_bucket(self):
        """Create the S3 bucket for Terraform state"""
        
        self.state_bucket_name = f"{self.project_name}-tfstate"
        self.state_bucket = s3_bucket.S3Bucket(self, f"{self.project_name}-tfstate-bucket",
            bucket=self.state_bucket_name,
            versioning=[{
                "enabled": True
            }],
            server_side_encryption_configuration=[{
                "rule": [{
                    "apply_server_side_encryption_by_default": [{
                        "sse_algorithm": "AES256"
                    }]
                }]
            }]
        )

        self.resources["state_bucket"] = self.state_bucket

    def create_terraform_backend(self):
        """Create the S3 bucket for Terraform state"""
        self.state_bucket_name = self.properize_s3_bucketname(f"{self.region}-{self.__class__.__name__}-tfstate")

        TerraformOutput(self, "state_bucket_name",
            value=self.state_bucket_name,
            description="Name of the S3 bucket for Terraform state. This bucket must be created before running cdktf deploy with S3Backend."
        )

        S3Backend(self,
            bucket=self.state_bucket_name,
            key=f"{self.project_name}/terraform.tfstate",
            region=self.region
        )
            




    def create_s3_bucket(self):
        # S3 Bucket for storing application data
         self.s3_bucket = s3_bucket.S3Bucket(
             self, "app_data_bucket",
             bucket=f"{self.project_name}-s3",
             acl="private",
             tags={
                 "Environment": self.environment,
                 "Project": self.project_name,
                 "Stack": self.__class__.__name__
             }
         )

        # Store the S3 bucket in resources
         self.resources["s3_bucket"] = self.s3_bucket
    
        


    def create_iam_resources(self):
        # IAM User for container service
        self.container_service_user = iam_user.IamUser(
            self, "container_service_user",
            name=f"{self.project_name}-service-user"
        )

        self.resources["iam_user"] = self.container_service_user

        # IAM Access Key
        self.container_service_key = iam_access_key.IamAccessKey(
            self, "container_service_key",
            user=self.container_service_user.name
        )
        self.resources["iam_access_key"] = self.container_service_key



        # IAM Policy
        self.container_service_policy = self.create_iam_policy_from_file()
        self.resources["iam_policy"] = self.container_service_policy

    def create_lightsail_resources(self):
        # Lightsail Container Service
        self.container_service = lightsail_container_service.LightsailContainerService(
            self, "app_container",
            name=f"{self.project_name}",
            power="nano",
            region=self.region,
            scale=1,
            is_disabled=False,
            tags={
                    "Environment": self.environment,
                    "Project": self.project_name, 
                    "Stack": self.__class__.__name__                  
                }
        )

        # Database Password
        self.db_password = password.Password(
            self, "db_password",
            length=16,
            special=True,
            override_special="!#$%&*()-_=+[]{}<>:?"
        )

        self.resources["lightsail_container_service"] = self.container_service

    def create_lightsail_database(self):

        if ArchitectureFlags.SKIP_DATABASE.value in self.flags:
            pass
        else:
            self.database = lightsail_database.LightsailDatabase(
                self, "app_database",
                relational_database_name=f"{self.project_name}-db",
                blueprint_id="postgres_14",
                bundle_id="micro_2_0",
            master_database_name=self.clean_hypens(f"{self.project_name}"),
            master_username=self.default_db_username,
            master_password=self.db_password.result,
            skip_final_snapshot=True,
            tags={
                    "Environment": self.environment,
                    "Project": self.project_name,
                    "Stack": self.__class__.__name__
                }

            )

            self.secrets["password"] = self.db_password.result
            self.secrets["username"] = self.default_db_username
            self.secrets["dbname"] = self.default_db_name
            self.secrets["host"] = self.database.master_endpoint_address
            self.secrets["port"] = self.database.master_endpoint_port


            self.resources["lightsail_database"] = self.database


    def create_lightsail_domain(self):
        # Lightsail Domain
        # self.domain = lightsail_domain.LightsailDomain(
        #     self, "app_domain",
        #     domain_name=self.domain_name
        # )
        pass

    def create_bastion_host(self):
        # Bastion Key Pair
        # self.bastion_key = lightsail_key_pair.LightsailKeyPair(
        #     self, "bastion_key",
        #     name=f"{self.project_name}-bastion-key-{self.environment}"
        # )

        # Bastion Host
        # self.bastion_host = lightsail_instance.LightsailInstance(
        #     self, "bastion_host",
        #     name=f"{self.project_name}-bastion-{self.environment}",
        #     availability_zone="us-east-1a",
        #     blueprint_id="amazon_linux_2",
        #     bundle_id="micro_2_0",
        #     key_pair_name=self.bastion_key.name,
        #     tags={
        #         "Environment": self.environment,
        #         "Role": "bastion"
        #     }
        # )
        pass

    def create_networking_resources(self):
        # CloudFront Distribution
        # self.cloudfront = cloudfront_distribution.CloudfrontDistribution(
        #     self, "app_distribution",
        #     enabled=True,
        #     default_root_object="index.html",
        #     origin=[cloudfront_distribution.CloudfrontDistributionOrigin(
        #         domain_name=f"{self.container_service.name}.{self.region}.cs.amazonlightsail.com",
        #         origin_id="lightsail-container-origin",
        #         custom_origin_config=cloudfront_distribution.CloudfrontDistributionOriginCustomOriginConfig(
        #             http_port=80,
        #             https_port=443,
        #             origin_protocol_policy="http-only",
        #             origin_ssl_protocols=["TLSv1.2"]
        #         )
        #     )],
        #     default_cache_behavior=cloudfront_distribution.CloudfrontDistributionDefaultCacheBehavior(
        #         allowed_methods=["GET", "HEAD", "OPTIONS"],
        #         cached_methods=["GET", "HEAD"],
        #         target_origin_id="lightsail-container-origin",
        #         forwarded_values=cloudfront_distribution.CloudfrontDistributionDefaultCacheBehaviorForwardedValues(
        #             query_string=False,
        #             cookies=cloudfront_distribution.CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies(
        #                 forward="none"
        #             )
        #         ),
        #         viewer_protocol_policy="redirect-to-https",
        #         min_ttl=0,
        #         default_ttl=3600,
        #         max_ttl=86400
        #     ),
        #     restrictions=cloudfront_distribution.CloudfrontDistributionRestrictions(
        #         geo_restriction=cloudfront_distribution.CloudfrontDistributionRestrictionsGeoRestriction(
        #             restriction_type="none"
        #         )
        #     ),
        #     viewer_certificate=cloudfront_distribution.CloudfrontDistributionViewerCertificate(
        #         cloudfront_default_certificate=True
        #     ),
        #     tags={
        #         "Environment": self.environment,
        #         "Name": f"{self.project_name}-distribution"
        #     }
        # )
        pass


    def get_extra_secret_env(self):
        #grab the environment variable  if it exists
        extra_secret_env = os.environ.get(self.default_extra_secret_env, None)

        #check if extra_secret_env is json or not
        if extra_secret_env:
            try:
                extra_secret_json = json.loads(extra_secret_env)
                for key, value in extra_secret_json.items():
                    if key not in self.secrets.keys():
                        self.secrets[key] = value
            except json.JSONDecodeError:
                pass

    def create_security_resources(self):
        # Secrets Manager Secret
        self.db_secret = SecretsmanagerSecret(
            self, self.secret_name,
            name=f"{self.secret_name}"
        )

        self.resources["secretsmanager_secret"] = self.db_secret

        self.secrets["service_user_access_key"] = self.container_service_key.id
        self.secrets["service_user_secret_key"] = self.container_service_key.secret
        self.secrets["access_key"] = self.container_service_key.id
        self.secrets["secret_access_key"] = self.container_service_key.secret
        self.secrets["region_name"] = self.region
        self.secrets["signature_version"] = self.default_signature_version

        # Secret Version
        self.get_extra_secret_env()  # Get extra secrets from environment variable

        # Secret Version
        SecretsmanagerSecretVersion(
            self, self.secret_name + "_version",
            secret_id=self.db_secret.id,
            secret_string=json.dumps(self.secrets, indent=2, sort_keys=True) if self.secrets else None
            )

    
    def has_flag(self, flag):
        """
        Check if a specific flag is set.
        """
        return flag in self.flags
    
    def create_outputs(self):
        TerraformOutput(
            self, "container_service_url",
            value=f"https://{self.container_service.name}.{self.region}.cs.amazonlightsail.com"
        )

        if not self.has_flag(ArchitectureFlags.SKIP_DATABASE.value):
            TerraformOutput(
                self, "database_endpoint",
                value=f"{self.database.master_endpoint_address}:{self.database.master_endpoint_port}"
             )
            TerraformOutput(
                self, "database_password",
                value=self.database.master_password,
                sensitive=True
             ) 


        TerraformOutput(
            self, "iam_user_access_key",
            value=self.container_service_key.id,
            sensitive=True
        )

        TerraformOutput(
            self, "iam_user_secret_key",
            value=self.container_service_key.secret,
            sensitive=True
        )

    