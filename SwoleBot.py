#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import zulip
import dotenv

import requests
import datetime
import json
import os
import sys
import time

STREAM_NAME = 'bot-test'
SUBSCRIBER_LIST = 'subscribers.txt'

RESPONSES = {
    "join_success": "You're gonna make all kinds of gains ... All kinds ...",
    "leave_success": "Well, it was nice knowing you buddy.  Auf wiedersehen",
    "already_joined": "You already made a positive life choice!",
    "already_not_subscribed": "New phone who dis",
    "help": 'Please enter "swolebot join" to subscribe to me, or "swolebot leave" to unsubscribe',
    "reminder": "It's time to exercise!!! 💪💪💪💪 "
}

# TO DO:
## Pickle list of subscribers
## Load upon SwoleBot initialization if present
class SwoleBot(object):

    def __init__(self, zulip_username, zulip_api_key, key_word, subscribed_streams=[]):
        """
        Parameters:
        -----------
        zulip_username: string
            Email address generated by Zulip, used to authenticate
        zulip_api_key: string
            Key generated when bot is registered, used to authenticate
        key_word: string
            Word at beginning of message used to trigger bot response
        subscribed_streams:
            Streams in which bot listens for commands and posts exercise reminders

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
        self.load_subscribers()

    def load_subscribers(self):
        """Initialize list of subscribers from a file.
        Should be called once on startup."""
        try:
            with open(SUBSCRIBER_LIST, "r") as f:
                self.subscribers = [line.strip() for line in f]
        except FileNotFoundError:
            self.subscribers = []

    def save_subscribers(self):
        """Save list of subscribers to a file,
        overwriting current contents of file.
        Should be called every time subscriber list is modified"""
        with open(SUBSCRIBER_LIST, "w") as f:
            for subscriber in self.subscribers:
                f.write(subscriber+"\n")

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
        """
        Parameters:
        -----------
        to: string
            Email address of message recipient
        content: string
            Body of message.

        """
        self.client.send_message({
            "type": "private",
            "to": to,
            "content": content
        })

    def respond(self, message):
        """
        Checks if message in private message or stream is valid SwoleBot command,
        (either join or leave).  Commands in public streams must begin with 'swolebot'
        commands in private messages do not have to.  If the command is 'join' SwoleBot
        adds the sender to the list of subscribers (if not already subscribed).  
        If it is 'leave' SwoleBot removes the subscriber (if subscribed).  Other commands
        are invalid; SwoleBot responds with help text.

        """
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
                self.save_subscribers()
                response = RESPONSES["join_success"]
            else:
                response = RESPONSES["already_joined"]
        elif command == 'leave':
            if sender in self.subscribers:
                self.subscribers.remove(sender)
                self.save_subscribers()
                response = RESPONSES["leave_success"]
            else:
                response = RESPONSES["already_not_subscribed"]
        else:
            response = RESPONSES["help"]
        self.send_private_message(email, response)

    def send_reminder(self):
        """
        Posts exercise reminder in subscribed stream.

        """
        self.client.send_message({
            "type": "stream",
            "to": STREAM_NAME,
            "subject": "exercise",
            "content": self.compose_message()
        })

    def compose_message(self):
        """
        Format exercise reminder message tagging all subscribers.

        """
        message = RESPONSES["reminder"] + ("@**%s** " * len(self.subscribers))
        message = message % tuple(self.subscribers)
        return message

    def main(self):
        """
        Searches subscribed streams and private messages for new subscriptions
        or unsubscribe requests.  Remind subscribers when it's time to workout
        every hour on the hour between 10am and 6pm Monday-Thursday.

        """
        time_last_reminded = datetime.datetime(1970, 1, 1)
        queue_id = None
        while True:
            # queue_id resets every 15 minutes or so
            if queue_id == None:
                queue_id, last_event_id = self.register()

            results = self.client.get_events(
                    queue_id=queue_id, last_event_id=last_event_id,
                    longpolling=True, dont_block=True)

            if results.get("events") == None:
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
    subscribed_streams = [STREAM_NAME]

    new_bot = SwoleBot(zulip_username, zulip_api_key, key_word, subscribed_streams)
    new_bot.main()