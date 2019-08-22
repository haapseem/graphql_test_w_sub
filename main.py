# hashtag important
import eventlet
eventlet.monkey_patch()

from graphene import ObjectType, String, Schema
from rx import Observable
import time
import logging
import math
import datetime

from flask import Flask, request, render_template
import socketio
import json
from flask_cors import CORS
from graphql.execution.base import ExecutionResult

logging.getLogger().setLevel(logging.DEBUG)
#
# schema
#

class Query(ObjectType):
    hello = String(name=String(default_value="stranger"))
    goodbye = String()

    def resolve_hello(root, info, name):
        return 'hello'

    def resolve_goodbye(root, info):
        return 'See ya!'

class Subscription(ObjectType):
    hello = String()
    goodbye = String()

    def resolve_hello(root, info):
        return Observable.interval(1000).map(lambda x: str(datetime.datetime.now()))

    def resolve_goodbye(root, info):
        return 'See ya!'

schema = Schema(query=Query, subscription=Subscription)

#
# server
#

sio = socketio.Server(logger=True)
app = Flask(__name__)
app.debug = True

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/graphql")
def graphql_query():
    q = request.args.get('query')
    q = schema.execute(q, allow_subscriptions=True)
    if type(q) == ExecutionResult:
        q=json.dumps(q.data)
        return q
    else:
        q.subscribe(lambda x: sio.emit('sub',x.data))
    return "a"


CORS(app)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

if __name__ == '__main__':
    app.run()
