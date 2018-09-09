
all: run

init:
	pip install -r requirements.txt

lint:
	pylint cya.py

run:
	./game.py
