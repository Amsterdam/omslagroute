# from swift.storage import SwiftStorage as SwiftStorageNative
# from storages.backends.azure_storage import AzureStorage

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
