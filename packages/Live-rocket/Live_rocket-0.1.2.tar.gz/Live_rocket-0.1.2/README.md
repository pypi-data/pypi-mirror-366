\# Live\_rocket 🚀



A lightweight, custom HTTP server framework written in Python.  

Designed to help you build simple web servers or REST APIs without external dependencies.



---



\## 🔧 Features



\- Minimal and dependency-free HTTP server

\- Supports routing, request parsing, response handling, Build in OMR

\- Multithreaded request handling

\- Educational and customizable



---



\## 📦 Installation



You can install `Live\_rocket` using pip (after uploading to PyPI):



```bash

pip install live-rocket


example:
from live_rocket import live_rocket
from ObjectModel import Model

class MainModel(Model):
    print()

def callable_(req):
    print("Hello")
app=live_rocket(middlewares=[])

@app.get('/',middlewares=[callable_])
def hello(req,res):
    res.render("index.html")
@app.get('/edit/<name>')
def redirect(req,res,name):
    print(name)
    res.redirect(hello)   
@app.get('/upload/<file>') 
def hell(req,res,file):
    print(file)
    res.send({file})
    
if __name__ == "__main__":

    server = app.run('localhost', 8000, app)