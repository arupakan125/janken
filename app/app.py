import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

class Janken():
    blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "じゃんけんしましょ",
                            "emoji": True
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": ":punch:ぐー",
                                    "emoji": True
                                },
                                "value": "gu",
                                "action_id": "button_gu"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": ":v:ちょき",
                                    "emoji": True
                                },
                                "value": "choki",
                                "action_id": "button_choki"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": ":raised_back_of_hand:ぱー",
                                    "emoji": True
                                },
                                "value": "pa",
                                "action_id": "button_pa"
                            }
                        ]
                    }
                ]

    def __init__(self, client, say, command):
        self.channel_id = None
        self.ts = None
        self.maximum_player = 2
        self.current_player = 0
        self.players = []
        self.client = None
        if command["text"]:
            if command["text"].split()[0].isdecimal():
                self.maximum_player = int(command["text"].split()[0])

        for i in range(self.maximum_player):
            self.players.append(
                {
                    "user_id": None,
                    "hand": None,
                }
            )
        message = say({
            "blocks": self.blocks + self.get_progress_block()
        })
        self.channel_id = message["channel"]
        self.ts = message["ts"]
        self.client = client


    def update(self, user_id, hand):
        for player in self.players:
            if player["user_id"] is None:
                player["user_id"] = user_id
                player["hand"] = hand
                self.current_player += 1
                break

        self.client.chat_update(
            channel = self.channel_id,
            ts = self.ts,
            blocks = self.blocks + self.get_progress_block()
        )

        if self.current_player == self.maximum_player:
            self.finish()

    def get_hand_as_string(self, hand):
        if hand == 0:
            return ":punch:"
        if hand == 1:
            return ":v:"
        if hand == 2:
            return ":raised_back_of_hand:"

    def finish(self):
        blocks = []
        for player in self.players:
            blocks.append(
                {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "<@" + player["user_id"] + "> " + self.get_hand_as_string(player["hand"]),
                        }
                }
            )
        self.client.chat_update(
            channel = self.channel_id,
            ts = self.ts,
            blocks = blocks
        )
    
    def get_progress_block(self):
        blocks = []
        for player in self.players:
            if player["user_id"] is None:
                blocks.append(
                    {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "誰かの手を待っています",
                            }
                    }
                )
                continue
            blocks.append(
                    {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "<@" + str(player["user_id"]) + ">" + "さんが手を出しました",
                            }
                    }
                )
        return blocks

class JankenManager():

    def __init__(self, client):
        self.client = client
        self.jankens = []
    
    def initiate_janken(self, say, command):
            self.jankens.append(Janken(self.client, say, command))

    def update_janken(self, channel_id, ts, user_id, hand):
        for janken in self.jankens:
            if janken.channel_id == channel_id and janken.ts == ts:
                janken.update(user_id, hand)

jm = JankenManager(app.client)

@app.command("/janken")
def handle_some_command(ack, say, body, command):
    ack()
    print(command)
    jm.initiate_janken(say, command)


@app.action("button_gu")
def handle_some_action(ack, body):
    ack()
    user_id = body["user"]["id"]
    channel_id = body["container"]["channel_id"]
    ts = body["container"]["message_ts"]
    hand = 0
    jm.update_janken(channel_id, ts, user_id, hand)

@app.action("button_choki")
def handle_some_action(ack, body):
    ack()
    user_id = body["user"]["id"]
    channel_id = body["container"]["channel_id"]
    ts = body["container"]["message_ts"]
    hand = 1
    jm.update_janken(channel_id, ts, user_id, hand)

@app.action("button_pa")
def handle_some_action(ack, body):
    ack()
    user_id = body["user"]["id"]
    channel_id = body["container"]["channel_id"]
    ts = body["container"]["message_ts"]
    hand = 2
    jm.update_janken(channel_id, ts, user_id, hand)


# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
