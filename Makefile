.PHONY: dist

dist:
	@rm -rf dist
	@mkdir dist
	@echo "Concatenating files..."
	@cat src/simple_slack_messenger/local_types.py >> dist/_notify.py
	@cat src/simple_slack_messenger/utils.py >> dist/_notify.py
	@cat src/simple_slack_messenger/slack.py >> dist/_notify.py
	@cat src/simple_slack_messenger/messenger.py >> dist/_notify.py
	@cat src/simple_slack_messenger/cli.py >> dist/_notify.py
	@echo "Removing local import..."
	@sed -i '' '/^from simple_slack_messenger/d' dist/_notify.py
	@echo "Sorting with isort..."
	@poetry run isort --float-to-top -q dist/_notify.py
	@echo "Formatting with Black..."
	@poetry run black -q dist/_notify.py
	@echo "Making executable..."
	@echo "#!/usr/bin/env python3" > dist/notify.py
	@cat dist/_notify.py >> dist/notify.py
	@chmod +x dist/notify.py
	@rm dist/_notify.py
	@echo "dist/notify.py is ready"
