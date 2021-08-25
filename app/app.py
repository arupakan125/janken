import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

class Janken():
    def __init__(self, client, channel_id, ts):
        self.channel_id = channel_id
        self.ts = ts
        self.players = []
        self.client = client
    def update(self, user_id, hand):
        if len(self.players) == 0:
            self.players.append({"user_id": user_id, "hand": hand})
            self.client.chat_update(
                channel = self.channel_id,
                ts = self.ts,
                attachments = [{"pretext": "<@" + user_id + ">" + "さんが手を出しました"}],
            )
        else:
            self.players.append({"user_id": user_id, "hand": hand})

            diff = (self.players[0]["hand"] - self.players[1]["hand"] + 3) % 3
            if diff == 0:
                # あいこ
                pass
            if diff == 1:
                # 先手の負け
                pass
            if diff == 2:
                # 先手の勝ち
                pass

            self.client.chat_update(
                channel = self.channel_id,
                ts = self.ts,
                blocks = [],
                attachments = [{"pretext": "<@" + self.players[0]["user_id"] + "> " + self.get_hand_as_string(self.players[0]["hand"]) + " VS " + self.get_hand_as_string(self.players[1]["hand"]) + " <@" + self.players[1]["user_id"] + ">"}],
            )
    def get_hand_as_string(self, hand):
        if hand == 0:
            return ":punch:"
        if hand == 1:
            return ":v:"
        if hand == 2:
            return ":raised_back_of_hand:"

class JankenManager():
    def __init__(self, client):
        self.jankens = []
        self.client = client
    
    def initiate_janken(self, say):
            message = say(
            {
                "blocks": [
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
            }
            )
            self.jankens.append(
                {
                    "channel_id": message["channel"],
                    "ts": message["ts"],
                    "janken": Janken(self.client, message["channel"], message["ts"])
                }
            )

    def update_janken(self, channel_id, ts, user_id, hand):
        for janken in self.jankens:
            if janken["channel_id"] == channel_id and janken["ts"] == ts:
                janken["janken"].update(user_id, hand)
                print("im here")

jm = JankenManager(app.client)

@app.command("/janken")
def handle_some_command(ack, say, body):
    ack()
    print(body)
    jm.initiate_janken(say)


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
