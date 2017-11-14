#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import unittest
from unittest.mock import patch
import datetime
import swolebot
import zulip

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
        z = patch('zulip.Client')
        self.addCleanup(z.stop)
        z.start()
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


    """Command tests"""
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

    def test_form_squat_public(self):
        exercise = "squat"
        command = SWOLEBOT + " " + FORM_COMMAND + " " + exercise
        message = self.construct_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form"] + swolebot.FORM_VIDEOS[exercise]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    def test_form_squat_private(self):
        exercise = "squat"
        command = FORM_COMMAND + " " + exercise
        message = self.construct_private_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form"] + swolebot.FORM_VIDEOS[exercise]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    def test_form_squat_private_full_command(self):
        exercise = "squat"
        command = SWOLEBOT + " " + FORM_COMMAND + " " + exercise
        message = self.construct_private_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form"] + swolebot.FORM_VIDEOS[exercise]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    def test_form_pushup_public(self):
        exercise = "pushup"
        command = SWOLEBOT + " " + FORM_COMMAND + " " + exercise
        message = self.construct_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form"] + swolebot.FORM_VIDEOS[exercise]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    def test_form_unknown_exercise_public(self):
        exercise = "iron_cross"
        command = SWOLEBOT + " " + FORM_COMMAND + " " + exercise
        message = self.construct_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form_help"]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    def test_form_unknown_exercise_private(self):
        exercise = "iron_cross"
        command = FORM_COMMAND + " " + exercise
        message = self.construct_private_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form_help"]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    def test_form_unknown_exercise_private_full_command(self):
        exercise = "iron_cross"
        command = SWOLEBOT + " " + FORM_COMMAND + " " + exercise
        message = self.construct_private_message(command)
        self.bot.respond(message)
        expected_message = swolebot.RESPONSES["form_help"]
        self.bot.send_private_message.assert_called_with(DEFAULT_EMAIL, expected_message)

    """Reminder tests"""    
    def test_is_reminder_time_day_false(self):
        fake_date = datetime.datetime(2017, 11, 12, 12) # A Saturday
        with patch('datetime.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = fake_date
            is_time = self.bot.is_reminder_time()
            self.assertFalse(is_time)

    def test_is_reminder_time_hour_false(self):
        fake_date = datetime.datetime(2017, 11, 14, 20) # A Monday at 8pm
        with patch('datetime.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = fake_date
            is_time = self.bot.is_reminder_time()
            self.assertFalse(is_time)   

    def test_is_reminder_time_true(self):
        fake_date = datetime.datetime(2017, 11, 14, 12) # A Monday at 12pm
        with patch('datetime.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = fake_date
            is_time = self.bot.is_reminder_time()
            self.assertTrue(is_time)

    def test_time_last_reminded_false(self):
        fake_time_reminded = datetime.datetime(2017, 11, 14, 12) # A Monday at 12pm
        fake_current_date = datetime.datetime(2017, 11, 14, 12, 30) # 30 minutes later
        self.bot.time_last_reminded = fake_time_reminded
        with patch('datetime.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = fake_current_date
            is_time = self.bot.is_reminder_time()
            self.assertFalse(is_time)

    def test_compose_message_no_subs(self):
        self.bot.subscribers = []
        message = self.bot.compose_message()
        self.assertEqual(message, swolebot.RESPONSES['reminder'])

    def test_compose_message_subs(self):
        self.bot.subscribers = [DEFAULT_USER_NAME]
        subscriber_tags = "@**%s** "
        subscriber_tags = subscriber_tags % DEFAULT_USER_NAME
        message = self.bot.compose_message()
        self.assertEqual(message, swolebot.RESPONSES['reminder'] + subscriber_tags)


if __name__ == "__main__":
    unittest.main()









