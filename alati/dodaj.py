#!/usr/bin/env python3
"""Dodaj nove riječi u rječnik (popuna praznina koje nađe kralježnica).

Pokretanje iz korijena repoa:  python3 alati/dodaj.py fr nove.tsv
nove.tsv ima zaglavlje s barem stupcima: razina, XX, en (ili hr za engleski), vrsta; ostali stupci
(oblici iz faze B) po potrebi. Tema se uzima iz razine-XX.tsv; redak ide na kraj bloka razine.
Riječ koja već postoji javlja grešku. Nakon dodavanja pokrenuti gradi.py i provjeri.py.
"""
import csv, os, sys

KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dodaj(jezik, datoteka):
    tsv = os.path.join(KORIJEN, jezik, f'rjecnik-{jezik}.tsv')
    with open(tsv, encoding='utf-8', newline='') as f:
        zaglavlje, *retci = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    with open(os.path.join(KORIJEN, jezik, f'razine-{jezik}.tsv'), encoding='utf-8') as f:
        teme = {r['razina']: r['tema'] for r in csv.DictReader(f, delimiter='\t')}
    with open(datoteka, encoding='utf-8', newline='') as f:
        nove = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    stupac = zaglavlje.index(jezik)
    postoje = {r[stupac] for r in retci}
    for n in nove:
        if n[jezik] in postoje:
            sys.exit(f'{jezik}: „{n[jezik]}“ već postoji')
        n['tema'] = teme[n['razina']]
        red = [n.get(s, '') or '' for s in zaglavlje]
        k = int(n['razina'][1:])
        mjesto = max((i for i, x in enumerate(retci) if int(x[0][1:]) <= k), default=-1) + 1
        retci.insert(mjesto, red)
        print(f'{jezik}: + {n[jezik]} ({n["razina"]})')
    with open(tsv, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\', lineterminator='\n')
        w.writerow(zaglavlje)
        w.writerows(retci)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    dodaj(sys.argv[1], sys.argv[2])
