from werkzeug.serving import run_simple
from werkzeug.wrappers import BaseRequest, BaseResponse

from slim.error import Error
from slim.log import add_url_log

ALLOWED_METHODS = ["get", "post", "delete", "head", "put", "options"]


class Slim(object):
    def __init__(self):
        self.URL_MAP = {}

    def __call__(self, environ, start_response):
        req = BaseRequest(environ)
        url = req.path
        method = req.method.lower()
        url_dict = self.URL_MAP.get(url)

        if url_dict:
            allowed_methods = [m for m in self.URL_MAP.get(url, {}).get("methods", {})]
            if method not in allowed_methods:
                response = BaseResponse('<h1>405 Method Not Allowed<h1>', content_type='text/html; charset=UTF-8',
                                        status=405)
            else:
                args = req.args.to_dict()
                view = url_dict.get("methods", {}).get(method, {}).get("function")
                response = view(**args)
                response = BaseResponse(response)
        else:
            response = BaseResponse('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8',
                                    status=404)
        return response(environ, start_response)

    def run(self, host="localhost", port=1112):
        run_simple(host, port, self)

    def route(self, url, methods=None):
        def decorator(f):
            self.add_url_map(url, f, methods=methods)

        return decorator

    def add_url_map(self, url, f, methods=None):
        url = format_url(url)
        if methods is None:
            if self.URL_MAP.get(url):
                self.URL_MAP[url]["methods"]["get"] = {"function": f}
                add_url_log(url, "get")
            else:
                self.URL_MAP[url] = {"methods": {"get": {"function": f}}}
                add_url_log(url, "get")
        elif isinstance(methods, list):
            if not methods:
                raise Error("Argument method should not be an empty list")
            for m in methods:
                if m not in ALLOWED_METHODS:
                    raise Error("Method {method} is not allowed".format(method=m))
                if self.URL_MAP.get(url):
                    self.URL_MAP[url]["methods"][m] = {"function": f}
                    add_url_log(url, m)
                else:
                    self.URL_MAP[url] = {"methods": {m: {"function": f}}}
                    add_url_log(url, m)
        else:
            raise Error("Argument methods should be a list")


class SlimModule(Slim):
    def __init__(self, slim_class, module_url):
        super(SlimModule, self).__init__()
        if isinstance(slim_class, Slim):
            self.slim_class = slim_class
        else:
            raise Error("Slim_class should be a Slim class")

        if isinstance(module_url, str):
            self.module_url = format_url(module_url)
        else:
            raise Error("Module_route should be a string")

    def module_route(self, url, methods=None):
        def decorator(f):
            self.add_module_url(url, f, methods=methods)

        return decorator

    def add_module_url(self, url, f, methods=None):
        final_url = self.module_url + url
        if isinstance(self.slim_class, SlimModule):
            self.slim_class.add_module_url(final_url, f, methods=methods)
        else:
            self.slim_class.add_url_map(final_url, f, methods=methods)


def format_url(ori_url):
    if not isinstance(ori_url, str):
        raise Error("url should be a string")
    if ori_url.startswith("/"):
        ori_url = ori_url[1:]
    if ori_url.startswith("/"):
        raise Error("url should not start with / or start with at most one /")
    url = "/" + ori_url
    return url
