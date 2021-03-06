#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#from subprocess import Popen, PIPE, STDOUT
#import os, shutil
from os.path import isdir, exists, join, split
import traceback
#from bz2 import compress, decompress
import time
#from git import *
import sys
from WebServerInterface import *
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from celery.task import task
from celery.exceptions import SoftTimeLimitExceeded
import pexpect
from os import remove
from subprocess import Popen

AWS_ACCESS_KEY = 'AKIAICYAQREP6CMTOZ7Q'

AWS_SECRET_KEY = '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'

password = 'blastfromthepast'

config = open("config.cfg",'r').read().split()
startport = int(config[0])
tentacle = config[1]
webserver=WebServerInterface('megaminerai.com')
rootdir = '/tmp/'+tentacle+'/'

repositories = dict()

working_copies=dict()

def update(program):
  #print "updating",program
  webs = webserver.get_ssh_path(program)
  path = webs['path']
  commit = webs['commit_id']
  repositories[program] = split(path)[1][:-4]
  if commit == None or commit == '':
    #print "bad request, no commit version"
    return "Git setup wrong for"+program
  working_copies[program]=commit
  if not exists(rootdir+repositories[program]):
    p = pexpect.spawn('rm -rf '+rootdir+split(path)[1][:-4])
    i = p.expect([pexpect.EOF])
    p.close(True)
    #print 'cloning'
    command = "git clone ssh://mmweb@r99acm.device.mst.edu:2222" + path
    cwd = rootdir
  else:
    #first git clean
    p = pexpect.spawn("git checkout master", cwd = rootdir+repositories[program])
    i = p.expect([pexpect.EOF])
    p.close(True)
    #print p.before
    p = pexpect.spawn("git clean -f", cwd = rootdir+repositories[program])
    i = p.expect([pexpect.EOF])
    p.close(True)
    #print p.before
    #print 'pulling'
    command = "git pull"
    cwd = rootdir+repositories[program]
  p = pexpect.spawn(command, cwd = cwd, timeout = 180) 
  #print "spawned a process:",command
  i = p.expect(['Password:',pexpect.EOF], timeout = 180)
  if i == 0:
    p.sendline(password)
    i = p.expect([pexpect.EOF, pexpect.TIMEOUT], timeout = 180)
    if i == 1:
      #print "error in git"
      #print p.before
      p.close(True)
      return "Git clone timed out for "+program
  else:
    #print "ERROR, can't clone git directory of",program
    #print p.before
    p.close(True)
    return "Git clone timed out for "+program
  if commit != None:
    p = pexpect.spawn("git checkout "+commit,cwd = rootdir+repositories[program])
    i = p.expect(['''[all] Error''',pexpect.EOF])
    if i == 0:
      #print "failed to get the build",commit
      #print p.before
      p.close(True)
      return "Failed to get commit "+str(commit)+" for "+program
  p.close(True)
  
  p = pexpect.spawn("make", cwd = rootdir+repositories[program])
  #makelog = open(rootdir+"make.log", 'w')
  #p.logfile = makelog
  i = p.expect(['Error',pexpect.EOF], timeout = 60)
  p.close(True)
  #makelog.close()
  if i == 0:
    #print "failed to make"
    #Popen('bzip2 '+rootdir+'make.log', shell = True).wait()
    #s3conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
    #logbucket = s3conn.get_bucket("megaminer7")
    #newkey = Key(logbucket)
    #logname = 'logs/arena/'+str(tentacle)+'-'+str(time.time())+'.make.log.bz2'
    #newkey.key = logname
    #newkey.set_contents_from_filename(rootdir+"make.log.bz2")
    #webserver.set_game_stat(program, "make", 0, 1, working_copies[program], None, logname)
    #print program, working_copies[program], logname
    #remove(rootdir+"make.log.bz2")
    return "Faild to make "+program
  #Popen("rm "+rootdir+"make.log", shell = True).wait()
  p = pexpect.spawn("chmod +x run", cwd = rootdir+repositories[program])
  i = p.expect([pexpect.EOF])
  p.close(True)
  return "good!"

@task
def run_game(client1, client2, name):
  c1_status = update(client1)
  if c1_status != "good!":
    return ("Error", c1_status)
  c2_status = update(client2)
  if c2_status != "good!":
    return ("Error", c2_status)
