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
2. **B — oblici**: množina, rod, ključni glagolski oblici. Gotovo za **sve jezike** (stupci se
   razlikuju po jeziku, vidi „Faza B“).
3. **C — hrvatski prijevod i ključevi slika** (po potrebi primjeri).

## Datoteke u mapi jezika

| Datoteka | Što je |
|---|---|
| `rjecnik-XX.tsv` | **izvor** — uređuje se (i u Excelu: tab kao razdjelnik, UTF-8) |
| `rjecnik-XX.jsonl` | za program; gradi se iz TSV-a, ne uređuje se ručno |
| `razine-XX.tsv` | razine, teme i ciljani broj riječi iz koncepta |
| `IZVJESTAJ.md` | rezultat zadnje provjere |
| `prijevod-SU-XX.tsv` | faza C: prijevod na jezik sučelja SU (`hr`, kasnije `de`, `es` …), ključ = riječ + vrsta; rječnik iz faze B se ne mijenja |
| `kraljeznica-XX.tsv` | riječi čiju razinu propisuje kralježnica tečaja (nepravilni glagoli, veznici, zamjenice); izvor je `croland/jezici-plan/XX/XX-gramaticka-kraljeznica.md` |

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

Stupci oblika dodaju se **iza** pet osnovnih. Svaki stupac pripada jednoj vrsti riječi (im, pr ili
gl; `deklinacija` u latinskom i im i pr): za nju je obavezan, za sve ostale vrste (pril, prij, vez,
zam, izraz, broj, čest, čl, usk, afiks) ostaje prazan. `—` znači „oblik se ne koristi / ne postoji“
(nije isto što i prazno polje). Jezik uzima samo stupce koji mu trebaju:

| Jezik | Imenice | Pridjevi | Glagoli |
|---|---|---|---|
| fr | rod, mnozina | zenski, mnozina_pr | gl_skupina, pomocni, particip, prezent (6) |
| it | rod, mnozina (s članom) | zenski, mnozina_pr | gl_skupina, pomocni, particip, prezent (6) |
| es | rod, mnozina (s članom) | zenski, mnozina_pr | gl_skupina, particip, prezent (6), preterit (2) |
| pt | rod, mnozina (s članom) | zenski, mnozina_pr | gl_skupina, particip, prezent (4), preterit (2) |
| en | mnozina | komparativ, superlativ | preterit, particip, ing |
| la | rod, genitiv, deklinacija | oblici_pr, deklinacija | konjugacija, glavni_oblici |
| eo | — | — | prelaznost |
| isv | rod | — | vid, prezent (2) |

Dolje je francuski kao obrazac, zatim razlike po jezicima.

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

`provjeri.py` provjerava: stupac postoji → popunjen za svoju vrstu i prazan za ostale; vrijednost
je iz popisa jezika (`VRIJEDNOSTI`: `rod`, `gl_skupina`, `pomocni`, `konjugacija`, `deklinacija`,
`vid`, `prelaznost`); dvorodna riječ ima `m,f` i jednak broj oblika množine (`(m/f)`: jedan ili
dva); `mnozina_pr` je `m / ž`; `prezent` ima propisani broj oblika (`PREZENT_LICA`, inače 6),
`preterit` u es/pt dva (`PRETERIT_LICA`);
`glavni_oblici` ima 1–3 dijela.

### Talijanski — razlike od francuskog

Isti stupci, s ovim razlikama:

- `mnozina` se piše **s članom** (`i libri`, `gli zii`, `le case`) jer je član u množini
  dio onoga što se uči (i/gli/le), a pokazuje i promjenu roda: `il braccio` → `le braccia`,
  `l'uovo (m)` → `le uova` (`rod` uvijek vrijedi za jedninu). Riječi bez člana također dobivaju
  član u množini (`lunedì` → `i lunedì`).
- `(m/f)` s istim oblikom: `gli / le ospiti`; ako se množina razlikuje po rodu, dva oblika:
  `l'artista (m/f)` → `gli artisti, le artiste`.
- `gl_skupina` prema završetku infinitiva: `1` -are, `2` -ere, `3` -ire (i `essere`/`avere` = 2,
  `fare`/`andare`/`stare`/`dare` = 1, `dire` = 3, skraćeni `bere`, `proporre` = 2). Glagoli
  na -isc- vide se u prezentu (`capisco · capisci …`).
- `pomocni`: `avere` / `essere`; povratni i bezlični glagoli (`piovere`, `nevicare`) = `essere`.
- `prezent`: io · tu · lui · noi · voi · loro; povratni sa zamjenicom (`mi alzo · ti alzi …`).

