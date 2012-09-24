from hyperadmin.resources.storages.storages import StorageResource

from s3resources.forms import S3UploadLinkForm

class S3StorageResource(StorageResource):
    upload_link_form_class = S3UploadLinkForm
    
    '''
    def get_upload_link(self, form_kwargs=None, **kwargs):
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs = self.get_form_kwargs(**form_kwargs)
        form_kwargs['resource'] = self
        
        link_kwargs = {'url':self.get_upload_link_url(),
                       'resource':self,
                       'on_submit':self.handle_upload_link_submission,
                       'method':'POST',
                       'form_kwargs':form_kwargs,
                       'form_class': self.get_upload_link_form_class(),
                       'prompt':'create upload link',
                       'rel':'upload-link',}
        link_kwargs.update(kwargs)
        create_link = Link(**link_kwargs)
        return create_link
    
    def get_upload_link_url(self):
        return self.reverse('%s_%s_uploadlink' % (self.app_name, self.resource_name))
    '''

