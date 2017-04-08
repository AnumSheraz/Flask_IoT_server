# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 10:16:19 2016

@author: Anum
"""
#from gevent import monkey
#monkey.patch_all()

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import threading, time

from FTP_n_IP_handler import FTP_IP_handler_class
from chk_connection import is_connected
from feed_history import time_line_history, update_timeline

from jinja2 import Template


old_feeds = time_line_history
update_timeline_history = update_timeline

interrupt_thread = None
users = 0
connected=False

app = Flask(__name__)
app.secret_key = 'some_key'

socketio = SocketIO(app)
count = 0

def new_feed(content, act):
   feed_time=time.ctime()[4:19]
   t = Template(''' 
                <div class="cd-timeline-block">
                	<div class="cd-timeline-img cd-{{act}} bounce-in">
                	   <img src="static/img/cd-icon-{{act}}.svg">
                	</div> 
                
                	<div class="cd-timeline-content bounce-in">
                		<p>{{content}}</p>
                		<span class="cd-date">{{time}}</span>
                	</div> 
                </div>    
              ''')
              
   feed = t.render(content=content, act=act, time=feed_time)
   #print feed
   socketio.emit("interrupt", {"new_feed":feed})
   update_timeline_history(content, act, feed_time)
   print 'send'              
   return feed
   


def manual_test():
    while 1:
        global count
        send = raw_input("enter:")
        count += 1
        new_feed(send, 'movie')

@app.route('/', methods=['POST','GET'])
def login():
    error = None
    global interrupt_thread
    if interrupt_thread == None:
       interrupt_thread = threading.Thread(target=manual_test)
       interrupt_thread.start()
    if request.method == 'POST':        
       if request.form['user'] != 'anum' or  request.form['password'] != "poi":
          print "GOT ERROR"  
          error = 'Please try again' 
       else:  
          print 'logged SUCCESS'
          
          return redirect(url_for('main'))
          
    return render_template('login.html', error=error)
        
@app.route('/index')
def main():
    flash('logged in as Anum Sheraz')
    return render_template('index.html')        

@app.route("/timeline") 
def timeline():
    global old_feeds
    flash('logged in as Anum Sheraz') 
    return render_template('timeline.html', feed_history=old_feeds())

@app.route("/Control")
def Control():
    return render_template('control.html')
    
@app.route('/<data>', methods=['POST', 'GET'])
def button_info(data):
    #print data
    return '\'' + data + '\' Acknoliged '
    
@app.route("/manual_feed", methods=['POST'])
def btnas():
    print request.form["manual_feed"]
    new_feed(request.form["manual_feed"], 'user')
    #socketio.emit("interrupt", {"new_feed":feed})
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
    new_feed(message['data'], 'user')

@socketio.on('button')
def btn(message):
    socketio.emit("my event", {'data': message['data']})
    
@socketio.on('connect')
def conn():
    global users, feed_content, send_feed
    users += 1
    socketio.emit('Users', {'count':users})
    #new_feed("User entered", 'user')

    
@socketio.on('disconnect')
def disconn():
    global users, feed_content, send_feed
    users -=1
    socketio.emit('Users', {'count':users})
    #new_feed("User exited", 'user')   
    
class IP_update(threading.Thread):
    """
    
    """
    def __init__(self):
        threading.Thread.__init__(self)
    

    def run(self):
        global IP_Update_time
        ip="" 
        last_ip=""
        while 1:
            if  connected is True :
             print "Conn True"   
             my_ip=FTP_IP_handler_class.get_ip()
             print 'got it'
             #print My_ip
             if last_ip!=my_ip:     
               if connected is True :   
                 FTP_IP_handler_class.update_FTP(my_ip) 
                 last_ip=my_ip
                 #time.sleep(IP_Update_time*60)
             else:
               print '> ip is same' 
               time.sleep(60)
            else:
               print 'no internet; chk your connection'
               time.sleep(5)
               
                      
            
class chk_connection(threading.Thread):
    """
    start transmission on UDP socket for control channel 2 
    """
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global connected
        while 1:
            connected=is_connected()
            #print 'internet:', connected
            time.sleep(1)    

if __name__ == '__main__':
    tx_socket_thread2 = IP_update()
    tx_socket_thread2.start()
    tx_socket_thread3 = chk_connection()
    tx_socket_thread3.start()    
    socketio.run(app, host='192.168.0.16', port=80)
    #app.run()