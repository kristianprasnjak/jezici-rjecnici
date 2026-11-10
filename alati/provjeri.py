#!/usr/bin/env python3
"""Provjera rječnika: stupci, prazna polja, razine, vrste, duplikati, broj riječi po razini.

Pokretanje iz korijena repoa:  python3 alati/provjeri.py fr   (bez argumenta = svi jezici)
Piše XX/IZVJESTAJ.md. Izlaz 1 ako ima grešaka.
Greška: krivi stupci, prazno polje, nepoznata razina/vrsta, ista riječ dvaput.
Faza B (neobavezni stupci oblika iza osnovnih): ako stupac postoji, mora biti popunjen za
svoju vrstu riječi i prazan za sve ostale; provjerava se i oblik vrijednosti (vidi OBLICI).
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

# faza B: stupac -> vrste riječi za koje je obavezan (za ostale vrste mora biti prazan).
# Svaki jezik uzima samo stupce koji mu trebaju (vidi README, „Faza B“).
OBLICI = {
    'rod': {'im'}, 'mnozina': {'im'}, 'genitiv': {'im'}, 'deklinacija': {'im', 'pr'},
    'zenski': {'pr'}, 'mnozina_pr': {'pr'}, 'oblici_pr': {'pr'},
    'komparativ': {'pr'}, 'superlativ': {'pr'},
    'gl_skupina': {'gl'}, 'konjugacija': {'gl'}, 'pomocni': {'gl'}, 'particip': {'gl'},
    'prezent': {'gl'}, 'preterit': {'gl'}, 'ing': {'gl'}, 'glavni_oblici': {'gl'}, 'vid': {'gl'},
    'prelaznost': {'gl'},
}
# smije, ali ne mora: sklonjive zamjenice (it *mio → mia, miei / mie*), dodano 10.11.2026.
NEOBAVEZNO = {'zenski': {'zam'}, 'mnozina_pr': {'zam'}}
# dopuštene vrijednosti: stupac -> {jezik ili '*': skup}
VRIJEDNOSTI = {
    'rod': {'*': {'m', 'f', 'm,f'}, 'la': {'m', 'f', 'n', 'm,f'}, 'isv': {'m', 'm.ž', 'f', 'n', 'm,f'}},
    'gl_skupina': {'*': {'1', '2', '3'}},
    'pomocni': {'fr': {'avoir', 'être'}, 'it': {'avere', 'essere'}},
    'konjugacija': {'la': {'1', '2', '3', '3io', '4', 'nepr'}},
    'deklinacija': {'la': {'1', '2', '3', '4', '5', '1-2', 'nesklonjivo'}},
    'vid': {'isv': {'ipf', 'pf', 'ipf,pf'}},
    'prelaznost': {'eo': {'tr', 'ntr', 'tr,ntr'}},
}
PREZENT_LICA = {'pt': 4, 'isv': 2}   # pt: eu · você/ele · nós · vocês/eles; isv: ja · on; ostali: 6
PRETERIT_LICA = {'es': 2, 'pt': 2}   # ja · on (en: jedan oblik, „was / were“)
NEMA = '—'   # oblik se ne koristi (nebrojivo, bezlični glagol …)


def dvorodna(rijec):
    """Broj oblika u stupcu riječi: „le voisin, la voisine“ = 2."""
    return len(re.sub(r'\s*\(.*?\)', '', rijec).split(','))


def provjeri_oblike(jezik, i, r, greske):
    rijec, vrsta = r[jezik], r['vrsta']
    for s, za in OBLICI.items():
        if s not in r:
            continue
        v = (r[s] or '').strip()
        if vrsta in za and not v:
            greske.append(f'redak {i}: „{rijec}“ ({vrsta}) nema „{s}“')
        elif vrsta not in za and v and vrsta not in NEOBAVEZNO.get(s, ()):
            greske.append(f'redak {i}: „{rijec}“ ({vrsta}) ne smije imati „{s}“ (samo {"/".join(sorted(za))})')
        elif v and s in VRIJEDNOSTI:
            dop = VRIJEDNOSTI[s].get(jezik, VRIJEDNOSTI[s].get('*'))
            if dop is not None and v not in dop:
                greske.append(f'redak {i}: {s} „{v}“ ({" / ".join(sorted(dop))})')
    if vrsta == 'im' and r.get('rod') and r.get('mnozina') is not None:
        n = dvorodna(rijec)
        if n == 2 and r['rod'] != 'm,f':
            greske.append(f'redak {i}: „{rijec}“ ima dva oblika, rod mora biti m,f')
        mn = r.get('mnozina') or ''
        dopusteno = {n, 2} if r['rod'] == 'm,f' else {n}   # (m/f): jedan zajednički oblik ili m, ž
        if mn and NEMA not in mn and len(mn.split(',')) not in dopusteno:
            greske.append(f'redak {i}: množina „{mn}“ mora imati {n} oblik(a) kao „{rijec}“')
    if vrsta in ('pr', 'zam') and r.get('mnozina_pr') and r['mnozina_pr'] != NEMA:
        if len(r['mnozina_pr'].split(' / ')) != 2:
            greske.append(f'redak {i}: mnozina_pr „{r["mnozina_pr"]}“ mora biti „m / ž“')
    if vrsta == 'gl':
        if r.get('prezent'):
            lica = PREZENT_LICA.get(jezik, 6)
            f = r['prezent'].split(' · ')
            if len(f) != lica or not all(x.strip() for x in f):
                greske.append(f'redak {i}: prezent mora imati {lica} oblika odvojenih „ · “ ({len(f)})')
        if r.get('preterit') and jezik in PRETERIT_LICA:
            f = r['preterit'].split(' · ')
            if len(f) != PRETERIT_LICA[jezik] or not all(x.strip() for x in f):
                greske.append(f'redak {i}: preterit mora imati {PRETERIT_LICA[jezik]} oblika odvojena „ · “ ({len(f)})')
        go = r.get('glavni_oblici')
        if go and go != NEMA and not 1 <= len(go.split(', ')) <= 3:
            greske.append(f'redak {i}: glavni_oblici „{go}“ (infinitiv[, perfekt[, supin]])')


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
    for s in zaglavlje[len(stupci):]:
        if s not in OBLICI:
            greske.append(f'nepoznat stupac „{s}“ (faza B dopušta: {", ".join(OBLICI)})')
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
        provjeri_oblike(jezik, i, r, greske)
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
    oblici = [s for s in zaglavlje[len(stupci):] if s in OBLICI]

    izv = [f'# Izvještaj provjere — {jezik}', '',
           f'Riječi: **{len(retci)}** · greške: **{len(greske)}** · upozorenja: **{len(upoz)}**', '',
           '## Po razinama', ''] + tablica + ['', '## Po vrstama', '',
           '| Vrsta | Broj |', '|---|---:|'] + \
          [f'| {VRSTE[v]} | {n} |' for v, n in po_vrsti.most_common() if v in VRSTE]
    if oblici:
        izv += ['', '## Faza B — oblici', '', '| Vrsta | Stupci | Popunjeno |', '|---|---|---:|']
        for vr in dict.fromkeys(v for s in oblici for v in sorted(OBLICI[s])):
            st = [s for s in oblici if vr in OBLICI[s]]
            pun = sum(1 for r in retci if r['vrsta'] == vr and all((r[s] or '').strip() for s in st))
            izv.append(f'| {VRSTE[vr]} | {", ".join(st)} | {pun} / {po_vrsti[vr]} |')
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
