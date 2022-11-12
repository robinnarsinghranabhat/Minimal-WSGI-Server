## Minimal Example of WSGI server and application interaction

I merely used this gist. And instead of importing the classes like `PollSelector`, `TCPServer`, `WSGIServer`, I
copied them from the standard library into local files. 
- https://gist.github.com/nottrobin/8c12c9921aeb885dbe07 by https://github.com/nottrobin

### What ?
This is an example to emulate interaction between a web-framework and an web-server according to WSGI Standards (https://peps.python.org/pep-3333/).
When we try to build a web-application, we only work with an application object.

### Structure
server module hold


### How it works : 
- The Code Structure  
    - Web-Application
    - Web-Server

- WSGIServer (built on top of TCPServer) accepts new request one at a time. It does so in a non-blocking fashion.
  To make it non-blocking, we use `select` sys calls through `Selectors` module, which is just a nice OOP wrapper around 
  more raw `select` module. 

- WSGIServer has TCPServer as it's base class. Each new request (i.e the socket file descriptor between client and server) created 
  after connection is established is passed to the `process_request` method, along with a `RequestHandlerClass`. Not object ! 
  
  `process_request` is then instantiates the `RequestHandlerClass` with socket file descriptor. And during this instantiation,
  the Handler also invokes a `handle` method that will read the content from the file descriptor, parse that content and write to it.

- Remember that all we pass to the `RequestHandler` is the socket file descriptor. How it deals with it is totally based on usecase. 
  For our usecase, we use handler meant for parsing HTTP Requests. That means our handler assumes that contents read from the socket (i.e request sent by client)
  will be something this : 
  
  ```
  GET / HTTP/1.1
  Host: www.example.com
  User-Agent: Mozilla/5.0
  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
  Accept-Language: en-GB,en;q=0.5
  Accept-Encoding: gzip, deflate, br
  Connection: keep-alive
  ```

- INSIDE `RequestHandler.handle()`
    Some namings : 
    - `self.server` is TCP server object
    - `self.server.application` is our application callable.
    - `self.connection` is our file descriptor
    - `self.rfile`, `self.wfile` is our interface to this descriptor

    






    
