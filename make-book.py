#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Mallam-Town-BOOK.html — the complete paginated book mockup.

Source of truth:
    Mallam-Town-Draft-Chapters.md   the 15 chapters
    Mallam-Town-Front-Matter.md     half title .. names
    Mallam-Town-Glossary.md         Parts A-D
    Mallam-Town-Activities.md       questions, quiz, writing, activities
    art-ch01..15.jpg                chapter illustrations
    cover-gate.jpg                  cover (Option B)
    map-l.jpg / map-r.jpg           endpapers

Run:  python3 make-book.py
"""
import base64, html, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
CSS  = open(os.path.join(BASE, 'book-css.txt'), encoding='utf-8').read()

# ───────────────────────────── helpers ─────────────────────────────
def uri(fn):
    with open(os.path.join(BASE, fn), 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

def md(t):
    """escape, then apply the book's two inline styles"""
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=re.S)
    t = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', t, flags=re.S)
    return t

def P(t, cls='', raw=False):
    c = f' class="{cls}"' if cls else ''
    t = t.replace('\n', ' ')
    return f'<p{c}>{t if raw else md(t)}</p>'

def wc(htmls):
    t = re.sub(r'<[^>]+>', ' ', ''.join(htmls))
    t = re.sub(r'http\S+', '', t)
    return len(t.split())

# ───────────────────────────── page list ─────────────────────────────
pages = []          # list of dicts: side, html, folio
folio_n = [1]

def push(side, body, folio=True, cls=''):
    """append a page; folio=True numbers it, False leaves it blank"""
    f = ''
    if folio:
        n = folio_n[0]; folio_n[0] += 1
        f = f'<div class="fol">{n}</div>'
    pages.append({'side': side, 'html': body, 'folio': f})

def blank(side):
    push(side, '', folio=False)

def next_side():
    return 'left' if len(pages) % 2 == 0 else 'right'

# ───────────────────────────── assets ─────────────────────────────
ART   = {i: uri(f'art-ch{i:02d}.jpg') for i in range(1, 16)}
COVER = uri('cover-gate.jpg')
MAPL  = uri('map-l.jpg')
MAPR  = uri('map-r.jpg')

# ───────────────────────────── chapters ─────────────────────────────
def load_chapters():
    s = open(os.path.join(BASE, 'Mallam-Town-Draft-Chapters.md'), encoding='utf-8').read()
    s = s.split('## Continuity notes')[0]
    parts = re.split(r'\n# Chapter (\d+) — ', s)
    out = []
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        body = re.sub(r'\*\s*\(~?[\d,]+\s*words?\)\s*\*', '', parts[i + 1])
        lines = body.strip().split('\n')
        title = lines[0].strip()
        paras = [p.strip() for p in '\n'.join(lines[1:]).split('\n\n') if p.strip()]
        out.append((n, title, [p for p in paras if p != '---']))
    return out

CH = load_chapters()

# ───────────────────────────── pagination ─────────────────────────────
FULL, OPEN = 264, 126          # measured capacity at 17px / 23.6px

def split_long(paras, cap):
    out = []
    for p in paras:
        if len(p.split()) <= cap:
            out.append(p); continue
        cur = ''
        for snt in re.split(r'(?<=[.!?"])\s+', p):
            if cur and len((cur + ' ' + snt).split()) > cap:
                out.append(cur); cur = snt
            else:
                cur = (cur + ' ' + snt).strip()
        if cur: out.append(cur)
    return out

def flow(paras, cap):
    out, cur, n = [], [], 0
    for p in paras:
        w = len(p.split())
        if cur and n + w > cap:
            out.append(cur); cur, n = [], 0
        cur.append(p); n += w
    if cur: out.append(cur)
    return out

NUMW = {1:'One',2:'Two',3:'Three',4:'Four',5:'Five',6:'Six',7:'Seven',8:'Eight',
        9:'Nine',10:'Ten',11:'Eleven',12:'Twelve',13:'Thirteen',14:'Fourteen',15:'Fifteen'}

# ══════════════════════════ FRONT MATTER ══════════════════════════
push('right', '<div class="halfttl">MALLAM TOWN</div>', folio=False)

push('left',
     '<div class="epi">'
     + P('“Everything in this town happens in the dark,” she said. '
         '“Let us have this one in the light, for once.”')
     + '<p class="attr">— Nene</p></div>', folio=False)

