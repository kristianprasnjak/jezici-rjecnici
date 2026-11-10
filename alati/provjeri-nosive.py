#!/usr/bin/env python3
"""Provjera nosivih rečenica (C2): zna li polaznik svaku riječ nosive rečenice na njezinoj razini?

Uporaba:  python3 alati/provjeri-nosive.py XX [put/do/croland/jezici-plan] [--sve]   (zadano: ../croland/jezici-plan)
          --sve ispisuje i svaku riječ prihvaćenu preko pravilnog oblika (token ← natuknica), za ručni pregled.

Čita nosive iz dva izvora i uspoređuje ih:
- kralježnica `XX/XX-gramaticka-kraljeznica.md`, odj. 7: redak „- **Nosiva…:** *…*“ ispod „### L<n>“;
- popis lekcija `XX/XX-popis-lekcija.md`, odj. 3: zadnji stupac retka „| <n> | …“.

Greška:
- nosiva postoji samo u jednom izvoru ili se tekst razlikuje (kralježnica i popis moraju se slagati);
- riječ nije u rječniku ni u zamrznutoj frazi (odj. 6 kralježnice) — „nema“;
- riječ je u rječniku na višoj razini od nosive — „prekasno“.
Riječi se uspoređuju kao u `provjeri-blobby.py` (`rijeci.py`): svi stupci oblika, pravilni oblici za isv i eo,
rastavljanje esperantskih izvedenica, za la pravilni oblici s makronima (`oblici_la.py`).
Imena likova (podebljana u tablici likova popisa lekcija, „| **Léa** …“; za la i sklonjena) i oblici u retku kralježnice
„Ručno provjereno (nosive): *oblik* …“ (npr. konjugirani oblik koji rječnik ne navodi) se prihvaćaju.
Riječ s velikim slovom usred rečenice koje nema u rječniku (*Lyon*, *Aegyptō*) nije greška, nego se ispisuje
kao vlastito ime za ručnu provjeru. Pravilni oblici su heuristika (nastavak + infinitiv iz rječnika), pa
„nema“ i „prekasno“ treba pročitati: nepravilni oblici (*fuimos*, *ero*) idu u redak „Ručno provjereno (nosive)“.
Izlazni kod je 1 ako ima grešaka.
"""
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rijeci import KORIJEN, KURZIV, tokeni, rjecnik, fraze, eo_dijelovi, razina_tokena, raspakiraj, objasni  # noqa: E402
import oblici_la  # noqa: E402

RUCNO = "Ručno provjereno (nosive):"


def norm(s):
    s = unicodedata.normalize("NFC", s.replace("’", "'"))
    return re.sub(r"\s+", " ", s).strip()


def iz_kraljeznice(put):
    nosive, rucno, n = {}, set(), None
    for red in put.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### L(\d{1,2})\b", red)
        if m:
            n = int(m.group(1))
        elif red.startswith("## "):
            n = None
        if red.startswith(RUCNO):
            for k in KURZIV.findall(red):
                rucno.update(tokeni(k))
        if n is not None and re.match(r"- \*\*Nosiva[^*]*:\*\*", red):
            k = KURZIV.findall(red.split(":**", 1)[1])
            if k:
                nosive[n] = norm(k[0])     # prvi kurziv; ostali su objašnjenja (*por la tarde*)
    return nosive, rucno


def iz_popisa(put):
    nosive, imena, odj = {}, set(), ""
    for red in put.read_text(encoding="utf-8").splitlines():
        if red.startswith("## "):
            odj = red
        if red.startswith("|") and "lik" in odj.lower():
            for ime in re.findall(r"\*\*([^*]+)\*\*", red.split("|")[1]):
                imena.update(tokeni(re.sub(r"\([^)]*\)", " ", ime)))
        m = re.match(r"\| (\d{1,2}) \|", red)
        if m and "pregled" in odj.lower():
            zadnji = red.rstrip().rstrip("|").split("|")[-1]
            k = KURZIV.findall(zadnji)
            if k:
                nosive[int(m.group(1))] = norm(k[0])
    return nosive, imena


def vlastita_imena(tekst):
    """Riječi s velikim slovom koje nisu na početku rečenice (Lyon, Madrid, Aegyptō)."""
    out = set()
    for m in re.finditer(r"[^\W\d_]+", unicodedata.normalize("NFC", tekst)):
        prije = tekst[: m.start()].rstrip(" ¿¡«\"„")
        if m.group()[0].isupper() and prije and prije[-1] not in ".!?":
            out.add(m.group().lower())
    return out


def main():
    sve = "--sve" in sys.argv
    argv = [a for a in sys.argv if a != "--sve"]
    if len(argv) not in (2, 3):
        sys.exit(__doc__)
    kod = argv[1]
    plan = Path(argv[2]) if len(argv) == 3 else KORIJEN.parent / "croland" / "jezici-plan"
    K = kod.upper()
    kralj = plan / kod / f"{K}-gramaticka-kraljeznica.md"
    nos_k, rucno = iz_kraljeznice(kralj)
    nos_p, imena = iz_popisa(plan / kod / f"{K}-popis-lekcija.md")
    rj, fr = rjecnik(kod), fraze(kralj)
    eo = eo_dijelovi(kod) if kod == "eo" else None

    if kod == "la":                                       # imena se sklanjaju: Valeriam, Theodōrō, Cornēliae
        for ime in list(imena):
            if ime.endswith(("us", "um")):
                imena |= oblici_la.pridjev12(ime[:-2])
            elif ime.endswith("a"):
                imena |= oblici_la.pridjev12(ime[:-1])
    greske, rijeci, nepoznata_imena, pregled = [], 0, set(), []
    for n in sorted(set(nos_k) | set(nos_p)):
        a, b = nos_k.get(n), nos_p.get(n)
        if a is None or b is None:
            greske.append(f"  L{n}: nosiva samo u {'popisu lekcija' if a is None else 'kralježnici'}")
        elif a != b:
            greske.append(f"  L{n}: kralježnica i popis se razlikuju:\n      K: {a}\n      P: {b}")
        tekst = raspakiraj(kod, a or b)
        velika = vlastita_imena(tekst)
        for t in tokeni(tekst):
            if len(t) < 2 and t not in rj or t in imena or t in rucno:
                continue
            rijeci += 1
            ok = razina_tokena(kod, t, rj, fr, eo)
            if ok == 99 and t in velika:
                nepoznata_imena.add(t)
                continue
            if sve and ok <= n and objasni(kod, t, rj, fr) != "izravno":
                pregled.append(f"  L{n}: {t} {objasni(kod, t, rj, fr)} (L{ok})")
            if ok > n:
                gdje = f"rječnik L{rj[t]}" if t in rj else ("fraza L%d" % fr[t] if t in fr else "nema")
                vrsta = "nema" if ok == 99 else "prekasno"
                greske.append(f"  L{n}: „{t}“ — {vrsta} ({gdje})")
    print(f"{kod}: {len(nos_k)} nosivih (kralježnica), {len(nos_p)} (popis), {rijeci} riječi, grešaka: {len(greske)}")
    if greske:
        print("\n".join(greske))
    if pregled:
        print("  pravilni oblici (--sve):\n" + "\n".join(pregled))
    if nepoznata_imena:
        print("  (vlastita imena izvan rječnika, provjeriti ručno: " + ", ".join(sorted(nepoznata_imena)) + ")")
    sys.exit(1 if greske else 0)


if __name__ == "__main__":
    main()
