# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 10:16:19 2016

@author: Anum
"""
# from gevent import monkey
# monkey.patch_all()

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
import threading, time

from feed_history import time_line_history, update_timeline

from functools import wraps
from jinja2 import Template

old_feeds = time_line_history
update_timeline_history = update_timeline

interrupt_thread = None
users = 0
connected = False

app = Flask(__name__)
app.secret_key = 'some_key'

socketio = SocketIO(app)
count = 0


def new_feed(act, title, content):
    feed_time = time.ctime()[4:19]
    t = Template('''
                <div class="cd-timeline-block">
                	<div class="cd-timeline-img cd-{{act}} bounce-in">
                	   <img src="static/img/cd-icon-{{act}}.svg">
                	</div> 
                
                	<div class="cd-timeline-content bounce-in">
                	   <h2>{{title}}</h2>
                		<p>{{content}}</p>
                		<span class="cd-date">{{time}}</span>
                	</div> 
                </div>    
              ''')

    feed = t.render(content=content, title=title, act=act, time=feed_time)
    # print feed
    socketio.emit("interrupt", {"new_feed": feed})
    update_timeline_history(title, content, act, feed_time)
    print 'send'
    return feed


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print 'wrapper function ran with args {}'.format(f.__name__)
        if "logged_in" in session:
           print 'logged in true' 
           return f(*args, **kwargs)
        else:
           flash("pleae login first !") 
           return redirect(url_for('login'))  
    return wrapper    

@app.route('/', methods=['POST', 'GET'])
def login():
    error = None
    session['user'] = None
    global interrupt_thread
    if interrupt_thread == None:
       interrupt_thread = threading.Thread(target=manual_test)
       interrupt_thread.start()
    #print "got /"    
    if request.method == 'POST':
        if request.form['password'] != "poi": #or request.form['user'] != 'anum' or :
            print "GOT ERROR"
            error = 'Please try again'
        else:
            session['logged_in'] = True            
            session['user'] = request.form['user']
            new_feed("user", session['user'], "Logged in")
            print 'logged SUCCESS', session['user']
            return redirect(url_for('main'))

    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    new_feed('user', session['user'], "Logged out")
    session.pop('logged_in', None)
    session['user'] = None
    flash("you just logged out")
    return redirect(url_for('login'))
    


@app.route('/main')
@login_required
def main():
    flash('logged in as ' + session['user'])
    return render_template('index.html')


@app.route("/timeline")
@login_required
def timeline():
    global old_feeds
    flash('logged in as Anum Sheraz')
    return render_template('timeline.html', feed_history=old_feeds())


@app.route("/Control")
@login_required
def Control():
    return render_template('control.html')


@app.route('/<data>', methods=['POST', 'GET'])
def button_info(data):
    # print data
    return '\'' + data + '\' Acknoliged '


@app.route("/manual_feed", methods=['POST'])
def btnas():
    print request.form["manual_feed"]
    new_feed(request.form["manual_feed"], 'user')
    # socketio.emit("interrupt", {"new_feed":feed})
    return True


@app.errorhandler(404)
def error404(e):
    return '404 error oOps!', e


@app.errorhandler(500)
def error500(e):
    try:
        return '500 error oOps!'
    except Exception as e:
        return "WoOps" + e


@socketio.on('client_interrupt')
def form_data(message):
    print message['data']
    new_feed('user', session['user'], message['data'])


@socketio.on('button')
def btn(message):
    socketio.emit("my event", {'data': message['data']})


@socketio.on('connect')
def conn():
    global users, feed_content, send_feed
    users += 1
    socketio.emit('Users', {'count': users})
    # new_feed("User entered", 'user')


@socketio.on('disconnect')
def disconn():
    global users, feed_content, send_feed
    users -= 1
    socketio.emit('Users', {'count': users})
    # new_feed("User exited", 'user')



if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=80)#, debug=True)
    # app.run()
