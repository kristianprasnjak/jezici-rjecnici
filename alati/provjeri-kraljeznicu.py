#!/usr/bin/env python3
"""Provjera rječnika prema kralježnici tečaja.

Pokretanje iz korijena repoa:  python3 alati/provjeri-kraljeznicu.py fr   (bez argumenta = svi jezici
koji imaju XX/kraljeznica-XX.tsv)
kraljeznica-XX.tsv (stupci: rijec, razina, izvor) je strojni oblik tablica iz
croland/jezici-plan/XX/XX-gramaticka-kraljeznica.md (nepravilni glagoli, veznici, zamjenice).
Greška: riječ je u rječniku na drugoj razini. Upozorenje: riječi nema u rječniku.
Izlaz 1 ako ima grešaka.
"""
import csv, os, re, sys

KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cisto(s):
    return re.sub(r'\s*\(.*?\)', '', s).strip()


def provjeri(jezik):
    k = os.path.join(KORIJEN, jezik, f'kraljeznica-{jezik}.tsv')
    with open(os.path.join(KORIJEN, jezik, f'rjecnik-{jezik}.tsv'), encoding='utf-8', newline='') as f:
        rj = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    razine = {}
    for r in rj:
        razine.setdefault(cisto(r[jezik]), set()).add(r['razina'])
    greske, upoz = [], []
    with open(k, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            w, raz = cisto(r['rijec']), r['razina']
            ima = razine.get(w)
            if not ima:
                upoz.append(f'„{w}“ ({raz}, {r["izvor"]}) nije u rječniku')
            elif raz not in ima:
                greske.append(f'„{w}“: kralježnica {raz}, rječnik {", ".join(sorted(ima))}')
    for g in greske:
        print(f'{jezik} GREŠKA: {g}')
    for u in upoz:
        print(f'{jezik} upozorenje: {u}')
    print(f'{jezik}: kralježnica — {len(greske)} grešaka, {len(upoz)} upozorenja')
    return not greske


if __name__ == '__main__':
    jez = sys.argv[1:] or sorted(d for d in os.listdir(KORIJEN)
                                 if os.path.isfile(os.path.join(KORIJEN, d, f'kraljeznica-{d}.tsv')))
    sys.exit(0 if all([provjeri(j) for j in jez]) else 1)
