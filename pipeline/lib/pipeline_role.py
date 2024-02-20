from constructs import Construct
from aws_cdk import aws_iam as iam


# TODO make this extend the iam.Role class or implement the iam.IRole interface.
class PipelineRole(Construct):
    """
    An IAM role that allows the CodePipeline principal to push an image to any ECR repository.
    """

    @property
    def role(self) -> iam.Role:
        return self._role

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self._role = iam.Role(
            self,
            f"{id}AllowPushToEcrRepository",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
        )

        self._role.attach_inline_policy(
            iam.Policy(
                self,
                "AllowPushToEcrRepositoryPolicy",
                document=iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:CompleteLayerUpload",
                                "ecr:GetAuthorizationToken",
                                "ecr:InitiateLayerUpload",
                                "ecr:PutImage",
                                "ecr:UploadLayerPart",
                                "ecr:BatchGetImage",
                                "ecr:GetDownloadUrlForLayer",
                            ],
                            resources=["*"],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                ),
            )
        )
