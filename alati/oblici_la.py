"""Pravilni latinski oblici iz retka rječnika (lema, genitiv, deklinacija, oblici_pr, konjugacija, glavni_oblici).

Rječnik navodi samo lemu i glavne oblike; tekstovi (nosive, Blobby) trebaju *Valeriam*, *vocat*, *mānsimus*.
`oblici(red)` vraća skup pravilnih oblika **s makronima**, pa usporedba ujedno provjerava makrone (nalaz 11).
Generira se samo ono što je pravilno; nepravilne glagole (*sum, possum, eō, ferō, volō*) i zamjenice treba
navesti u rječniku ili ručno. Oblik ne kaže na kojoj se razini uči padež ili vrijeme — to provjerava kralježnica
(odj. 5); ovdje se gleda samo riječ.
"""
import re
import unicodedata


N1 = ["a", "ae", "am", "ā", "ārum", "īs", "ās"]
N2M = ["us", "e", "ī", "ō", "um", "ōrum", "īs", "ōs"]
N2N = ["um", "ī", "ō", "a", "ōrum", "īs"]
N3 = ["is", "ī", "em", "e", "ēs", "um", "ium", "ibus", "īs", "a", "ia", "im"]
N4 = ["us", "ūs", "uī", "ū", "um", "uum", "ibus", "ua"]
N5 = ["ēs", "ēī", "eī", "em", "ē", "ērum", "ēbus"]

# prezentski sustav po konjugaciji: nastavci na korijen (voc-, vid-, dūc-, aud-, cap-)
AKT = {
    "1": "ō ās at āmus ātis ant ābam ābās ābat ābāmus ābātis ābant ābō ābis ābit ābimus ābitis ābunt ā āte āre "
         "em ēs et ēmus ētis ent ārem ārēs āret ārēmus ārētis ārent āns antis antem ante antēs antium antibus "
         "andum andī andō",
    "2": "eō ēs et ēmus ētis ent ēbam ēbās ēbat ēbāmus ēbātis ēbant ēbō ēbis ēbit ēbimus ēbitis ēbunt ē ēte ēre "
         "eam eās eat eāmus eātis eant ērem ērēs ēret ērēmus ērētis ērent ēns entis entem ente entēs entium entibus "
         "endum endī endō",
    "3": "ō is it imus itis unt ēbam ēbās ēbat ēbāmus ēbātis ēbant am ēs et ēmus ētis ent e ite ere "
         "ās at āmus ātis ant erem erēs eret erēmus erētis erent ēns entis entem ente entēs entium entibus "
         "endum endī endō",
    "4": "iō īs it īmus ītis iunt iēbam iēbās iēbat iēbāmus iēbātis iēbant iam iēs iet iēmus iētis ient ī īte īre "
         "iās iat iāmus iātis iant īrem īrēs īret īrēmus īrētis īrent iēns ientis ientem iente ientēs ientium "
         "ientibus iendum iendī iendō",
    "3io": "iō is it imus itis iunt iēbam iēbās iēbat iēbāmus iēbātis iēbant iam iēs iet iēmus iētis ient e ite ere "
           "iās iat iāmus iātis iant erem erēs eret erēmus erētis erent iēns ientis ientem iente ientēs ientium "
           "ientibus iendum iendī iendō",
}
PAS = {
    "1": "or āris ātur āmur āminī antur ābar ābāris ābātur ābāmur ābāminī ābantur ābor āberis ābitur ābimur "
         "ābiminī ābuntur ārī ētur entur ārētur ārentur",
    "2": "eor ēris ētur ēmur ēminī entur ēbar ēbāris ēbātur ēbāmur ēbāminī ēbantur ēbor ēberis ēbitur ēbimur "
         "ēbiminī ēbuntur ērī eātur eantur ērētur ērentur",
    "3": "or eris itur imur iminī untur ēbar ēbāris ēbātur ēbāmur ēbāminī ēbantur ar ēris ētur ēmur ēminī entur "
         "ī ātur antur erētur erentur",
    "4": "ior īris ītur īmur īminī iuntur iēbar iēbāris iēbātur iēbāmur iēbāminī iēbantur iar iēris iētur iēmur "
         "iēminī ientur īrī iātur iantur īrētur īrentur",
    "3io": "ior eris itur imur iminī iuntur iēbar iēbāris iēbātur iēbāmur iēbāminī iēbantur iar iēris iētur "
           "iēmur iēminī ientur ī iātur iantur erētur erentur",
}
PERF = ("ī istī it imus istis ērunt eram erās erat erāmus erātis erant erō eris erit erimus eritis erint isse "
        "erim erit issem issēs isset issēmus issētis issent").split()
INF = {"1": "āre", "2": "ēre", "4": "īre", "3": "ere", "3io": "ere"}
INF_DEP = {"1": "ārī", "2": "ērī", "4": "īrī", "3": "ī", "3io": "ī"}