push('right',
     '<div class="ttlpg"><h1>MALLAM TOWN</h1>'
     '<div class="by">by</div><div class="au">Lecturer Sam</div>'
     '<div class="im">Illustrated by [ILLUSTRATOR]<br>with a map by [CARTOGRAPHER]</div>'
     '<div class="publ">[PUBLISHER] · [CITY]</div></div>', folio=False)

CR = ['MALLAM TOWN — A Junior High School edition',
      'First published in Ghana in 2026 by [PUBLISHER]',
      'Text copyright © 2026 Lecturer Sam',
      'The right of Lecturer Sam to be identified as the author of this work has been asserted '
      'in accordance with the Copyright Act, 2005 (Act 690).',
      'All rights reserved. No part of this publication may be reproduced, stored in a retrieval '
      'system, or transmitted in any form or by any means — electronic, mechanical, photocopying, '
      'recording or otherwise — without the prior written permission of the publisher, except for '
      'the quotation of brief passages in criticism and review, and except for the copying of the '
      'discussion questions and activities by a teacher for use in their own classroom, which is '
      'permitted without charge.',
      'A catalogue record for this book is available from the Ghana Library Authority.',
      'ISBN 978-[ ]-[ ]-[ ]-[ ]',
      'Printed and bound in Ghana by [PRINTER]',
      'Mallam Town is a real place in the Greater Accra Region. Every person, family and event in '
      'this book is invented, and no resemblance to any person living or dead is intended.']
push('left', '<div class="cr">' + ''.join(P(x) for x in CR) + '</div>', folio=False)

push('right', '<div class="ded">'
     + P('For the ones who were in the room<br>and were never asked.', raw=True)
     + '</div>', folio=False)

NOTE = [
 'Mallam Town is a story for readers of about twelve to fifteen — the Junior High School years, and '
 'the upper end of primary. It is set in a real township on the road out of Accra, and nearly all of '
 'it happens within walking distance of one compound house.',
 'The reading level. The book is fifteen chapters and about 15,600 words, with one illustration '
 'opening each chapter. Sentences average between nine and fifteen words. The measured reading level '
 'sits at Flesch–Kincaid 4.3, which means a pupil in JHS 1 should be able to read it independently '
 'and a weaker reader in JHS 3 comfortably. Nothing in the book requires a dictionary, but there is a '
 'glossary at the back for the Ghanaian words, the harder English, and the names.',
 'What the book is careful about. This is a story about a man who is wrongly accused and a woman who '
 'disappears, and both of those could have been written brutally. They have not been. There is no '
 'sexual content in this book. There is no description of the injuries people receive, beyond what is '
 'needed to understand what happened. There is no mob, and nobody in this story is hurt by a crowd. '
 'When the worst thing in the book happens, it is described by its sound and by the faces of the '
 'people watching it, and not by anything the reader is made to look at.',
 'A note on Nene. Nene is a traditional herbalist — a healer who treats people with plants, and who '
 'has been doing it for forty years. This book uses the words herbs, medicine, and her knowledge. It '
 'does not use fetish, juju, witch, charms, magic, or spirits, about her or about anyone else. This '
 'is a deliberate choice, and it is worth explaining to a class: those words are used carelessly '
 'about traditional healers, and none of them are needed to tell this story. Nene is not mysterious. '
 'She is old, her knees hurt, she is paid in yam, and she is the most competent person in the book.',
 'The two questions the book asks. The first is: what is the difference between keeping the peace and '
 'keeping quiet? Kwame spends twenty years being called the Peacemaker before he finds out that they '
 'are not the same thing. The second is: whose knowledge counts? The police have a ledger. Nene has '
 'forty years of listening. The book’s answer is that you need both, and that a town which only '
 'believes one of them will lose people.',
 'How to use this book in class. There are discussion questions at the back, arranged in four parts '
 'of three or four chapters each, mixing comprehension with questions that have more than one good '
 'answer. There are seven writing tasks — including the radio correction that Chief Inspector Nanfuri '
 'has to read out, and the letter that Maame Adjoa takes to the police station. There is a map on the '
 'endpapers; pupils can mark on it where each chapter happens. And there is a glossary, which '
 'includes a table of the Akan day-names — every major character in this book is named for the day of '
 'the week they were born, and working out which day is a good first lesson.',
 'A note on the English. The dialogue in this book is written in the English that Ghanaians actually '
 'speak, and the narration is written in standard Ghanaian English. Neither is a mistake, and neither '
 'is a deficiency. Both are on the page on purpose.']
