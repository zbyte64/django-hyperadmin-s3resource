import mimeparse

from django.views.generic import View

from hyperadmin.resources.views import ResourceViewMixin
from hyperadmin.resources.storages.views import BoundFile, StorageMixin


class S3UploadSuccessView(StorageMixin, ResourceViewMixin, View):
    '''
    Redirects to the appropriate REST path based on the key
    '''
    view_class = 'redirect'
    
    def get_response_type(self):
        return mimeparse.best_match(
            self.resource_site.media_types.keys(), 
            self.request.GET.get('response_type', self.request.META.get('HTTP_ACCEPT', ''))
        )
    
    def get(self, request, *args, **kwargs):
        key = self.request.GET.get('key', None)
        assert key
        bound_file = BoundFile(self.resource.storage, key)
        item = self.resource.get_resource_item(bound_file)
        link = self.resource.get_item_link(item)
        return self.resource.generate_response(self.get_response_media_type(), self.get_response_type(), link)

