import argparse
import os

from simple_slack_messenger.messenger import Messenger


def create(args: argparse.Namespace) -> None:
    messenger = Messenger(channel=os.environ["SLACK_CHANNEL"], message_id=args.id)

    messenger.create_deployment(
        steps=args.step, initial_state=args.initial_state, header=args.header
    )


def update(args: argparse.Namespace) -> None:
    messenger = Messenger(channel=os.environ["SLACK_CHANNEL"], message_id=args.id)

    messenger.update_deployment(step=args.step, state=args.state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post an editable deployment message on Slack"
    )
    parser.add_argument(
        "--error",
        action="store_false",
        help=(
            "If not provided, the script will ignore all errors, "
            "to prevent the script from blocking a CI run for example"
        ),
    )
    subparsers = parser.add_subparsers()

    # Create
    create_parser = subparsers.add_parser("create", help="Create a deployment message")
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
    update_parser = subparsers.add_parser("update", help="Update an existing one")
    update_parser.add_argument(
        "id", help="A unique id for the deployment, used when message was created"
    )
    update_parser.add_argument("step", help="Which step to update")
    update_parser.add_argument("state", help="The new state of the step")
    update_parser.set_defaults(func=update)

    args = parser.parse_args()
    if args.error:
        args.func(args)
    else:
        try:
            args.func(args)
        except Exception as e:
            print(f"Encountered error: {e}")
