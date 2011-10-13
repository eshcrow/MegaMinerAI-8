#!/usr/bin/env python
### Missouri S&T ACM SIG-Game Arena (Thunderdome)
#####

# My AWS credentials
from aws_creds import access_cred, secret_cred

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


def main():
    # FIXME eventually want a way to break out of this loop gracefully
    while True:
        looping()


def looping():
    # get a game
    stalk = beanstalkc.Connection()
    stalk.watch('game-requests')
    job = stalk.reserve()
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
        result = subprocess.call(['make'], cwd=x.client.name,
                                 stdout=file("/dev/null", "w"), 
                                 stderr=subprocess.STDOUT)

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
    
    # fire up the processes
    get_fresh_server()    
    server = subprocess.Popen(['python', 'main.py'], 
                              cwd='server',
                              stdout=file("/dev/null", "w"),
                              stderr=subprocess.STDOUT)
    time.sleep(2)

    players = list()
    execution = ['/bin/bash', 'run', 'localhost']
    for gamedata in gamedatas:
        players.append(subprocess.Popen(execution,
                                        cwd=gamedata.client.name,
                                        stdout=file("/dev/null", "w"),
                                        stderr=subprocess.STDOUT))
        time.sleep(1)
        if len(execution) == 3:  # grumble grumble server
            execution += ['1'] 

    # game is running. watch for gamelog
    print "running..."
    game.status = "Running"
    game.save()
    while not os.access('server/logs/1.gamelog.bz2', os.F_OK):
        job.touch()
        time.sleep(1)
        
    # figure out who won by reading the gamelog
    print "determining winner..."
    winner = parse_gamelog()
    if winner == '0':
        gamedatas[0].won = True
        gamedatas[1].won = False
    elif winner == '1':
        gamedatas[0].won = False
        gamedatas[1].won = True
    [x.save() for x in gamedatas]        
        
    # clean up
    [x.terminate() for x in [server] + players]
    print "pushing gamelog..."
    push_gamelog(game)
    game.status = "Complete"
    game.save()
    job.delete()
    stalk.close()    
    print "done!"


def parse_gamelog():
    ### Determine winner by parsing that last s-expression in the gamelog
    f = open('server/logs/1.gamelog', 'r')
    log = f.readline()
    f.close()
    match = re.search("\"game-winner\" (\d) \"[\w ]+\" (\d+)", log)
    if match:
        return match.groups()[1]
    return None

    
def push_gamelog(game):
    ### Push the gamelog to S3
    c = boto.connect_s3(access_cred, secret_cred)
    b = c.get_bucket('siggame-gamelogs')
    k = boto.s3.key.Key(b)
    k.key = "%s.gamelog.bz2" % game.pk
    k.set_contents_from_filename("server/logs/1.gamelog.bz2")
    k.set_acl('public-read')
    game.gamelog_url = 'http://siggame-gamelogs.s3.amazonaws.com/%s' % k.key
    game.save()
    os.remove("server/logs/1.gamelog.bz2")
    os.remove("server/logs/1.gamelog")


def get_fresh_server():
    ### Pull a new server, just in case
    git.Repo("/home/mies/megaminer8").remotes.origin.pull()
    shutil.rmtree('server', ignore_errors=True)
    shutil.copytree('/home/mies/megaminer8/server', 'server')
    
    
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