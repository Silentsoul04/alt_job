from scrapy import signals
import os
import stem
import stem.control

def _set_new_ip():
    with stem.control.Controller.from_port(port=9051) as controller:
        controller.authenticate(password='tor_password')
        controller.signal(stem.Signal.NEWNYM)

class TorMiddleware(object):
    """
    NOT USED 
    You must first install the Tor service on your system
    """
    def process_request(self, request, spider):
        _set_new_ip()
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        spider.log('Proxy : %s' % request.meta['proxy'])

#   TODO: ENABLE MIDDLEWARE ONLY IF CONFIG FILE OPTION IS ON AND SITE 
#   IS NOT PROTECTED BY CLOUDFLARE (=> MAKE A CONSTANT OF CLOUD FLARE PROTECTED SITES)

# class GoogleCacheMiddleware(object):
#     def process_request(self, request, spider):
#         if spider.use_google_cache == True and 'googleusercontent' not in request.url:
#             new_url = 'https://webcache.googleusercontent.com/search?q=cache:' + request.url
#             request = request.replace(url=new_url)
#             return request