NCAP = 330
for i, blk in enumerate(flow(NOTE, NCAP)):
    push('right' if i == 0 else next_side(),
         ('<h3>Note on this edition</h3>' if i == 0 else '')
         + '<div class="fm">' + ''.join(P(x) for x in blk) + '</div>')

CAST = [
 ('Kwame Asante', 'forty-four, a taxi driver. Twenty years at the rank in Mallam Town. Everyone calls '
                  'him the Peacemaker, because he is the man people bring their small quarrels to.'),
 ('Mansa Asante', 'his wife. Thirty-eight, and deliberate in everything she does.'),
 ('Nene', 'seventy-one. A traditional herbalist. She has bad knees, a stick, a basket, and a mortar '
          'worn smooth on one side.'),
 ('Chief Inspector Nanfuri', 'head of the Mallam Town Police Post. In his forties, and tired in the '
                             'way of a man with too many open files.'),
 ('Inspector Adzo Mensah', 'about thirty. She has read every page of a file nobody asked her to read.'),
 ('Kwabena Dapaah', 'fifty-four. A carpenter, built like the thing he works with. He comes to Nene '
                    'about his hands.'),
 ('Yaw Sarpong', 'fifty-six. A landlord. He owns the houses behind the cemetery — the ones that have '
                 'been going up for four years and have never got past the first floor.'),
 ('Papa Kofi and Mr. Tee', 'drivers at the rank.'),
 ('Maame Adjoa and Maame Akua', 'two mothers. Their sons stopped coming home.'),
 ('Efua Nanfuri', 'twenty-four. She does not appear in this book, and the whole of it happens because '
                  'of her.'),
 ('The Old Woman on the veranda', 'she has not walked past her own gate in two years.')]
cast_html = ''.join(f'<p class="ge"><b>{n}.</b> {md(d)}</p>' for n, d in CAST)
push('right', '<h3>The people in this book</h3>' + cast_html)

DAYS = [('Sunday','Kwesi, Kwasi','Akosua'), ('Monday','Kojo, Kwadwo','Adwoa, Adjoa, Adzo'),
        ('Tuesday','Kwabena','Abena'), ('Wednesday','Kwaku, Kweku','Akua'),
        ('Thursday','Yaw, Ekow','Yaa'), ('Friday','Kofi','Afua, Efua'), ('Saturday','Kwame','Ama')]
NAMES = [
 'Most of the people in this book have Akan names, and an Akan name often tells you the day of the '
 'week a person was born.',
 'So Kwame was born on a Saturday, Kwabena on a Tuesday, and Kofi on a Friday. Adjoa and Adzo are the '
 'same name in two different languages. Ekow and Yaw were both born on a Thursday.',
 'Nene is not a day-name. It is a Ga-Dangme word, and it is a title of respect — for a chief, for a '
 'queenmother, or for any elder. In this book it is not really her name. It is what you call an old '
 'woman you are about to ask a favour of.',
 'Mansa means “of three” — the name given to a third-born girl.']
tbl = ('<table class="toc2"><tr><th>Born on</th><th>A boy is called</th><th>A girl is called</th></tr>'
       + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in DAYS) + '</table>')
push('right', '<h3>A note on the names</h3>' + P(NAMES[0]) + tbl
     + ''.join(P(x) for x in NAMES[1:]))

# ══════════════════════════ THE CHAPTERS ══════════════════════════
folio_n[0] = 1
for n, title, paras in CH:
    if len(pages) % 2 == 0:
        blank('left')
    paras = split_long(paras, FULL)
    op, n0, rest = [], 0, list(paras)
    while rest and n0 < OPEN:
        w = len(rest[0].split())
        if op and n0 + w > OPEN: break
        op.append(rest.pop(0)); n0 += w
    panel = (f'<div class="panel"><img src="{ART[n]}" alt=""></div>' if n in ART
             else f'<div class="panel pend"><span>illustration {n}</span></div>')
    head = (f'<div class="chnum">Chapter {NUMW[n]}</div><h2 class="chttl">{title}</h2>'
            f'<div class="rule"></div>')
    body = ''.join(P(x, 'first') if i == 0 else P(x) for i, x in enumerate(op))
    if n == 1:
        body = body.replace('<p class="first">', '<p class="first"><span class="dc">M</span>', 1)
        body = body.replace('</span>Mallam Town woke', '</span>allam Town woke', 1)
    push('right', panel + head + body)
    for pg in flow(rest, FULL):
        push(next_side(), ''.join(P(x, 'first') if i == 0 else P(x) for i, x in enumerate(pg)))

