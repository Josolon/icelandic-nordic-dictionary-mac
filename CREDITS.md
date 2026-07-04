# Credits

This project compiles local build tooling around the ISLEX dataset. All
lexicographic work belongs entirely to the people and institutions below —
this repository only contains scripts that convert their data into a local
Apple Dictionary format.

## Dataset used by this project

- **ISLEX — Icelandic-Scandinavian multilingual dictionary (2026-02 release)**
- Editors of record (dataset authors, per the dataset's own embedded metadata):
  **Þórdís Úlfarsdóttir**, **Halldóra Jónsdóttir**
- Publisher: Stofnun Árna Magnússonar í íslenskum fræðum (The Árni Magnússon
  Institute for Icelandic Studies), Reykjavík
- Persistent record: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/376
- License: **CC BY-SA 4.0** — https://creativecommons.org/licenses/by-sa/4.0/
  (attribution + share-alike; redistribution of derivatives, including
  compiled dictionary bundles, is allowed under the same license — see LICENSE)

Suggested citation:

> Úlfarsdóttir, Þórdís og Halldóra Jónsdóttir (ritstj.).
> *ISLEX — Icelandic-Scandinavian multilingual dictionary* (2026-02).
> Stofnun Árna Magnússonar í íslenskum fræðum / CLARIN-IS.
> http://hdl.handle.net/20.500.12537/376

## Participating institutions

Per the ISLEX project's own description, ISLEX is a collaboration between
research and university institutions in six countries. Each country's team
is independently responsible for its own target language:

| Country | Institution | Location |
|---|---|---|
| Iceland | Stofnun Árna Magnússonar í íslenskum fræðum (The Árni Magnússon Institute for Icelandic Studies) — source-language (Icelandic) editorial team and system development | Reykjavík |
| Denmark | Det Danske Sprog- og Litteraturselskab (Society for Danish Language and Literature) | Copenhagen |
| Sweden | Institutionen för svenska språket, Göteborgs universitet (Dept. of Swedish, University of Gothenburg) | Gothenburg |
| Norway | Institutt for lingvistiske, litterære og estetiske studier, Universitetet i Bergen (Dept. of Linguistic, Literary and Aesthetic Studies, University of Bergen) | Bergen |
| Faroe Islands | Fróðskaparsetur Føroya (University of the Faroe Islands) | Tórshavn |
| Finland | Háskólinn í Helsinki (University of Helsinki) | Helsinki |

The Icelandic team is responsible for the source language and the
underlying database/system; each Nordic partner institution's editorial
team is independently responsible for translating into and maintaining its
own target language.

## Additional documented contributors

The following people are named as ISLEX project contributors in the
project's own published literature (cited below); listed here for fuller
attribution beyond the names recorded as formal dataset creators in the
dataset's own metadata:

- **Jón Hilmar Jónsson** — credited as a dataset editor on the prior
  **2023-12** ISLEX release (the version this project used before migrating
  to 2026-02); no longer listed as an author on the 2026-02 metadata, but
  his earlier editorial contribution to ISLEX is part of its history.
- **Aldís Sigurðardóttir**, **Anna Hannesdóttir**, **Håkan Jansson**,
  **Lars Trap-Jensen** — co-authors, *ISLEX - An Icelandic-Scandinavian
  Multilingual Online Dictionary*, Proceedings of the XIII Euralex
  International Congress, 2008.
- **Margunn Rauset** — co-author (with Aldís Sigurðardóttir and Anna
  Hannesdóttir), *En-, två- eller flerspråkig ordbok?*, Nordiska studier i
  lexikografi 11, 2011.
- **Kristín Bjarnadóttir** — led "Norræna verkefnið" (1994–), the earlier
  Orðabók Háskólans project that ISLEX grew out of.

Source: Úlfarsdóttir, Þórdís. *ISLEX – norræn margmála orðabók*, 2012.
https://islex.is/greinar/islex2012-OogT.pdf

## Data version history (as used by this project)

| Version | Handle | License | Editors of record |
|---|---|---|---|
| 2023-12 | `.../319` | CC BY-NC-ND 4.0 | Þórdís Úlfarsdóttir, Halldóra Jónsdóttir, Jón Hilmar Jónsson |
| **2026-02 (current)** | `.../376` | **CC BY-SA 4.0** | Þórdís Úlfarsdóttir, Halldóra Jónsdóttir |

This project originally built from the 2023-12 release and has since
migrated to 2026-02, which added ~55 entries, removed ~31, and revised
roughly 4,700 more (translation/example corrections, expanded Norwegian
Bokmål/Nynorsk coverage) — verified directly against both XML dumps before
migrating, not assumed from changelog text.

## Tooling and Packaging

- Dictionary conversion/build scripts and packaging in this repository:
  Jónatan Sólon and contributors.

## Compiled bundles

Compiled `.dictionary` bundles built from this data are published at
https://github.com/Josolon/icelandic-nordic-dictionary-mac/releases —
each bundle is itself CC BY-SA 4.0 (see LICENSE's "This Repository's Data
License" section); if you redistribute one further, keep this attribution
and the same license with it.

## License Reminder

ISLEX 2026-02 (the version this project uses) is CC BY-SA 4.0: attribution
required, and any redistributed derivative (including a compiled dictionary
bundle) must carry the same CC BY-SA 4.0 license. See LICENSE for full detail.
