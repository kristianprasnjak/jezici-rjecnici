# Jezici — rječnici tečajeva

Rječnici za tečajeve stranih jezika na Croland engineu. Repo postoji samo online (nije povezan s
lokalnim folderom Crolanda). Kad tečaj ide u gradnju, gotov rječnik se preuzme odavde u Croland.

Razine i teme slijede koncepte iz `croland/jezici-koncept/<jezik>.md` (odj. 4). Prema odluci G7
sada su samo latinični jezici; ruski, kineski, japanski i arapski dolaze 2027.

| Mapa | Jezik | Razine |
|---|---|---|
| `fr/` | francuski | L0–L20 |
| `it/` | talijanski | L0–L20 |
| `es/` | španjolski (Španjolska) | L0–L20 |
| `pt/` | portugalski (brazilski) | L0–L20 |
| `en/` | engleski (britanski) | L0–L20 |
| `eo/` | esperanto | L0–L18 |
| `la/` | latinski (klasični, makroni) | L0–L20 |
| `isv/` | interslavenski (školski standard tečaja) | L0–L16 |

Njemački rječnik je u Crolandu (`deutsch/rjecnik/`).

## Faze

1. **A — popis riječi + engleski** (sada): riječ, prijevod, vrsta riječi, razina i tema.
2. **B — oblici**: množina, rod, ključni glagolski oblici. Gotovo: **fr**. Sljedeći: it, es, pt.
3. **C — hrvatski prijevod i ključevi slika** (po potrebi primjeri).

## Datoteke u mapi jezika

| Datoteka | Što je |
|---|---|
| `rjecnik-XX.tsv` | **izvor** — uređuje se (i u Excelu: tab kao razdjelnik, UTF-8) |
| `rjecnik-XX.jsonl` | za program; gradi se iz TSV-a, ne uređuje se ručno |
| `razine-XX.tsv` | razine, teme i ciljani broj riječi iz koncepta |
| `IZVJESTAJ.md` | rezultat zadnje provjere |

Stupci TSV-a: `razina | tema | XX | en | vrsta` (za engleski tečaj `razina | tema | en | hr | vrsta`).

- **Riječ** je osnovni oblik. Imenice u romanskim jezicima pišu se s članom zbog roda
  (`le livre`, `la maison`, `l'ami (m)`); kod `l'` i istog oblika za oba roda rod je u zagradi.
  Engleski: imenica bez člana, glagol u osnovnom obliku (`book`, `go`); ista riječ kao imenica i
  glagol dva je retka s različitom vrstom.
  Latinski: lema s makronima (`rosa`, `amō`); esperanto: lema; interslavenski: školski standard
  (odluke ISV1/ISV2 u `croland/jezici-koncept/ODLUKE-VLASNIKA.md`).
- Napomena u zagradi razlikuje značenja (`la muñeca (juguete)`); za provjeru duplikata se zanemaruje.
- **Vrsta**: `im` imenica, `gl` glagol, `pr` pridjev, `pril` prilog, `zam` zamjenica, `prij` prijedlog,
  `vez` veznik, `broj`, `izraz` (više riječi / fraza), `usk` uzvik, `čest` čestica, `čl` član,
  `afiks` (tvorba riječi, esperanto).
- Svaka riječ je u rječniku **jednom**, na razini na kojoj se prvi put uči.

## Faza B — oblici (obrazac: francuski)

Stupci oblika dodaju se **iza** pet osnovnih, u ovom redoslijedu. Svaki stupac pripada jednoj
vrsti riječi: za nju je obavezan, za sve ostale vrste (pril, prij, vez, zam, izraz, broj, čest,
čl, usk) ostaje prazan. `—` znači „oblik se ne koristi“ (nije isto što i prazno polje).

