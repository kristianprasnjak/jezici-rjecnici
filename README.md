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
2. **B — oblici**: množina, rod, ključni glagolski oblici.
3. **C — hrvatski prijevod i ključevi slika** (po potrebi primjeri).

## Datoteke u mapi jezika

| Datoteka | Što je |
|---|---|
| `rjecnik-XX.tsv` | **izvor** — uređuje se (i u Excelu: tab kao razdjelnik, UTF-8) |
| `rjecnik-XX.jsonl` | za program; gradi se iz TSV-a, ne uređuje se ručno |
| `razine-XX.tsv` | razine, teme i ciljani broj riječi iz koncepta |
| `IZVJESTAJ.md` | rezultat zadnje provjere |

Stupci TSV-a: `razina | tema | XX | en | vrsta` (za engleski tečaj `razina | tema | en | hr | vrsta`).

- **Riječ** je osnovni oblik. Imenice u romanskim jezicima i engleskom pišu se s članom zbog roda
  (`le livre`, `la maison`, `l'ami (m)`); kod `l'` i istog oblika za oba roda rod je u zagradi.
  Latinski: lema s makronima (`rosa`, `amō`); esperanto: lema; interslavenski: školski standard
  (odluke ISV1/ISV2 u `croland/jezici-koncept/ODLUKE-VLASNIKA.md`).
- **Vrsta**: `im` imenica, `gl` glagol, `pr` pridjev, `pril` prilog, `zam` zamjenica, `prij` prijedlog,
  `vez` veznik, `broj`, `izraz` (više riječi / fraza), `usk` uzvik, `čest` čestica, `čl` član,
  `afiks` (tvorba riječi, esperanto).
- Svaka riječ je u rječniku **jednom**, na razini na kojoj se prvi put uči.

## Alati

```
python3 alati/gradi.py [fr …]      TSV -> JSONL
python3 alati/provjeri.py [fr …]   provjera, piše IZVJESTAJ.md (izlaz 1 ako ima grešaka)
```

Provjera javlja grešku za prazno polje, nepoznatu razinu ili vrstu, temu koja ne odgovara razini i
riječ koja se javlja dvaput. Upozorava kad broj riječi u razini odstupa od koncepta više od 10 %.
