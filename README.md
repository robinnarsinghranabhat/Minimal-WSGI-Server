## Minimal Example of WSGI server and application interaction

### **ABOUT**
This is my notes on how interaction happen between a web-framework and a web-server built according to WSGI Standards [WSGI Standards](https://peps.python.org/pep-3333/).
When we build a web-application, we only build this `application` callable.

REFERENCE
> (I merely used [this gist](https://gist.github.com/nottrobin/8c12c9921aeb885dbe07). And instead of importing standard library provided the classes like `PollSelector`, `TCPServer`, `WSGIServer`, just copied necessary part of those.)


### **Project Structure**
  `_server` module is an basic implementation of a `WSGI server`. 
  Similarly `demo_app.py` implements a simple application callable following WSGI standards. 
  This is the same kind of callable that we build while working with web-frameworks 
  like flask, django e.t.c. It's job is to simply return the HTML page (as byte-string ) for browser to render.  
  
  All production WSGI web-servers like `guicorn`, `eventlet` e.t.c simply takes in the WSGI app callable, uses it to get the raw html-page as string. It then add that html-response string along with other information like response-headers to create a complete response (byte-string). Which it sends back to the client (say your browser). Taking a look at the code for these servers, 60 percentage of code is mostly error-handling when things don't go well (Incoming Request not according to HTTP Protocol).

### **Running the Application**
To run our simple application : `python demo_app.py`

Since our server follows WSGI Standard, we can use it to run a flask application as well. Navigate to `flask_application` folder and run `python flask_app.py`


### **How things work** 

WSGIServer (built on top of TCPServer) accepts new request one at a time. It does so in a non-blocking fashion.
To make it non-blocking, we use `select` sys calls through `Selectors` module, which is just a nice OOP wrapper around 
more raw `select` module. 

WSGIServer has `TCPServer` as it's base class. Each new request (i.e the socket file descriptor between client and server) that's created after connection is established is passed to the `process_request` method, along with a `RequestHandlerClass`. Not object ! 
  
`process_request` then instantiates the `RequestHandlerClass` with socket file descriptor. We call `process_request` for each new connection. It's during this instantiation, the Handler also invokes a `handle` method that will read the client request from the file descriptor, parse that content and send back results to client.

> **MAKING THINGS CONCURRENT**:
In this design, we could easily handle multiple clients by override the `process_request` so that `handle` for each new connection is called in a new thread or a process. Check `socketserver.ThreadingMixin`. 
 **How things work our for single-threaded, single-process design with asyncio is something I haven't looked at yet**  

Remember that all we pass to the `RequestHandlerClass` is the socket file descriptor. How it deals with the contents is totally based on usecase. 
For our usecase, we assume we our client is sending requests according to HTTP Protocol. Our handler assumes that contents read from the socket (i.e request sent by client)
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

**INSIDE `RequestHandler.handle()`**
- Some namings first : 
  - `self.server` is TCP server object
  - `self.server.application` is our application callable.
  - `self.connection` is our file descriptor
    - `self.rfile` or `self.stdin`, `self.wfile` or `self.stdout` is our interface to this descriptor. Generally, reading from socket is buffered. While writing is u

- **THE MEAT** :
    ```
    handler = ServerHandler(
        self.rfile, self.wfile, self.get_stderr(), self.get_environ(),
        multithread=False,
    )
    handler.request_handler = self      # backpointer for logging
    # All SHIT HAPPENS HERE
    handler.run(self.server.get_app())
    ``` 

    - Inside `handler.run` || Actually `wsgiref.handlers.BaseHandler.run`
      ```
      self.setup_environ()

      self.result = application(self.environ, self.start_response) #
      # self.result holds the actual html byte string that browser will render. 
      # also, inside application, `BaseHandler.start_response` is called. It prepares the response-headers. 
      # But doesn't send anything yet.

      self.finish_response()
      # First write contents of headers to our `FREAKING SOCKET FILE OBJECT` using `ServerHandler._write`
      # As in the code, we write one byte at a time. 
      # And write contents of `self.result` to the socket.
      # By the way, self.stdout is a 
      ```

    






    
