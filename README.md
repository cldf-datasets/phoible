# The PHOIBLE Database as CLDF StructureDataset

This dataset provides [PHOIBLE 2.0](https://phoible.org) serialized as
[CLDF](https://cldf.clld.org) StructureDataset. The semantics of the
CSV files in the cldf directory are as follows:

- languages.csv - a CLDF LanguageTable - provides metadata about Glottolog
  languoids for which PHOIBLE has information on phoneme inventories.
- parameters.csv - a CLDF ParameterTable - provides information about segments
  which appear in these phoneme inventories, including features.
- contributors.csv - provides information about the (secondary) sources of 
  phoneme inventories aggregated in PHOIBLE.
- contributions.csv - provides information about individual phoneme inventories.
- values.csv - provides the actual inventory data, i.e. each row represents a
  single phoneme found in a particular inventory, by refrencing:
  - a language in languages.csv
  - an inventory in contributions.csv
  - a segment in parameters.csv

