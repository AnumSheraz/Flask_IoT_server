# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 01:35:22 2015

@author: AnumSheraz

Upload file
"""



from ftplib import FTP
import urllib2

class FTP_IP_handler_class():
  def __init__(self):
      pass
      #print 'class FTP_n_IP_handler called '
    
  def get_ip(self):
    ############################################### gettig the IP
    try:
       response = urllib2.urlopen('http://checkip.dyndns.org/')
    except urllib2.HTTPError, e:
        print 'failed to get page', e 
    else:    
     html = response.read()
     #print html
     index_start = html.index('<body>')
     #print index_start, html[index_start:len(html)]
     index_end=html.index('</body>')
     current_IP=html[index_start+26:index_end]
     print 'Current IP:',current_IP,
     return current_IP

  def update_FTP(self, current_IP_is):
    ############################################### Accessing FTP Server
    #print 'logging in'
    ftp = FTP("67.222.129.78")
    try:
     #print 'logging in'   
     ftp.login("anumsheraz@maxcotec.com", "Anum6630")
     #print 'logged in'
    except KeyboardInterrupt:
        pass
    # open the file to read it as a file like object
    #ftp.cwd("/public_html/")
    #ftp.retrlines('LIST')     # list directory contents
    
    ############################################# uploading the file (initialy)
    #f = open("IP_temp.txt", "r")
    #print 'found IP_temp.txt'
    #
    ## save file like object as to the ftp path 
    #ftp.storlines("STOR IP.txt", f)   #file stored to FTP server
    #print 'file stored'  
    current_IP=current_IP_is
    ################################################ download the file
    ftp.retrbinary('RETR IP.txt', open('IP_temp.txt', 'wb').write)
    with open ("IP_temp.txt", "r") as myfile:
        data=myfile.read()#.replace('\n', '')
        #print data
        index_1=data.index('P2:')
        index_2=data.index('<P2')
        last_ip=data[index_1+3:index_2]
        print 'last IP:',last_ip
        new_data=data.replace(last_ip,current_IP)
        #print 'new data'
        #print new_data 
    if last_ip != current_IP :    
        ############################################### updating the IP_temp.txt text file   
        file1 = open('IP_temp.txt','r+')
        file1.truncate() #
        file1 = open('IP_temp.txt', 'w') 
        file1.writelines(new_data) # Write a sequence of strings to a file
        
        ############################################### uploading the file
        file1 = open ("IP_temp.txt", "r")
        # save file like object as to the ftp path 
        ftp.storlines("STOR IP.txt", file1)  #file stored to FTP server
        print 'IP stored'
        file1.close()
    else:
        print 'IP is Same'    
    ftp.quit()
    print 'done'