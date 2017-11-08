#!/usr/bin/env python

import zulip
import dotenv

import requests
import datetime
import json
import os
import sys
import time

STREAM_NAME = 'bot-test'


# TO DO:
## Pickle list of subscribers
## Load upon SwoleBot initialization if present
## Different messages if attempting to join when already subscribed \
## or leave when not subscribed
class SwoleBot(object):

    def __init__(self, zulip_username, zulip_api_key, key_word, subscribed_streams=[]):
        """
        SwoleBot takes a Zulip username and API key,
        a key word to respond to (case insensitive),
        and a list of the Zulip streams it should be active in.
        """
        self.username = zulip_username
        self.api_key = zulip_api_key
        self.key_word = key_word.lower()

        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_username, zulip_api_key, site="https://recurse.zulipchat.com/api")
        self.subscriptions = self.subscribe_to_streams()
        self.stream_names = []
        for stream in self.subscriptions:
            self.stream_names.append(stream["name"])
        self.subscribers = []

    @property
    def streams(self):
        """Standardizes a list of streams in the form [{"name": stream}]"""
        streams = [{"name": stream} for stream in self.subscribed_streams]
        return streams

    def subscribe_to_streams(self):
        """Subscribes to Zulip streams"""
        streams = self.streams
        self.client.add_subscriptions(streams)
        return streams

    def register(self):
        """
        Keeps trying to register the bot until successful
        Returns queue_id and last_event_id on success
        """
        queue_id = None
        while queue_id == None:
            # print "Attempting to register..."
            registration = self.client.register(json.dumps(["message"]))
            queue_id = registration.get("queue_id")
            last_event_id = registration.get("last_event_id")
        return queue_id, last_event_id

    def send_private_message(self, to, content):
        """Minimal requirements for sending a private message"""
        self.client.send_message({
            "type": "private",
            "to": to,
            "content": content
        })

    def respond(self, message):
        content = message['content']
        content = content.lower().split()
        private = message["type"] == "private"
        if not private and self.key_word != content[0]:
            return None
        if private and (self.key_word != content[0]):
            command = content[0]
        else:
            command = content[1]
        sender = message['sender_full_name']
        email = message["sender_email"]
        if 'SwoleBot' in sender:
            return None
        if command == "join":
            if sender not in self.subscribers:
                self.subscribers.append(sender)
                response = "You're gonna make all kinds of gains ... All kinds ..."
            else:
                response = "You already made a positive life choice!"
        elif command == 'leave':
            if sender in self.subscribers:
                self.subscribers.remove(sender)
                response = "Well, it was nice knowing you buddy.  Auf wiedersehen"
            else:
                response = "New phone who dis"
        else:
            response = 'Please enter "swolebot join" to subscribe to me, or "swolebot leave" to unsubscribe'
        self.send_private_message(email, response)

    def send_reminder(self):
        self.client.send_message({
            "type": "stream",
            "to": STREAM_NAME,
            "subject": "exercise",
            "content": self.compose_message()
        })

    def compose_message(self):
        message = "It's time to exercise!!! 💪💪💪💪 " + ("@**%s** " * len(self.subscribers))
        message = message % tuple(self.subscribers)
        return message

    def main(self):
        """Write me"""

        # this both checks that SwoleBot is on, and will create
        # the entire database and its' columns if it doesn't exist
        time_last_reminded = datetime.datetime(1970, 1, 1)
        queue_id = None
        while True:
            # queue_id resets every 15 minutes or so
            if queue_id == None:
                queue_id, last_event_id = self.register()
                # print "registered!"

            results = self.client.get_events(
                    queue_id=queue_id, last_event_id=last_event_id,
                    longpolling=True, dont_block=True)

            if results.get("events") == None:
                # print results["msg"], results["result"]
                # force queue_id to reset
                queue_id = None
                continue

            for event in results["events"]:
                last_event_id = max(last_event_id, event["id"])
                try:
                    self.respond(event["message"])
                except ValueError as e:
                    print(e)

            current_time = datetime.datetime.now()
            current_hour = current_time.hour
            time_elapsed = current_time - time_last_reminded
            if 10 <= current_hour < 18 and time_elapsed >= datetime.timedelta(seconds=15):    
                self.send_reminder()
                time_last_reminded = current_time
            time.sleep(1)

# blocks SwoleBot from running automatically when imported
if __name__ == "__main__":

    dotenv.load_dotenv(dotenv.find_dotenv())
    zulip_username = os.environ["SWOLEBOT_USR"]
    zulip_api_key = os.environ["SWOLEBOT_API"]
    key_word = "SwoleBot"
    # an empty list will make it subscribe to all streams
    subscribed_streams = ['bot-test']

    new_bot = SwoleBot(zulip_username, zulip_api_key, key_word, subscribed_streams)
    new_bot.main()