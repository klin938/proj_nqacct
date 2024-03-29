import os, sys, argparse,logging

from config.definitions import LOG_FORMATTER
from config.definitions import PRELOAD_USER_DEPARTMENTS
from config.definitions import PRELOAD_USER_MANAGERS
from nqacct.common.utils import valid_path
import nqacct.qacct2dict.builder as dict_builder
import nqacct.reporting.df_reporter as reporter

def main(argv):
    print('args=%s' % args)
    if args.groupby == 'ad_dept':
        dict_builder.init(args.input, args.groupby, args.grouplist, args.period, args.years, PRELOAD_USER_DEPARTMENTS)
    elif args.groupby == 'ad_manager':
        dict_builder.init(args.input, args.groupby, args.grouplist, args.period, args.years, PRELOAD_USER_MANAGERS)
    else:
        dict_builder.init(args.input, args.groupby, args.grouplist, args.period, args.years, None)
    data = dict_builder.build()
    logger.debug('Criteria: groupby-{} | {} | {}'.format(dict_builder.groupby,dict_builder.grouplist,dict_builder.years))
    reporter.init(data)
    report = reporter.usage_yearly_group_summary('group', 'submission_time', 'cpuhours')
    print('\n\n{}'.format(report))

    os.makedirs(args.outdir, exist_ok=True)
    report.to_csv(args.outdir + args.cluster + '_yearly_summary_' + args.groupby + '_' + str(args.grouplist) + '_' + str(args.years) +'.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True, type=valid_path, help='path to the source of input')
    parser.add_argument('--outdir', default='./outdir/', help='path for the output files (default: ./outdir/)')
    parser.add_argument('-c', '--cluster', required=True, choices=['wolfpack60', 'wp60', 'wolfpack62', 'wp62','wolfpack70', 'wp70','brenner70', 'br70', 'grandline70', 'gl70'], help='name of cluster for files prefix')
    parser.add_argument('-g', '--groupby', required=True, choices=['user', 'group', 'ad_manager', 'ad_dept'], help='aggregation group. Prefix of choices (e.g. ad_) indicates external data source, otherwise sources from accounting files')
    parser.add_argument('-G', '--grouplist', help="provide comma seperated list of name/id which correspond to the type in --groupby such as a list of ad_manager (default: None)")
    parser.add_argument('-p', '--period', default='Y', choices=['Y', 'M'], help="present data in either monthly or yearly")
    parser.add_argument('-y', '--years', help="provide comma seperated list of years (default: None)")
    parser.add_argument('-d', '--debug', help="Print lots of debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING,)
    parser.add_argument('-v', '--verbose', help="Be verbose (INFO)", action="store_const", dest="loglevel", const=logging.INFO,)
    args = parser.parse_args()
    # Configure the root logger but will not be used directly (e.g. logging.debug(blahblah)). 
    # Each sub module can enable the same loglevel by creating its own local logger (which is
    # forked from the root logger configured in here).
    logging.basicConfig(format=LOG_FORMATTER, level=args.loglevel)
    logger = logging.getLogger(__name__)
    main(args)