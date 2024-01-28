from bs4 import BeautifulSoup

h = BeautifulSoup(open('expanded.html'), 'html.parser')
for svg in h.find_all('svg'):
    notation = svg.parent.attrs.get('id')
    if notation is None:
        continue
    # print(notation)
    with open(f'Images/{notation}.svg', 'w', encoding='utf-8') as f:
        print(svg.prettify(), file=f)
print(notation)
