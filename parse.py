from collections import defaultdict
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path

import yaml
import re


@dataclass
class Note:
    octave: int
    note_name: str
    duration: str
    beat_position: float = 0
    lyric: str = ''
    trailing_bar: bool = False
    trailing_space: bool = False # to break beams
    open_paren: bool = False
    close_paren: bool = False
    triplet_prefix: str = ''


class MusicState:
    NOTE_PARTS_RE = re.compile(r'(\(?)(\&\d)?([\^v]?)([abcdefgr][+@-]?)(\d*\.?)(\)?)(\`)?')

    # iterate down the list of notes statefully,
    # creating a list of Note objects that are stateless
    def __init__(self, piece: dict):
        self.piece = piece
        self.debugging = piece.get('debug')
        self.music : list[Note] = []
        state : Note = Note(octave = 4,
                            note_name = 'x',
                            duration = '4')
        dont_beam_across : list[float]= {
            '4/4': [2/4],
            '6/8': [3/8],
            '3/4': [1/3, 2/3],
            '2/2': [1/2],
            '2/4': [1/4],
        }.get(piece.get('time', '4/4'), [])

        if 'notes' not in piece:
            piece['notes'] = ''

        if 'notes_abc' in piece:
            return

        if self.debugging:
            print(self.parse_notes(piece['notes']))


        parsed_notes = self.parse_notes(piece['notes'])
        parsed_lyrics = self.parse_lyrics(piece.get('lyrics'))
        if len(parsed_lyrics) < len(parsed_notes):
            parsed_lyrics += [[""]] * (len(parsed_notes) - len(parsed_lyrics))

        for measure in zip(parsed_notes, parsed_lyrics):
            current_beat = 0
            lyric_syllables = [] + measure[1]

            for note in measure[0]:
                if note is None:
                    print("Not a match:", piece['title'], note)
                    continue
                if len(note) == 0:
                    continue  # but why?

                open_paren, triplet_prefix, octave_change, note_name, duration, close_paren, break_beams = note
                if octave_change == 'v':
                    state.octave -= 1
                elif octave_change == '^':
                    state.octave += 1
                state.note_name = note_name
                if duration:
                    if duration == '.':
                        state.duration += '.'
                    else:
                        state.duration = duration

                # TODO: Account for triplets

                duration_ratio = 1/int(state.duration.replace('.', ''))
                if state.duration.endswith('.'):
                    duration_ratio *= 1.5
                next_beat = current_beat + duration_ratio

                trailing_space = break_beams == '`'
                if next_beat in dont_beam_across:
                    trailing_space = True

                if note_name == 'r' or len(lyric_syllables) == 0:
                    lyric = ''
                else:
                    lyric = lyric_syllables.pop(0)

                self.music.append(Note(
                    octave = state.octave,
                    note_name = state.note_name,
                    duration = state.duration,
                    beat_position = current_beat,
                    lyric = lyric,
                    open_paren = open_paren == '(',
                    close_paren = close_paren == ')',
                    trailing_space = trailing_space,
                    triplet_prefix = (triplet_prefix[1:] if triplet_prefix else None)
                ))

                current_beat = next_beat

            if self.music:
                self.music[-1].trailing_bar = True

            self.add_implied_parens()

    def add_implied_parens(self):
        last_index_with_lyric = None
        was_inside_parens = False
        for index, note in enumerate(self.music):
            # for now, erase all known parens
            note.open_paren = False
            note.close_paren = False

            has_lyric = any(c.isalpha() for c in note.lyric)
            if has_lyric or index == 0 or note.note_name == 'r':
                last_index_with_lyric = index
                if was_inside_parens:
                    self.music[index-1].close_paren = True
                    was_inside_parens = False
            else:
                self.music[last_index_with_lyric].open_paren = True
                was_inside_parens = True
        if was_inside_parens:
            self.music[-1].close_paren = True

    def parse_notes(self, s:str) -> list[str]:
        measures = re.split(r'\s*\|\s*', s)
        notes = [
            MusicState.NOTE_PARTS_RE.findall(
                m.replace(' ', '')
            )
            for m in measures
        ]
        # print(notes)
        return notes

    def parse_lyrics(self, s):
        if s is None:
            return [['']]
        # hyphens END a syllable and imply a trailing space
        # underscores ARE a syllable an imply both leading and trailing spaces
        s_with_implicit_spaces = s.replace('-', '- ').replace('_', ' _ ') #.replace("'", "’")
        measures = re.split(r'\s*\|\s*', s_with_implicit_spaces)
        lyrics = [
            m.split() for m in measures
            ]
        return lyrics

    def abc_notes(self):
        # old-style legacy mode
        if 'notes_abc' in self.piece:
            return [(self.piece['notes_abc'], self.piece.get('lyrics', ''))]

        bar_number = 0
        n = []
        matching_lyrics = []
        return_list = []

        def add_to_return_list():
            nonlocal n
            nonlocal matching_lyrics
            if len(n) == 0:
                return
            return_list.append(
                (''.join(n),
                 ' '.join(matching_lyrics).replace(' _', '_'))
            )
            n = []
            matching_lyrics = []

        accidentals = {}
        for note in self.music:

            nn = note.note_name[0]
            if nn == 'r':
                nn = 'z'

            octave = note.octave - 1

            if nn != 'z':
                if octave < 3:
                    nn = nn.upper() + ','*(3-octave)
                elif octave == 3:
                    nn = nn.upper()
                elif octave == 4:
                    nn = nn.lower()
                else:
                    nn = nn.lower() + "'"*(octave-4)

                note_letter = note.note_name[0]
                current_accidental = accidentals.get(note_letter)

                if note.note_name.endswith('+'):
                    if current_accidental != '+':
                        nn = '^'+nn
                        accidentals[note_letter] = '+'
                elif note.note_name.endswith('-'):
                    if current_accidental != '-':
                        nn = '_'+nn
                        accidentals[note_letter] = '-'
                elif note.note_name.endswith('@'):
                    nn = '='+nn
                    accidentals[note_letter] = ''

            # default note length is 1/8
            try:
                len_numerator = 8/int(note.duration.replace('.', ''))
            except:
                print(f"Exception for note with duration {note.duration}")
            if note.duration.endswith('.'):
                len_numerator *= 1.5  # TODO: double-dots
            len_denominator = 1.0
            while len_numerator != int(len_numerator):
                len_numerator *= 2
                len_denominator *= 2
            if len_denominator == 1:
                if len_numerator == 1:
                    len_ratio = ''
                else:
                    len_ratio = str(int(len_numerator))
            else:
                len_ratio = f'{int(len_numerator):d}/{int(len_denominator):d}'

            matching_lyrics.append(note.lyric)

            if note.open_paren:
                n.append('(')

            if note.triplet_prefix:
                n.append('(' + note.triplet_prefix)

            n.append(nn+len_ratio)

            if note.close_paren:
                n.append(')')

            if note.trailing_space:
                n.append(' ')

            if note.trailing_bar:
                n.append(' | ')
                accidentals = {}
                bar_number += 1
                if bar_number in self.piece.get('break_bars', []):
                    add_to_return_list()


        add_to_return_list()
        return return_list
    #[(''.join(n),
    #             ' '.join(matching_lyrics).replace(' _', '_'))
    #            ]


    # def abc_lyrics(self):
    #     if 'notes_abc' in self.piece:
    #         # then also assume lyrics are already converted
    #         return self.piece.get('lyrics', '')

    #     return ' '.join(note.lyric for note in self.music).replace(' _', '_')

    def abc(self):
        # TODO: M: time signature
        time_sig = f'M:{self.piece.get("time", "QQQ")}\\n'
        if 'QQQ' in time_sig:
            time_sig = ''
        key_sig = f'K:{self.piece.get("key", "QQQ")}\\n'
        if 'QQQ' in key_sig:
            key_sig = ''
        heading = f'{key_sig}{time_sig}L:1/8\\n'
        body = '\\n'.join(f'{notes}\\nw: {lyrics}'
                          for notes, lyrics in self.abc_notes())
        return heading + body