### Španjolski (Španjolska)

- Kao talijanski: `mnozina` s članom (`los libros`, `las aguas` za `el agua (f)`), dvorodne
  `los niños, las niñas`, bez člana `lunes` → `los lunes`; mjeseci, zemlje i nebrojive `—`.
- `pomocni` se izostavlja (uvijek *haber*). `gl_skupina`: `1` -ar, `2` -er, `3` -ir/-ír.
- `prezent`: yo · tú · él · nosotros · vosotros · ellos (europski, s *vosotros*); povratni sa
  zamjenicom (`me levanto · te levantas …`); promjena osnove vidi se u oblicima (`pienso`, `puedo`).
- `particip`: participio (m. jd.): `hecho`, `escrito`, `leído`.
- `preterit`: pretérito indefinido, **2 oblika** yo · él, jer 3. lice pokazuje promjenu osnove:
  `hice · hizo`, `dormí · durmió`, `leí · leyó`, `busqué · buscó`; povratni `me levanté · se levantó`;
  pravopis 2010. (`vi · vio`, `reí · rio`); `soler` → `— · —` (ne koristi se).
- Boje `rosa`, `naranja` kao pridjevi slažu se u broju (`rosas / rosas`, prema DPD-u).

### Portugalski (brazilski)

- Isto kao španjolski (`mnozina` s članom, `—` za nebrojive), `pomocni` se izostavlja (*ter*).
- `prezent` ima **4 oblika**: eu · você/ele · nós · vocês/eles (oblici koji se u Brazilu stvarno
  koriste; *tu* i *vós* izostavljeni). Povratni glagoli s **proklizom** (`me levanto · se levanta …`).
- `preterit`: pretérito perfeito, **2 oblika** eu · você/ele: `fiz · fez`, `pude · pôde`,
  `cheguei · chegou`, `me levantei · se levantou`.
- `cinza`, `rosa`, `laranja` kao pridjevi su nepromjenjivi (`rosa / rosa`).
- Pravopis po Ortografskom sporazumu 1990. (`veem`, `doo`, `ideia`).

### Engleski (britanski)

- Nema roda; `mnozina` za imenice (`children`, `knives`, `potatoes`, `—` za nebrojive,
  `trousers` → `trousers`).
- Pridjevi: `komparativ` i `superlativ` bez *the* (`bigger` / `biggest`, `more interesting` /
  `most interesting`, `good` → `better` / `best`); nestupnjevani (`married`, nacionalnosti,
  `perfect`) `—`.
- Glagoli: `preterit` (past simple) i `particip` (past participle), britanski pravopis
  (`travelled`, `learnt / learned`). Riječi koje su same oblik drugog glagola (`went`, `been`) i
  modalni glagoli (`must`, `should`) imaju `—`; `can` → `could` / `—`.
- `ing`: oblik na -ing zbog pravopisa (`making`, `running`, `lying`, `travelling`, `seeing`).

### Latinski (klasični, makroni)

- `rod`: `m` / `f` / `n` / `m,f` (zajednički rod: `cīvis`, `canis`, `comes`).
- `genitiv`: cijeli oblik genitiva jednine (`rosae`, `rēgis`, `diēī`); za riječi samo u množini
  genitiv množine (`castrōrum`, `līberōrum`, `Īduum`).
- `deklinacija`: `1`–`5` za imenice; za pridjeve `1-2` ili `3`.
- `oblici_pr`: rječnički oblik — tri završetka `bonus, bona, bonum` / `ācer, ācris, ācre`, dva
  `fortis, forte`, jedan s genitivom `fēlīx, gen. fēlīcis`; komparativi `maior, maius`.
- `konjugacija`: `1`, `2`, `3`, `3io` (*capiō*), `4`, `nepr` (*sum, eō, ferō, volō* … i riječi
  koje su oblik drugog glagola: `est`, `fuī`).
- `glavni_oblici`: infinitiv, perfekt, supin (`amāre, amāvī, amātum`); deponenti
  `loquī, locūtus sum`; bez supina dva oblika (`timēre, timuī`); oblici drugog glagola `—`.

### Esperanto

Imenice, pridjevi i glagoli potpuno su pravilni (-oj, -n, -as/-is/-os), pa im oblici ne trebaju.
Jedini stupac je `prelaznost` glagola (`tr` / `ntr` / `tr,ntr`, prema PIV-u), jer o njoj ovisi
akuzativ i tvorba s -igi / -iĝi (-iĝi je uvijek `ntr`, -igi uvijek `tr`).