| Stupac | Vrsta | Sadržaj (fr) | Primjer |
|---|---|---|---|
| `rod` | im | `m` / `f` / `m,f` | `l'hôtel (m)` → `m`; `le voisin, la voisine` → `m,f`; `l'élève (m/f)` → `m,f` |
| `mnozina` | im | množina bez člana, **uvijek** (i pravilna); `—` za nebrojive i vlastita imena | `cafés`, `chevaux`, `grands-pères`, `rez-de-chaussée`, `le lait` → `—` |
| `zenski` | pr | ženski oblik (za nepromjenjive isti) | `beau` → `belle`, `jeune` → `jeune` |
| `mnozina_pr` | pr | množina `m / ž` | `beaux / belles`, `marron / marron` |
| `gl_skupina` | gl | `1` (-er), `2` (-ir, -issons), `3` (ostali, i `aller`) | `finir` → `2` |
| `pomocni` | gl | pomoćni glagol za passé composé: `avoir` / `être` | `aller` → `être` |
| `particip` | gl | participe passé (m. jd.) | `prendre` → `pris` |
| `prezent` | gl | 6 oblika (je · tu · il · nous · vous · ils) bez zamjenice, odvojeno ` · ` | `suis · es · est · sommes · êtes · sont` |

Pravila:

- Imenica s dva oblika u stupcu riječi (`le voisin, la voisine`) ima rod `m,f` i množinu s
  jednako mnogo oblika, istim redom: `voisins, voisines` (i kad su isti: `touristes, touristes`).
  Ista riječ za oba roda s oznakom `(m/f)` ima jedan oblik: `l'enfant (m/f)` → `enfants`.
- Riječi koje se uče samo u množini (`les vacances (f)`) u `mnozina` imaju taj isti oblik.
- Riječi bez člana (dani, mjeseci, `madame`, `midi`, `Noël`) moraju imati `rod`.
- Složenice: standardni pravopis prije reforme 1990. (`après-midi`, `gratte-ciel`,
  `lave-linge` nepromjenjivi; `grands-mères`).
- Povratni glagoli: skupina prema osnovnom glagolu, `pomocni` = `être`, prezent sa zamjenicom
  (`me lève · te lèves · se lève · nous levons · vous levez · se lèvent`, `m'appelle …`).
- Bezlični glagoli: nepostojeća lica su `—` (`— · — · pleut · — · — · —`).
- Glagoli koji mogu imati oba pomoćna (`monter`, `sortir`, `passer` …) dobivaju pomoćni za
  značenje u stupcu `en` (`monter` „to go up“ → `être`; `passer` „to spend (time)“ → `avoir`).

`provjeri.py` provjerava: stupac postoji → popunjen za svoju vrstu i prazan za ostale; `rod` je
`m`/`f`/`m,f`; dvorodna riječ ima `m,f` i jednak broj oblika množine; `mnozina_pr` je `m / ž`;
`gl_skupina` je 1–3; `pomocni` iz popisa jezika (`POMOCNI` u skripti); `prezent` ima 6 oblika.
Jezici bez tih stupaca prolaze kao i prije.

**Za it / es / pt** isti obrazac, s prilagodbom: `pomocni` je `avere`/`essere` (it), za es i pt
izostaje (uvijek haber / ter); `gl_skupina` po infinitivu (-are/-ere/-ire, -ar/-er/-ir);
dodati odgovarajuće vrijednosti u `POMOCNI` i, ako treba, nove stupce u `OBLICI`.

## Alati

```
python3 alati/gradi.py [fr …]      TSV -> JSONL
python3 alati/provjeri.py [fr …]   provjera, piše IZVJESTAJ.md (izlaz 1 ako ima grešaka)
```

Interslavenski se dodatno provjerava prema zaključanoj bazi (odluka ISV2, commit `53d42b2af`):
`python3 alati/provjeri-isv-baza.py <klon medzuslovjansky/database>` (upute u zaglavlju skripte).

Provjera javlja grešku za prazno polje, nepoznatu razinu ili vrstu, temu koja ne odgovara razini i
riječ koja se javlja dvaput. Upozorava kad broj riječi u razini odstupa od koncepta više od 10 %.
