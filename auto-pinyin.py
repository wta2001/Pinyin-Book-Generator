import re
import jieba
import tkinter
from tkinter import font
from pypinyin import lazy_pinyin
from pylatex import Document, Command, Package
from pylatex.utils import NoEscape
import click
import os


def generate(doc, path, font_size, pinyin_size, split_space):
    tkinter.Frame().destroy()
    txt = font.Font(family="KaiTi", size=font_size)
    space = split_space[0]*txt.measure('M')
    indent = txt.measure('汉字')
    indent_flag = True
    newline_flag = False
    firstline_flag = True
    oneline_flag = False
    width = 0
    section_number = 1
    line = []
    with open(path) as f:
        text = f.readlines()
    for row in text:
        split = jieba.lcut(row)
        if split[0] == '#':
            makesection(doc, split, firstline_flag, section_number)
            section_number += 1
            continue
        elif split[0] == '##':
            makesection(doc, split, firstline_flag)
            continue
        elif split[0] == '{':
            del split[0]
            oneline_flag = True
        elif split[0] == '}':
            oneline_flag = None
            line += ['\n']
        if oneline_flag is False:
            line = split
        elif oneline_flag:
            line += split[:-1]
            continue
        doc.append(Command('indent'))
        firstline_flag = False
        for index,word in enumerate(line):
            if re.match('[\u4e00-\u9fa5]', word):
                if newline_flag and (line[index+1]!='\n'):
                    doc.append('\n')
                    newline_flag = False
                pin = ' '.join(lazy_pinyin(word, style=1))
                doc.append(NoEscape(fr'\ruby{{{word}}}{{\{pinyin_size} {pin}}}{split_space[1]}'))
                width += txt.measure(word)+space
            elif word == '\n':
                    doc.append('\n')
                    width = 0
                    indent_flag = True
                    newline_flag = False
            else:
                if word == '^':
                    doc.append(NoEscape(r'\ '))
                    width += 1/3*txt.measure('M')
                else:    
                    doc.append(word)
                    width += txt.measure(word)
                if newline_flag and (line[index+1]!='\n'):
                    doc.append('\n')
                    newline_flag = False
            if indent_flag:
                if width > 580 - indent:
                    width = 0
                    indent_flag = False
                    newline_flag = True
            else:
                if width > 580:
                    newline_flag = True
                    width = 0
        oneline_flag = False
        line = []
                    
                                       
def maketitle(doc, inputpath):
    tkinter.Frame().destroy()
    title = os.path.splitext(os.path.basename(inputpath))[0]
    txt = font.Font(family="SimSun", size=44)
    space = 1/6*txt.measure('M')
    indent = txt.measure('汉字')
    indent_flag = True
    newline_flag = False
    width = 0
    title = jieba.lcut(title)
    doc.append(NoEscape(r'{\indent\zihao{0}\songti\textbf{'))
    for index,word in enumerate(title):
        if re.match('[\u4e00-\u9fa5]', word):
            if newline_flag and (title[index+1]!='\n'):
                doc.append('\n')
                newline_flag = False
            pin = ' '.join(lazy_pinyin(word, style=1))
            doc.append(NoEscape(fr'\ruby{{{word}}}{{\LARGE {pin}}}\,'))
            width += txt.measure(word)+space
        elif word == '\n':
            break
        else:
            if word == '^':
                doc.append(NoEscape(r'\ '))
                width += 1/3*txt.measure('M')
            else:
                doc.append(word)
                width += txt.measure(word)
            if newline_flag and (title[index+1]!='\n'):
                doc.append('\n')
                newline_flag = False
        if indent_flag:
            if width > 570 - indent:
                width = 0
                indent_flag = False
                newline_flag = True
        else:
            if width > 570:
                newline_flag = True
                width = 0
    doc.append(NoEscape(r'}}\newline\newline'))
    

def makesection(doc, split, firstline_flag, section_number=None):
    tkinter.Frame().destroy()
    txt = font.Font(family="SimSun", size=26)
    space = 1/6*txt.measure('M')
    newline_flag = False
    width = 0
    if firstline_flag is False:
        doc.append(NoEscape(r'\newline'))
        firstline_flag = False
    if section_number:
        doc.append(NoEscape(fr'{{\noindent\zihao{{1}}\songti\textbf{{{section_number}.'))
    else:
        doc.append(NoEscape(r'{\noindent\zihao{1}\songti\textbf{'))
    for index,word in enumerate(split[1:]):
        if re.match('[\u4e00-\u9fa5]', word):
            if newline_flag and (split[index+1]!='\n'):
                doc.append('\n')
                newline_flag = False
            pin = ' '.join(lazy_pinyin(word, style=1))
            doc.append(NoEscape(fr'\ruby{{{word}}}{{\large {pin}}}\,'))
            width += txt.measure(word)+space
        elif word == '\n':
            break
        else:
            if word == '^':
                doc.append(NoEscape(r'\ '))
                width += 1/3*txt.measure('M')
            else:
                doc.append(word)
                width += txt.measure(word)
            if newline_flag and (split[index+1]!='\n'):
                doc.append('\n')
                newline_flag = False
        if width > 580:
            newline_flag = True
            width = 0
    doc.append(NoEscape(r'}}\newline\newline'))
    
             
@click.command()
@click.option('-p', '--path', default='text.txt', help='path of the input file')
@click.option('-t', '--title', is_flag=True, help='use file name as title')
@click.option('--tex', is_flag=True, help='return tex file instead of pdf file')
@click.option('--font_size', default=18)
@click.option('--line_space', default=20)
@click.option('--pinyin_size', default=3, help='integer from 0-9')
@click.option('--split_space', default=2, help='integer from 0-5')
def create(path, tex, title, font_size, line_space, pinyin_size, split_space):
    pinyin_size_list = ('tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge')
    split_space_list = ((0, ''), (1/6, '\,'), (2/7, '\;'), (1/3, '\ '), (1, '\quad'), (2, '\qquad'))
    inputpath = os.path.realpath(os.path.expanduser(path))
    if os.path.isfile(inputpath) is False:
        click.echo('ERROR: File Not Found')
        return
    outputpath = os.path.splitext(inputpath)[0]
    geometry = {'paper': 'a4paper',
                'left': '2cm',
                'right': '2cm',
                'top': '2cm',
                'bottom': '2cm'
    }
    doc = Document(default_filepath=outputpath, documentclass='ctexart', geometry_options=geometry)
    doc.packages.append(Package('ruby'))
    doc.packages.append(Package('fontspec'))
    doc.preamble.append(Command('setCJKmainfont', 'KaiTi'))
    doc.preamble.append((Command('setmainfont', 'SimSun')))
    doc.append(NoEscape(fr'\fontsize{{{font_size}pt}}{{{line_space}pt}}\selectfont'))
    if title: maketitle(doc, inputpath)
    generate(doc, inputpath, font_size, pinyin_size_list[pinyin_size], split_space_list[split_space])
    if tex: doc.generate_tex()
    else: doc.generate_pdf(compiler='xelatex')
    
    
if __name__ == '__main__':
    create()