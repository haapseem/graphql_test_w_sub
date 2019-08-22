
from graphene import ObjectType, String, Schema
from rx import Observable
import time
import logging
import math
import datetime

logging.getLogger().setLevel(logging.DEBUG)


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
        return Observable.interval(1).map(lambda x: str(datetime.datetime.now()))

    def resolve_goodbye(root, info):
        return 'See ya!'

schema = Schema(query=Query, subscription=Subscription)

# r = schema.execute('subscription { hello }', allow_subscriptions=True)
# print(type(r), type(schema.execute('query { hello }', allow_subscriptions=True)))
#
# r.subscribe(lambda x: print(x.data))
#
# time.sleep(5)

# flask_sqlalchemy/app.py



from flask import Flask, request, render_template
import socketio
import json
from flask_cors import CORS
from graphql.execution.base import ExecutionResult
import eventlet

eventlet.monkey_patch()

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