# zamjenice i nepravilni glagoli: puni oblici (rječnik ih navodi samo lemom)
ZAMJENICE = {
    "ego": "ego mē mihi mihī meī",
    "tū": "tū tē tibi tibī tuī",
    "nōs": "nōs nostrum nostrī nōbīs",
    "vōs": "vōs vestrum vestrī vōbīs",
    "sē": "sē sēsē suī sibi sibī",
    "is": "is ea id eius eī eum eam eō eā iī eae eōrum eārum eīs iīs eōs eās",
    "hic": "hic haec hoc huius huic hunc hanc hōc hāc hī hae hōrum hārum hīs hōs hās",
    "ille": "ille illa illud illīus illī illum illam illō illā illae illōrum illārum illīs illōs illās",
    "iste": "iste ista istud istīus istī istum istam istō istā istae istōrum istārum istīs istōs istās",
    "ipse": "ipse ipsa ipsum ipsīus ipsī ipsam ipsō ipsā ipsae ipsōrum ipsārum ipsīs ipsōs ipsās",
    "īdem": "īdem eadem idem eiusdem eīdem eundem eandem eōdem eādem iīdem eaedem eōrundem eārundem eīsdem "
            "eōsdem eāsdem",
    "quī": "quī quae quod cuius cui quem quam quō quā quōrum quārum quibus quōs quās",
    "quis": "quis quid cuius cui quem quō quibus",
    "nēmō": "nēmō nēminis nēminī nēminem",
}
POSVOJNE = {"meus": "me", "tuus": "tu", "suus": "su", "noster": "nostr", "vester": "vestr"}
NEPRAVILNI = {
    "sum": "sum es est sumus estis sunt eram erās erat erāmus erātis erant erō eris erit erimus eritis erunt "
           "sim sīs sit sīmus sītis sint essem essēs esset essēmus essētis essent esse este",
    "possum": "possum potes potest possumus potestis possunt poteram poterās poterat poterāmus poterātis poterant "
              "poterō poteris poterit poterimus poteritis poterunt possim possīs possit possīmus possītis possint "
              "possem possēs posset possēmus possētis possent posse",
    "eō": "eō īs it īmus ītis eunt ībam ībās ībat ībāmus ībātis ībant ībō ībis ībit ībimus ībitis ībunt eam eās "
          "eat eāmus eātis eant īrem īrēs īret īrēmus īrētis īrent ī īte īre iēns euntis euntem eunte euntēs "
          "euntium euntibus itum itūrus iī īvī iit iērunt īsse iisse",
    "ferō": "ferō fers fert ferimus fertis ferunt ferēbam ferēbās ferēbat ferēbāmus ferēbātis ferēbant feram ferēs "
            "feret ferēmus ferētis ferent fer ferte ferre ferrem ferrēs ferret ferrēmus ferrētis ferrent fertur "
            "feruntur ferrī ferēns ferentis",
    "volō": "volō vīs vult volumus vultis volunt volēbam volēbās volēbat volēbāmus volēbātis volēbant volam volēs "
            "volet volēmus volētis volent velim velīs velit velīmus velītis velint vellem vellēs vellet vellēmus "
            "vellētis vellent velle volēns",
    "nōlō": "nōlō nōlumus nōlunt nōlēbam nōlēbat nōlēbant nōlam nōlēs nōlet nōlī nōlīte nōlle nōllem nōllet",
    "mālō": "mālō māvīs māvult mālumus māvultis mālunt mālēbam mālam mālle māllem",
    "dō": "dō dās dat damus datis dant dabam dabās dabat dabāmus dabātis dabant dabō dabis dabit dabimus dabitis "
          "dabunt dem dēs det dēmus dētis dent darem darēs daret darēmus darētis darent dare dā date datur "
          "dantur darī dāns dantis",
    "fīō": "fīō fīs fit fīmus fītis fīunt fīēbam fīēbat fiam fierī fieret fierent",
}


def nfc(s):
    return unicodedata.normalize("NFC", s)


def pridjev12(osnova):
    return {osnova + n for n in set(N1 + N2M + N2N)}


def imenica(lema, gen, dekl, rod):
    out = {lema}
    if not gen:
        return out
    if dekl == "1" and gen.endswith("ae"):
        out |= {gen[:-2] + n for n in N1}
    elif dekl == "2" and gen.endswith("ī"):
        out |= {gen[:-1] + n for n in (N2N if lema.endswith("um") and rod == "n" else N2M)}
    elif dekl == "3" and gen.endswith("is"):
        out |= {gen[:-2] + n for n in N3}
    elif dekl == "4" and gen.endswith("ūs"):
        out |= {gen[:-2] + n for n in N4}
    elif dekl == "5":
        out |= {lema[:-2] + n for n in N5}
    return out


