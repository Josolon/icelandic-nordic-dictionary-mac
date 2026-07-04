# Credits

This project compiles local build tooling around the ISLEX dataset. All
lexicographic work belongs entirely to the people and institutions below —
this repository only contains scripts that convert their data into a local
Apple Dictionary format.

## Dataset used by this project

- **ISLEX — Icelandic-Scandinavian multilingual dictionary (2023-12 release)**
- Editors of record (dataset creators, per the CLARIN-IS catalog entry):
  **Þórdís Úlfarsdóttir**, **Halldóra Jónsdóttir**, **Jón Hilmar Jónsson**
- Publisher: Stofnun Árna Magnússonar í íslenskum fræðum (The Árni Magnússon
  Institute for Icelandic Studies), Reykjavík
- Persistent record: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/319
- License: **CC BY-NC-ND 4.0** — https://creativecommons.org/licenses/by-nc-nd/4.0/
  (this is *why* this project only distributes build tooling, never compiled
  dictionaries or the source data itself — see LICENSE)

Suggested citation:

> Úlfarsdóttir, Þórdís, Halldóra Jónsdóttir og Jón Hilmar Jónsson (ritstj.).
> *ISLEX — Icelandic-Scandinavian multilingual dictionary* (2023-12).
> Stofnun Árna Magnússonar í íslenskum fræðum / CLARIN-IS.
> http://hdl.handle.net/20.500.12537/319

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
attribution beyond the two/three names recorded as formal dataset creators
in the CLARIN catalog entry:

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

## A note on data versions and licensing

This project builds from the **2023-12** ISLEX release (CC BY-NC-ND 4.0,
handle `.../319`), which is why this repository is build-tooling-only and
never distributes compiled dictionaries.

A **newer 2026-02 release** exists (handle
`.../376`, https://repository.clarin.is/repository/xmlui/handle/20.500.12537/376),
credited to Þórdís Úlfarsdóttir and Halldóra Jónsdóttir, and licensed under
**CC BY-SA 4.0** instead — a materially more permissive, share-alike license
that would change what this project is legally allowed to do (e.g.
redistribution with attribution, under share-alike terms). This project has
**not** been migrated to that release; doing so would be a deliberate,
separate decision (new source data, re-verify the license terms directly
before relying on this note, and likely a version bump across the whole
build pipeline).

## Tooling and Packaging

- Dictionary conversion/build scripts and packaging in this repository:
  Jónatan Sólon and contributors.

## License Reminder

ISLEX 2023-12 (the version this project uses) is CC BY-NC-ND 4.0: personal,
non-commercial use only, no redistribution of the source data or of any
compiled dictionary bundle built from it. See LICENSE for full detail.