@dataclass
class ParsedPiece:
    title: str
    composer: str
    abc: str
    book: str
    page: str
    nb: str
    fk: str
    pk: str


def parse_music_yaml(yaml_path:Path, parsed_music:dict[list[ParsedPiece]]) -> None:
    if '.yaml' not in str(yaml_path):
        raise ValueError(f"{yaml_path} is not a yaml file")
    print(f"Parsing YAML file {yaml_path}")
    y = yaml.safe_load(yaml_path.open('r', encoding='utf-8'))
    if 'Music' not in y:
        print("No Music in", yaml_path)
        return
    for piece in y['Music']:
        # print(piece.get('title'))
        music = MusicState(piece)
        book = piece.get('book', y['Book'])
        composer = piece.get('composer', y.get('Composer', '?'))
        parsed_music[piece['title']].append(ParsedPiece(
            title = piece['title'].replace("'", "’"),
            composer = composer,
            abc = music.abc(),
            book = book,
            page = piece.get('page', '?'),
            nb = (lambda s: 'NB: ' + s if s is not None else '')(piece.get('nb')),
            fk = piece.get('FK'),
            pk = piece.get('PK'),
            ))
        # print(music.abc())

def print_counts(parsed_music: dict[list]) -> None:
    total_pieces = sum(len(x) for x in parsed_music.values())
    print(f"There are {total_pieces} total versions of {len(parsed_music.keys())} incipits")


