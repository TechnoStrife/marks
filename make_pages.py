import sys
import json
import shutil
import requests
import pathlib

only_build = '--only-build' in sys.argv
root = pathlib.Path(__file__).parent
pages = root / 'gh-pages'

URL = 'http://127.0.0.1:8000'
API_URL = URL + '/api'
SAVE = [
    '/summary/classes',
    '/summary/subjects',
    '/summary/teachers',
]
LIST = [
    'class',
    'student',
    'subject',
    'teacher',
]

if only_build:
    shutil.copy2(root / 'dist' / 'bundle.js', pages / 'static' / 'bundle.js')
    shutil.copy2(root / 'dist' / 'style.css', pages / 'static' / 'style.css')
    exit(0)


r = requests.get(URL)
with (pages / 'index.html').open('wb') as f:
    f.write(r.content)

shutil.rmtree(pages / 'static')
shutil.rmtree(pages / 'api')
shutil.copytree(root / 'static', pages / 'static', dirs_exist_ok=True)
shutil.copy2(root / 'dist' / 'bundle.js', pages / 'static' / 'bundle.js')
shutil.copy2(root / 'dist' / 'style.css', pages / 'static' / 'style.css')

api = pages / 'api'
api.mkdir(exist_ok=True)
summary = api / 'summary'
summary.mkdir(exist_ok=True)

for name in ['classes', 'subjects', 'teachers']:
    with (summary / (name + '.json')).open('wb') as f:
        r = requests.get(f'{API_URL}/summary/{name}/?format=json')
        f.write(r.content)


for group in LIST:
    group_path = api / group
    group_path.mkdir(exist_ok=True)
    next_page = f'{API_URL}/{group}/?format=json'
    while next_page is not None:
        r = requests.get(next_page)
        data = r.json()
        next_page = data['next']
        data = data['results']
        for entry in data:
            id_ = entry["id"]
            with (group_path / f'{id_}.json').open('wb') as f:
                full_entry = requests.get(f'{API_URL}/{group}/{id_}/?format=json')
                f.write(full_entry.content)






