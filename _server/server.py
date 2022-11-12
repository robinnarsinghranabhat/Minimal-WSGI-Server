# This is our TCPServer 
from .tcp_server import TCPServer 
# This is instantiated by TCPServer for each request it gets 
from .minimal_req_handler import WSGIRequestHandler 
import socket

class HTTPServer(TCPServer):

    allow_reuse_address = 1    # Seems to make sense in testing environment

    def server_bind(self):
        """Override server_bind to store the server name."""
        TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

class WSGIServer(HTTPServer):

    """BaseHTTPServer that implements the Python WSGI protocol"""
    application = None

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''

    def get_app(self):
        return self.application

    def set_app(self,application):
        self.application = application

def make_server(
    host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler
):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    ## This internally uses a TCPServer
    ## one socket object is created during initialization. It's only job is to accept new connection.
    server = server_class((host, port), handler_class)
    server.set_app(app)
    return server
