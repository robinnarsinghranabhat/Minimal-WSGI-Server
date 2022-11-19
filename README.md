## Minimal Example of WSGI server and application interaction

### **ABOUT**
Simple Example of of how interaction happen between a web-framework and a web-server built according to WSGI Standards [WSGI Standards](https://peps.python.org/pep-3333/). 
When we build a web-application, we only build this `application` callable.

REFERENCE
> (I merely used [this gist](https://gist.github.com/nottrobin/8c12c9921aeb885dbe07). And instead of importing standard library provided the classes like `PollSelector`, `TCPServer`, `WSGIServer`, just copied necessary part of those.)


### **Project Structure**
  `_server` module is an basic implementation of a `WSGI server`. 
  **It's job is to process client request, generate response and send back to client.**
  
  In `demo_app.py`, we implement a simple `callable object` following WSGI standards. This callable is called `web-application`.
  **Web App holds the business logic. i.e. Take in `Request` from the WSGI-Server, process it and return back `Response` to the Server.**.

  This is the same kind of callable that we build while working with web-frameworks 
  like flask, django e.t.c. `Respone` returned by application callable is simply the HTML page (as byte-string ) for browser to render.
    
  All production WSGI web-servers like `guicorn`, `eventlet` e.t.c simply uses the WSGI app callable to get html-page as byte-string. 
  Server then adds Header information to create a complete response (list of byte-string). It sends back to the client (say your browser). Taking a look at the code for these servers, 60 percentage of code is mostly error-handling when things don't go well (Incoming Request not according to HTTP Protocol).

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
By design, we could handle multiple clients by overriding the `process_request` method of server so that each new connection is handled in a new thread or a process. Check `socketserver.ThreadingMixin`. 
 **How things work our for single-threaded, single-process design with asyncio is infact one of WSGI limitation. That's one of main reason why ASGI was proposed.**  

### **Extras : Implementation Details of Handling the `Request`.**
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
    - `self.rfile` or `self.stdin`, `self.wfile` or `self.stdout` is our interface to this descriptor. Generally, reading from socket is buffered. While writing is unbuffered (If confused, This is Explained at last section)

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

### **Extras : WSGI Server Quick implementation notes**
  - `start_response` : It is implemented by the web-server. It's called from inside the application callable. It will collect the request headers and create response header in `self.headers` attribute for `SeverHandler`. It return's a `self.write` file descriptor. But that's just for backward compatibility and should be ignored.

### **Extras : Understanding blocking, read and writes in socket-programming.**

Let's start with what socket is. When a client-server connection is establised, each side gets a `socket` object. For each side socket object, two array is allocated. 
First array is "Read/Send Buffer" and second one is "Write/Receive Buffer".
Imagine socket object created out of Class/Structure like this in C. 
```
typedef struct {
  char[1024] read_buff;
  char[1024] write_buff;
  ...
} Socket;
Socket socket_object;
```

For client side to send data, client side socket does  `socket.write("SOME CLIENT REQUEST")`. Now this value is written to client-socket's "Write Buffer" Array. Afterwards, it's job of underlying OS/HARDWARE/INTERNET/WHATEVERSHIT  is to somehow send this to server-side and fill the "Read Buffer" array on server-side socket. 

On the server side code, when server does `socket.read(...)`, it's asking for data from it's "Read Buffer". By default, if client data hasn't reached yet or client hasn't sent yet, code on server side just freezes at `read` operation waiting for data. This is called `Blocking`. By Default, CPU remains idle. 

Similarly, when server does,  `socket.send( "SOME HTML RESPONSE" )`, you are writing this data to "Write Buffer" array of server-socket. 

#### WHY DO WE NEED A BUFFER ?
Once we write to these local-buffer,  The TCP layer will collect this data from local buffer, bundle up them into packet of certain size and send it. It's **far efficient to create `packets` for allocated say 1024 bytes of data and send it over than create a packet for each incoming byte and send it 1024 times**.
Also explained (here)[http://www.unixguide.net/network/socketfaq/2.11.shtml].

#### So What does an `unbuffered write` from server side mean ?
After server has created a complete response, we will call this internally : `socket.sendall(SHITLOAD_OF_HTML_RESPONSE)` to do an `unbuffered write`. 
This will call the `socket.send` in a loop until all the data is sent to client. Meaning, say local write-buffer size is 1000. But your html data is 
10000 byte. Now server's write-array will be packed with after first `socket.send` call in loop. So, will wait (loop jams there, cpu is idle) until some or all of that data to consumed by Operating system (into it's own Kernel Buffer) before next write. OS will then pack and send to client socket's "Read-Buffer" which we frankly don't care.  


    
