run-reddit:
	@poetry run python -m src.reddit.ask_reddit

run-twitter: 
	@rm -rf db && poetry run python -m src.twitter.main