from hyperadmin.endpoints import LinkPrototype, Endpoint
from hyperadmin.resources.storages.endpoints import BoundFile


class UploadLinkSuccessPrototype(LinkPrototype):
    def show_link(self, **kwargs):
        return self.resource.has_add_permission()
    
    def get_link_kwargs(self, **kwargs):
        link_kwargs = {'url':self.get_url(),
                       'on_submit':self.handle_submission,
                       'rel':'upload-link',}
        link_kwargs.update(kwargs)
        return super(UploadLinkSuccessPrototype, self).get_link_kwargs(**link_kwargs)
    
    def on_success(self, link):
        return link

class S3UploadSuccessEndpoint(Endpoint):
    '''
    Redirects to the appropriate REST path based on the key
    '''
    endpoint_class = 'redirect'
    
    name_suffix = 'upload_success'
    url_suffix = r'^upload-success/$'
    
    def get_link_prototypes(self):
        return {'GET':UploadLinkSuccessPrototype(endpoint=self, name='upload_success'),}
    
    def get(self, request, *args, **kwargs):
        key = self.request.GET.get('key', None)
        assert key
        bound_file = BoundFile(self.resource.storage, key)
        item = self.resource.get_resource_item(bound_file)
        link = self.resource.get_item_link(item)
        return link
