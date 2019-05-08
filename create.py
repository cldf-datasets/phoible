from pathlib import Path
from collections import Counter, OrderedDict, defaultdict
import logging
from hashlib import md5

from clldutils.misc import slug
from clldutils.path import git_describe, read_text, write_text
from pycldf import StructureDataset
from csvw.dsv import reader
from csvw import ForeignKey
from pyglottolog import Glottolog
from pybtex.database import parse_string


def desc(dev, src):
    res = (dev / 'raw-data' / src.upper() / 'README.md').read_text()
    assert res
    return res


def main(scripts, dev, glr):
    cldf_dir = Path('cldf')
    bib = parse_string(read_text(cldf_dir / 'sources.bib'), bib_format='bibtex')
    for _, e in bib.entries.items():
        for field in e.fields:
            e.fields[field] = e.fields[field].replace('\\', '')
    write_text(cldf_dir / 'sources.bib', bib.lower().to_string('bibtex'))

    glottolog = Glottolog(glr)

    ds = StructureDataset.in_dir(cldf_dir)

    def describe_repos(r, org, name=None):
        return OrderedDict([
            ('dc:title', '{0}/{1}'.format(org, name or r.name)),
            ('dc:description', git_describe(r))])

    ds.tablegroup.common_props['prov:wasDerivedFrom'] = [
        describe_repos(dev, 'phoible'),
        describe_repos(scripts, 'bambooforest'),
        describe_repos(glottolog.repos, 'clld'),
    ]
    ds.tablegroup.common_props['prov:wasGeneratedBy'] = describe_repos(
        Path(__file__).parent, 'cldf-datasets', name='phoible')

    ds.add_columns(
        'ValueTable',
        {'name': 'Marginal', 'datatype': 'boolean'},
        {'name': 'Allophones', 'separator': ' '},
        'Contribution_ID')
    features = ["tone","stress","syllabic","short","long","consonantal","sonorant","continuant","delayedRelease","approximant","tap","trill","nasal","lateral","labial","round","labiodental","coronal","anterior","distributed","strident","dorsal","high","low","front","back","tense","retractedTongueRoot","advancedTongueRoot","periodicGlottalSource","epilaryngealSource","spreadGlottis","constrictedGlottis","fortis","raisedLarynxEjective","loweredLarynxImplosive","click"]
    ds.add_component('ParameterTable', 'SegmentClass', *features)
    ds.add_component('LanguageTable', 'Family_Glottocode', 'Family_Name')
    table = ds.add_table(
        'contributions.csv', 
        'ID', 
        'Name', 
        'Contributor_ID', 
        {'name': 'Source', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source', 'separator': ';'},
        'URL',
        {'name': 'count_phonemes', 'required': True, 'datatype': {'base': 'integer', 'minimum': 0}},
        {'name': 'count_consonants', 'required': True, 'datatype': {'base': 'integer', 'minimum': 0}},
        {'name': 'count_vowels', 'required': True, 'datatype': {'base': 'integer', 'minimum': 0}},
        {'name': 'count_tones', 'datatype': {'base': 'integer', 'minimum': 0}, 'null': 'NA'},
    )
    table.tableSchema.primaryKey = ['ID']
    table.tableSchema.foreignKeys.append(ForeignKey.fromdict(dict(
        columnReference='Contributor_ID',
        reference=dict(resource='contributors.csv', columnReference='ID'))))
    table.common_props['dc:conformsTo'] = None
    table = ds.add_table(
        'contributors.csv',
        'ID',
        'Name',
        'Description',
        'Readme',
        'Contents',
        {'name': 'Source', 'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source', 'separator': ';'},
        'URL',
        {'name': 'with_tones', 'datatype': {'base': 'boolean', 'format': '1|0'}},
    )
    table.tableSchema.primaryKey = ['ID']
    table.common_props['dc:conformsTo'] = None

    def read(what):
        return reader(scripts / 'to_cldf' / 'cldf' / what, namedtuples=True)

    languoids = {l.id: l for l in glottolog.languoids()}

    values, segments, languages, inventories, sources = [], [], OrderedDict(), OrderedDict(), []
    with_tones = {}
    for contrib in read('contributors.csv'):
        sources.append(dict(
            ID=contrib.Name,
            Name=contrib.Contributor,
            Description=contrib.Description,
            Readme=desc(dev, contrib.Name),
            Contents=contrib.Contents,
            Source=[c.strip().lower() for c in contrib.Citation.split(';')],
            URL=contrib.SourceURL if contrib.SourceURL != 'NA' else '',
            with_tones=contrib.with_tones == '1',
        ))
        with_tones[contrib.Name] = contrib.with_tones == '1'

    pid_map = {}
    for row in read('parameters.csv'):
        pid = md5(row.Description.encode('utf8')).hexdigest().upper()
        pid_map[row.ID] = (pid, row.SegmentClass)
        segments.append(dict(
            ID=pid,
            Name=row.Name,
            Description=row.Description,
            SegmentClass=row.SegmentClass,
            **{f: getattr(row, f) for f in features}
        ))

    src = {}
    for row in read('contributions.csv'):
        src[row.ID] = row.References.split(';') if row.References != 'no source given' else []
        src[row.ID] = [sid.lower() for sid in src[row.ID]]
        inventories[row.ID] = dict(
            ID=row.ID, 
            Name=row.Name, 
            Contributor_ID=row.Contributor_ID.upper(), 
            URL=row.URI if row.URI != 'NA' else '',
            Source=src[row.ID],
            count_phonemes=0,
            count_consonants=0,
            count_vowels=0,
            count_tones=0,
        )

    uniq, counts = set(), Counter()
    for row in read('values.csv'):
        pk = (row.Language_ID, row.Parameter_ID, row.Contribution_ID)
        if pk in uniq:
            print('skipping duplicate phoneme {0}'.format(pk))
            continue
        uniq.add(pk)
        lid = row.Language_ID if row.Language_ID in languoids else slug(inventories[row.Contribution_ID]['Name'])
        if lid not in languages:
            #
            # FIXME: Language_ID == 'NA' for three inventories! This must be mapped!
            #
            lang = languoids.get(lid)
            fam = lang.lineage[0] if lang and lang.lineage else None
            languages[lid] = dict(
                ID=lid,
                Name=lang.name if lang else None,
                Glottocode=lang.id if lang else None,
                ISO639P3code=row.ISO639P3code if row.ISO639P3code != 'NA' else None,
                Macroarea=lang.macroareas[0].value if lang and lang.macroareas else None,
                Latitude=lang.latitude if lang else None,
                Longitude=lang.longitude if lang else None,
                Family_Glottocode=fam[1] if fam else None,
                Family_Name=fam[0] if fam else None,
            )
        pid, sc = pid_map[row.Parameter_ID]
        counts.update([(row.Contribution_ID, sc)])
        values.append(dict(
            ID=row.ID,
            Language_ID=lid,
            Parameter_ID=pid,
            Contribution_ID=row.Contribution_ID,
            Value=row.Name,
            Marginal=None if row.Marginal == 'NA' else eval(row.Marginal.lower().capitalize()),  # FALSE|TRUE|NA
            Allophones=row.Allophones.split() if row.Allophones != 'NA' else [],
            Source=src[row.Contribution_ID],
        ))
    for key, count in counts.items():
        inventories[key[0]]['count_{0}s'.format(key[1])] = count
        inventories[key[0]]['count_phonemes'] += count

    for inv in inventories.values():
        if not with_tones[inv['Contributor_ID']]:
            assert inv['count_tones'] == 0
            inv['count_tones'] = 'NA'

    ds.write(**{
        'ValueTable': values,
        'LanguageTable': languages.values(),
        'ParameterTable': segments,
        'contributions.csv': inventories.values(),
        'contributors.csv': sources
    })
    ds.validate(logging.getLogger(__name__))


if __name__ == '__main__':
    main(
        Path('../phoible-scripts'),
        Path('../phoible-dev'),
        Path('../../glottolog/glottolog'),
    )
