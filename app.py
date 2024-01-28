from flask import Flask, request

from render import format_music
from parse import parse_music

app = Flask(__name__, static_folder='static')

@app.route("/")
def hello_world():
    print("Parsing music")
    parse_music()
    print("Formatting music")
    format_music()
    with open('index.html', 'r', encoding='utf-8') as f:
        s = f.read()
    return s


@app.route('/p', methods=['POST'])
def post_back():
    with open('expanded.html', 'wb') as f:
        f.write(request.data)
    return "ok"


if __name__ == "__main__":
  app.run(debug=True, port=8000)

'''
TODO:
Better Flask template
Can underscores extend under the notes?
Make triplet handling more robust
Make dotted rhythms easier to input
Put this under git!
Sort within incipits by scale degrees to make it easy to find one
Composer names: FIRST LAST or LAST, FIRST?  (lookup/normalize)
Smart quotes
Implicit ties
Explicit ties/slurs
xrefs PK/FK <-- data entry!
convert remainiong original_data <-- data entry!
trriplets should break beams before
'''
