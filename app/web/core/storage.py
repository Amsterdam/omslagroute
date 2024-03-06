from swift.storage import SwiftStorage as SwiftStorageNative
from storages.backends.azure_storage import AzureStorage
from azure.identity import DefaultAzureCredential

# from time import time
# from six.moves.urllib import parse as urlparse
# from .utils import generate_temp_url


# class SwiftStorage(AzureStorage):
#     def _path(self, name):
#         try:
#             name = name.encode('utf-8')
#         except UnicodeDecodeError:
#             pass
#         url = urlparse.urljoin(self.base_url, urlparse.quote(name))

#         # Are we building a temporary url?
#         if self.use_temp_urls:
#             expires = int(time() + int(self.temp_url_duration))
#             path = urlparse.unquote(urlparse.urlsplit(url).path)
#             tmp_path = generate_temp_url(path, expires, self.temp_url_key, 'GET', absolute=True)
#             url = urlparse.urljoin(self.base_url, tmp_path)

#         return url
class MyAzureStorage(AzureStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.azure_credentials = DefaultAzureCredential()

    def _save(self, name, content):
        # Obtain a token using AZURE_CREDENTIAL
        print("Saving..")
        token = self.azure_credentials.get_token('https://storage.azure.com/.default')
        
        # Pass the token to azure_storage for authentication
        self.azure_token_credential = token.token

        return super()._save(name, content)