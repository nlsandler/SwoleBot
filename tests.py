#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import patch
import swolebot

DEFAULT_USER_NAME = "bob"
DEFAULT_EMAIL = "bob@example.com"
SWOLEBOT = 'swolebot'
JOIN_COMMAND = 'join'
LEAVE_COMMAND = 'leave'
INSPIRATION_COMMAND = 'inspiration'
FORM_COMMAND = 'form'

class SwoleBotTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        key_word = SWOLEBOT
        subscribed_streams = [swolebot.STREAM_NAME]
        self.bot = swolebot.SwoleBot('', '', key_word, subscribed_streams)
        self.bot.subscribers = []
        p = patch('swolebot.SwoleBot.send_private_message')
        self.addCleanup(p.stop)
        p.start()

    def construct_message(self, content, msg_type="stream", sender_full_name=DEFAULT_USER_NAME, sender_email=DEFAULT_EMAIL):
        return {
            "content": content,
            "type": msg_type,
            "sender_full_name": sender_full_name,
            "sender_email": sender_email
        }

    def construct_private_message(self, content, sender_full_name=DEFAULT_USER_NAME, sender_email=DEFAULT_EMAIL):
        return self.construct_message(content, msg_type="private", sender_full_name=sender_full_name, sender_email=sender_email)


    def test_join_public(self):
        command = SWOLEBOT + " " + JOIN_COMMAND
        message = self.construct_message(command)
        self.bot.respond(message)
        #verify that we sent the correct private message
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, swolebot.RESPONSES["join_success"])
        #verify they're in the subscriber list
        self.assertEqual(self.bot.subscribers, [DEFAULT_USER_NAME])

    def test_leave_public(self):
        command = SWOLEBOT + " " + LEAVE_COMMAND
        self.bot.subscribers = [DEFAULT_USER_NAME]
        message = self.construct_message(command)
        self.bot.respond(message)
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, swolebot.RESPONSES["leave_success"])
        #verify they're in the subscriber list
        self.assertEqual(self.bot.subscribers, [])

    def test_join_private(self):
        command = JOIN_COMMAND
        message = self.construct_private_message(command)
        self.bot.respond(message)
        #verify that we sent the correct private message
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, swolebot.RESPONSES["join_success"])
        #verify they're in the subscriber list
        self.assertEqual(self.bot.subscribers, [DEFAULT_USER_NAME])

    def test_leave_private(self):
        command = LEAVE_COMMAND
        self.bot.subscribers = [DEFAULT_USER_NAME]
        message = self.construct_private_message(command)
        self.bot.respond(message)
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, swolebot.RESPONSES["leave_success"])
        #verify they're in the subscriber list
        self.assertEqual(self.bot.subscribers, [])

    def test_join_private_full_command(self):
        command = SWOLEBOT + " " + JOIN_COMMAND
        message = self.construct_private_message(command)
        self.bot.respond(message)
        #verify that we sent the correct private message
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, swolebot.RESPONSES["join_success"])
        #verify they're in the subscriber list
        self.assertEqual(self.bot.subscribers, [DEFAULT_USER_NAME])

    def test_leave_private_full_command(self):
        command = SWOLEBOT + " " + LEAVE_COMMAND
        self.bot.subscribers = [DEFAULT_USER_NAME]
        message = self.construct_private_message(command)
        self.bot.respond(message)
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, swolebot.RESPONSES["leave_success"])
        #verify they're in the subscriber list
        self.assertEqual(self.bot.subscribers, [])

if __name__ == "__main__":
    unittest.main()









