import os

def load_env():
    with open('local.env') as f:
        data = f.read()
    data = [x.split('=') for x in data.split('\n')]

    for item in data:
        key, value = item 
        os.environ[key] = value
