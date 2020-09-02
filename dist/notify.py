#!/usr/bin/env python3
import argparse
import json
import os
import tempfile
import urllib.request
from typing import Dict, List, Optional, TypedDict


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


def set_block_state(blocks: List[Block], step: str, state: str) -> List[Block]:
    """ Find the block based on step and set the state """
    block_idx = -1

    for idx, block in enumerate(blocks):
        if f"*{step}*" in block["text"]["text"]:
            block_idx = idx
            break

    if block_idx == -1:
        raise Exception("Block not found")

    blocks[block_idx]["text"]["text"] = f"*{step}*: {state}"

    return blocks


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


def create(args: argparse.Namespace) -> None:
    messenger = Messenger(
        channel=os.environ["SLACK_CHANNEL"], message_id=args.id, verbose=True
    )

    messenger.create_deployment(
        steps=args.step, initial_state=args.initial_state, header=args.header
    )


def update(args: argparse.Namespace) -> None:
    messenger = Messenger(
        channel=os.environ["SLACK_CHANNEL"], message_id=args.id, verbose=True
    )

    messenger.update_deployment(step=args.step, state=args.state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post an editable deployment message on Slack"
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # Create
    create_parser = subparsers.add_parser("create", help="create help")
    create_parser.add_argument(
        "id", help="A unique id for the deployment, used for updating"
    )
    create_parser.add_argument("step", nargs="+", help="Steps in the deployment")
    create_parser.add_argument(
        "--initial-state",
        "-i",
        default="Not started",
        help="The initial state of each step (default: Not started)",
    )
    create_parser.add_argument("--header", "-e", help="Optional header")
    create_parser.set_defaults(func=create)

    # Update
    update_parser = subparsers.add_parser("update", help="update help")
    update_parser.add_argument(
        "id", help="A unique id for the deployment, used when message was created"
    )
    update_parser.add_argument("step", help="Which step to update")
    update_parser.add_argument("state", help="The new state of the step")
    update_parser.set_defaults(func=update)

    args = parser.parse_args()
    args.func(args)
