import os

from hyperadmin.resources.storages.forms import UploadLinkForm

from django import forms


def form_factory(fields):
    class GeneratedForm(forms.Form):
        def __init__(self, **kwargs):
            self.instance = kwargs.pop('instance', None)
            self.storage = kwargs.pop('storage')
            super(GeneratedForm, self).__init__(**kwargs)
    GeneratedForm.base_fields.update(fields)
    return GeneratedForm

class S3UploadLinkForm(UploadLinkForm):
    def save(self, commit=True):
        file_name = self.storage.get_valid_name(self.cleaned_data['name'])
        path = os.path.join(self.cleaned_data['upload_to'], file_name)
        overwrite = self.cleaned_data.get('overwrite', False)
        if overwrite:
            name = path
        else:
            name = self.storage.get_available_name(path)
        
        url_maker = S3Backend()
        
        url_maker.update_post_params(targetpath=name, upload_to=self.cleaned_data['upload_to'])
        
        fields = dict()
        for key, value in url_maker.post_data.iteritems():
            fields[key] = forms.CharField(initial=value, widget=forms.HiddenInput)
        fields['file'] = forms.FileField()
        form_class = form_factory(fields)
        
        form_kwargs = {'initial':url_maker.post_data}
        link = self.resource.get_create_link(form_kwargs=form_kwargs, form_class=form_class, url=url_maker.get_target_url())
        return link



from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from urllib import quote_plus
from datetime import datetime
from datetime import timedelta
import base64
import hmac
import hashlib

def _set_default_if_none(dict, key, default=None):
    if key not in dict:
        dict[key] = default

#TODO django-storages should make these variables accessible from the storage object

# AWS Options
ACCESS_KEY_ID       = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
SECRET_ACCESS_KEY   = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
BUCKET_NAME         = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
SECURE_URLS         = getattr(settings, 'AWS_S3_SECURE_URLS', False)
BUCKET_URL          = getattr(settings, 'AWS_BUCKET_URL',  '%s%s.s3.amazonaws.com' % (('https://' if SECURE_URLS else 'http://'), BUCKET_NAME))
DEFAULT_ACL         = getattr(settings, 'AWS_DEFAULT_ACL', 'public-read')
DEFAULT_KEY_PATTERN = getattr(settings, 'AWS_DEFAULT_KEY_PATTERN', '${targetname}')
DEFAULT_FORM_TIME   = getattr(settings, 'AWS_DEFAULT_FORM_LIFETIME', 36000) # 10 HOURS
BUCKET_PREFIX       = getattr(settings, 'AWS_MEDIA_STORAGE_BUCKET_PREFIX', getattr(settings, 'AWS_BUCKET_PREFIX', None))


class S3Backend(object):
    def __init__(self, options={}, post_data={}, conditions={}):
        self.conditions = conditions
        self.options = getattr(settings, 'DEFAULT_DIRECTUPLOAD_OPTIONS', {})
        self.options.update(options)
        
        _set_default_if_none(self.options, 'url', self.get_target_url())
        
        self.build_options()
        self.post_data = post_data
    
    def get_target_url(self):
        return BUCKET_URL
    
    def build_options(self):
        self.options['forceIframeTransport'] = True
        self.options['fileObjName'] = 'file'
    
    def build_post_data(self):
        if 'folder' in self.options:
            key = os.path.join(self.options['folder'], DEFAULT_KEY_PATTERN)
        else:
            key = DEFAULT_KEY_PATTERN
        #_set_default_if_none(self.post_data, 'key', key) #this is set by update_post_params
        _set_default_if_none(self.post_data, 'acl', DEFAULT_ACL)
        
        try:
            _set_default_if_none(self.post_data, 'bucket', BUCKET_NAME)
        except ValueError:
            raise ImproperlyConfigured("Bucket name is a required property.")
 
        try:
            _set_default_if_none(self.post_data, 'AWSAccessKeyId', ACCESS_KEY_ID)
        except ValueError:
            raise ImproperlyConfigured("AWS Access Key ID is a required property.")

        self.conditions = self.build_conditions()

        if not SECRET_ACCESS_KEY:
            raise ImproperlyConfigured("AWS Secret Access Key is a required property.")
        
        expiration_time = datetime.utcnow() + timedelta(seconds=DEFAULT_FORM_TIME)
        self.policy_string = self.build_post_policy(expiration_time)
        self.policy = base64.b64encode(self.policy_string)
         
        self.signature = base64.encodestring(hmac.new(SECRET_ACCESS_KEY, self.policy, hashlib.sha1).digest()).strip()
        
        self.post_data['policy'] = self.policy
        self.post_data['signature'] = self.signature
    
    def build_conditions(self):
        conditions = list()
        
        path = self.options['upload_to']
        if BUCKET_PREFIX:
            path = os.path.join(BUCKET_PREFIX, path)
        
        #make s3 happy with uploadify
        conditions.append(['starts-with', '$targetname', '']) #variable introduced by this package
        conditions.append(['starts-with', '$targetpath', path])
        conditions.append({'success_action_status': '200'})
        
        #real conditions
        conditions.append(['starts-with', '$key', path])
        conditions.append({'bucket': self.post_data['bucket']})
        conditions.append({'acl': self.post_data['acl']})
        return conditions
    
    def build_post_policy(self, expiration_time):
        policy = {'expiration': expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                  'conditions': self.conditions,}
        return json.dumps(policy)
    
    def update_post_params(self, targetpath, upload_to):
        #instruct s3 that our key is the targetpath
        self.options['targetpath'] = targetpath
        self.options['upload_to'] = upload_to
        self.build_post_data()
        #params.update(self.post_data)
        #params['key'] = params['targetpath']
        #params['success_action_status'] = '200'

def _uri_encode(str):
    try:
        # The Uploadify flash component apparently decodes the scriptData once, so we need to encode twice here.
        return quote_plus(quote_plus(str, safe='~'), safe='~')
    except:
        raise ValueError