def build_fks(parsed_music):
    fks = {}
    for title, pieces in parsed_music.items():
        for piece in pieces:
            if piece.pk is not None:
                fks[piece.pk] = []
    for title, pieces in parsed_music.items():
        for piece in pieces:
            if piece.fk is not None and piece.fk in fks:
                fks[piece.fk].append(piece)
    return fks


def parse_music():
    parsed_music = defaultdict(list)

    for yaml_path in Path('data').glob('*.yaml'):
        parse_music_yaml(yaml_path, parsed_music)

    fks = build_fks(parsed_music)

    incipits = {}
    with open('incipits.txt', encoding='utf-8') as inp:
        for i, row in enumerate(inp):
            incipits[row.strip()] = i
    missing_incipits = set()
    with open('missing_incipits.txt', 'w', encoding='utf-8') as o:
        for k in parsed_music.keys():
            if k not in incipits  and f"={k}" not in incipits and k not in missing_incipits:
                print(k, file=o)
                missing_incipits.add(k)
    for k in sorted(list(missing_incipits)):
        incipits[k] = len(incipits)

    with open('x.tsv', 'w', encoding='utf-8') as o:
        print('Incipit\tComposer\tMusic\tSource', file=o)
        last_k = ''
        for k in incipits.keys():
            if k.startswith('# '):
                print(k[2:], sep='\t', file=o)
                continue
            if k.startswith('='):
                k = k[1:]
            else:
                last_k = k
            v = parsed_music[k]
            for row in v:
                source = f"<i>{row.book}</i>:{row.page}"
                if row.pk is not None and row.pk in fks:
                    for fk_piece in fks.get(row.pk):
                        source += f"<br/><i>{fk_piece.book}</i>:{fk_piece.page}"
                # if this row has a FK and it's a key in FKS (thus the PK exists)
                # then skip it
                if row.fk is not None and row.fk in fks:
                    continue
                if row.nb:
                    source += f"<br>{row.nb}"
                    # <br/>{fk_piece.nb}"
                print(last_k, # row.title,
                      row.composer,
                      row.abc,
                      source,
                      sep='\t', file=o)


    print_counts(parsed_music)

if __name__ == '__main__':
    parse_music()
