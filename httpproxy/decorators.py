from httpproxy import settings
from httpproxy.recorder import ProxyRecorder


proxy = ProxyRecorder(settings.PROXY_DOMAIN, settings.PROXY_PORT)

def normalize_request(fn):
    """
    Updates all path-related info in the original request object with the url
    given to the proxy.
    
    This way, any further processing of the proxy'd request can just ignore
    the url given to the proxy and use request.path safely instead.
    """
    def decorate(request, url, *args, **kwargs):
        if not url.startswith('/'):
            url = u'/' + url
        request.path = url
        request.path_info = url
        request.META['PATH_INFO'] = url
        return fn(request, *args, **kwargs)
    return decorate

def record(fn):
    """
    Decorator for recording the request being made and its response.
    """
    def decorate(request, *args, **kwargs):
        
        # Make the actual live request as usual
        response = fn(request, *args, **kwargs)
        
        # Record the request and response
        proxy.record(request, response)

        return response
    return decorate

def play(fn):
    """
    Decorator for playing back the response to a request, based on a
    previously recorded request/response.
    """
    def decorate(request, *args, **kwargs):
        return proxy.playback(request)
    return decorate

