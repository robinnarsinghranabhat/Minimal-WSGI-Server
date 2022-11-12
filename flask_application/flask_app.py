from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World! I am a flask app'

# @app.route('/')
@app.route('/index')
def index():
    name = 'Andre'
    return render_template('base.html', title='Welcome', username=name)


"""
EXTRA NOTE on Imports
Following statement shows all the paths where python will search for any module (conside folders having __init_.py) we try to import
    `import sys; sys.path`.

When we run a python script, it adds the parent directory of that script to system path. That in turn makes
it possible to use all the folder having `__init__.py` file in that directory like regular python modules. 
That's why, while running `python demo_app.py`, we could simply use the `_server` module.

Now we are Executing `python flask_app.py` from inside `minimal_wsgi/flask_application`. `minimal_wsgi` folder is not 
added to system path and python won't find the `_server` module. 
Thus we have to manually add the parent folder `minimal_wsgi` to system path.
"""
import sys
sys.path.append('../')
from _server import make_server

if __name__ == "__main__":
    wsgi_server = make_server('', 8000, app)
    wsgi_server.serve_forever()
