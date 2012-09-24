from hyperadmin.resources.storages.storages import StorageResource

from s3resource.forms import S3UploadLinkForm

class S3StorageResource(StorageResource):
    upload_link_form_class = S3UploadLinkForm

