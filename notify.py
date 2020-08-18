#!/usr/bin/env python3
import json
import os
import tempfile
import time
import urllib.request
from typing import Any, Dict, List, Optional, TypedDict

#########
# Types #
#########


class Text(TypedDict):
    type: str
    text: str


class Block(TypedDict):
    type: str
    text: Text


class PayloadBase(TypedDict):
    channel: str


class Payload(PayloadBase, total=False):
    blocks: List[Block]
    text: str
    ts: str


#########
# Utils #
#########


def set_block_state(
    blocks: List[Block], environment: str, step: str, state: str
) -> List[Block]:
    """ Find the block based on environment and step and set the state """
    block_idx = -1
    environment_section = False

    for idx, block in enumerate(blocks):
        if block["text"]["text"] == environment:
            environment_section = True
        if environment_section and f"*{step}*" in block["text"]["text"]:
            block_idx = idx
            break

    if block_idx == -1:
        raise Exception("Block not found")

    blocks[block_idx]["text"]["text"] = f"*{step}*: {state}"

    return blocks


###########
# Classes #
###########


class Slack:
    token: str
    base_url: str

    def __init__(self, token: str, base_url: str = "https://slack.com/api/") -> None:
        self.token = token
        self.base_url = base_url

    def _post(self, method: str, payload: Optional[Payload] = None) -> Dict:
        if payload is None:
            data = None
        else:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}{method}",
            data=data,
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        response = urllib.request.urlopen(request)
        parsed = json.loads(response.read())

        if not parsed["ok"]:
            print(json.dumps(parsed, indent=2))
            raise Exception("Request failed")

        return parsed

    def post_message(
        self,
        channel: str,
        text: Optional[str] = None,
        blocks: Optional[List[Block]] = None,
    ) -> Dict:
        method = "chat.postMessage"

        payload: Payload = {
            "channel": channel,
        }
        if text is not None:
            payload["text"] = text
        if blocks is not None:
            payload["blocks"] = blocks

        return self._post(method, payload)

    def edit_message(
        self,
        channel: str,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[List[Block]] = None,
    ) -> Dict:
        method = "chat.update"

        payload: Payload = {
            "channel": channel,
            "ts": ts,
        }
        if text is not None:
            payload["text"] = text
        if blocks is not None:
            payload["blocks"] = blocks

        return self._post(method, payload)

    def auth_test(self) -> Dict:
        method = "auth.test"

        return self._post(method)


class Messenger:
    """ An opinionated messenger class to post and update messages regarding deployments

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

    def __init__(self, channel: str, message_id: str, verbose=False) -> None:
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


if __name__ == "__main__":
    messenger = Messenger(
        channel=os.environ["SLACK_CHANNEL"], message_id="deployment-test", verbose=True
    )

    envs = ["Dev", "Staging"]
    steps = ["Migrations", "Deploy", "Other things", "Extra stuff"]

    result = messenger.create_deployment(environments=envs, steps=steps)

    channel_id = result["channel"]
    ts = result["ts"]
    blocks = result["message"]["blocks"]
    text = result["message"]["text"]

    # Simulate waits for testing
    for environment in envs:
        time.sleep(1)
        for step in steps:
            blocks = set_block_state(
                blocks,
                environment=environment,
                step=step,
                state=":loading: In progress...",
            )
            response = messenger.update_deployment(ts, blocks=blocks)
            time.sleep(1)
            blocks = set_block_state(
                blocks,
                environment=environment,
                step=step,
                state=":heavy_check_mark: Done!",
            )

    blocks[0]["text"]["text"] = "The deployment has been finished"
    messenger.update_deployment(ts, blocks=blocks)