### Interslavenski

- `rod`: `m` / `m.ž` (muški živi: osobe i životinje, akuzativ = genitiv) / `f` / `n`.
- `rod` i `vid` (`ipf` / `pf` / `ipf,pf`) uzimaju se iz zaključane baze
  (odluka ISV2); dvoznačne natuknice riješene ručno prema značenju u stupcu `en`.
- `prezent`: **2 oblika**, ja · on, po školskom standardu ISV1 (1. lice na -m, kratki oblici):
  `dělam · děla`, `vidim · vidi`, `pišem · piše`, `kupujem · kupuje`; povratni `učim se · uči se`.
  Nepravilna osnova iz baze (polje *addition*: `piše`, `ide`, `vȯzme` → `vozme`), inače po
  pravilu (-ati → -a, -ovati → -uje, -iti/-ěti s osnovom na -i → -i, -ěti → -ěje, -nuti → -ne).
- Imenice i pridjevi su pravilni; nepravilnosti (*člověk – ljudi, oko – oči*) uče se kao riječi.

### Novi jezik

Stupci se biraju po tome što učenik mora naučiti napamet (ono što ne slijedi iz pravila).
Novi stupac dodati u `OBLICI` (vrste riječi) i po potrebi u `VRIJEDNOSTI` (dopuštene vrijednosti
po jeziku) i `PREZENT_LICA` u `provjeri.py`; `gradi.py` prenosi sve stupce bez izmjena.

## Alati

```
python3 alati/gradi.py [fr …]      TSV -> JSONL
python3 alati/provjeri.py [fr …]   provjera, piše IZVJESTAJ.md (izlaz 1 ako ima grešaka)
```

Interslavenski se dodatno provjerava prema zaključanoj bazi (odluka ISV2, commit `53d42b2af`):
`python3 alati/provjeri-isv-baza.py <klon medzuslovjansky/database>` (upute u zaglavlju skripte).

Provjera javlja grešku za prazno polje, nepoznatu razinu ili vrstu, temu koja ne odgovara razini i
riječ koja se javlja dvaput. Upozorava kad broj riječi u razini odstupa od koncepta više od 10 %.

## Usklađivanje s kralježnicom

Kad za jezik postoji kralježnica (`croland/jezici-plan/XX/`), razina riječi iz `kraljeznica-XX.tsv` je obavezna:

- `python3 alati/provjeri-kraljeznicu.py XX` — greška ako je riječ u rječniku na drugoj razini;
- `python3 alati/premjesti.py XX "riječ" L3 [riječ razina …]` — premješta redak (tema iz `razine-XX.tsv`),
  nakon toga `gradi.py` i `provjeri.py`.

## Faza C — prijevod na jezike sučelja

Svaki jezik sučelja je zasebna datoteka `XX/prijevod-SU-XX.tsv` (stupci `XX | vrsta | SU`), jer će tečaj imati
≈ 10 sučelja (G4), a rječnik iz faze B ostaje jedan. Provjera: `python3 alati/provjeri-prijevod.py XX SU`
(riječ i vrsta moraju postojati u rječniku; izvještaj pokrivenosti po razini).

Pravila prijevoda: imenice u nominativu jednine (množinske riječi u množini), glagoli u infinitivu (vidski par kad
je potreban: *kupiti, kupovati*), pridjevi u muškom rodu; više značenja odvojeno „; “; lažni prijatelji i razlike
prema hrvatskom kratko u zagradi (*le magasin* → „trgovina (ne magazin!)“); standardni hrvatski (VODIC C4.8).

Stanje (10.11.2026.): `fr`, `it`, `es`, `pt`, `isv`, `eo` i `la → hr` **potpuno** (isv s oznakama „lokalizam“ gdje HR riječ zavodi); `en` ima hrvatski od faze A.

## Blobbyjev glas (`blobby-glas-XX.md` u `croland/jezici-plan/XX/`)

`python3 alati/provjeri-blobby.py XX ../croland/jezici-plan/XX/blobby-glas-XX.md ../croland/jezici-plan/XX/XX-gramaticka-kraljeznica.md`

U tim datotekama *kurziv* je uvijek i samo ciljni jezik. Skripta provjerava da polaznik svaku Blobbyjevu riječ
ciljnog jezika već zna: rječnik na razini ≤ tekuće ili zamrznuta fraza (odj. 6 kralježnice) s „Od“ ≤ tekuće.
Oblici koje rječnik ne navodi (futur, kondicional…) prihvaćaju se u retku „Ručno provjereno: *oblik*“.