def pridjev(lema, dekl, obl):
    out = {lema}
    dijelovi = [d.strip() for d in obl.replace("gen.", "").split(",") if d.strip()]
    if dekl == "1-2" and len(dijelovi) >= 2:
        osn = dijelovi[1][:-1]
        out |= pridjev12(osn)
        out |= pridjev12(lema + "rim" if lema.endswith("er") else osn + "issim")      # pulcherrimus, longissimus
        out |= {osn + "ior", osn + "ius"} | {osn + "iōr" + n for n in N3 if n not in ("ium", "ia", "im")}
    elif dekl == "3":
        if lema.endswith("ior"):                         # komparativ: melior, meliōris
            osn = lema[:-2] + "ōr"
            out |= {osn + n for n in N3 if n not in ("ium", "ia", "im")} | set(dijelovi)
        elif len(dijelovi) >= 2 and dijelovi[1].endswith("is") and dijelovi[1] != lema:
            osn = dijelovi[1][:-2]                       # ingēns, ingentis / ācer, ācris, ācre
            out |= {osn + n for n in N3} | set(dijelovi)
        elif len(dijelovi) >= 2 and dijelovi[1].endswith("e"):
            osn = dijelovi[1][:-1]                       # fortis, forte
            out |= {osn + n for n in N3} | set(dijelovi)
        if not lema.endswith("ior") and len(dijelovi) >= 2:
            osn = (dijelovi[1][:-2] if dijelovi[1].endswith("is") and dijelovi[1] != lema else dijelovi[1][:-1])
            out |= pridjev12(lema + "rim" if lema.endswith("er") else osn + "issim")      # fortissimus, ācerrimus
            out |= {osn + "ior", osn + "ius"} | {osn + "iōr" + n for n in N3 if n not in ("ium", "ia", "im")}
    return out


def glagol(lema, konj, glavni):
    out = {lema}
    dijelovi = [d.strip() for d in re.split(r"[,/]", glavni or "") if d.strip() and d.strip() != "—"]
    dep = lema.endswith("or")
    if konj in AKT and dijelovi:
        inf = dijelovi[0]
        kraj = (INF_DEP if dep else INF)[konj]
        if inf.endswith(kraj):
            korijen = inf[: -len(kraj)]
            if not dep:
                out |= {korijen + n for n in AKT[konj].split()}
            out |= {korijen + n for n in PAS[konj].split()}
            if dep:   # deponenti: aktivni participi i imperativ
                out |= {korijen + n for n in AKT[konj].split() if n.startswith(("ā", "ē", "e", "i", "ī"))
                        and n.endswith(("ns", "ntis", "ntem", "nte", "ntēs", "ndum", "ndī", "ndō"))}
                out |= {korijen + {"1": "āre", "2": "ēre", "4": "īre", "3": "ere", "3io": "ere"}[konj]}
    for d in dijelovi[1:]:
        d = d.split()[0]
        if d.endswith("ī") and not dep:                  # perfekt: vocāvī
            out |= {d[:-1] + n for n in PERF}
        elif d.endswith(("um", "us")):                   # supin / PPP: vocātum, secūtus (sum)
            osn = d[:-2]
            out |= pridjev12(osn) | pridjev12(osn + "ūr") | {osn + "um", osn + "ū"}
    return out


def oblici(red):
    """Svi pravilni oblici retka rječnika (NFC, mala slova)."""
    lema = nfc(red.get("la", "").lower())
    vrsta = red.get("vrsta", "")
    if vrsta == "im":
        out = imenica(lema, nfc(red.get("genitiv", "").lower()), red.get("deklinacija", ""), red.get("rod", ""))
    elif vrsta == "pr":
        out = pridjev(lema, red.get("deklinacija", ""), nfc(red.get("oblici_pr", "").lower()))
    elif vrsta == "gl":
        out = glagol(lema, red.get("konjugacija", ""), nfc(red.get("glavni_oblici", "").lower()))
    else:
        out = {lema}
    for dio in re.split(r",\s*", lema):                   # „hic, haec, hoc“, „quī, quae, quod“
        dio = dio.strip()
        if dio in ZAMJENICE:
            out |= set(ZAMJENICE[dio].split())
        if dio in POSVOJNE:
            out |= pridjev12(POSVOJNE[dio]) | ({"mī"} if dio == "meus" else set())
    if vrsta == "gl" and red.get("konjugacija") == "nepr":
        for osnova, oblici_ in NEPRAVILNI.items():       # i složenice: redeō, afferō, abeō
            if lema == osnova or (lema.endswith(osnova) and osnova in ("eō", "ferō")):
                pref = lema[: len(lema) - len(osnova)]
                out |= {pref + o for o in oblici_.split()}
    if lema in NEPRAVILNI:
        out |= set(NEPRAVILNI[lema].split())
    return {o for o in out if o}
