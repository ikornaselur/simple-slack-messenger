# Simple Slack messenger

A script that support sending messages to Slack from command line, with just
Python 3 and a Slack Bot token. There are no Python dependencies, other than
development ones. The whole project should just live in a single Python file.

The idea is to have a very simple script that support sending a message to a
channel and store temporary the `ts` for the message to be able to edit the
message later. I want to use this as a minimal script in CI to post status
update to a single message (by editing) on Slack.

## Usage

The script has two commands: create and update

```
-> % notify.py --help
usage: notify.py [-h] {create,update} ...

Post an editable deployment message on Slack

positional arguments:
  {create,update}
    create         Create a deployment message
    update         Update an existing one

optional arguments:
  -h, --help       show this help message and exit
```

First a message needs to be created, with a unique id, which will be used for
any updates. Creating a message will require a number of steps.

The following usage

```
-> % notify.py create unique_id "Search for Llamas" "Normalize power" "Reticulate splines" --header Production
```

will create the following Slack message

```
A deployment has been started

*Production*
Search for Llamas: Not started
Normalize power: Not started
Reticulate splines: Not started
```

then updating with

```
-> % notify.py update unique_id "Search for Llamas" ":loading: In progress..."
```

updates the message to

```
A deployment has been started

*Production*
Search for Llamas: :loading: In progress...
Normalize power: Not started
Reticulate splines: Not started
```
