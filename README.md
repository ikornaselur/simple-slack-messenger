# Simple Slack messager

A script that support sending messages to Slack from command line, with just
Python 3 and a Slack Bot token. There are no Python dependencies, other than
development ones. The whole project should just live in a single Python file.

The idea is to have a very simple script that support sending a message to a
channel and store temporary the `ts` for the message to be able to edit the
message later. I want to use this as a minimal script in CI to post status
update to a single message (by editing) on Slack.
