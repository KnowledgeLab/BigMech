from os.path import expanduser
from bm_support.add_features import define_laststage_metrics
from bm_support.supervised_aux import run_neut_models
from bm_support.reporting import dump_info
import json


# predict_mode = 'neutral'
predict_mode = 'posneg'
fprefix = f'predict_{predict_mode}'

selectors = ['claim', 'batch']

# model_type = 'lr'
model_type = 'rf'

if model_type == 'rf':
    forest_flag = True
else:
    forest_flag = False

thr_dict = {'gw': (0.218, 0.305), 'lit': (0.157, 0.256)}

df_dict = {}

for origin in ['gw', 'lit']:
    df_dict[origin] = define_laststage_metrics(origin, predict_mode=predict_mode, verbose=True)
    print(f'>>> {origin} {predict_mode} {df_dict[origin].shape[0]}')


fname = expanduser('~/data/kl/columns/feature_groups_v3.txt')
with open(fname, 'r') as f:
    feat_selector = json.load(f)


fpath = expanduser('~/data/kl/reports/')

max_len_thr = 1

n_iter = 5
fsuffix = 'v5'

fprefix = f'predict_{predict_mode}'

cfeatures = ['mu*', 'mu*_pct', 'mu*_absmed', 'mu*_absmed_pct',
             # 'degree_source_in', 'degree_source_out',
             # 'degree_target_in', 'degree_target_out'
             'degree_source', 'degree_target'
             ]

extra_features = [c for c in feat_selector['interaction'] if ('same' in c or 'eff' in c) and ('_im_ud' in c)]
cfeatures += extra_features

complexity_dict = {'min_samples_leaf': 10, 'max_depth': 6, 'n_estimators': 100}
sreport = {}

for cur_depth in range(2, 10):
    complexity_dict['max_depth'] = cur_depth
    report, coeffs = run_neut_models(df_dict, cfeatures,
                                     max_len_thr=max_len_thr, n_iter=n_iter,
                                     forest_flag=forest_flag, asym_flag=False,
                                     target='bint',
                                     complexity_dict=complexity_dict,
                                     verbose=True)
    sreport[cur_depth] = report[0]