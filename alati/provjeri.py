#!/usr/bin/env python3
"""Provjera rječnika: stupci, prazna polja, razine, vrste, duplikati, broj riječi po razini.

Pokretanje iz korijena repoa:  python3 alati/provjeri.py fr   (bez argumenta = svi jezici)
Piše XX/IZVJESTAJ.md. Izlaz 1 ako ima grešaka.
Greška: krivi stupci, prazno polje, nepoznata razina/vrsta, ista riječ dvaput.
Upozorenje: broj riječi u razini odstupa od koncepta više od 10 %.
"""
import csv, os, re, sys
from collections import Counter, defaultdict

KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VRSTE = {
    'im': 'imenica', 'gl': 'glagol', 'pr': 'pridjev', 'pril': 'prilog', 'zam': 'zamjenica',
    'prij': 'prijedlog', 'vez': 'veznik', 'broj': 'broj', 'izraz': 'izraz', 'usk': 'uzvik',
    'čest': 'čestica', 'čl': 'član', 'afiks': 'afiks (tvorba riječi)',
}
# drugi stupac prijevoda: engleski za sve, hrvatski za engleski tečaj
PRIJEVOD = {'en': 'hr'}


def kljuc(rijec):
    """Riječ bez napomene u zagradi, za traženje duplikata (član ostaje: la poste ≠ le poste)."""
    return re.sub(r'\s*\(.*?\)', '', rijec).strip().lower()


def provjeri(jezik):
    d = os.path.join(KORIJEN, jezik)
    stupci = ['razina', 'tema', jezik, PRIJEVOD.get(jezik, 'en'), 'vrsta']
    with open(os.path.join(d, f'razine-{jezik}.tsv'), encoding='utf-8') as f:
        razine = {r['razina']: r for r in csv.DictReader(f, delimiter='\t')}
    with open(os.path.join(d, f'rjecnik-{jezik}.tsv'), encoding='utf-8', newline='') as f:
        citac = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        zaglavlje = citac.fieldnames
        retci = list(citac)

    greske, upoz = [], []
    if zaglavlje[:len(stupci)] != stupci:
        greske.append(f'zaglavlje {zaglavlje} umjesto {stupci}')
    vidjeno = defaultdict(list)
    po_razini, po_vrsti = Counter(), Counter()
    for i, r in enumerate(retci, start=2):
        for s in stupci:
            if not (r.get(s) or '').strip():
                greske.append(f'redak {i}: prazno polje „{s}“')
        if r['razina'] not in razine:
            greske.append(f'redak {i}: nepoznata razina {r["razina"]}')
        elif r['tema'] != razine[r['razina']]['tema']:
            greske.append(f'redak {i}: tema „{r["tema"]}“ ne odgovara razini {r["razina"]}')
        if r['vrsta'] not in VRSTE:
            greske.append(f'redak {i}: nepoznata vrsta „{r["vrsta"]}“')
        vidjeno[(kljuc(r[jezik]), r['vrsta'])].append(f'{i} ({r["razina"]})')
        po_razini[r['razina']] += 1
        po_vrsti[r['vrsta']] += 1
    for (k, v), gdje in vidjeno.items():
        if len(gdje) > 1:
            greske.append(f'duplikat „{k}“ ({v}): retci {", ".join(gdje)}')

    tablica = ['| Razina | Tema | Koncept | Ima | |', '|---|---|---:|---:|---|']
    for rz, info in razine.items():
        cilj, ima = int(info['broj']), po_razini[rz]
        ok = abs(ima - cilj) <= max(2, cilj * 0.10)
        if not ok:
            upoz.append(f'{rz}: {ima} riječi, koncept {cilj}')
        tablica.append(f'| {rz} | {info["tema"]} | {cilj} | {ima} | {"✓" if ok else "⚠"} |')
    ukupno_cilj = sum(int(x['broj']) for x in razine.values())
    tablica.append(f'| **ukupno** | | **{ukupno_cilj}** | **{len(retci)}** | |')

    izv = [f'# Izvještaj provjere — {jezik}', '',
           f'Riječi: **{len(retci)}** · greške: **{len(greske)}** · upozorenja: **{len(upoz)}**', '',
           '## Po razinama', ''] + tablica + ['', '## Po vrstama', '',
           '| Vrsta | Broj |', '|---|---:|'] + \
          [f'| {VRSTE[v]} | {n} |' for v, n in po_vrsti.most_common() if v in VRSTE]
    if greske:
        izv += ['', '## Greške', ''] + [f'- {g}' for g in greske]
    if upoz:
        izv += ['', '## Upozorenja', ''] + [f'- {u}' for u in upoz]
    with open(os.path.join(d, 'IZVJESTAJ.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(izv) + '\n')
    print(f'{jezik}: {len(retci)} riječi, {len(greske)} grešaka, {len(upoz)} upozorenja')
    for g in greske[:30]:
        print('  GREŠKA', g)
    for u in upoz:
        print('  pazi  ', u)
    return not greske


if __name__ == '__main__':
    jez = sys.argv[1:] or sorted(x for x in os.listdir(KORIJEN)
                                 if os.path.isfile(os.path.join(KORIJEN, x, f'rjecnik-{x}.tsv')))
    sys.exit(0 if all([provjeri(j) for j in jez]) else 1)
