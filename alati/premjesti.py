#!/usr/bin/env python3
"""Premjesti riječ u drugu razinu (uskladi rječnik s kralježnicom).

Pokretanje iz korijena repoa:  python3 alati/premjesti.py fr "parce que" L3 [riječ razina …]
Riječ se traži točno u stupcu jezika; tema se uzima iz razine-XX.tsv; redak ide na kraj
bloka ciljne razine. Nakon premještanja pokrenuti gradi.py i provjeri.py.
"""
import csv, os, sys

KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def premjesti(jezik, parovi):
    tsv = os.path.join(KORIJEN, jezik, f'rjecnik-{jezik}.tsv')
    with open(tsv, encoding='utf-8', newline='') as f:
        r = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        zaglavlje, *retci = list(r)
    with open(os.path.join(KORIJEN, jezik, f'razine-{jezik}.tsv'), encoding='utf-8') as f:
        teme = {red['razina']: red['tema'] for red in csv.DictReader(f, delimiter='\t')}
    stupac = zaglavlje.index(jezik)
    for rijec, razina in parovi:
        nadeno = [i for i, x in enumerate(retci) if x[stupac] == rijec]
        if len(nadeno) != 1:
            sys.exit(f'{jezik}: „{rijec}“ nađeno {len(nadeno)} puta')
        red = retci.pop(nadeno[0])
        stara = red[0]
        red[0], red[1] = razina, teme[razina]
        n = int(razina[1:])
        mjesto = max((i for i, x in enumerate(retci) if int(x[0][1:]) <= n), default=-1) + 1
        retci.insert(mjesto, red)
        print(f'{jezik}: {rijec}  {stara} -> {razina}')
    with open(tsv, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\', lineterminator='\n')
        w.writerow(zaglavlje)
        w.writerows(retci)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 3 or len(a) % 2 == 0:
        sys.exit(__doc__)
    premjesti(a[0], list(zip(a[1::2], a[2::2])))