#  if not update('server'):
#    return -13
  startTime = time.time()
  #now start the server...
  servergood = False
  port = startport
  #slog = open(rootdir+"server.log","w")
  while not servergood:
    serverp = pexpect.spawn('python main.py '+str(port), cwd = rootdir+'server/', timeout = 600)
    i = serverp.expect(['Unable to open socket!','Server Started',pexpect.EOF,pexpect.TIMEOUT], timeout = 10)
    if i == 0 or i == 3 or i == 2:
      #print "bad socket"
      port += 1
      serverp.close(True)
    elif i == 1:
      #print tentacle+" server should be started on port "+str(port)
      servergood = True
    else:
      print 'THE WORLD IS AT AN END'
      return ("Error","fail")
  #serverp.logfile = slog
  time.sleep(2)
  #now client 1..
  client1p = Popen('/bin/bash ./run localhost:'+str(port), cwd = rootdir+repositories[client1], shell=True, stdout = file('/dev/null', 'w'), stderr = file('/dev/null', 'w'))
  #client1p = pexpect.spawn('/bin/bash ./run localhost:'+str(port)+'> /dev/null 2>&1', cwd = rootdir+repositories[client1], timeout = 600)
  #i = client1p.expect(['Creating game 1',pexpect.EOF,pexpect.TIMEOUT], timeout = 10)
  i = serverp.expect(['Creating game 1',pexpect.EOF,pexpect.TIMEOUT], timeout = 10)
  if i == 0:
    pass
    #print tentacle+" game created!"
  else:
    #print client1p.returncode
    #print tentacle+" game failed to create:"+str(i)
    return ("Error","Game failed to create "+client1)
  #and client 2...
  client2p = Popen(['/bin/bash ./run localhost:'+str(port) + ' 0'], cwd = rootdir+repositories[client2], shell=True, stdout = file('/dev/null', 'w'), stderr = file('/dev/null', 'w'))
  #client2p = pexpect.spawn('/bin/bash ./run localhost:'+str(port)+' 0 > /dev/null 2>&1', cwd = rootdir+repositories[client2], timeout = 600)
  #i = client2p.expect([pexpect.EOF,pexpect.TIMEOUT],timeout=5)
  i = serverp.expect(['Starting',pexpect.EOF,pexpect.TIMEOUT], timeout = 5)
  if i != 0:
    #print tentacle+' '+client2+" couldn't connect"
    return ("Error",client2+" couldn't connect to server")
  print tentacle+" game started! (" + client1 + " vs. " + client2 + " on port "+str(port)+")"
  result = ''
  try:
    while time.time() < startTime + 600 and len(result) < 5:
    #result = serverp.expect(["Tie game!", "1 Wins!", "2 Wins", pexpect.TIMEOUT], timeout = 5)
    #try:
    #  client1p.read_nonblocking(1024, timeout = 0)
    #except:
    #  pass
    #try:
    #  client2p.read_nonblocking(1024, timeout = 0)
    #except:
    #  pass
      try:
        result = serverp.readline()
        if "win" not in result.lower() and "tie" not in result.lower():
          result = ''
      except pexpect.TIMEOUT:
        pass
  except SoftTimeLimitExceeded:
    print tentacle+" TIMEOUT!"
    serverp.close(True)
    client1p.kill()
    client2p.kill()
    return ("Error","Timeout!")
  #result = serverp.readlines()
  #print result
  #print tentacle+" game completed!"
  c1_score = 0
  c2_score = 0
  if "1" in result:# == "1 Wins!":
    c1_score = 1
    winner = client1
    #print client1, "wins"
  elif "2" in result or result == '':# == "2 Wins!":
    c2_score = 1
    winner = client2
    #print client2, "wins"
  elif "tie" in result.lower():# == "Tie game!":
    #print "tie"
    winner = client2
    c2_score = 1
  elif result == '':
    pass
    #print "someone crashed!"
  else:
    print "wat?",result
    return ("Error","Unknown results from server:"+result)
  serverp.close(True)
  client1p.kill()
  client2p.kill()
  #slog.close()
  #client1p.close(True)
  #client2p.close(True)
  #Popen("cp "+rootdir+"server.log ~/"+tentacle+str(time.time())+".server.log", shell = True).wait()
  #logfile = open(rootdir+'server/logs/1.gamelog.bz2','rb')
  #log = logfile.read()
  s3conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
  logbucket = s3conn.get_bucket("megaminer7")
  newkey = Key(logbucket)
  logname = 'logs/arena/'+str(tentacle)+'-'+str(time.time())+'.gamelog.bz2'
  newkey.key = logname
  newkey.set_contents_from_filename(rootdir+"server/logs/1.gamelog.bz2")
  webserver.set_game_stat(client1, client2, c1_score, c2_score, working_copies[client1], working_copies[client2], logname)
  remove(rootdir+"server/logs/1.gamelog")
  remove(rootdir+"server/logs/1.gamelog.bz2")
  
  return (winner, logname)

#run_game('Shell AI','Shell AI', 19000)

