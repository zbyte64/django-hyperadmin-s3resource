from django.conf.urls.defaults import patterns, url

from hyperadmin.resources.storages.storages import StorageResource

from s3resource.forms import S3UploadLinkForm
from s3resource.views import S3UploadSuccessView


class S3StorageResource(StorageResource):
    upload_link_form_class = S3UploadLinkForm
    directupload_sucess_view = S3UploadSuccessView
    
    def get_form_kwargs(self, item=None, **kwargs):
        kwargs = super(S3StorageResource, self).get_form_kwargs(item, **kwargs)
        kwargs['resource'] = self
        return kwargs
    
    def get_extra_urls(self):
        urlpatterns = super(S3StorageResource, self).get_extra_urls()
        
        def wrap(view, cacheable=False):
            return self.as_view(view, cacheable)
        
        init = self.get_view_kwargs()
        
        urlpatterns += patterns('',
            url(r'^directupload-sucess/$',
                wrap(self.directupload_success_view.as_view(**init)),
                name='%sdirectupload_success' % self.get_base_url_name()),
        )
        return urlpatterns
    
    def get_directupload_success_url(self):
        return self.reverse('%sdirectupload_success' % self.get_base_url_name())

