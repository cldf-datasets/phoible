# The PHOIBLE Database as CLDF StructureDataset

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

