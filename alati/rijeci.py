"""Zajedničke funkcije za provjere teksta prema rječniku (provjeri-blobby.py, provjeri-nosive.py).

`rjecnik(kod)` → {token: najniža razina} iz svih stupaca oblika (za la i pravilni oblici, `oblici_la.py`);
`fraze(kraljeznica)` → isto za zamrznute fraze iz odj. 6 kralježnice; `razina_tokena(...)` → razina riječi
uz pravilne oblike (isv, eo) i rastavljanje esperantskih izvedenica.
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oblici_la  # noqa: E402

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
            if kod == "la":   # pravilni oblici (Valeriam, vocat, mānsimus) iz glavnih oblika
                for o in oblici_la.oblici(red):
                    for t in tokeni(o):
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


BEZ_NAGLASKA = str.maketrans("áéíóúâêôãõàèìòù", "aeiouaeoaoaeiou")

# romanski jezici: nastavci glagolskih oblika (prezent, imperfekt, futur, kondicional, perfekt, participi, gerund,
# konjunktiv); ostatak + nastavak infinitiva mora biti glagol iz rječnika
GL_NAST = {
    "fr": "e es ent ons ez ais ait aient ions iez ai as a âmes èrent é ée és ées i ie is ies it u ue us ues ant "
          "rai ras ra rons rez ront rais rait raient rions riez isse issent issons issez issais issait issaient "
          "issant isses",
    "it": "o i a iamo ate ete ite ano ono avo avi ava avamo avate avano evo evi eva evamo evate evano ivo ivi iva "
          "ivamo ivate ivano erò erai erà eremo erete eranno irò irai irà iremo irete iranno erei eresti erebbe "
          "eremmo ereste erebbero irei irebbe ato ata ati ate uto uta uti ute ito ita iti ite ando endo isco isci "
          "isce iscono iamo",
    "es": "o as a amos áis an es e emos éis en is imos ís aba abas ábamos abais aban ía ías íamos íais ían é aste "
          "ó asteis aron í iste ió isteis ieron ado ada ados adas ido ida idos idas ando iendo aré arás ará aremos "
          "aréis arán eré erás erá eremos erán iré irás irá iremos irán aría arías aríamos arían ería erías "
          "eríamos erían iría irías iríamos irían",
    "pt": "o as a amos am es e emos em is imos ava avas ávamos avam ia ias íamos iam ei aste ou aram i este eu "
          "eram iste iu iram ado ada ados adas ido ida idos idas ando endo indo arei arás ará aremos arão erei "
          "erá eremos erão irei irá iremos irão aria arias aríamos ariam eria iria",
}
INF_NAST = {"fr": ("er", "ir", "re", "oir"), "it": ("are", "ere", "ire"), "es": ("ar", "er", "ir"),
            "pt": ("ar", "er", "ir")}
ENKLITIKE = ("te", "me", "se", "lo", "la", "le", "nos", "os", "los", "las", "les", "toi", "moi", "vous", "nous")


def osnove(kod, t):
    """Pravilni oblici koje rječnik ne navodi: moguće natuknice (leme) za token."""
    out = []
    if kod == "isv":
        for nast in ("ogo", "omu", "ymi", "ych", "ym", "oj", "o", "a", "e", "u", "i", "ě"):
            if t.endswith(nast) and len(t) > len(nast) + 2:
                out += [t[: -len(nast)] + "y", t[: -len(nast)] + "i"]
        m = re.fullmatch(r"(?:naj)?(.+?)(?:ějš|ejš|š)(?:i|a|e|y|ego|ej)", t)
        if m:                                            # najzelenějša → zeleny
            out += [m.group(1) + "y", m.group(1) + "i"]
        # imenice: brata, sestru, večerju, polnoči, jablok, podarky
        for nast in ("ami", "ah", "am", "om", "oju", "ov", "ej", "em", "a", "u", "e", "y", "i", "ě", "o", ""):
            if t.endswith(nast) and len(t) > len(nast) + 2:
                b = t[: len(t) - len(nast)]
                out += [b, b + "a", b + "o", b + "e", b + "j", b + "ja", b[:-1] + "o" + b[-1]]
        # glagoli: rabotam, byla, odhodi, pij, idu, byh
        for nast in ("jut", "ut", "at", "mo", "te", "em", "eš", "m", "š", "l", "la", "lo", "li", "j", "h", "u", "e", ""):
            if t.endswith(nast) and len(t) > len(nast) + 1:
                b = t[: len(t) - len(nast)]
                out += [b + "ti", b + "ati", b + "iti", b + "ěti"]
    if kod == "eo":
        b = re.sub(r"(?<=[oau])(jn|j|n)$", "", t)
        out.append(b)
        if t.endswith("n"):                              # akuzativ zamjenice: min, lin
            out.append(t[:-1])
        for nast in ("as", "is", "os", "us", "u"):
            if b.endswith(nast) and len(b) > len(nast) + 1:
                out.append(b[: -len(nast)] + "i")
        if b.endswith(("o", "a", "e", "i")) and len(b) > 2:   # izvedenice: bon·a → bon·e, bon·o
            out += [b[:-1] + x for x in "oaei"]
    if kod in GL_NAST:
        oblici = [t]
        for kl in ENKLITIKE:                             # quédate → queda, repose-toi → repose
            for k in (kl, "-" + kl):
                if t.endswith(k) and len(t) > len(k) + 2:
                    oblici.append(t[: -len(k)].translate(BEZ_NAGLASKA))
        if kod in ("it", "fr", "es", "pt"):              # elizija: trent' → trenta
            out += [t + v for v in "aeoi"]
        for o in oblici:
            out.append(o)
            if o[-1:] in "aeios" and len(o) > 3:         # pridjevi: molta → molto, quante → quanto
                out += [o[:-1] + "o", o[:-1] + "e", o.rstrip("s")]
                if o.endswith(("as", "os", "es")):
                    out.append(o[:-2] + "o")
            for nast in GL_NAST[kod].split() + [""]:
                if o.endswith(nast) and len(o) > len(nast) + 1:
                    b = o[: len(o) - len(nast)]
                    osn = {b, b.translate(BEZ_NAGLASKA)}
                    if b.endswith(("ch", "gh")):         # dimenticherò → dimenticare
                        osn.add(b[:-1])
                    for x in list(osn):                  # vuelvas → volver, pienso → pensar
                        osn |= {x.replace("ue", "o"), x.replace("ie", "e")}
                    for x in osn:
                        out += [x] + [x + inf for inf in INF_NAST[kod]] + [x + "e"]
    if kod == "en":
        for nast, zam in (("ies", "y"), ("ied", "y"), ("ing", ""), ("ing", "e"), ("ed", ""), ("ed", "e"),
                          ("es", ""), ("s", ""), ("d", ""), ("er", ""), ("est", "")):
            if t.endswith(nast) and len(t) > len(nast) + 1:
                b = t[: -len(nast)] + zam
                out.append(b)
                if len(b) > 2 and b[-1] == b[-2]:         # stopped → stop
                    out.append(b[:-1])
        out += {"has": ["have"], "does": ["do"], "is": ["be"], "are": ["be"], "am": ["be"], "was": ["be"],
                "were": ["be"]}.get(t, [])
    return out


EN_SAŽECI = [("can't", "can not"), ("won't", "will not"), ("n't", " not"), ("'re", " are"), ("'m", " am"),
             ("'ll", " will"), ("'ve", " have"), ("'d", " would"), ("'s", "")]


def raspakiraj(kod, tekst):
    """Engleski sažeci (don't → do not) prije rastavljanja na riječi."""
    if kod != "en":
        return tekst
    tekst = tekst.replace("’", "'")
    for a, b in EN_SAŽECI:
        tekst = re.sub(re.escape(a), b, tekst, flags=re.I)
    return tekst


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


def objasni(kod, t, rj, fr):
    """Odakle je razina: sam token, fraza ili natuknica dobivena iz pravilnog oblika (za ručni pregled)."""
    if t in rj or t in fr:
        return "izravno"
    kand = [(rj[b], b) for b in osnove(kod, t) if b in rj]
    return "← " + min(kand)[1] if kand else "?"


def razina_tokena(kod, t, rj, fr, eo=None):
    """Najniža razina na kojoj polaznik zna token (99 = ne zna)."""
    ok = min([rj.get(t, 99), fr.get(t, 99)] + [rj.get(b, 99) for b in osnove(kod, t)])
    if eo:
        ok = min(ok, eo_razina(t, *eo) or 99)
    return ok
