from pandas import read_csv, DataFrame, merge
from os import listdir
from os.path import join, expanduser, isfile
import gzip
import pickle

up = 'up'
dn = 'dn'
o_columns = [up, dn]


def get_id_up_dn_df(fpath, origin, n, a, b, version):
    # load id up dn freq DataFrame
    prefix_str = 'pairs_freq_{0}_v_{1}_n_{2}_a_{3}_b_{4}.csv.gz'.format(origin, version, n, a, b)
    df = read_csv(join(fpath, prefix_str),
                  compression='gzip', index_col=2)
    return df


def get_reports(fpath, origin, version, datatype, batchsize, n, a, b, func, case, filter_out=[],
                old_format=False):
    # load available reports
    # fpath = expanduser('~/data/kl/reports')

    prefix_str = '{0}_v_{1}_c_{2}_m_{3}_n_{4}_a_{5}_' \
                 'b_{6}_f_{7}_case_{8}'.format(origin, version, datatype, batchsize,
                                               n, a, b, func, case)
    files = [f for f in listdir(fpath) if isfile(join(fpath, f)) and
             (prefix_str in f)]

    filter_out_str = list(map(lambda x: 'it_{0}'.format(x), filter_out))
    files2 = list(filter(lambda x: all([y not in x for y in filter_out_str]), files))
    print('Skipping the following iterations : {0}'.format(filter_out))
    reports = {}

    for f in files2:
        with gzip.open(join(fpath, f), 'rb') as fp:
            rep = pickle.load(fp)
        if old_format:
            rep = convert_dict_format(rep)
        reports.update(rep)

    reports_df = DataFrame.from_dict(reports, dtype=float).T
    reports_df.index = map(int, reports_df.index)
    return reports_df


def get_up_dn_report(fpath_reps, fpath,
                     origin, version, datatype, batchsize, n, a, b, func, case, filter_out=[],
                     old_format=False):
    # attach [up, dn] to reports
    df_pairs = get_id_up_dn_df(fpath, origin, n, a, b, version)
    reports_df = get_reports(fpath_reps, origin, version, datatype, batchsize,
                             n, a, b, func, case, filter_out, old_format)
    df_merged = merge(df_pairs[o_columns], reports_df, right_index=True, left_index=True, how='right')
    return df_merged


def get_lincs_df(fpath, origin, version, n, a, b):
    # load lincs data
    # fpath = expanduser('~/data/kl/claims')
    df = read_csv(join(fpath, 'lincs_{0}_v_{1}_n_{2}_a_{3}_b_{4}.csv.gz'.format(origin, version, n, a, b)),
                  compression='gzip')
    return df


def convert_dict_format(old_dict):
    ids = list(old_dict['data_size'][0].keys())
    new_dict = {i : {} for i in ids}
    for k in old_dict['posterior_info']['flatness'].keys():
        flat = 'flat_'
        if '_a' in k:
            new_dict[k[3:-2]][flat + 'a'] = old_dict['posterior_info']['flatness'][k][0]
            new_dict[k[3:-2]][flat + 'a_bool'] = old_dict['posterior_info']['flatness'][k][1][0]
        if '_b' in k:
            new_dict[k[3:-2]][flat + 'b'] = old_dict['posterior_info']['flatness'][k][0]
            new_dict[k[3:-2]][flat + 'b_bool'] = old_dict['posterior_info']['flatness'][k][1][0]
        if 't0' in k:
            new_dict[k[3:]][flat + 't0'] = old_dict['posterior_info']['point'][k][0]
            new_dict[k[3:]][flat + 't0_bool'] = old_dict['posterior_info']['point'][k][1][0]

    for k in old_dict['posterior_info']['point'].keys():
        if '_a' in k:
            new_dict[k[3:-2]]['a'] = old_dict['posterior_info']['point'][k][0]
            new_dict[k[3:-2]]['a_bool'] = old_dict['posterior_info']['point'][k][1][0]
        if '_b' in k:
            new_dict[k[3:-2]]['b'] = old_dict['posterior_info']['point'][k][0]
            new_dict[k[3:-2]]['b_bool'] = old_dict['posterior_info']['point'][k][1][0]

        if 't0' in k:
            new_dict[k[3:]]['t0'] = old_dict['posterior_info']['point'][k][0]
            new_dict[k[3:]]['t0_bool'] = old_dict['posterior_info']['point'][k][1][0]

    for k in old_dict['freq'][0].keys():
        new_dict[k]['freq'] = old_dict['freq'][0][k]

    for k in old_dict['data_size'][0].keys():
        new_dict[k]['len'] = old_dict['data_size'][0][k]
    return new_dict
