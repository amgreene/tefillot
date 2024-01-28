''' render my tefillot music tsv into html/svg
    Andrew M Greene
'''

import codecs
import csv
import datetime

from flask import render_template

def render(music, notation_number):
    ''' Actually, for now, just assume it's valid ABC '''
    abc = music
    # abc = abc.replace('\\', '\\\\')
    abc = abc.replace("'", "\\'")
    # abc += '\\nQ:1/4=108'
    return f"<div id='notation{notation_number}'></div><script>make('notation{notation_number}', 'X:{notation_number}\\n{abc}');</script>"


def format_music():
    s = []
    notation_number = 0
    incipit = ''
    for filename in ('x.tsv',): # 'data.tsv'):
        for row in csv.DictReader(codecs.open(filename, 'r', 'utf-8'), delimiter='\t'):
            if row['Incipit'].startswith('#'):
                continue
            composer = row['Composer']

            # This is how we do section headers
            if composer is None:
                s.append(f'<tr class="section"><td colspan=4>{row["Incipit"]}</td></tr>')
                continue

            if incipit != row["Incipit"]:
                incipit = row["Incipit"]
                s.append(f'<tr class="incipit"><td colspan=4>{row["Incipit"]}</td></tr>')

            if composer.startswith('.'):
                composer = composer[1:]

            style = 'x' if 'Carlebach' in composer else ''
            notation_number += 1

            s.append(''.join([
                f'<tr valign="top"><td>',
                f'<td><br><div style="width: 200px" id="notation{notation_number}a" /></td>',
                f'<td class="{style}">{render(row["Music"], notation_number)}</td>',
                f'<td><br><b>{composer}</b><br/>{row["Source"]}</td></tr>',
            ]))

    data = {
        'table_body': '\n'.join(s),
        'datetime': datetime,
    }
    rendered = render_template('main.html', **data)

    with codecs.open('index.html', 'w', 'utf-8') as fout:
        print(rendered, file=fout)


'''

Currently relying on "abc" notation, see
http://abcnotation.com/wiki/abc:standard:v2.1

----

How I want to write out the musical notes

First octave is cdefgab
Second octave is CDEFGAB
^ Shift the "first" octave up
_ Shift the "first" octav down

Accidentals precede the note (as they do in sheet music)
+ sharp the next note
- flat the next note
# natural the next note

| bar line

Duration always precedes the notes to which it applies
1 = whole
2 = half
4 = quarter
8 = eighth
6 = sixteenth (note that 16 works too because no note follows the 1)
3 = next three notes are a triplet of the given duration
0 = do not render the note (but do render accidentals -- used for key signatures)

For now, no beams

'''