# ══════════════════════════ GLOSSARY ══════════════════════════
def load_glossary():
    s = open(os.path.join(BASE, 'Mallam-Town-Glossary.md'), encoding='utf-8').read()
    ents = []
    part = None
    for ln in s.split('\n'):
        if ln.startswith('# Part'):
            part = ln.lstrip('# ').strip()
            ents.append(('head', part)); continue
        m = re.match(r'^\*\*(.+?)\*\*(\s*\([^)]*\))?\s*—\s*(.+)$', ln.strip())
        if m and part:
            w = m.group(1); pron = (m.group(2) or '').strip(); d = m.group(3)
            ents.append(('e', f'<p class="ge"><b>{md(w)}</b> {md(pron)} — {md(d)}</p>'))
    # the day-name table + cast belong to Part C
    return ents

GLOSS = load_glossary()
GH = ('<h3>Glossary</h3><p class="gintro">Part A — words from Ghana. Part B — difficult words. '
      'Part C — the names. Part D — Nene’s medicine. Words are explained the way this book uses '
      'them, not the way a dictionary would.</p>')
GCAP = 380
chunks, cur = [], []
for kind, val in GLOSS:
    if kind == 'head':
        if cur: chunks.append(cur); cur = []
        cur.append(f'<h4 class="qh">{val}</h4>')
    else:
        cur.append(val)
        if wc(cur) > GCAP: chunks.append(cur); cur = []
if cur: chunks.append(cur)
for i, c in enumerate(chunks):
    push(next_side(), (GH if i == 0 else '') + ''.join(c))

# ══════════════════════════ QUESTIONS ══════════════════════════
def load_questions():
    s = open(os.path.join(BASE, 'Mallam-Town-Activities.md'), encoding='utf-8').read()
    s = s.split('# Who said these words')[0]        # stop before the quiz
    out, part = [], None
    for ln in s.split('\n'):
        if ln.startswith('# Part ') or ln == '# The whole book':
            part = ln.lstrip('# ').strip(); out.append(('h', part)); continue
        if ln.startswith('### ') and part and 'JHS edition' not in ln:
            out.append(('s', ln[4:].strip())); continue
        m = re.match(r'^(\d+)\.\s+(.+)$', ln.strip())
        if m and part:
            out.append(('q', f'<p class="qs">{md(m.group(2))}</p>'))
    return out

QS = load_questions()
QCAP = 620
chunks, cur = [], []
for kind, val in QS:
    if kind == 'h':
        if cur: chunks.append(cur); cur = []
        cur.append(f'<h3>{val}</h3>')
    elif kind == 's':
        cur.append(f'<h4 class="qh">{val}</h4>')
    else:
        cur.append(val)
        if wc(cur) > QCAP: chunks.append(cur); cur = []
if cur: chunks.append(cur)
first = True
for c in chunks:
    push(next_side(), ('<h3>Discussion questions</h3>' if first else '') + ''.join(c))
    first = False

# ══════════════════════════ QUIZ ══════════════════════════
s = open(os.path.join(BASE, 'Mallam-Town-Activities.md'), encoding='utf-8').read()
quiz = re.search(r'# Who said these words\?(.*?)### Answers(.*?)\n---', s, re.S)
if quiz:
    qs = re.findall(r'^\d+\.\s+(.+)$', quiz.group(1), re.M)
    ans = re.findall(r'^\d+\.\s+(.+)$', quiz.group(2), re.M)
    q_html = ''.join(f'<li>{md(x)}</li>' for x in qs)
    a_html = ''.join(f'<li>{md(x)}</li>' for x in ans)
    push(next_side(), '<h3>Who said these words?</h3>'
         '<p class="gintro">Ten lines from the book. Write down who says each one, and to whom. '
         'Answers are at the bottom of the page.</p>'
         f'<ol class="qz">{q_html}</ol><h4 class="qh">Answers</h4><ol class="qz ans">{a_html}</ol>')

