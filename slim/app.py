import logging
from werkzeug.serving import run_simple
from werkzeug.wrappers import BaseRequest, BaseResponse


class Slim(object):
    ALLOWED_METHODS = ["get", "post", "delete", "put", "head", "connect", "option", "trace", "patch"]
    LOG = logging.getLogger("slim.app")
    LOG.setLevel(logging.DEBUG)

    def __init__(self):
        self.url_map = {}

    def add_to_url_map(self, url, func, methods=None):
        """
        add url to url_map
        :param str url:
        :param func:
        :param methods:
        :return:
        """
        self._check_url(url)

        if methods is None:
            methods = ["get"]
        tmp_url_map = {}
        for m in methods:
            assert m in self.ALLOWED_METHODS, "Method [{}] not allowed".format(m)
            tmp_url_map[m] = func

            self.LOG.info("Mounted [{m}] {url}".format(m=m, url=url))
        if url in self.url_map:
            self.url_map[url].update(tmp_url_map)
        else:
            self.url_map[url] = tmp_url_map

    def _check_url(self, url):
        assert isinstance(url, str), "Url should be string"
        assert url.startswith("/"), "Url should start with a slash"

    def route(self, url, methods=None):
        def decorator(f):
            self.add_to_url_map(url, f, methods=methods)
            return f

        return decorator

    def get(self, url):
        def decorator(f):
            self.add_to_url_map(url, f, methods=["get"])
            return f

        return decorator

    def post(self, url):
        def decorator(f):
            self.add_to_url_map(url, f, methods=["post"])
            return f

        return decorator

    def run(self, host="127.0.0.1", port=1112):
        try:
            run_simple(host, port, self)
        except:
            pass

    def __call__(self, environ, start_response):
        req = BaseRequest(environ)
        url = req.path
        method = req.method.lower()
        url_dict = self.url_map.get(url)

        if url_dict:
            allowed_methods = [m for m in self.url_map.get(url, {})]
            if method not in allowed_methods:
                response = BaseResponse('<h1>405 Method Not Allowed<h1>', content_type='text/html; charset=UTF-8',
                                        status=405)
            else:
                args = req.args.to_dict()
                view = url_dict.get(method)
                response = view(**args)
                response = BaseResponse(response)
        else:
            response = BaseResponse('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8',
                                    status=404)
        return response(environ, start_response)
