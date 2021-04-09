<a name="ds-structuredatasetmetadatajson"> </a>

# StructureDataset PHOIBLE

**CLDF Metadata**: [StructureDataset-metadata.json](./StructureDataset-metadata.json)

**Sources**: [sources.bib](./sources.bib)

PHOIBLE's phoneme inventories are modeled as follows:
- Phonemes are rows in `ParameterTable`
- Inventories are rows in `inventories.csv`
- Each row in `ValueTable` marks a Phoneme as member of an inventory


property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF StructureDataset](http://cldf.clld.org/v1.0/terms.rdf#StructureDataset)
[dc:identifier](http://purl.org/dc/terms/identifier) | https://phoible.org/
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/cldf-datasets/phoible
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/phoible/dev/tree/435f657">phoible/dev v2.0-54-g435f657</a></li><li><a href="https://github.com/cldf-datasets/phoible/tree/7cde4cb">cldf-datasets/phoible v2.0.1-1-g7cde4cb</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v4.3">Glottolog v4.3</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.8.5</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | phoible
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-valuescsv"></a>Table [values.csv](./values.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ValueTable](http://cldf.clld.org/v1.0/terms.rdf#ValueTable)
[dc:extent](http://purl.org/dc/terms/extent) | 105459


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | References [parameters.csv::ID](#table-parameterscsv)
[Value](http://cldf.clld.org/v1.0/terms.rdf#value) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
`Marginal` | `boolean` | Marginal phonemes are those that are notably different phonologically from the majority of segments found in a particular language. For example, loanwords containing non-native sounds can introduce marginal phonemes into the borrowing language. Any type of phoneme described as “marginal”, “dubious” or “occurs only in loan words” is included in the database alongside other phonemes, but is marked with a boolean 'True' value. Ordinary phonemes typically have the value 'False', although for data sources that explicitly exclude marginal phonemes, the value is NULL, i.e. ''.
`Allophones` | list of `string` (separated by ` `) | If a phonological description includes some information about allophonic alternations, it is assumed that phonemes with no allophones mentioned do not exhibit “major” allophonic variation (in the judgment of the original author(s) of the language description). For such phonemes, the sole allophone is treated as identical with the phonemic representation. In phonological descriptions where *no* information about allophonic alternations was given about *any* of the phonemes, the description is considered incomplete with regard to allophonic information, and all phonemes of that inventory are given an empty value for their allophones.
`Inventory_ID` | `string` | References [inventories.csv::ID](#table-inventoriescsv)

## <a name="table-parameterscsv"></a>Table [parameters.csv](./parameters.csv)

PHOIBLE includes distinctive feature data for every phoneme in every inventory. The feature system was created by the PHOIBLE developers to be descriptively adequate cross-linguistically. In other words, if two phonemes differ in their graphemic representation, then they should necessarily differ in their featural representation as well (regardless of whether those two phonemes coexist in any known doculect). The feature system is loosely based on the feature system in Hayes (2009) with some additions drawn from Moisik & Esling (2011).

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable)
[dc:extent](http://purl.org/dc/terms/extent) | 3164


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
`SegmentClass` | `string` | 
`tone` | `string` | 
`stress` | `string` | 
`syllabic` | `string` | 
`short` | `string` | 
`long` | `string` | 
`consonantal` | `string` | 
`sonorant` | `string` | 
`continuant` | `string` | 
`delayedRelease` | `string` | 
`approximant` | `string` | 
`tap` | `string` | 
`trill` | `string` | 
`nasal` | `string` | 
`lateral` | `string` | 
`labial` | `string` | 
`round` | `string` | 
`labiodental` | `string` | 
`coronal` | `string` | 
`anterior` | `string` | 
`distributed` | `string` | 
`strident` | `string` | 
`dorsal` | `string` | 
`high` | `string` | 
`low` | `string` | 
`front` | `string` | 
`back` | `string` | 
`tense` | `string` | 
`retractedTongueRoot` | `string` | 
`advancedTongueRoot` | `string` | 
`periodicGlottalSource` | `string` | 
`epilaryngealSource` | `string` | 
`spreadGlottis` | `string` | 
`constrictedGlottis` | `string` | 
`fortis` | `string` | 
`raisedLarynxEjective` | `string` | 
`loweredLarynxImplosive` | `string` | 
`click` | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 2177


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal` | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal` | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string` | 
`Family_Glottocode` | `string` | Glottocode of the top-level family this variety belongs to.
`Family_Name` | `string` | Name of the top-level family this variety belongs to.

## <a name="table-inventoriescsv"></a>Table [inventories.csv](./inventories.csv)

This table lists the phoneme inventories which are aggregated in PHOIBLE

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 3020


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
`Inventory_source_ID` | `string` | References [inventory_sources.csv::ID](#table-inventorysourcescsv)
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
`URL` | `string` | 
`count_phonemes` | `integer` | 
`count_consonants` | `integer` | 
`count_vowels` | `integer` | 
`count_tones` | `integer` | 

## <a name="table-inventorysourcescsv"></a>Table [inventory_sources.csv](./inventory_sources.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 10


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
`Readme` | `string` | 
`Contents` | `string` | Semi-structured description of the contents of inventories fromthis contribution
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
`URL` | `string` | 
`with_tones` | `boolean` | 1 if the inventories from this source containtones, 0 if tone is systematically left out.

