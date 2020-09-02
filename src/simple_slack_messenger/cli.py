import argparse
import os

from simple_slack_messenger.messenger import Messenger


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
