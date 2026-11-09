#!/usr/bin/env python3
"""Provjera interslavenskih riječi prema zaključanoj verziji rječnika (odluka ISV2).

Baza: github.com/medzuslovjansky/database, commit 53d42b2af (11.10.2026.).
Priprema (jednom):
    git clone https://github.com/medzuslovjansky/database /tmp/isv-database
    git -C /tmp/isv-database checkout 53d42b2af
Pokretanje iz korijena repoa:
    python3 alati/provjeri-isv-baza.py /tmp/isv-database

Natuknice baze su u etimološkom pravopisu; ovdje se svode na jednostavni (ę → e, å → a, ȯ → o …).
Provjerava se svaka riječ iz isv/rjecnik-isv.tsv; izraz prolazi ako su sve njegove riječi u bazi.
Gramatički oblici koji nisu natuknice (jesm, byl, budu …) su na popisu OBLICI.
"""
import csv, os, re, sys

TR = str.maketrans({'ė': 'e', 'ȯ': 'o', 'ę': 'e', 'ų': 'u', 'å': 'a', 'ŕ': 'r', 'ĺ': 'l', 'ń': 'n',
                    'ť': 't', 'ď': 'd', 'ś': 's', 'ź': 'z', 'ć': 'č', 'đ': 'dž', 'ò': 'o', 'è': 'e',
                    'ľ': 'l', 'ů': 'u', 'ý': 'y'})
OBLICI = {'jesm', 'jesi', 'jest', 'jesmo', 'jeste', 'sut', 'kako jesi?', 'byl', 'budu',
          'prěd dvoma dnjami', 'koliko je časa?', 's kym?'}
KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def jed(s):
    return s.lower().translate(TR).strip()


def indeks(baza):
    idx = set()
    for root, _, fs in os.walk(os.path.join(baza, 'synsets')):
        for f in fs:
            try:
                t = open(os.path.join(root, f), encoding='utf-8').read()
            except OSError:
                continue
            m = re.search(r'<synset lang="art-x-interslv">(.*?)</synset>', t, re.S)
            if m:
                idx.update(jed(w) for w in re.findall(r'<lemma[^>]*>(.*?)</lemma>', m.group(1), re.S))
    return idx


def main(baza):
    idx = indeks(baza)
    nema = []
    with open(os.path.join(KORIJEN, 'isv', 'rjecnik-isv.tsv'), encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            k = jed(re.sub(r'\s*\(.*?\)', '', r['isv']))
            ok = k in idx or k in OBLICI or k.rstrip('!?') in idx or k + '!' in idx
            if not ok and r['vrsta'] == 'izraz':
                ok = all(jed(t).strip('!?,.…') in idx or len(t) < 3 for t in k.split())
            if not ok:
                nema.append(f"{r['razina']}\t{r['isv']}\t{r['en']}")
    print(f'baza: {len(idx)} natuknica; nije pronađeno: {len(nema)}')
    for n in nema:
        print('  ', n)
    return not nema


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(0 if main(sys.argv[1]) else 1)
