#-------------------------------------------------------------------------------
# Copyright 2024 Vodéna
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# SPDX-License-Identifier: Apache-2.0
#-------------------------------------------------------------------------------

TPOT = "tpot"
VERBOSITY_TPOT = 2
USE_DASK_TPOT = False
MEMORY_TPOT = None
WARM_START_TPOT = False
N_JOBS_TPOT = -1

OBSERVER_LOGS_SLEEP = 10 # How many seconds to wait before checking the logs again
AVAILABLE_CONFIG_DICTS = [None, 'TPOT light', 'TPOT MDR', 'TPOT sparse']
AVAILABLE_CLASSIFICATION_METRICS = [
    'accuracy', 'adjusted_rand_score', 'average_precision', 'balanced_accuracy',
    'f1', 'f1_macro', 'f1_micro', 'f1_samples', 'f1_weighted', 'neg_log_loss',
    'precision', 'precision_macro', 'precision_micro', 'precision_samples',
    'precision_weighted', 'recall', 'recall_macro', 'recall_micro', 'recall_samples',
    'recall_weighted', 'jaccard', 'jaccard_macro', 'jaccard_micro', 'jaccard_samples',
    'jaccard_weighted', 'roc_auc', 'roc_auc_ovr', 'roc_auc_ovo', 'roc_auc_ovr_weighted',
    'roc_auc_ovo_weighted'
]
AVAILABLE_REGRESSION_METRICS = [
    'neg_median_absolute_error', 'neg_mean_absolute_error', 'neg_mean_squared_error', 'r2'
]