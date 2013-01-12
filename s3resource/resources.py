from hyperadmin.resources.storages import StorageResource

from s3resource.forms import S3UploadLinkForm
from s3resource.endpoints import S3UploadSuccessEndpoint


class S3StorageResource(StorageResource):
    upload_link_form_class = S3UploadLinkForm
    
    def get_view_endpoints(self):
        endpoints = super(StorageResource, self).get_view_endpoints()
        endpoints.append((S3UploadSuccessEndpoint, {}))
        return endpoints
