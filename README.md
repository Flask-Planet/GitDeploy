This project is used to allow Flask apps to be auto updated via git webhook. 

It works best with gitlab, with a deployment token. These can be found by going to

`Settings -> Repository -> Deploy tokens`

Place the token url in a `.env` file in the root of your project. See `.env_example`

Running `python3 github.py` will start a Flask server on port 5500 that has some basic routes setup to allow git actions.