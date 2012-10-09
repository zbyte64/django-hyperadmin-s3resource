from urllib import urlencode

from django.views.generic import View

from hyperadmin.resources.views import ResourceViewMixin
from hyperadmin.resources.storages.views import BoundFile, StorageMixin


class S3UploadSuccessView(StorageMixin, ResourceViewMixin, View):
    '''
    Redirects to the appropriate REST path based on the key
    '''
    view_class = 'redirect'
    
    def get(self, request, *args, **kwargs):
        key = self.request.GET.get('key', None)
        assert key
        bound_file = BoundFile(self.resource.storage, key)
        item = self.resource.get_resource_item(bound_file)
        link = self.resource.get_item_link(item)
        if '_HTTP_ACCEPT' in self.request.GET:
            params = {'_HTTP_ACCEPT': self.request.GET['_HTTP_ACCEPT']}
            link.url = '%s?%s' % (link.url, urlencode(params))
        return self.resource.generate_response(self.get_response_media_type(), self.get_response_type(), link)

