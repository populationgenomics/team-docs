from pulumi_gcp.storage.outputs import BucketEncryption
import pulumi
import pulumi_gcp as gcp

DOMAIN = 'populationgenomics.org.au'
REGION = 'australia-southeast1'

# Fetch configuration.
config = pulumi.Config()
customer_id = config.require('customer_id')
enable_release = config.get_bool('enable_release')
archive_age = config.get_int('archive_age') or 30
dataset = pulumi.get_stack()


def bucket_name(kind: str) -> str:
    return f'cpg-{dataset}-{kind}'


def create_bucket(name: str, **kwargs) -> gcp.storage.Bucket:
    return gcp.storage.Bucket(
        name,
        name=name,
        location=REGION,
        versioning=gcp.storage.BucketVersioningArgs(enabled=True),
        labels={'bucket': name},
        **kwargs)


undelete_rule = gcp.storage.BucketLifecycleRuleArgs(
    action=gcp.storage.BucketLifecycleRuleActionArgs(
        type='Delete'),
    condition=gcp.storage.BucketLifecycleRuleConditionArgs(
        age=30, with_state='ARCHIVED'))

upload_bucket = create_bucket(
    bucket_name('upload'), lifecycle_rules=[undelete_rule])

# The Cloud Identity API is required for creating access groups.
cloudidentity = gcp.projects.Service('cloudidentity-service',
                                     service='cloudidentity.googleapis.com',
                                     disable_on_destroy=False)

upload_account = gcp.serviceaccount.Account(
    'upload-service-account',
    account_id='upload',
    display_name='upload',
    opts=pulumi.resource.ResourceOptions(depends_on=[cloudidentity]))

gcp.storage.BucketIAMMember(
    'upload-permissions-viewer',
    bucket=upload_bucket.name,
    role='roles/storage.objectViewer',
    member=pulumi.Output.concat('serviceAccount:', upload_account.email))

gcp.storage.BucketIAMMember(
    'upload-permissions-creator',
    bucket=upload_bucket.name,
    role='roles/storage.objectCreator',
    member=pulumi.Output.concat('serviceAccount:', upload_account.email))

archive_bucket = create_bucket(
    bucket_name('archive'),
    lifecycle_rules=[
        gcp.storage.BucketLifecycleRuleArgs(
            action=gcp.storage.BucketLifecycleRuleActionArgs(
                type='SetStorageClass', storage_class='ARCHIVE'),
            condition=gcp.storage.BucketLifecycleRuleConditionArgs(
                age=archive_age)),
        undelete_rule])

main_bucket = create_bucket(
    bucket_name('main'), lifecycle_rules=[undelete_rule])
analysis_bucket = create_bucket(
    bucket_name('analysis'), lifecycle_rules=[undelete_rule])
test_bucket = create_bucket(
    bucket_name('test'), lifecycle_rules=[undelete_rule])

temporary_bucket = create_bucket(
    bucket_name('temporary'),
    lifecycle_rules=[
        gcp.storage.BucketLifecycleRuleArgs(
            action=gcp.storage.BucketLifecycleRuleActionArgs(
                type='Delete'),
            condition=gcp.storage.BucketLifecycleRuleConditionArgs(
                age=30, with_state='LIVE')),
        undelete_rule])


def group_mail(kind: str) -> str:
    return f'{dataset}-{kind}@{DOMAIN}'


def create_group(mail: str) -> gcp.cloudidentity.Group:
    name = mail.split('@')[0]
    return gcp.cloudidentity.Group(
        name,
        display_name=name,
        group_key=gcp.cloudidentity.GroupGroupKeyArgs(id=mail),
        labels={'cloudidentity.googleapis.com/groups.discussion_forum': ''},
        parent=f'customers/{customer_id}',
        opts=pulumi.resource.ResourceOptions(depends_on=[cloudidentity]))


def add_bucket_permissions(name: str,
                           group: gcp.cloudidentity.Group,
                           bucket: gcp.storage.Bucket,
                           role: str) -> gcp.storage.BucketIAMMember:
    return gcp.storage.BucketIAMMember(
        name,
        bucket=bucket.name,
        role=role,
        member=pulumi.Output.concat('group:', group.group_key.id))


restricted_access_group = create_group(group_mail('restricted-access'))

listing_role = gcp.projects.IAMCustomRole(
    "storage-listing-role",
    description="Allows listing of storage objects",
    permissions=["storage.objects.list"],
    role_id="storageObjectLister",
    title="Storage Object Lister",
    opts=pulumi.resource.ResourceOptions(depends_on=[cloudidentity]))

add_bucket_permissions('restricted-access-main-lister',
                       restricted_access_group,
                       main_bucket,
                       listing_role.name)

