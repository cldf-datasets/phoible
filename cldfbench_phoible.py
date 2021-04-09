import re
import hashlib
import pathlib
import itertools
import subprocess
import collections
import unicodedata

from pybtex import errors, database
import attr
from csvw import dsv
from csvw.metadata import ForeignKey, Datatype
from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFSpec
from cldfcatalog import Repository


def na_is_none(s):
    return None if s == 'NA' else s


@attr.s
class Doculect:
    Glottocode = attr.ib(converter=na_is_none)
    ISO6393 = attr.ib(converter=na_is_none)
    LanguageName = attr.ib()
    SpecificDialect = attr.ib(converter=na_is_none)
    Source = attr.ib(converter=lambda s: s.upper())

    @classmethod
    def from_row(cls, row):
        return cls(**{k: v for k, v in row.items() if k in attr.fields_dict(cls)})

    @property
    def name(self):
        if self.SpecificDialect:
            return '{0.LanguageName} ({0.SpecificDialect})'.format(self)
        return self.LanguageName


@attr.s
class Phoneme:
    GlyphID = attr.ib()
    Phoneme = attr.ib()
    Allophones = attr.ib(converter=lambda s: [] if (not s) or (s == 'NA') else s.split())
    Marginal = attr.ib(converter=lambda s: None if s == 'NA' else (True if s == 'True' else False))
    SegmentClass = attr.ib(validator=attr.validators.in_(['consonant', 'vowel', 'tone']))
    features = attr.ib()
    Description = attr.ib(default=None)

    def __attrs_post_init__(self):
        res = [self.GlyphID, self.Phoneme, self.SegmentClass]
        res.extend([v for k, v in sorted(self.features.items())])
        self._key = tuple(res)
        self.Description = ' - '.join(unicodedata.name(c) for c in self.Phoneme)

    def is_same(self, other):
        return self._key == other._key

    @classmethod
    def from_row(cls, row):
        attrs = {k: v for k, v in row.items() if k in attr.fields_dict(cls)}
        attrs['features'] = {k: v for k, v in row.items() if k[0] == k[0].lower()}
        return cls(**attrs)

    @property
    def pid(self):
        return hashlib.md5(self.Description.encode('utf8')).hexdigest().upper()


def iter_inventories(p):
    """
    Read the raw PHOIBLE data file, splitting rows into inventory, language and phoneme information
    and grouping the data by inventory.
    """
    for iid, rows in itertools.groupby(
        sorted(dsv.reader(p, dicts=True), key=lambda r: int(r['InventoryID'])),
        lambda r: r['InventoryID'],
    ):
        rows = list(rows)
        yield iid, Doculect.from_row(rows[0]), [Phoneme.from_row(row) for row in rows]


def desc(dev, src):
    res = (dev / 'raw-data' / src.upper() / 'README.md').read_text()
    # FIXME: should we try to make links portable?
    assert res
    return res