# ══════════════════════════ THINGS TO WRITE / DO ══════════════════════════
def load_tasks(header):
    """grab a '# Header' section and return [(bold title, body), ...]"""
    s = open(os.path.join(BASE, 'Mallam-Town-Activities.md'), encoding='utf-8').read()
    m = re.search(rf'^# {re.escape(header)}\s*$(.*?)(?=^# |\Z)', s, re.S | re.M)
    blk = m.group(1)
    return re.findall(r'^\d+\.\s+\*\*(.+?)\.\*\*\s*(.+?)(?=\n\d+\.|\Z)', blk, re.S | re.M)

wr = load_tasks('Things to write')
wr_html = ''.join(f'<p class="ge"><b>{md(t)}.</b> {md(re.sub(r"\s+", " ", d).strip())}</p>'
                 for t, d in wr)
push(next_side(), '<h3>Things to write</h3>' + wr_html)

do = load_tasks('Things to do')
do_html = [f'<p class="ge"><b>{md(t)}.</b> {md(re.sub(r"\s+", " ", d).strip())}</p>'
           for t, d in do]
half = (len(do_html) + 1) // 2
for i, grp in enumerate([do_html[:half], do_html[half:]]):
    if not grp: continue
    push(next_side(), f'<h3>Things to do{"" if i == 0 else " (continued)"}</h3>' + ''.join(grp))

# ══════════════════════════ AUTHOR ══════════════════════════
push(next_side(), '<h3>About the author</h3><div class="authbox">[PHOTOGRAPH]</div>'
     '<p class="ge"><b>Lecturer Sam</b> — [about the author note, 45 words, to be supplied.]</p>')

# ══════════════════════════ EMIT ══════════════════════════
if len(pages) % 2 == 1:
    blank('right')

def page_div(p):
    return f'<div class="pg {p["side"]}">{p["html"]}{p["folio"]}</div>'

spreads = []
for i in range(0, len(pages), 2):
    a = page_div(pages[i])
    if i + 1 < len(pages):
        spreads.append(f'<div class="spread">{a}<div class="gut"></div>{page_div(pages[i+1])}</div>')
    else:
        spreads.append(f'<div class="spread">{a}</div>')

BANNER = ('<div class="banner"><b>MALLAM TOWN — complete book mockup.</b> A5, 148 × 210 mm, shown at '
          '4.2 px per mm. Laid out to the design specification: mirrored margins (24 mm inner, '
          '18 mm outer), Georgia 11.5 / 16 pt, chapter openings on rectos with a 106 × 62 mm '
          'illustration panel. Cover: Option B, the half-open gate. All fifteen chapters carry '
          'finished artwork.</div>')

COVERHTML = (f'<div class="tag">Cover</div><div class="coverwrap"><div class="cv">'
             f'<div class="hd"><h1 class="tt">MALLAM<br>TOWN</h1><div class="rl"></div>'
             f'<div class="by">Lecturer Sam</div></div>'
             f'<div class="art"><img src="{COVER}" alt=""></div>'
             f'<div class="pb">Senior Supplementary Reader</div></div></div>')

ENDS = (f'<div class="tag">Front endpapers — the map</div><div class="epwrap">'
        f'<div class="ep"><img src="{MAPL}" alt=""></div><div class="gut"></div>'
        f'<div class="ep"><img src="{MAPR}" alt=""></div></div>')

doc = (f'<!doctype html><html><head><meta charset="utf-8">'
       f'<title>MALLAM TOWN — complete book mockup</title><style>{CSS}</style></head>'
       f'<body><div class="wrap">{BANNER}{COVERHTML}{ENDS}'
       + ''.join(spreads) +
       '</div></body></html>')

out = os.path.join(BASE, 'Mallam-Town-BOOK.html')
open(out, 'w', encoding='utf-8').write(doc)

# ───────────────────────────── report ─────────────────────────────
over = []
for i, p in enumerate(pages):
    h = p['html']
    if re.search(r'<p(\s+class="first")?>', h):
        w = wc([h])
        if 'class="fm"' in h:            cap = 357   # 14.5px front matter
        elif 'class="panel"' in h:       cap = OPEN  # chapter opening
        else:                            cap = FULL  # 17px body text
        if w > cap: over.append((i, w, cap))
print(f"pages: {len(pages)}  |  illustrations: {len(ART)}  |  {len(doc)/1024:.0f} KB")
print("pages over capacity:", over if over else "none")
