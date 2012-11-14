#!/usr/bin/env python
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Response, json
from contextlib import closing

# postgres setup
import psycopg2
import os
import urlparse

urlparse.uses_netloc.append('postgres')
DATABASE_URL = "put here your Heroku postgres connection string"

try:
    # if we are in production on Heroku
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
except KeyError:
    # we need to construct the connection string ourselves, still connecting to
    # the hosted postgresql , but from our local development machine.
    url = urlparse.urlparse(DATABASE_URL)

try:
    PORT = int(os.environ['PORT']) # production
except KeyError:
    PORT = 5000 # local dev

# config
SECRET_KEY = "put here your secret key" # http://flask.pocoo.org/docs/quickstart/#sessions 
USERNAME = 'admin'
PASSWORD = 'default'
API_VERSION = 0.1

# create app
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    conn = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))
    return conn

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().execute(f.readline())
            db.commit()

@app.errorhandler(404)
def not_found(error=None):
    message = {
                'status': 404,
                'message': 'Not Found: ' + request.url,
                }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def api_welcome():
    return "Welcome @ Peeper API v%s" % app.config['API_VERSION']

@app.route('/get_global_feed', methods=['GET'])
def global_feed():
    # by default fetch just the latest
    # 20 entries to not hog our servers.
    max_returned = request.args.get('max_returned', 20)
    cur = g.db.cursor()
    cur.execute('select users.username, peeps.message_text, peeps.t from peeps INNER JOIN users ON peeps.userid = users.id  order by peeps.t desc')
    dated_result = [dict(user=user, msg=msg, tstamp=str(tstamp)) for user, msg, tstamp in cur.fetchmany(max_returned)]
    return Response(json.dumps(dated_result), status=200, mimetype='application/json')

@app.route('/get_feed/<userid>', methods = ['GET'])
def get_feed(userid):
    max_returned = request.args.get('max_returned', 20)
    cur = g.db.cursor()
    cur.execute("""SELECT N.username, N.message_text, N.t FROM 
    (SELECT users.username, peeps.message_text, peeps.t, peeps.userid FROM peeps  INNER JOIN users ON peeps.userid = users.id) AS N
                INNER JOIN follow on N.userid = follow.followed WHERE
                    follow.follower = %s""", (userid, ))
    dated_result = [dict(user=user, msg=msg, tstamp=str(tstamp)) for user, msg, tstamp in cur.fetchmany(max_returned)]
    return Response(json.dumps(dated_result), status=200, mimetype='application/json')

@app.route('/post_message/<userid>', methods = ['POST'])
def post_message(userid):
    cur = g.db.cursor()
    try:
        cur.execute("insert into peeps (userid, message_text) values (%s, %s);",(userid, request.args['message_text']))
        g.db.commit()
    except Exception as e:
        return Response(e.message, status=500)
    return Response('saved', status=200)

@app.route('/create_user/<username>', methods = ['GET'])
def create_user(username):
    print username
    uid = 0
    cur = g.db.cursor()
    try:
        cur.execute("insert into users(username) VALUES (%s) returning id;", (username,))
        g.db.commit()
        uid = cur.fetchone()[0]
    except Exception as e:
        return Response(e.message, status=500)
    return Response(json.dumps(dict(uid=uid)), status=200, mimetype='application/json')
        
def resolve_uid(username):
    cur = g.db.cursor()
    cur.execute('SELECT id from users where username = %s', (username, ))
    t = cur.fetchone()
    return t[0]

def enable_follow(follower, followed, disable=False):
    sql = 'INSERT INTO follow(follower, followed)  VALUES(%s, %s);'
    if disable:
        sql = 'DELETE FROM follow where follower = %s AND followed = %s;'
    cur = g.db.cursor()
    follower_uid = resolve_uid(follower)
    followed_uid = resolve_uid(followed)
    cur.execute(sql, (follower_uid, followed_uid))
    g.db.commit()
    return (follower_uid, followed_uid)
        

@app.route('/follow/<following_user>', methods=['GET'])
def follow(following_user):
    try:
        f1, f2 = enable_follow(following_user, request.args['followed_user'])
    except Exception as e:
        return Response(e.message, status=500)
    return Response(json.dumps(dict(follower=f1, followed=f2)), status=200)

@app.route('/unfollow/<following_user>', methods=['GET'])
def unfollow(following_user):
    try:
        f1, f2 = enable_follow(following_user, request.args['followed_user'], disable=True)
    except Exception as e:
        return Response(e.message, status=500)
    return Response(json.dumps(dict(follower=f1, stopped_following=f2)), status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
