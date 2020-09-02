import json
import os
import tempfile
from typing import Dict, List, Optional

from simple_slack_messenger.local_types import Block
from simple_slack_messenger.slack import Slack
from simple_slack_messenger.utils import set_block_state


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

    def _write(self, payload: Dict) -> None:
        with open(
            os.path.join(self.tmp_dir, "simple_slack_messenger", self.message_id), "w"
        ) as f:
            json.dump(payload, f)

    def _read(self) -> Dict:
        with open(os.path.join(self.tmp_dir, self.message_id), "r") as f:
            return json.load(f)

    def create_deployment(
        self,
        steps: List[str],
        initial_state: str = "Not started",
        header: Optional[str] = None,
    ) -> None:
        blocks: List[Block] = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "A deployment has been started",
                },
            }
        ]
        if header:
            blocks.append(
                {"type": "header", "text": {"type": "plain_text", "text": header}}
            )

        for step in steps:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{step}*: {initial_state}"},
                },
            )
        response = self.slack.post_message(self.channel, blocks=blocks)

        # Write response to disk to be able to reuse it
        self._write(response)

    def update_deployment(self, *, step: str, state: str) -> None:
        # Get the previous from disk
        response = self._read()

        ts = response["ts"]
        blocks = response["message"]["blocks"]
        text = response["message"]["text"]

        blocks = set_block_state(blocks, step=step, state=state)

        update_response = self.slack.edit_message(
            channel=self.channel, ts=ts, text=text, blocks=blocks
        )

        # Write updated response to disk
        self._write(update_response)
