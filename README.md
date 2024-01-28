# tefillot

This is an index of "melodies for various tefillot." It is roughly organized in the order of the tefillot for a typical Shabbat; within each tefillah there is not currently a particular order.

The goal is (a) to be able to put names to the melodies that we take for granted, and (b) to act as a prompt, when I'm serving as shaliach tzibbur, to help revive the great melodies of the past century that have fallen into disuse.

Each melody is represented by a few measures from its incipit; just enough to identify it. They are all accompanied by a list of reference books from which I got the composer's name, and which also will tell you where you can find/purchase the complete sheet music.

There are two versions: The HTML version has a "play" button if you want to listen instead of read; the PDF version is convenient to have with you in shul.

Melodies by Carlebach are marked in red, so that those of us who avoid using his melodies, given the credible accusations against him, can quickly determine whether a given melody is problematic. See below for why red.

I had set myself a goal of finishing version 1.0 in time for Shabbat Shirah, the Sabbath of Song. I still have a bunch of melodies to add, but this has already shown itself to be useful to me, so I'm publishing it in the hopes that it will help others as well.

Added: This is very much a work in progress. I haven't cleaned up the code yet, and there are still gaps and errors in the data. But I got such an enthusiastic response that I'm putting it on github before I had intended to.

# Data flow

Everything starts with the YAML files in the data directory. I've been using one YAML per source reference book.

The Flask app.py uses the parse module to read the YAMLs, convert them to a TSV which uses ABC music syntax; then it uses the render module to read that TSV back in and convert it to HTML. The HTML then posts the contents of the page, including the rendered SVG, back to the Flask server, where the SVG files get saved out to the Images directory. Finally, a ReportLab-based script reconstructs the HTML and SVG into a PDF.

# YAML fields:

Top-level must start with `Book` which identifies the source, and then `Music` which contains a list of pieces.

Each piece must provide: `title`, `composer`, `page`, `key`, `time`, `notes`, and `lyrics`

Key should be a capital letter between `A` and `G`, modified by `#` for sharp and `b` for flat, and optionally followed by `m` for minor.

Time should be a fraction, such as `4/4`. Do not use `c`

If a piece is found in multiple sources, choose which one will be definitive and assign it a primary key in the `PK` field; all the others should provide the same key values marked as a foreign key in the `FK` field.

If you disagree with how a source has notated something, feel free to say so in a comment, but record the notes exactly as they are in the source material.

If you don't trust your source's attribution of the composer, you should put it in quotes (such as `composer: "Traditional"` or even `composer: According to "101 Favorite Folk Tunes", "from Vishnietz"` Many books misattribute works, which is one of the reasons this project exists.

If you want to add additional notes, such as "Also used by many as a contrafact for Titgadal in Kedushah", you may add a field labeled `NB`.

See below for guidelines on transliteration.

# Notation syntax

Music syntax: Loosely based on the PLAY command syntax from MSBasic on my IBM PCjr back in the mid-1980s. Sorry, that's how my brain thinks of rendering music as a string, and it was easier to convert that to ABC programmatically than it was to reprogram my brain.

Octaves start at C and and at B. We are initialized in octave 4, i.e., middle-C is the lowest note of the default octave.

`abcdefg` each identify a pitch. They may be followed by `+` and `-` to sharp or flat the note, or `@` for a natural. If we ever need double-sharps or double-flats we'll use `++` and `--`. To move up or down an octave, use `^` and `v` respectively.

`r` identifies a rest

A pitch (and any accidentals) or rest may be followed by a duration which is the denominator of the name of the note (e.g., `4` for a quarter note and `8` for an eighth note. Note durations may be dotted with `.` and double-dotted with `..`. If the duration is omitted, the previous note's duration is used.

I am thinking of adding auto-dot-complete, in which `g4.a` would imply that the `a` is really `a8` after which we'd reset the default duration to an _undotted_ `4`.

The program will automatically provide slurs and ties based on the lytics (see next section) but if you want to include your own slurs or ties you may start them with `(` and end with `)`

Triplets should be _preceded_ with `&3`

Beams will break at suitable points based on the time signature. If you want to break a beam elsewhere, follow all this with a backtick.

You must provide bar lines with `|`. The system doesn't track how many beats you have put into a bar.

# Lyrics

I am _not_ faithful to the transliterations of the sources, because that juxtaposition would be too confusing when scanning quickly down the page. My pronounciation is the version of so-called "Sephardic" taught in American Hebrew Schools. I tend to transliterate vowels using Italian-like patterns, but I can hardly claim consistency.

On to technical stuff:

As with the notes, you need to provide bar lines with `|`

Words of more than one syllable need hyphens between each syllable.

When a syllable takes up more than one note, if it's in the middle of a word, use one additional hyphen for each additional note; if it's at the end of the word, use an underscore `_` for each additional note.

# The incipits file

This controls the order in which things are presented.

`#` is a top-level heading indicator (as in Markdown), not a comment indicator (as in YAML)

A line beginning `=` means "I was inconsistent about how I entered the title, so anything that matches this title (excluding the `#`) should silently be merged with whatever came above it.

When you run things through the system, it will create a `missing-incipits.txt` file which you can use to cut-and-paste into the main `incipits.txt` file.

# Red

I tried different approaches to the Carlebach problem. Omitting them does not solve my problem of having to determine as soon as the shatz starts whether I'm singing along or placing my fingers across my lips -- I would have to check all the other melodies to determine that it's missing, and then try to remember whether it's missing because I made a conscious choice to omit it or whether it's one I haven't been able to source yet. And I don't want to leave them looking like everything else, both because I *do* want to make the point that these are in a distinct class, and because a pre-attentive signal will make it even faster for me to check the most critical options first.

# Tempos

Right now it's conditionalized whether to include tempo (always the same one) in the ABC, but since it generates both outputs from the single call, and the tempo marks are clutter on the PDFs, I'm defaulting to "off"

# Sources

Sources need to be _print_ and _published_. People need to be able to track them down to verify the correctness (of the attribution and the notation) and to learn the entire music for melodies that are new to them. Links to recordings are lovely -- and can be added as comments for now -- but they are not a substitute for a print citation in an area like this where so much misinformation abounds.

# Original compositions

I have received a few queries about including original compositions in this index. Much as I'd love to do so (of course I have some original compositions of my own that I'd want to include) that is the opposite direction from the purpose of this work, which is to provide a quick way to look up the composer of a familiar melody. When our melodies get familiar, we should be zocheh to have them included in this index.

On the other hand, having a separate web page with an index of newly-composed tefillah melodies, with links to places where one can sample them and download or purchase the music would be a nice complement to this. So I'll add it to the github soon, bli neder.



