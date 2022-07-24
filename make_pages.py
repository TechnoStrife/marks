import shutil
import requests
import pathlib

root = pathlib.Path(__file__).parent
pages = root / 'gh-pages'

URL = 'http://127.0.0.1:8000'
SAVE = [
    '/summary/classes',
    '/summary/subjects',
    '/summary/teachers',
]
LIST = [
    '/class/',
    '/student/',
    '/subject/',
    '/teacher/',
]

r = requests.get(URL)
with (pages / 'index.html').open('wb') as f:
    f.write(r.content)


shutil.copytree(root / 'static', pages / 'static', dirs_exist_ok=True)

api = pages / 'api'
api.mkdir(exist_ok=True)
summary = api / 'summary'
summary.mkdir(exist_ok=True)

for name in ['classes', 'subjects', 'teachers']:
    with (summary / name).open('wb') as f:
        r = requests.get(URL + '/api/summary/' + name + '/?format=json')
        f.write(r.content)

