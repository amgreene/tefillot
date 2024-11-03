import datetime
import json
from flask import Flask, request

from render import format_music
from parse import parse_music, MusicState

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

@app.route('/abc', methods=['GET'])
def abc():
    arg_dict = {k: request.args.get(k)
                for k in ('time', 'key', 'notes', 'lyrics', 'book', 'page', 'title', 'composer', 'nb')}
    music = MusicState(arg_dict)
    saved_msg = ''
    if request.args.get('save') == '1':
        arg_dict['timestamp'] = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        with open("saves.json", "a") as f:
            print(json.dumps(arg_dict), file=f)
        saved_msg = f'<h3>Saved to disk at {arg_dict["timestamp"]}</h3>'
    html = """<script src="static/abcjs_basic_5.9.1-min.js" type="text/javascript"></script>
<meta charset="utf-8">
<link href="static/audio.css" media="all" rel="stylesheet" type="text/css" />
<div id="test">Music goes here</div>
<div id="testa">Controls go here</div>

<script>
  function make(id, abc) {
      var visualObj = ABCJS.renderAbc(id, abc)[0];
      var synthControl = new ABCJS.synth.SynthController();
      synthControl.load('#' + id + "a", null, {displayRestart: true, displayPlay: true, displayProgress: true});
      synthControl.setTune(visualObj, false);
  }""" + f"make('test', '{music.abc()}');\n" + "</script>" + saved_msg
    return html; # music.abc()

if __name__ == "__main__":
  app.run(debug=True, port=8000)

'''
TODO:
Key, time signaturs
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
