"""Host renderer: produces grayscale PNG states; never required on the Kindle."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from library_model import load_catalog
from covers import discover

FONT_PATH = str(Path(__file__).parent / 'fonts/DejaVuSans.ttf')
FONT = ImageFont.truetype(FONT_PATH, 16)
SMALL = ImageFont.truetype(FONT_PATH, 12)

def wrap(draw, text, width, font, max_lines=2):
    lines = []; current = ''
    for c in text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' '):
        if draw.textlength(current+c, font=font) > width:
            lines.append(current); current = c
        else:
            current += c
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-3] + '...'
    return lines

def render(books, page, selected, usb=None, demo=False):
    im = Image.new('L', (600,800), 255); d = ImageDraw.Draw(im)
    d.text((12,10), 'Kindle Cover Home 0.2', font=FONT, fill=0)
    d.text((12,32), 'DEMONSTRACAO' if demo else 'CATALOGO / PREPARADO NO PC', font=SMALL, fill=0)
    subset = books[page*6:page*6+6]
    if not subset:
        d.text((74,350), 'Nenhum livro no catalogo.', font=FONT, fill=0)
    for cell, book in enumerate(subset):
        x=12+(cell%2)*294; y=56+(cell//2)*238
        d.rectangle((x,y,x+281,y+225), outline=0, width=4 if cell==selected else 1)
        box=(x+69,y+7,x+212,y+174)
        cover = discover(book,usb) if usb is not None else None
        if cover is not None:
            cover=ImageOps.contain(cover,(144,168))
            im.paste(cover,(x+69+(144-cover.width)//2,y+7+(168-cover.height)//2))
        else:
            d.rectangle(box,fill=224 if demo else 240,outline=0,width=2)
            d.line((x+78,y+18,x+78,y+162),fill=96,width=3)
            d.text((x+94,y+64), f'{page*6+cell+1:02}',font=FONT,fill=0)
            d.text((x+88,y+100),'FICTICIA' if demo else 'SEM CAPA',font=SMALL,fill=0)
        for i,line in enumerate(wrap(d,book.title,257,FONT)):
            d.text((x+10,y+178+i*19),line,font=FONT,fill=0)
    pages=max(1,(len(books)+5)//6)
    d.text((12,774),f'Pagina {page+1}/{pages} | Controles no KUAL | Sem abertura',font=SMALL,fill=0)
    return im

def prepare(catalog, output, usb=None, demo=False):
    books=load_catalog(catalog)
    output=Path(output)
    # Never overwrite an existing prepared library silently.
    output.mkdir(parents=True,exist_ok=False)
    for page in range(max(1,(len(books)+5)//6)):
        for cell in range(max(1,len(books[page*6:page*6+6]))):
            render(books,page,cell,usb,demo).save(output/f'page-{page+1}-select-{cell}.png')
    (output/'count').write_text(str(len(books))+'\n')
    (output/'catalog.tsv').write_bytes(Path(catalog).read_bytes())
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('catalog',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--usb-root',type=Path);p.add_argument('--demo',action='store_true')
    a=p.parse_args();prepare(a.catalog,a.output,a.usb_root,a.demo)
