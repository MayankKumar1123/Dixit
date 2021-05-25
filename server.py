import os.path
import logging

import json

from math import ceil

import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.locks
import tornado.gen

from chat import ChatLog
from codes import APIError, Codes
from core import Limits, States, StringClue, Game
from deck import CardSet
from users import Users
from utils import INFINITY, hash_obj, get_sorted_positions, url_join, \
    capture_stdout
import config
import display
import asyncio
import sys

from tornado.options import define, options, parse_command_line

define("port", default=5556, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


totalGames = 0
clients = {}

class Commands(object):
    """Possible commands for the GameHandler, to be used in the JavaScript."""

    GET_BOARD = 0
    JOIN_GAME = 1
    START_GAME = 2
    CREATE_CLUE = 3
    PLAY_CARD = 4
    CAST_VOTE = 5
    KICK_PLAYER = 6
    createRoom = 7
    enterRoom = 8
    changeColor = 9


class RequestHandler(tornado.web.RequestHandler):
    """Base class for all request handlers. Injects authenticated self.user."""

    USER_COOKIE_NAME = 'dixit_user'

    def prepare(self):
        """Sets self.user based off hash in existing cookie, or a new cookie."""
        uid = self.get_cookie(self.USER_COOKIE_NAME)
        if not self.application.users.has_user(uid):
            if uid is None:
                uid = hash_obj(id(self), add_random=True)
                self.set_cookie(self.USER_COOKIE_NAME, uid)
            puid = hash_obj(uid, add_random=True)
            self.user = self.application.users.add_user(uid, puid)
        else:
            self.user = self.application.users.get_user(uid)
        


class LoginHandler(RequestHandler):
    def get(self):
        self.render("login.html")

class LoginJSHandler(RequestHandler):
    """Handler for rendering login.js with the server's template variables."""

    def get(self):
        self.set_header('Content-Type', 'text/javascript')
        self.render('login.js', messageTypes = Commands)

class LoginCSSHandler(RequestHandler):
    """Handler for rendering login.css with the server's template variables."""

    def get(self):
        self.set_header('Content-Type', 'text/css')
        self.render('login.css')        
        
class gameLoginHandler(RequestHandler):
    def post(self):
        global totalGames
        
        
        tp = int(self.get_argument('type'))
        username = self.get_argument('nickname')
        roomname = self.get_argument('room')
        password = self.get_argument('password')
        
        if tp == Commands.createRoom:#To create a new room
        
            notFound = -1
            for i, gm in self.application.games.items():
                if gm.name == roomname :
                    notFound = i
                    break
                    
            if notFound != -1:
                #Room already exists
                self.write(json.dumps({'game':'exists'}))
            else:
                game = Game(self.user, [self.application.card_sets[0]], password, roomname,
                        12, 40, 100)
                        
                self.user.set_name(username)
                self.user.gid = totalGames
                
                game.add_player(self.user, 'RED')
                self.application.games[totalGames] = game
                self.write(json.dumps({'game':str(totalGames)}))
                totalGames += 1
                
                #ADDING EXTRA PLAYERS TO HELP TEST
                #x1 = self.application.users.add_user('2dfsgsdfg', '2dsgsdfg')
                #x2 = self.application.users.add_user('3dfgsfdfg', '3dfgdfgd')
                #x3 = self.application.users.add_user('4dsfgsdfg', '4fsfoias')
                #game.add_player(x1, display.BunnyPalette.allColors[1])
                #game.add_player(x2, display.BunnyPalette.allColors[2])
                #game.add_player(x3, display.BunnyPalette.allColors[3])
                
                
            
        elif tp == Commands.enterRoom:#He is trying to enter room

            print(roomname, password)
            
            notFound = -1
            for i, gm in self.application.games.items():
                if gm.name == roomname and gm.password == password:
                    print('game exists, add him in', i, gm.name, gm.password)
                    notFound = i
                    break
                    
            if notFound == -1:
                self.write(json.dumps({'game':'na'}))
            else:
                #add into game given by totalGames = i
                blob = {'game':str(notFound)}
                
                self.user.set_name(username)
                self.user.gid = notFound
                
                i = 0
                for col in display.BunnyPalette.allColors:
                    if col not in list(self.application.games[notFound].colours.values()):
                        i = col
                    
                self.application.games[notFound].add_player(self.user, i)
                
                #players = {}
                
                #for i in self.application.games[notFound].players:
                #    players.update({'name': i.name , 'color': i})
                
                #blob.update({'players':players})
                
                
                
                self.write(json.dumps(blob))
        else:
            print(self.request.arguments)
                
class gameBoardHandler(RequestHandler):
    def get(self):
        if self.user.gid == -1:
            self.redirect('/')
        else:
            self.render("board.html", display = display) #Send in the parameters

            


class BoardJSHandler(RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'text/javascript')
        self.render('board.js', display = display, commands = Commands, states = States)

class BoardCSSHandler(RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'text/css')
        self.render('board.css', display = display)  


class GameHandler(RequestHandler):
    def get(self):
        if self.user.gid == -1:
            self.redirect('/')
        else:
            gid = self.user.gid
            cmd = int(self.get_argument('cmd'))
            #print(gid, cmd)
            
            if gid not in self.application.games:
                raise APIError(Codes.ILLEGAL_RANGE, gid)
            
            game = self.application.games[gid]
            #print(game.state)
            
            
            if cmd == Commands.GET_BOARD:
                self.write(self._get_board(self.user, game))
#            elif cmd == Commands.JOIN_GAME:
#                colour = self.get_argument('colour')
#                game.add_player(self.user, colour)
            elif cmd == Commands.START_GAME:
                game.start_game()
                self.write('OK')
            elif cmd == Commands.CREATE_CLUE:
                clue = StringClue(self.get_argument('clue'))
                card = game.get_card(self.get_argument('cid'))
                self.write('OK')
                game.create_clue(self.user, clue, card)
            elif cmd == Commands.PLAY_CARD:
                card = game.get_card(self.get_argument('cid'))
                game.play_card(self.user, card)
                self.write('OK')
            elif cmd == Commands.CAST_VOTE:
                card = game.get_card(self.get_argument('cid'))
                game.cast_vote(self.user, card)
                self.write('OK')
#            elif cmd == Commands.KICK_PLAYER:
#                puid = self.get_argument('puid')
#                game.kick_player(self.application.users.get_user_by_puid(puid))
            elif cmd == Commands.changeColor:
                game.add_player(self.user, self.get_argument('color'))
                self.write('OK')
            else:
                raise APIError(Codes.ILLEGAL_RANGE, cmd)
                
                
    @classmethod
    def _get_board(cls, user, game):
    
        players = {u.puid:{'name':u.name, 'score':game.players[u].score, 'color':game.colours[u], 'color_val': display.BunnyPalette.allColors[game.colours[u]]} for u in game.players}

        requires_action = {}
        for u in game.players:
            requires_action[u.puid] = {
                States.BEGIN: game.host == u and \
                    len(players) >= Limits.MIN_PLAYERS,
                States.CLUE: game.clue_maker() == u,
                States.PLAY: not game.round.has_played(u),
                States.VOTE: not game.round.has_voted(u),
                States.END: False,  # game.host == u,
            }[game.state]

        puids = list(players.keys())
        ranked = get_sorted_positions(puids, key=lambda puid: players[puid]['score'])

        rnd = {}
        if game.round.has_everyone_played():
            rnd['cards'] = [card.to_json()
                for card in game.round.get_cards()]
            rnd['cardsHash'] = hash_obj(rnd['cards'])
        if game.round.has_everyone_voted():
            rnd['votes'] = dict((u.puid, card.cid)
                for u, card in list(game.round.user_to_vote.items()))
            rnd['owners'] = dict((u.puid, card.cid)
                for u, card in list(game.round.user_to_card.items()))
            rnd['votesHash'] = hash_obj(rnd['votes'])
        if game.round.clue:
            rnd['clue'] = str(game.round.clue)
        if game.round.clue_maker:
            rnd['clueMaker'] = game.round.clue_maker.puid
        rnd['scores'] = dict((u.puid, score)
            for u, score in list(game.round.scores.items()) if score > 0)

        plr = {}
        if game.players[user].hand:
            plr['hand'] = [card.to_json() for card in game.players[user].hand]
            plr['handHash'] = hash_obj(plr['hand'])
            
        

        blob = {
            'name' : game.name,
            'user' : user.puid,
            'host' : game.host.puid,
            'players' : players,
            'isHost' : user == game.host,
            'maxScore' : game.max_score if game.max_score != INFINITY else None,
            'maxClueLength' : game.max_clue_length,
            'order' : [u.puid for u in game.order],
            'turn' : game.turn,
            'ranked' : dict((uid, rank) for uid, rank in zip(puids, ranked)),
            'state' : game.state,
            'requiresAction' : requires_action,
            'round' : rnd,
            'player' : plr
        }
        gamehash = hash_obj(blob);
        
        blob.update({'gamehash':gamehash})
        
        return json.dumps(blob)

        
def has_suffix(name, suffixes):
    """Returns true iff name ends with at least one of the given suffixes."""
    return True in (name.endswith(suffix) for suffix in suffixes)


def find_cards(folder, suffixes=('.jpg','.png')):
    """Returns all urls for a given folder, matching the given suffixes."""
    path = os.path.join(
        os.path.dirname(__file__), display.WebPaths.CARDS, folder)
    return [url_join(display.WebPaths.CARDS, folder, name)
        for name in os.listdir(path) if has_suffix(name, suffixes)]


class Application(tornado.web.Application):
    """Main application class for holding all state."""

    def __init__(self, *args, **kwargs):
        """Initializes the users, games, chat log, and cards."""
        self.users = Users()
        self.games = {}
        self.chat_log = ChatLog()

        # Specifies where to find all the card images for each set.
        self.card_sets = [CardSet(name, find_cards(folder), enabled)
            for name, (folder, enabled) in kwargs['card_sets'].items()]
        self.admin_password = kwargs['admin_password']
        self.admin_enable = kwargs['admin_enable']

        super(Application, self).__init__(*args, **kwargs)
        
settings = dict(
        cookie_secret="SX4gEWPE6bVr0vbwGtMl",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
)

configFilename = "config.json"
settings.update(config.parse(configFilename))


handlers = [
        (r'/', LoginHandler),
        (r'/login.js', LoginJSHandler),
        (r'/login.css', LoginCSSHandler),
        (r"/getGame", gameLoginHandler),
        (r"/gameBoard", gameBoardHandler),
        (r'/board.js', BoardJSHandler),
        (r'/board.css', BoardCSSHandler),
        (r'/gamePlay', GameHandler)
      
]

if __name__ == "__main__":
    if sys.version_info >= (3,8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = Application(handlers, **settings)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()