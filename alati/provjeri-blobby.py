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
Za la se iz glavnih oblika grade pravilni oblici (`oblici_la.py`: *Valeriam* od *Valeria*, *vocat* od *vocō*,
*mānsimus* od *mānsī*), s makronima — riječ bez makrona gdje ih rječnik ima javlja se kao upozorenje.
Esperanto se uz to rastavlja na korijen, afikse i nastavak (*malbelan* = mal- L2 + bel L2 + -a L2 + -n L3);
razina riječi je najviša razina dijela.
Riječ je u redu ako je u rječniku na razini ≤ n (bilo koji stupac oblika) ili u zamrznutoj frazi
iz odj. 6 kralježnice s „Od“ ≤ n. Ostalo se ispisuje kao upozorenje za ručnu provjeru
(npr. oblik koji rječnik ne navodi). Izlazni kod je 1 ako ima upozorenja.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rijeci import KURZIV, RAZ, tokeni, rjecnik, fraze, eo_dijelovi, razina_tokena  # noqa: E402


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
                ok = razina_tokena(kod, t, rj, fr, eo)
                if ok > n:
                    gdje = f"rječnik L{rj[t]}" if t in rj else ("fraza L%d" % fr[t] if t in fr else "nema")
                    upozorenja.append(f"  r.{br} L{n}: „{t}“ ({gdje}) u *{k}*")
    print(f"{kod}: {ukupno} riječi ciljnog jezika, upozorenja: {len(upozorenja)}")
    print("\n".join(upozorenja))
    sys.exit(1 if upozorenja else 0)


if __name__ == "__main__":
    main()
