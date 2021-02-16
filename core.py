class Application:

    def input_data_parse(self, data: str):
        result = {}
        if data:
            params = data.split('&')
            for item in params:
                k, v = item.split('=')
                result[k] = v
        return result

    def wsgi_input_data_get(self, environ):
        content_len_data = environ.get('content_len')
        content_len = int(content_len_data) if content_len_data else 0
        data = environ['wsgi.input'].read(content_len) if content_len > 0 else b''
        return data

    def wsgi_input_data_parse(self, data: bytes):
        result = {}
        if data:
            data_str = data.decode(encoding='utf-8')
            result = self.input_data_parse(data_str)
        return result
    
    def new_route(self, url):
        def inner(view):
            self.routes[url] = view
        return inner

    def __init__(self, routes: dict, front: list):
        """
        :param routes: словарь связок url: view
        :param front: список front controllers
        """
        self.routes = routes
        self.front = front

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if not path.endswith('/'):
            path = f'{path}/'

        method = environ['REQUEST_METHOD']
        data = self.wsgi_input_data_get(environ)
        data = self.wsgi_input_data_parse(data)

        query_string = environ['QUERY_STRING']
        request_params = self.input_data_parse(query_string)

        if path in self.routes:
            view = self.routes[path]
            request = {}
            request['method'] = method
            request['data'] = data
            request['request_params'] = request_params

            for controller in self.front:
                controller(request)

            code, text = view(request)
            start_response(code, [('Content-Type', 'text/html')])
            return [text.encode('utf-8')]
        else:
            start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
            return [b"Not Found"]


class DebugApplication(Application):

    def __init__(self, routes, front):
        self.application = Application(routes, front)
        super().__init__(routes, front)

    def __call__(self, environ, start_response):
        print('DEBUG MODE')
        print(environ)
        return self.application(environ, start_response)
    
    
class MockApplication(Application):

    def __init__(self, routes, front):
        self.application = Application(routes, front)
        super().__init__(routes, front)

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Mock']