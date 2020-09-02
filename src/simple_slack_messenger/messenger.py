import os
import tempfile
from typing import Dict, List, Optional

from simple_slack_messenger.slack import Slack
from simple_slack_messenger.types import Block


class Messenger:
    """ An opinionated messenger to post and update messages regarding deployments

    Has two main methods.

        1. Start a deployment message
        2. Update a deployment message

    Starting a deployment message is to create a message on Slack, that will be
    updated multiple times.

    Since this script is called multiple times to apply changes, the current
    message is stored, by an ID, in a temp directory
    """

    slack: Slack
    tmp_dir: str
    message_id: str
    channel: str
    verbose: bool

    def __init__(self, channel: str, message_id: str, verbose: bool = False) -> None:
        self.slack = Slack(os.environ["SLACK_TOKEN"])
        self.channel = channel
        self.tmp_dir = tempfile.gettempdir()
        self.message_id = message_id
        self.verbose = verbose

        if self.verbose:
            print(f"temp dir: {self.tmp_dir}")

    def create_deployment(self, environments: List[str], steps: List[str]) -> Dict:
        blocks: List[Block] = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "A deployment has been started",
                },
            }
        ]
        for environment in environments:
            blocks.append(
                {"type": "header", "text": {"type": "plain_text", "text": environment}}
            )
            for step in steps:
                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*{step}*: Not started"},
                    },
                )
        return self.slack.post_message(self.channel, blocks=blocks)

    def update_deployment(
        self,
        ts: str,
        *,
        text: Optional[str] = None,
        blocks: Optional[List[Block]] = None,
    ) -> Dict:
        return self.slack.edit_message(
            channel=self.channel, ts=ts, text=text, blocks=blocks
        )
