import bz2
import csv
import os.path
import shutil
import logging
from time import mktime

from django.conf import settings

import commonware.log
import cronjobs

from input import PRODUCT_IDS
from feedback.models import Opinion
from input import OPINION_TYPES


BUCKET_SIZE = 10000  # Bucket size to split query set into.
log = commonware.log.getLogger('i.export_tsv')


class TSVDialect(csv.Dialect):
    """*Tab* separated values."""
    delimiter = "\t"
    escapechar = "\\"
    doublequote = False
    lineterminator = "\n"
    quoting = csv.QUOTE_NONE
    quotechar = None


def _fix_row(row):
    """Convert row to UTF-8 and strip instances of CRLF."""
    return map(lambda x: (x if not isinstance(x, basestring) else
                          x.replace("\r\n", "\n").encode('utf-8')), row)


def _split_queryset(qs):
    """Generator splitting a queryset into buckets."""
    start = 0
    end = BUCKET_SIZE
    while True:
        split = qs[start:end]
        if split:
            yield split
        else:
            raise StopIteration

        start = end
        end = end + BUCKET_SIZE


@cronjobs.register
def export_tsv():
    """
    Exports a complete dump of the Opinions table to disk, in
    TSV format.
    """
    opinions_path = os.path.join(settings.TSV_EXPORT_DIR, 'opinions.tsv.bz2')
    opinions_tmp = '%s_exporting' % opinions_path
    log.info('Dumping all opinions into TSV file %s.', opinions_path)

    opinions = Opinion.objects.order_by('id')
    try:
        outfile = bz2.BZ2File(opinions_tmp, 'w')
        tsv = csv.writer(outfile, dialect=TSVDialect)
        for bucket in _split_queryset(opinions):
            for opinion in bucket:
                try:
                    tsv.writerow(_fix_row([
                        opinion.id,
                        int(mktime(opinion.created.timetuple())),
                        getattr(OPINION_TYPES.get(opinion._type), 'short', None),
                        getattr(PRODUCT_IDS.get(opinion.product), 'short', None),
                        opinion.version,
                        opinion.platform,
                        opinion.locale,
                        opinion.manufacturer,
                        opinion.device,
                        opinion.url,
                        opinion.description,
                    ]))
                except Exception, e:
                    log.warning('Error exporting opinion %d: %s' % (
                        opinion.id, str(e)))
    finally:
        outfile.close()
    shutil.move(opinions_tmp, opinions_path)
    log.info('All opinions dumped to disk.')
