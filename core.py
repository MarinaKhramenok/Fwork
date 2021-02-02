class Application:

    def __init__(self, routes: dict, front: list):
        """
        :param routes: словарь связок url: view
        :param front: список front controllers
        """
        self.routes = routes
        self.front = front

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        if path in self.routes:
            view = self.routes[path]
            request = {}
            for controller in self.front:
                controller(request)

            code, text = view(request)
            start_response(code, [('Content-Type', 'text/html')])

            return [text.encode('utf-8')]
        else:
            start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
            return [b"Not Found"]
