#!/usr/bin/env python3
"""Provjera Blobbyjeva glasa: zna li polaznik svaku riječ ciljnog jezika koju Blobby kaže?

Uporaba:  python3 alati/provjeri-blobby.py XX putanja/blobby-glas-XX.md putanja/XX-gramaticka-kraljeznica.md

Pravilo za blobby-glas-XX.md: *kurziv* je uvijek i samo ciljni jezik (kao u deutsch/blobby-glas-de.md).
Razina se uzima iz naslova „## L<n> …“ ili iz prvog ili drugog stupca retka tablice („| L<n> |“).
Odjeljak „## …“ bez razine se ne provjerava (osim redaka tablice s razinom). Jedno slovo, skup od dva slova kojeg nema
nigdje u rječniku (*zz*) i dio riječi s crticom (*-ent*) se ne provjeravaju. Redak „Ručno provjereno: *oblik*, *oblik*“ prihvaća oblike koje
rječnik ne navodi (npr. futur), nakon što ih je čovjek provjerio.
Riječ je u redu ako je u rječniku na razini ≤ n (bilo koji stupac oblika) ili u zamrznutoj frazi
iz odj. 6 kralježnice s „Od“ ≤ n. Ostalo se ispisuje kao upozorenje za ručnu provjeru
(npr. oblik koji rječnik ne navodi). Izlazni kod je 1 ako ima upozorenja.
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

KORIJEN = Path(__file__).resolve().parent.parent
KURZIV = re.compile(r"(?<![*\w])\*(?!\*)([^*\n]+?)\*(?![*\w])")
RIJEC = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)
RAZ = re.compile(r"^L?(\d{1,2})$")
PRESKOČI = {"razina", "tema", "en", "hr", "vrsta", "rod", "vid", "prelaznost", "deklinacija",
            "konjugacija", "gl_skupina", "pomocni"}


def tokeni(tekst):
    tekst = unicodedata.normalize("NFC", tekst.lower().replace("’", "'"))
    out = []
    for dio in re.split(r"[' ]", tekst):
        out += [t for t in RIJEC.findall(dio) if t]
    return out


def razina(s):
    m = re.search(r"L(\d{1,2})", s or "")
    return int(m.group(1)) if m else None


def rjecnik(kod):
    po_razini = {}
    with open(KORIJEN / kod / f"rjecnik-{kod}.tsv", encoding="utf-8") as f:
        for red in csv.DictReader(f, delimiter="\t"):
            n = razina(red["razina"])
            stupci = [v for k, v in red.items() if k not in PRESKOČI and v]
            if kod == "en":
                stupci.append(red["en"])
            for v in stupci:
                for t in tokeni(re.sub(r"\([^)]*\)", " ", v)):
                    po_razini[t] = min(po_razini.get(t, 99), n)
    return po_razini


def fraze(kraljeznica):
    po_razini = {}
    unutra = False
    for red in Path(kraljeznica).read_text(encoding="utf-8").splitlines():
        if red.startswith("## "):
            unutra = "fraz" in red.lower() or "zamrznut" in red.lower()
            continue
        if unutra and red.startswith("|"):
            stupci = [s.strip() for s in red.strip("|").split("|")]
            if len(stupci) < 2:
                continue
            n = razina(stupci[1])
            if n is None:
                continue
            for k in KURZIV.findall(stupci[0]):
                for t in tokeni(k):
                    po_razini[t] = min(po_razini.get(t, 99), n)
    return po_razini


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    kod, glas, kralj = sys.argv[1:]
    rj, fr = rjecnik(kod), fraze(kralj)
    trenutna, upozorenja, ukupno = None, [], 0
    retci = Path(glas).read_text(encoding="utf-8").splitlines()
    rucno = set()
    for red in retci:
        if red.startswith("Ručno provjereno:"):
            for k in KURZIV.findall(red):
                rucno.update(tokeni(k))
    for br, red in enumerate(retci, 1):
        if red.startswith("Ručno provjereno:"):
            continue
        if red.startswith("## "):
            m = RAZ.match(red.split()[1]) if len(red.split()) > 1 else None
            trenutna = int(m.group(1)) if m else None
            continue
        n = trenutna
        if red.startswith("|"):
            for stupac in red.strip("|").split("|")[:2]:
                m = re.fullmatch(r"L(\d{1,2})", stupac.strip().strip("*"))
                if m:
                    n = int(m.group(1))
                    break
        if n is None:
            continue
        for k in KURZIV.findall(red):
            if k.startswith("-"):
                continue
            for t in tokeni(k):
                if len(t) < 2 or t in rucno or (len(t) == 2 and t not in rj and t not in fr):
                    continue  # slovo ili skup slova (*zz*, *ch*), ne riječ
                ukupno += 1
                ok = min(rj.get(t, 99), fr.get(t, 99))
                if ok > n:
                    gdje = f"rječnik L{rj[t]}" if t in rj else ("fraza L%d" % fr[t] if t in fr else "nema")
                    upozorenja.append(f"  r.{br} L{n}: „{t}“ ({gdje}) u *{k}*")
    print(f"{kod}: {ukupno} riječi ciljnog jezika, upozorenja: {len(upozorenja)}")
    print("\n".join(upozorenja))
    sys.exit(1 if upozorenja else 0)


if __name__ == "__main__":
    main()
