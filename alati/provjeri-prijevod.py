#!/usr/bin/env python3
"""Faza C: provjera prijevoda rječnika na jezik sučelja.

Pokretanje iz korijena repoa:  python3 alati/provjeri-prijevod.py fr hr
Datoteka XX/prijevod-SU-XX.tsv (stupci: XX, vrsta, SU) drži prijevod na jezik sučelja SU, jedan redak
po riječi rječnika (ključ = riječ + vrsta). Jezici sučelja su zasebne datoteke (G4: ≈ 10 sučelja),
pa se rječnik iz faze B ne mijenja.
Greška: riječ ili vrsta koje nema u rječniku, prazan prijevod, ista riječ dvaput.
Izvještaj: pokrivenost po razini (koliko riječi razine ima prijevod).
"""
import csv, os, sys
from collections import Counter

KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def provjeri(jezik, su):
    with open(os.path.join(KORIJEN, jezik, f'rjecnik-{jezik}.tsv'), encoding='utf-8', newline='') as f:
        rj = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    razina = {(r[jezik], r['vrsta']): r['razina'] for r in rj}
    p = os.path.join(KORIJEN, jezik, f'prijevod-{su}-{jezik}.tsv')
    with open(p, encoding='utf-8', newline='') as f:
        pr = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    greske, vidjeno, ima = [], Counter(), Counter()
    for i, r in enumerate(pr, start=2):
        k = (r[jezik], r['vrsta'])
        if k not in razina:
            greske.append(f'redak {i}: „{k[0]}“ ({k[1]}) nije u rječniku')
        if not (r.get(su) or '').strip():
            greske.append(f'redak {i}: „{k[0]}“ nema prijevod')
        vidjeno[k] += 1
        if k in razina:
            ima[razina[k]] += 1
    greske += [f'„{k[0]}“ ({k[1]}) {n} puta' for k, n in vidjeno.items() if n > 1]
    ukupno = Counter(razina.values())
    for g in greske:
        print(f'{jezik}-{su} GREŠKA: {g}')
    red = sorted(ukupno, key=lambda x: int(x[1:]))
    print(f'{jezik} → {su}: ' + ' · '.join(f'{z} {ima[z]}/{ukupno[z]}' for z in red))
    print(f'ukupno {sum(ima.values())}/{len(razina)}, grešaka {len(greske)}')
    return not greske


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(0 if provjeri(*sys.argv[1:]) else 1)
