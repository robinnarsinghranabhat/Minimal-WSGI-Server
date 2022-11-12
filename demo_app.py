from _server import make_server

def app(env, start_response):
    """
    A basic WSGI application. 
    Any Web-Framework we build should return a callable object as per WSGI 
    standards. So that our web-framework can run on any Server that follows 
    WSGI Standard.
    """

    http_status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    response_text = b"Hello World"

    start_response(http_status, response_headers)
    return [response_text]

if __name__ == "__main__":
    wsgi_server = make_server('', 8000, app)
    wsgi_server.serve_forever()