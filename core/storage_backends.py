from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """To handle project's static files"""
    location = 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    """Storage backend for user uploaded files"""
    location = 'media'
    default_acl = 'public-read'
    # eg. users can have files with the same name..
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    """To handle private media files"""
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False


