#!/usr/bin/env python3
"""Provjera Blobbyjeva glasa: zna li polaznik svaku riječ ciljnog jezika koju Blobby kaže?

Uporaba:  python3 alati/provjeri-blobby.py XX putanja/blobby-glas-XX.md putanja/XX-gramaticka-kraljeznica.md

Pravilo za blobby-glas-XX.md: *kurziv* je uvijek i samo ciljni jezik (kao u deutsch/blobby-glas-de.md).
Razina se uzima iz naslova „## L<n> …“ ili iz prvog ili drugog stupca retka tablice („| L<n> |“).
Odjeljak „## …“ bez razine se ne provjerava (osim redaka tablice s razinom). Jedno slovo, skup od dva slova kojeg nema
nigdje u rječniku (*zz*) i dio riječi s crticom (*-ent*) se ne provjeravaju. Redak „Ručno provjereno: *oblik*, *oblik*“ prihvaća oblike koje
rječnik ne navodi (npr. futur), nakon što ih je čovjek provjerio.
Za isv i eo prihvaćaju se i pravilni oblici kojih u rječniku nema (isv *dobro* od *dobry*; eo *bonan* od *bona*,
*estas* od *esti*, *bone* od *bona*).
Esperanto se uz to rastavlja na korijen, afikse i nastavak (*malbelan* = mal- L2 + bel L2 + -a L2 + -n L3);
razina riječi je najviša razina dijela.
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


def osnove(kod, t):
    """Pravilni oblici koje rječnik ne navodi (isv pridjevi, esperanto): moguće natuknice za token."""
    out = []
    if kod == "isv":
        for nast in ("ogo", "omu", "ymi", "ych", "ym", "oj", "o", "a", "e", "u", "i", "ě"):
            if t.endswith(nast) and len(t) > len(nast) + 2:
                out += [t[: -len(nast)] + "y", t[: -len(nast)] + "i"]
    if kod == "eo":
        b = re.sub(r"(?<=[oa])(jn|j|n)$", "", t)
        out.append(b)
        for nast in ("as", "is", "os", "us", "u"):
            if b.endswith(nast) and len(b) > len(nast) + 1:
                out.append(b[: -len(nast)] + "i")
        if b.endswith(("o", "a", "e", "i")) and len(b) > 2:   # izvedenice: bon·a → bon·e, bon·o
            out += [b[:-1] + x for x in "oaei"]
    return out


# esperanto: razina gramatičkog nastavka (EO-gramaticka-kraljeznica, odj. 7)
EO_NASTAVCI = [("as", 1), ("is", 7), ("os", 7), ("us", 15), ("u", 12), ("i", 3), ("o", 1), ("a", 2), ("e", 2)]


def eo_razina(t, korijeni, afiksi):
    """Razina izvedenice: korijen(i) + afiksi + nastavak, sve poznato. None ako se ne da rastaviti."""
    raz = 0
    for kraj, n in (("jn", 3), ("n", 3), ("j", 2)):
        if t.endswith(kraj) and len(t) > len(kraj) + 2 and t[-len(kraj) - 1] in "oa":
            t, raz = t[: -len(kraj)], n
            break
    for kraj, n in EO_NASTAVCI:
        if t.endswith(kraj) and len(t) > len(kraj) + 1:
            osnova, raz = t[: -len(kraj)], max(raz, n)
            break
    else:
        return None
    dijelovi = {**afiksi, **korijeni}
    najbolje = {0: (0, False)}          # pozicija -> (najveća razina, ima li korijen)
    for i in range(len(osnova)):
        if i not in najbolje:
            continue
        for j in range(i + 1, len(osnova) + 1):
            d = osnova[i:j]
            if d in dijelovi:
                r = max(najbolje[i][0], dijelovi[d])
                k = najbolje[i][1] or d in korijeni
                if j not in najbolje or (k, -r) > (najbolje[j][1], -najbolje[j][0]):
                    najbolje[j] = (r, k)
    kraj = najbolje.get(len(osnova))
    return max(raz, kraj[0]) if kraj and kraj[1] else None


def eo_dijelovi(kod):
    korijeni, afiksi = {}, {}
    with open(KORIJEN / kod / f"rjecnik-{kod}.tsv", encoding="utf-8") as f:
        for red in csv.DictReader(f, delimiter="\t"):
            n, w = razina(red["razina"]), red["eo"].lower()
            if re.fullmatch(r"-?[a-zĉĝĥĵŝŭ]+-?", w) and "-" in w:
                a = w.strip("-")
                afiksi[a] = min(afiksi.get(a, 99), n)
            elif re.fullmatch(r"[a-zĉĝĥĵŝŭ]+[oaei]", w):
                k = w[:-1]
                korijeni[k] = min(korijeni.get(k, 99), n)
    return korijeni, afiksi


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    kod, glas, kralj = sys.argv[1:]
    rj, fr = rjecnik(kod), fraze(kralj)
    eo = eo_dijelovi(kod) if kod == "eo" else None
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
                ok = min([rj.get(t, 99), fr.get(t, 99)] + [rj.get(b, 99) for b in osnove(kod, t)])
                if eo and ok > n:
                    ok = min(ok, eo_razina(t, *eo) or 99)
                if ok > n:
                    gdje = f"rječnik L{rj[t]}" if t in rj else ("fraza L%d" % fr[t] if t in fr else "nema")
                    upozorenja.append(f"  r.{br} L{n}: „{t}“ ({gdje}) u *{k}*")
    print(f"{kod}: {ukupno} riječi ciljnog jezika, upozorenja: {len(upozorenja)}")
    print("\n".join(upozorenja))
    sys.exit(1 if upozorenja else 0)


if __name__ == "__main__":
    main()
