import codecs
import csv
import datetime

from pathlib import Path

from reportlab.graphics import renderPDF, renderPM
from reportlab.graphics.shapes import Drawing, Group, Rect, Path as ShapePath
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Flowable
# from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, PageBreak, PageTemplate, KeepTogether, CondPageBreak

from svglib.svglib import svg2rlg

from bs4 import BeautifulSoup

def recursivelyRed(group):
    if isinstance(group, Group):
        children = group.contents
    else:
        children = group  # list
    for child in children:
        if isinstance(child, Group):
            recursivelyRed(child.contents)
        else:
            p = child.getProperties()
            if isinstance(child, Rect):
                if p.get('strokeOpacity') < 0.0001:
                    continue
            child.setProperties({
                'fillColor': 'darkred',
                # 'strokeColor': 'darkred'
                })


def svg(p:Path):
    drawing = svg2rlg(p.open(encoding='utf8'))
    if drawing is None:
        return None
    # Scale the Drawing.
    scale = 0.33
    drawing.scale(scale, scale)
    drawing.width *= scale
    drawing.height *= scale

    return drawing


INCIPIT_STYLE = ParagraphStyle(
    'incipit',
    fontSize = 12,
    backColor = 'lightgrey',
    )

RED = ParagraphStyle(
    'red',
    textColor = 'darkred',
    )

# print(getSampleStyleSheet().byName.keys())

def get_doc(pdf_path):
    doc = BaseDocTemplate(pdf_path,
                          pageSize=letter,
                          leftMargin = 24,
                          rightMargin = 24,
                          topMargin = 36,
                          bottomMargin = 36,
                          )

    #Two Columns
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='col1')
    frame2 = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height, id='col2')

    # Elements.append(Paragraph(" ".join([random.choice(words) for i in range(1000)]),styles['Normal']))
    template = PageTemplate(id='TwoCol',
                            frames=[frame1,frame2],
                            onPageEnd=addPageNumbers,
                            )
    doc.addPageTemplates([template, ])

    return doc


def addPageNumbers(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(72*4, 0.55 * 72, f"Page {doc.page}")
    canvas.restoreState()


def boilerplate(story):
    story.extend([Paragraph(f"""Work in progress; this version {datetime.datetime.utcnow()} (UTC).
  There are typos in the music, typos in the lyrics, etc. Sometimes a given
  melody appears in multiple of my source books and I am still combining those.
  Composer names are inconsistently formatted."""),
            Paragraph("""<a href="http://www.greenehouse.com/a/tefillot">An interactive webpage version is available at <font color="blue">http://www.greenehouse.com/a/tefillot</font></a>.</p>"""),
            Paragraph("""Feedback to <a href="mailto:andrew@greenehouse.com">andrew@greenehouse.com</a>""")
            ])

def example(content):
    styles = getSampleStyleSheet()
    pdf_path = 'tefilot.pdf'

    story = []
    boilerplate(story)

    keep_together = []
    for row in content:
        if row[0] == 'notation':
            drawing = svg(Path(f'Images/notation{row[1]}.svg'))
            if drawing is None:
                continue
            if 'Carlebach' in row[2]:
                style = RED
                # print('----')
                recursivelyRed(drawing.contents)
            else:
                style = styles['Normal']

            composer = row[2]
            if composer.startswith('.'):
                composer = composer[1:]

            source = row[3].replace('<br>', '<br/>').split("<br/>")

            keep_together.extend([
                Paragraph('<b>' + composer.replace('<br>', '<br/>') + '</b>', style),
                *[
                    Paragraph('<i><font size=9>' + s + '</font></i>', style)
                    for s in source
                ],
                drawing,
                ])
            story.append(KeepTogether(keep_together))
            keep_together = []
        elif row[0] == 'incipit':
            keep_together.extend([
                Paragraph('<b>' + row[1] + '</b>', INCIPIT_STYLE),
                ])
        elif row[0] == 'section':
            keep_together.extend([
                CondPageBreak(144),
                Paragraph(row[1], styles['Heading1']),
                ])

    doc = get_doc(pdf_path)
    #doc = SimpleDocTemplate(pdf_path,
    #                        pagesize=letter)
    doc.build(story,
              )

#for p in Path('Images').glob('notation*.svg'):
#    drawing = svg2rlg(p)
#    renderPDF.drawToFile(drawing, str(p).replace('.svg', '.pdf'))
# renderPM.drawToFile(drawing, "Images/notation2.png", fmt="PNG")

h = BeautifulSoup(open('expanded.html'), 'html.parser')

def parse_tsv():
    content = []
    incipit = ''
    notation_number = 0

    for filename in ('x.tsv',): # 'data.tsv'):
        for row in csv.DictReader(codecs.open(filename, 'r', 'utf-8'), delimiter='\t'):
            if row['Incipit'].startswith('#'):
                continue
            composer = row['Composer']

            # This is how we do section headers
            if composer is None:
                content.append(('section', row["Incipit"]))
                continue

            if incipit != row["Incipit"]:
                incipit = row["Incipit"]
                content.append(('incipit', row["Incipit"]))

            style = 'x' if 'Carlebach' in composer else ''
            notation_number += 1
            content.append(('notation', notation_number,
                            composer, row['Source']))

    return content

example(parse_tsv())
