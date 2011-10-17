#!/usr/bin/env python
### Missouri S&T ACM SIG-Game Arena (Thunderdome)
#####

import sys

if len(sys.argv) != 4:
    gladiator      = 'localhost'
    my_hostname     = 'mnuck.com'
    print "referee.py gladiator my_hostname"
else:
    (junk, gladiator, my_hostname) = sys.argv

# My AWS credentials
from aws_creds import access_cred, secret_cred, username, password

# Some magic to get a standalone python program hooked in to django
import sys
sys.path = ['/home/mies/', '/home/mies/mysite/mysite'] + sys.path

from django.core.management import setup_environ
import settings

setup_environ(settings)

# Non-Django 3rd Part Imports
import re, json               # special strings
import beanstalkc, git, boto  # networky
import subprocess, shutil, os # shellish
import random, time

# My Imports
from thunderdome.models import Game


from threading import Thread

class Smile_And_Nod(Thread):
    def __init__(self, pipe):
        Thread.__init__(self)
        self.pipe = pipe
        
    def run(self):
        while True:
            if len(self.pipe.readline()) == 0:
                break


def main():
    # FIXME eventually want a way to break out of this loop gracefully
    while True:
        looping()


def looping():
    # get a game
    stalk = beanstalkc.Connection()
    stalk.watch('game-requests')
    job = stalk.reserve(timeout=2)
    if job is None:
        stalk.close()
        return
    game_id = json.loads(job.body)['game_id']
    game = Game.objects.get(pk=game_id)
    print "processing game", game_id

    gamedatas = list(game.gamedata_set.all())
    random.shuffle(gamedatas) # even split of p0, p1        
    
    # handle embargoed players
    if any([x.client.embargoed for x in gamedatas]):
        game.status = "Failed"
        game.save()
        job.delete()
        stalk.close()
        print "failing the game, embargoed player"
        return
    
    # get and compile the clients
    for x in gamedatas:
        x.version = x.client.current_version
        update_local_repo(x.client)
        update_downstream_repo(gladiator, x.client)
        result = remote_compile(gladiator, x.client)
        x.compiled = (result is 0)
        if not x.compiled:
            x.client.embargoed = True
            x.client.save()
        x.save()
        print "result for make in %s was %s" % (x.client.name, x.compiled)

    # handle a failed game
    if not all([x.compiled for x in gamedatas]):
        game.status = "Failed"
        game.save()
        job.delete()
        stalk.close()
        print "failing the game, someone didn't compile"
        return
    
    players = list()
    
    e = ["ssh", "gladiator@%s" % gladiator] + \
        ["cd %s ; ./run %s" % \
             (gamedatas[0].client.name, my_hostname)]
    players.append(subprocess.Popen(e, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE))
    
    line = players[0].stdout.readline()
    match = re.search("Creating game (\d+)", line)
    if match:
        game_number = match.groups()[0]
    else:
        line = players[0].stderr.readline()
        if re.search("Unable to open socket", line):
            print "server is probably down. that's bad."
        else:
            print "unexpected output from client. bail."
        players[0].terminate()
        stalk.close()
        return

    print "server says this is game number", game_number
    
    nodder1 = Smile_And_Nod(players[0].stdout)
    nodder1.start()
    nodder2 = Smile_And_Nod(players[0].stderr)
    nodder2.start()
    

    e = ["ssh", "gladiator@%s" % gladiator] + \
        ["cd %s ; ./run %s %s" % \
             (gamedatas[1].client.name, my_hostname, game_number)]
    players.append(subprocess.Popen(e, stdout=file("/dev/null", "w"),
                                    stderr=subprocess.STDOUT))


    # game is running. watch for gamelog
    print "running..."
    game.status = "Running"
    game.save()
    while not os.access("server/logs/%s.gamelog" % game_number, os.F_OK):
        job.touch()
        time.sleep(1)
        
    # figure out who won by reading the gamelog
    print "determining winner..."
    winner = parse_gamelog(game_number)
    if winner == '0':
        gamedatas[0].won = True
        gamedatas[1].won = False
    elif winner == '1':
        gamedatas[0].won = False
        gamedatas[1].won = True
    [x.save() for x in gamedatas]        
        
    # clean up
    [x.join() for x in (nodder1, nodder2)]
    [x.terminate() for x in players]
    print "pushing gamelog..."
    push_gamelog(game, game_number)
    game.status = "Complete"
    game.save()
    job.delete()
    stalk.close()    
    print "done!"


import socket
import libssh2
    
def remote_compile(hostname, client):
    command = 'cd %s ; make >/dev/null 2>/dev/null' % client.name
    return remote_call(hostname, command)


def update_downstream_repo(hostname, client):
    command = 'git clone ssh://mies@%s/home/mies/arena/%s >/dev/null 2>/dev/null' % (my_hostname, client.name)
    remote_call(hostname, command)
    command = 'cd %s ; git pull >/dev/null 2>/dev/null' % client.name
    remote_call(hostname, command)
    

def remote_call(hostname, command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, 22))

    session = libssh2.Session()
    session.startup(sock)

    session.userauth_password(username, password)
    channel = session.open_session()
    channel.execute(command)
    while not channel.eof():
        junk = channel.read(1024)
        time.sleep(1)
    
    result = channel.exit_status()
    session.close()
    return result        
    

def parse_gamelog(game_number):
    ### Determine winner by parsing that last s-expression in the gamelog
    f = open("server/logs/%s.gamelog" % game_number, 'r')
    log = f.readline()
    f.close()
    match = re.search("\"game-winner\" (\d) \"[\w ]+\" (\d+)", log)
    if match:
        return match.groups()[1]
    return None

    
def push_gamelog(game, game_number):
    ### Push the gamelog to S3
    c = boto.connect_s3(access_cred, secret_cred)
    b = c.get_bucket('siggame-gamelogs')
    k = boto.s3.key.Key(b)
    k.key = "%s.gamelog.bz2" % game.pk
    k.set_contents_from_filename("server/logs/%s.gamelog.bz2" % game_number)
    k.set_acl('public-read')
    game.gamelog_url = 'http://siggame-gamelogs.s3.amazonaws.com/%s' % k.key
    game.save()
    os.remove("server/logs/%s.gamelog.bz2" % game_number)
    os.remove("server/logs/%s.gamelog" % game_number)
    
    
def update_local_repo(client):
    ### This is the repo the gladiators will be grabbing from
    base_path = "ssh://mnuck@r99acm.device.mst.edu:2222/home/mnuck/clients/"
    try:
        git.Git().clone('%s%s.git' % (base_path, client.name))
    except git.exc.GitCommandError:
        pass
    git.Repo(client.name).remotes.origin.pull()
    # FIXME set the right tag
    
main()
