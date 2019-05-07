# The PHOIBLE Database as CLDF StructureDataset

[![Build Status](https://travis-ci.org/cldf-datasets/phoible.svg?branch=master)](https://travis-ci.org/cldf-datasets/phoible)

This dataset provides the data of PHOIBLE, which is curated at
https://github.com/phoible/dev
as [CLDF](https://cldf.clld.org) StructureDataset. This CLDF data is
browsable online at https://phoible.org

The semantics of the CSV files in the `cldf` directory are as follows:

- `languages.csv` - a CLDF LanguageTable - provides metadata about Glottolog 3.3.2
  languoids for which PHOIBLE has information on phoneme inventories.
- `parameters.csv` - a CLDF ParameterTable - provides information about segments
  which appear in these phoneme inventories, including features.
- `contributors.csv` - provides information about the (secondary) sources of 
  phoneme inventories aggregated in PHOIBLE.
- `contributions.csv` - provides information about individual phoneme inventories.
- `values.csv` - provides the actual inventory data, i.e. each row represents a
  single phoneme found in a particular inventory, by refrencing:
  - a language in languages.csv
  - an inventory in contributions.csv
  - a segment in parameters.csv


## Summary statistics

Summary statistics can easily be computed using the [pycldf](https://pypi.org/project/pycldf/) package (>=1.6.1):

Create a SQLite database loaded with the CLDF dataset using the `cldf` command which has been installed together with `pycldf`:
```bash
cldf createdb cldf/StructureDataset-metadata.json
```

Now you can query the data in SQL, which means easily join data from multiple tables.
The query
```sql
SELECT
    c.cldf_id AS Inventory_ID,
    l.cldf_iso639P3code AS ISO639P3code,
    l.cldf_glottocode AS Glottocode,
    count(v.cldf_id) AS phonemes,
    sum(CASE WHEN p.segmentclass = 'consonant' THEN 1 ELSE 0 END) AS consonants,
    sum(CASE WHEN p.segmentclass = 'vowel' THEN 1 ELSE 0 END) AS vowels,
    CASE WHEN cc.with_tones = 1 THEN sum(CASE WHEN p.segmentclass = 'tone' THEN 1 ELSE 0 END) ELSE 'NA' END AS tones
FROM
    `contributions.csv` AS c,
    `contributors.csv` AS cc,
    languagetable AS l,
    valuetable AS v,
    parameterTable AS p
WHERE
    v.cldf_languageReference = l.cldf_id
    and v.cldf_parameterReference = p.cldf_id
    and v.contribution_id = c.cldf_id
    and c.contributor_id = cc.cldf_id
GROUP BY
    c.cldf_id
ORDER BY
    cast(c.cldf_id AS int);
```
can be saved in a file `stats.sql` and then run via the `sqlite3` command
```bash
cat stats.sql | sqlite3 -csv -header phoible.sqlite > stats.csv
```
to create output which looks like
```bash
$ head stats.csv 
Inventory_ID,ISO639P3code,Glottocode,phonemes,consonants,vowels,tones
1,kor,kore1280,40,22,18,0
2,ket,kett1243,32,18,14,0
3,lbe,lakk1252,69,60,9,0
4,kbd,kaba1278,56,49,7,0
5,kat,nucl1302,35,29,6,0
6,bsk,buru1296,53,38,12,3
7,kru,kuru1302,68,46,22,0
8,tel,telu1262,68,47,21,0
9,kfe,kota1263,34,23,11,0
```

Note that the `tones` column will either list the number of tones in the inventory, or `NA` if the source of the inventory 
does not have information about tone.