def glang_attrs(glang, languoids):
    """
    Enrich language metadata with attributes we can fetch from Glottolog.
    """
    res = {k: None for k in 'Macroarea,Latitude,Longitude,Family_Glottocode,Family_Name'.split(',')}
    if glang.latitude is None:
        if glang.level.name == 'dialect':
            for _, gc, _ in reversed(glang.lineage):
                if languoids[gc].latitude is not None:
                    res['Latitude'] = languoids[gc].latitude
                    res['Longitude'] = languoids[gc].longitude
                    break
    else:
        res['Latitude'] = glang.latitude
        res['Longitude'] = glang.longitude

    if glang.lineage:
        flang = languoids[glang.lineage[0][1]]
        res['Family_Glottocode'] = flang.id
        res['Family_Name'] = flang.name

    if not glang.macroareas:
        if glang.level.name == 'dialect':
            for _, gc, _ in reversed(glang.lineage):
                if languoids[gc].macroareas:
                    res['Macroarea'] = languoids[gc].macroareas[0].name
                    break
    else:
        res['Macroarea'] = glang.macroareas[0].name

    return res


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "phoible"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        subprocess.check_call(
            'git -C {} submodule update --remote'.format(self.dir.resolve()), shell=True)

    def cmd_makecldf(self, args):
        dev = self.raw_dir / 'dev'
        bibdata = database.parse_file(str(dev.joinpath('data', 'phoible-references.bib')))
        args.writer.cldf.add_sources(bibdata)
        feature_values = collections.defaultdict(set)

        iid2sid = collections.defaultdict(list)
        iid2url = {}
        for row in dsv.reader(dev / 'mappings' / 'InventoryID-Bibtex.csv', dicts=True):
            if row['BibtexKey'] != 'NO SOURCE GIVEN':
                iid2sid[row['InventoryID']].append(row['BibtexKey'])
            if row['URI'] != 'NA':
                iid2url[row['InventoryID']] = row['URI']

        glangs = {l.id: l for l in args.glottolog.api.languoids()}

        self.create_schema(args.writer.cldf)
        contributors = {r['ID'].lower(): r for r in self.etc_dir.read_csv('contributors.csv', dicts=True)}
        for cid in contributors:
            contributors[cid]['Readme'] = desc(dev, cid)
            contributors[cid]['with_tones'] = contributors[cid]['with_tones'] == '1'
            contributors[cid]['Source'] = [s.strip() for s in contributors[cid]['Source'].split(';')]
            contributors[cid]['URL'] = contributors[cid]['SourceURL']
        args.writer.objects['inventory_sources.csv'] = [
            {k: v for k, v in c.items() if k in [
                'ID', 'Name', 'Description', 'Readme', 'Contents', 'Source', 'URL', 'with_tones']}
            for c in contributors.values()]
        lids, nogc, pids, sid = set(), 0, {}, 0
        for iid, doculect, phonemes in iter_inventories(
                self.raw_dir / 'dev' / 'data' / 'phoible.csv'):
            if not doculect.Glottocode:
                nogc += 1
                lid = 'l{}'.format(nogc)
            else:
                lid = doculect.Glottocode
            if lid not in lids:
                lids.add(lid)
                args.writer.objects['LanguageTable'].append(dict(
                    ID=lid,
                    Name=glangs[doculect.Glottocode].name if doculect.Glottocode else doculect.LanguageName,
                    Glottocode=doculect.Glottocode,
                    ISO639P3code=doculect.ISO6393 or None,
                    **glang_attrs(glangs[doculect.Glottocode], glangs) if doculect.Glottocode else {},
                ))
            args.writer.objects['inventories.csv'].append(dict(
                ID=iid,
                Name=doculect.name,
                Inventory_source_ID=doculect.Source,
                Source=iid2sid.get(iid, []),
                URL=iid2url.get(iid),
                count_phonemes=len(phonemes),
                count_vowels=sum([1 for p in phonemes if p.SegmentClass == 'vowel']),
                count_consonants=sum([1 for p in phonemes if p.SegmentClass == 'consonant']),
                count_tones=sum([1 for p in phonemes if p.SegmentClass == 'tone']),
            ))
            for phoneme in phonemes:
                for k, v in phoneme.features.items():
                    feature_values[k].add(v)
                if phoneme.pid not in pids:
                    pids[phoneme.pid] = phoneme
                    args.writer.objects['ParameterTable'].append(dict(
                        ID=phoneme.pid,
                        Name=phoneme.Phoneme,
                        Description=phoneme.Description,
                        SegmentClass=phoneme.SegmentClass,
                        **phoneme.features
                        # FIXME: link to CLTS/BIPA
                    ))
                else:
                    assert pids[phoneme.pid].is_same(phoneme)
                sid += 1
                args.writer.objects['ValueTable'].append(dict(
                    ID=str(sid),
                    Language_ID=lid,
                    Inventory_ID=iid,
                    Parameter_ID=phoneme.pid,
                    Value=phoneme.Phoneme,
                    Source=iid2sid.get(iid, []),
                    Marginal=phoneme.Marginal,
                    Allophones=phoneme.Allophones,
                ))
        args.writer.objects['ParameterTable'] = sorted(
            args.writer.objects['ParameterTable'],
            key=lambda r: r['Name'],
        )
        for k, v in feature_values.items():
            col = args.writer.cldf['ParameterTable', k]
            col.datatype = Datatype.fromvalue(dict(base='string', format='|'.join([re.escape(vv) for vv in v])))

    def create_schema(self, ds):
        ds.add_provenance(wasDerivedFrom=Repository(self.raw_dir / 'dev').json_ld())
        ds.properties['dc:description'] = """\
PHOIBLE's phoneme inventories are modeled as follows:
- Phonemes are rows in `ParameterTable`
- Inventories are rows in `inventories.csv`
- Each row in `ValueTable` marks a Phoneme as member of an inventory
"""
        ds.add_columns(
            'ValueTable',
            {
                'name': 'Marginal',
                'dc:description':
                    "Marginal phonemes are those that are notably different phonologically from "
                    "the majority of segments found in a particular language. For example, "
                    "loanwords containing non-native sounds can introduce marginal phonemes into "
                    "the borrowing language. Any type of phoneme described as “marginal”, "
                    "“dubious” or “occurs only in loan words” is included in the database "
                    "alongside other phonemes, but is marked with a boolean 'True' value. "
                    "Ordinary phonemes typically have the value 'False', although for data sources "
                    "that explicitly exclude marginal phonemes, the value is NULL, i.e. ''.",
                'datatype': {'base': 'boolean', 'format': 'True|False'}},
            {
                'name': 'Allophones',
                'dc:description':
                    "If a phonological description includes some information about allophonic "
                    "alternations, it is assumed that phonemes with no allophones mentioned do "
                    "not exhibit “major” allophonic variation (in the judgment of the original "
                    "author(s) of the language description). For such phonemes, the sole "
                    "allophone is treated as identical with the phonemic representation. In "
                    "phonological descriptions where *no* information about allophonic alternations "
                    "was given about *any* of the phonemes, the description is considered "
                    "incomplete with regard to allophonic information, and all phonemes of that "
                    "inventory are given an empty value for their allophones.",
                'separator': ' '},
            'Inventory_ID')
        ds.remove_columns('ValueTable', 'Code_ID', 'Comment')
        features = [
            "tone", "stress", "syllabic", "short", "long", "consonantal", "sonorant", "continuant",
            "delayedRelease", "approximant", "tap", "trill", "nasal", "lateral", "labial", "round",
            "labiodental", "coronal", "anterior", "distributed", "strident", "dorsal", "high",
            "low", "front", "back", "tense", "retractedTongueRoot", "advancedTongueRoot",
            "periodicGlottalSource", "epilaryngealSource", "spreadGlottis", "constrictedGlottis",
            "fortis", "raisedLarynxEjective", "loweredLarynxImplosive", "click"]
        table = ds.add_component('ParameterTable', 'SegmentClass', *features)
        table.common_props['dc:description'] = \
            "PHOIBLE includes distinctive feature data for every phoneme in every inventory. The " \
            "feature system was created by the PHOIBLE developers to be descriptively adequate " \
            "cross-linguistically. In other words, if two phonemes differ in their graphemic " \
            "representation, then they should necessarily differ in their featural representation " \
            "as well (regardless of whether those two phonemes coexist in any known doculect). " \
            "The feature system is loosely based on the feature system in Hayes (2009) with some " \
            "additions drawn from Moisik & Esling (2011)."
        ds.add_component(
            'LanguageTable',
            {
                'name': 'Family_Glottocode',
                'dc:description': "Glottocode of the top-level family this variety belongs to."
            },
            {
                'name': 'Family_Name',
                'dc:description': "Name of the top-level family this variety belongs to."
            },
        )
        table = ds.add_table(
            'inventories.csv',
            {'name': 'ID', 'propertyUrl': "http://cldf.clld.org/v1.0/terms.rdf#id"},
            {'name': 'Name', 'propertyUrl': "http://cldf.clld.org/v1.0/terms.rdf#name"},
            'Inventory_source_ID',
            {'name': 'Source', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source', 'separator': ';'},
            'URL',
            {'name': 'count_phonemes', 'required': True, 'datatype': {'base': 'integer', 'minimum': 0}},
            {'name': 'count_consonants', 'required': True, 'datatype': {'base': 'integer', 'minimum': 0}},
            {'name': 'count_vowels', 'required': True, 'datatype': {'base': 'integer', 'minimum': 0}},
            {'name': 'count_tones', 'datatype': {'base': 'integer', 'minimum': 0}, 'null': 'NA'},
        )
        table.tableSchema.primaryKey = ['ID']
        table.tableSchema.foreignKeys.append(ForeignKey.fromdict(dict(
            columnReference='Inventory_source_ID',
            reference=dict(resource='inventory_sources.csv', columnReference='ID'))))
        table.common_props['dc:conformsTo'] = None
        table.common_props['dc:description'] = \
            "This table lists the phoneme inventories which are aggregated in PHOIBLE"
        table = ds.add_table(
            'inventory_sources.csv',
            {'name': 'ID', 'propertyUrl': "http://cldf.clld.org/v1.0/terms.rdf#id"},
            {'name': 'Name', 'propertyUrl': "http://cldf.clld.org/v1.0/terms.rdf#name"},
            {'name': 'Description', 'propertyUrl': "http://cldf.clld.org/v1.0/terms.rdf#description"},
            'Readme',
            {
                'name': 'Contents',
                'dc:description': "Semi-structured description of the contents of inventories from"
                                  "this contribution",
            },
            {'name': 'Source', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source', 'separator': ';'},
            'URL',
            {
                'name': 'with_tones',
                'dc:description': "1 if the inventories from this source contain"
                                  "tones, 0 if tone is systematically left out.",
                'datatype': {'base': 'boolean', 'format': '1|0'}
            },
        )
        table.tableSchema.primaryKey = ['ID']
        table.common_props['dc:conformsTo'] = None
        ds.add_foreign_key('ValueTable', 'Inventory_ID', 'inventories.csv', 'ID')