add_bucket_permissions('restricted-access-analysis-viewer',
                       restricted_access_group,
                       analysis_bucket,
                       'roles/storage.objectViewer')

add_bucket_permissions('restricted-access-test-viewer',
                       restricted_access_group,
                       test_bucket,
                       'roles/storage.objectViewer')

add_bucket_permissions('restricted-access-temporary-admin',
                       restricted_access_group,
                       temporary_bucket,
                       'roles/storage.objectAdmin')

extended_access_group = create_group(group_mail('extended-access'))

add_bucket_permissions('extended-access-main-admin',
                       extended_access_group,
                       main_bucket,
                       'roles/storage.objectAdmin')

add_bucket_permissions('extended-access-analysis-admin',
                       extended_access_group,
                       analysis_bucket,
                       'roles/storage.objectAdmin')

add_bucket_permissions('extended-access-test-admin',
                       extended_access_group,
                       test_bucket,
                       'roles/storage.objectAdmin')

add_bucket_permissions('extended-access-temporary-admin',
                       extended_access_group,
                       temporary_bucket,
                       'roles/storage.objectAdmin')

if enable_release:
    release_bucket = create_bucket(bucket_name('release-requester-pays'),
                                   lifecycle_rules=[undelete_rule],
                                   requester_pays=True)

    add_bucket_permissions('restricted-access-release-viewer',
                           restricted_access_group,
                           release_bucket,
                           'roles/storage.objectViewer')

    add_bucket_permissions('extended-access-release-viewer',
                           extended_access_group,
                           release_bucket,
                           'roles/storage.objectAdmin')

    release_access_group = create_group(group_mail('release-access'))

    add_bucket_permissions('release-access-release-viewer',
                           release_access_group,
                           release_bucket,
                           'roles/storage.objectViewer')

# Cloud Run is used for the server component of the analysis-runner.
cloudrun = gcp.projects.Service('cloudrun-service',
                                service='run.googleapis.com',
                                disable_on_destroy=False)

analysis_runner_service_account = gcp.serviceaccount.Account(
    'analysis-runner-service-account',
    account_id='analysis-runner-server',
    display_name='analysis-runner service account',
    opts=pulumi.resource.ResourceOptions(depends_on=[cloudidentity]))

secretmanager = gcp.projects.Service('secretmanager-service',
                                     service='secretmanager.googleapis.com',
                                     disable_on_destroy=False)

# Add a secret that will hold the Hail token.
hail_token_secret = gcp.secretmanager.Secret(
    'hail-token-secret',
    replication=gcp.secretmanager.SecretReplicationArgs(
        user_managed=gcp.secretmanager.SecretReplicationUserManagedArgs(
            replicas=[
                gcp.secretmanager.SecretReplicationUserManagedReplicaArgs(
                    location=REGION
                ),
            ],
        ),
    ),
    secret_id="hail-token",
    opts=pulumi.resource.ResourceOptions(depends_on=[secretmanager]))

# The analysis-runner server needs to read the Hail token secret.
gcp.secretmanager.SecretIamMember(
    'analysis-runner-service-account-secret-reader',
    secret_id=hail_token_secret.id,
    role='roles/secretmanager.secretAccessor',
    member=pulumi.Output.concat('serviceAccount:', analysis_runner_service_account.email))

project_number = gcp.organizations.get_project().number

# Allow the Cloud Run Service Agent to pull the image.
repo_member = gcp.artifactregistry.RepositoryIamMember(
    'artifact-registry-reader',
    project='analysis-runner',
    location=REGION,
    repository = 'images',
    role='roles/artifactregistry.reader',
    member=f'serviceAccount:service-{project_number}@serverless-robot-prod.iam.gserviceaccount.com')

analysis_runner_server = gcp.cloudrun.Service(
    'analysis-runner-server',
    location=REGION,
    autogenerate_revision_name=True,
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                envs=[{'name': 'DATASET', 'value': dataset}],
                image=f'australia-southeast1-docker.pkg.dev/analysis-runner/images/server:06dd37129625'
            )],
            service_account_name=analysis_runner_service_account.email,
        ),
    ),
    opts=pulumi.resource.ResourceOptions(depends_on=[cloudrun, repo_member]))

pulumi.export('analysis-runner-server URL', analysis_runner_server.statuses[0].url)

# Restrict Cloud Run invokers to the restricted access group.
gcp.cloudrun.IamMember(
    'analysis-runner-invoker',
    service=analysis_runner_server.name,
    location=REGION,
    role='roles/run.invoker',
    member=pulumi.Output.concat('group:', restricted_access_group.group_key.id))
