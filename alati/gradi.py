#!/usr/bin/env python3
"""rjecnik-XX.tsv -> rjecnik-XX.jsonl (za program).

Pokretanje iz korijena repoa:  python3 alati/gradi.py fr   (ili bez argumenta = svi jezici)
TSV je izvor istine; JSONL se uvijek gradi iz njega i ne uređuje se ručno.
"""
import csv, json, os, sys

KORIJEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def jezici():
    return sorted(d for d in os.listdir(KORIJEN)
                  if os.path.isfile(os.path.join(KORIJEN, d, f'rjecnik-{d}.tsv')))


def gradi(jezik):
    tsv = os.path.join(KORIJEN, jezik, f'rjecnik-{jezik}.tsv')
    out = os.path.join(KORIJEN, jezik, f'rjecnik-{jezik}.jsonl')
    with open(tsv, encoding='utf-8', newline='') as f:
        retci = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    with open(out, 'w', encoding='utf-8') as f:
        for r in retci:
            z = {'razina': int(r['razina'][1:])}
            for k, v in r.items():
                if k != 'razina' and v:
                    z[k] = v
            f.write(json.dumps(z, ensure_ascii=False) + '\n')
    print(f'{jezik}: {len(retci)} riječi -> {os.path.relpath(out, KORIJEN)}')


if __name__ == '__main__':
    for j in (sys.argv[1:] or jezici()):
        gradi(j)
