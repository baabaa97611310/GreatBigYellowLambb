import random
import math
import requests
import json

LINKS = {
    "LCzero": "http://lczero.org/",
    "Lichess Bots": "https://lichess.org/api#tag/Chess-Bot"
}

ID = 41665


class Conversation():
    def __init__(self, game, engine, xhr, version, challenge_queue, config):
        self.game = game
        self.engine = engine
        self.xhr = xhr
        self.version = version
        self.challengers = challenge_queue
        self.config = config

    command_prefix = "!"
    chat_prefix = "@LeelaChess"

    def react(self, line, game):
        print("*** {} [{}] {}: {}".format(self.game.url(), line.room, line.username, line.text.encode("utf-8")))
        if (line.text[0] == self.command_prefix):
            self.command(line, game, line.text[1:].lower())

        if (self.chat_prefix.lower() in line.text[0:12].lower()):
            #return
            self.chat_bot(line, game, line.text[11:].lower())
        pass

    def chat_bot(self, line, game, text):
        URL = "http://localhost:5005/webhooks/rest/webhook"
        data = {}
        data["message"] = text
        r = requests.post(URL, json=data)
        resp = json.loads(r.text)
        print(resp)
        if len(resp) > 0:
            for r in resp:
                self.send_reply(line, r["text"])
            return

        self.send_reply(line, "Sorry, I do not understand!")

    def command(self, line, game, cmd):
        if cmd == "wait" and game.is_abortable():
            game.abort_in(60)
            self.send_reply(line, "Waiting 60 seconds...")
        elif cmd == "name":
            self.send_reply(line, "{} (lichess-bot v{})".format(self.engine.name(), self.version))
        elif cmd == "howto":
            self.send_reply(line, "How to run your own bot: lichess.org/api#tag/Chess-Bot")
        elif cmd == "commands" or cmd == "help":
            msg = "Commands: !name, !eval, !id, !leela, !hardware, !info, !queue, !chat, !nice and !howto"
            self.send_reply(line, msg)
        elif cmd == "eval" and line.room == "spectator":
            stats = self.engine.get_stats()
            num_moves = int(len(game.state["moves"].split())/2.0) + 1
            leela_stats = stats + ["move: {}".format(num_moves)]
            self.send_reply(line, ", ".join(leela_stats))
        elif cmd == "eval":
            self.send_reply(line, "I don't tell that to my opponent, sorry.")
        elif cmd == "id":
            self.send_reply(line, "ID {}".format(ID))
        elif cmd == "chat":
            self.send_reply(line, "You can chat with me if you type '@LeelaChess <your message>'")
        elif cmd == "elsie" or cmd == "leela":
            responses = [
                "Stop it. Let me focus!",
                "Like what you see? Help me improve at: {}".format(LINKS["LCzero"]),
                "Is that a free piece or are you happy to see me?",
                "Take the knight, it's a free knight!",
                "Pawns are small guys with big dreams",
                "Boomtown,  population you!",
                "Passed pawns must be pushed!",
                "The passed Pawn is a criminal, who should be kept under lock and key. Mild measures, such as police surveillance, are not sufficient",
                "COME ON HARRY! GET IN THERE, SON!",
                "Sit at the chessboard and play with yourself. It's amazing."]
            self.send_reply(line, random.choice(responses))
        elif cmd == "info":
            for name, url in LINKS.items():
                self.send_reply(line, "{}: {}".format(name, url))
        elif cmd == "hardware" or cmd == "gpu":
            self.send_reply(line, "RTX 2070 8GB, i5-6600K @ 3.50 GHz, Windows 10 Pro")
        elif cmd == "nice" or cmd == "benice":
            self.send_reply(line, "Would you like your loss to be less inevitable than it currently is?") 
            self.send_reply(line, "Try @LeelaNice - Because you aren't too proud for pity!")
        #elif cmd == "params":
            #self.send_reply(line, json.dumps(self.config["engine"]["lczero"]))
        elif cmd == "queue" or cmd == "challengers":
            if not self.challengers:
                self.send_reply(line, "No players in the queue!")
            else:
                challengers = ", ".join(["@" + challenger.challenger_name for challenger in reversed(self.challengers)])
                self.send_reply(line, "Current queue: {}".format(challengers))


    def send_reply(self, line, reply):
        self.xhr.chat(self.game.id, line.room, reply)

    def send_greeting(self):
        self.xhr.chat(self.game.id, "player", "Good luck, you're playing Leela ID {}.".format(ID))
        self.xhr.chat(self.game.id, "spectator", "Leela ID {}. Challenge me to play against me. !commands for commands.".format(ID))


class ChatLine():
    def __init__(self, json):
        self.room = json.get("room")
        self.username = json.get("username")
        self.text = json.get("text")
