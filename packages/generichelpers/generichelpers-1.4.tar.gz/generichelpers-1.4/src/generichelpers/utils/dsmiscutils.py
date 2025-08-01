# Import, load and reset commands
"""
# +++++++++++++++++
# Load & reset
%load dsmiscutils.py
%reset
%run dsmiscutils.py
# +++++++++++++++++
# Import & reload
import dsmiscutils
reload(dsmiscutils)
from dsmiscutils import *
"""

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# import matplotlib as mpl
# %matplotlib inline
# from importlib import reload
from sklearn import preprocessing
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import learning_curve
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from itertools import product, combinations
from copy import deepcopy
from IPython.core import display
from datetime import timedelta
from matplotlib import rcParams

warnings.filterwarnings('ignore')


def plot_lmplot(df, x_var=None, y_var=None, hue_var=None, fig_size=5, save_plot=False, plot_name='plot.png'):
    """Creates "sns.lmplot" of two variables with hue"""
    # plt.rc('font', size=14)
    # sns.set_style("dark")
    # sns.set_context("notebook", font_scale=1.5)

    sns.set_style("ticks")
    rcParams['figure.figsize'] = 11.7, 8.27
    facet = sns.lmplot(data=df, x=x_var, y=y_var, hue=hue_var, size=fig_size,
                       fit_reg=False, legend=True, legend_out=True, palette="deep")
    fig = facet.fig  # Access the figure
    fig.suptitle("lmplot of two variables", fontsize=12)  # Add a title to the Figure
    if save_plot:
        facet.savefig(plot_name)
    plt.show()
    return


def univ_histogram(data, bins=None, data_name=None, data_color="#539caf", x_label=None, y_label=None,
                   title=None, save_plot=False, plot_name='plot.png'):
    """Univariate histograms"""
    if bins is None:
        # Set the bounds for the bins so that the two distributions are fairly compared
        max_nbins = 10
        data_range = [min(data), max(data)]
        binwidth = (data_range[1] - data_range[0]) / max_nbins
        bins = np.arange(data_range[0], data_range[1] + binwidth, binwidth)
    else:
        bins = bins
    # Create the histogram plot
    sns.set_style("dark")
    sns.set_context("notebook", font_scale=1)
    f, ax = plt.subplots(figsize=(10, 8))
    plt.hist(data, normed=False, bins=bins, label=[data_name])
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    plt.legend(loc='best')
    if save_plot:
        plt.savefig(plot_name)
    plt.show()


def overlaid_histogram(data_1, data_2, bins=None, data_1_name=None, data_1_color="#539caf",
                       data_2_name=None, data_2_color="#7663b0", x_label=None, y_label=None,
                       title=None, save_plot=False, plot_name='plot.png'):
    """Overlay 2 histograms to compare them"""
    if bins is None:
        # Set the bounds for the bins so that the two distributions are fairly compared
        max_nbins = 10
        data_range = [min(min(data_1), min(data_2)), max(max(data_1), max(data_2))]
        binwidth = (data_range[1] - data_range[0]) / max_nbins
        bins = np.arange(data_range[0], data_range[1] + binwidth, binwidth)
    else:
        bins = bins
    # Create the plot
    plt.style.use('seaborn-deep')
    f, ax = plt.subplots(figsize=(10, 8))
    plt.hist([data_1, data_2], bins=bins, label=[data_1_name, data_2_name])
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    plt.legend(loc='best')
    if save_plot:
        plt.savefig(plot_name)
    plt.show()


def del_hcor_cols(data=None, corr_thresh=None, reduce_df=True):
    """
    Finds the highest correlation pairs based on the provided threshold and
    returns the dataframe removing the correlated columns
    """
    corr_res = {}
    df_red = None
    corr_mat = data.corr().abs()
    high_corr_var = np.where(corr_mat >= corr_thresh)
    high_corr_var = [[corr_mat.columns[x], corr_mat.columns[y], corr_mat.iloc[x, y].round(4)]
                     for x,y in zip(*high_corr_var) if x != y and x < y]
    high_corr_var = pd.DataFrame(high_corr_var, columns=['Variable-1', 'Variable-2', 'Correlation'])
    if reduce_df:
        df_red = data.copy()
        df_red = df_red.drop(list(set(high_corr_var['Variable-1'])), axis=1)
    corr_res['high_corr_vars'] = high_corr_var
    corr_res['df_reduced'] = df_red
    return corr_res


def sparsity_check(data=None, sparse_thr=0.85, nan_thr=0.85):
    """This function computes the proportion of NaNs,sparse and constant columns in a dataframe."""
    df, spcheck_res = data.copy(), {}
    nan_df = pd.DataFrame(df.isnull().mean()).reset_index(drop=False).rename(
        columns={'index': 'Variable', 0: 'nan_perc'})
    sp_df = pd.DataFrame((df == 0).mean()).reset_index(drop=False).rename(
        columns={'index': 'Variable', 0: 'sparse_perc'})
    const_df = pd.DataFrame(~(df != df.iloc[0]).any()).reset_index(drop=False).rename(
        columns={'index': 'Variable', 0: 'const_check'})
    check_df = nan_df.merge(sp_df, on='Variable').merge(const_df, on='Variable')
    # +++++++++++++++++
    # Find the alarming variables from each category
    nan_vars = list(check_df.Variable[check_df.nan_perc >= nan_thr])
    sparse_vars = list(check_df.Variable[check_df.sparse_perc >= sparse_thr])
    const_vars = list(check_df.Variable[check_df.const_check])
    spcheck_res = {"check_df": check_df, "nan_vars": nan_vars, "sparse_vars": sparse_vars, "const_vars": const_vars}
    return spcheck_res


def select_feats(score_func=f_classif, data=None, tg_col='', to_sample=False, samp_sz=None, random_state=42):
    """This functions performs feature selection on the provided lebel transformed dataset
    on the basis of independent and target features."""
    df_reduced = data.copy()
    if to_sample:
        df_reduced = df_reduced.sample(n=samp_sz, random_state=random_state)
    # +++++++++++++++++
    # Perform features importance scoring
    df_feats = df_reduced.drop(tg_col, axis=1)
    df_labels = df_reduced[tg_col]
    df_vfeats = df_feats.values
    df_vlabels = df_labels.values
    # +++++++++++++++++
    # Perform relevant feature selection
    X, y = df_vfeats, df_vlabels
    selector = SelectKBest(score_func=score_func, k=df_feats.shape[1])
    df_reduced = selector.fit_transform(X, y)
    best_feats = df_feats.columns.values[selector.get_support()]
    feat_scores = selector.scores_[selector.get_support()]
    names_scores = list(zip(best_feats, feat_scores))
    df_bestfs = pd.DataFrame(data=names_scores, columns=['Feat_names', 'F_Scores'])
    df_bestfs_sorted = df_bestfs.sort_values(['F_Scores', 'Feat_names'], ascending=[False, True])
    # +++++++++++++++++
    # Ranks the features based on F-score
    df_bestfs_sorted = df_bestfs_sorted.dropna()
    df_bestfs_sorted['Rank'] = df_bestfs_sorted['F_Scores'].rank(ascending=False, method='dense')
    df_bestfs_sorted['Rank'] = df_bestfs_sorted['Rank'].astype('int64')
    df_bestfs_sorted = df_bestfs_sorted.reset_index(drop=True)
    # +++++++++++++++++
    return df_bestfs_sorted


def create_intrcs(data=None, intrc_feats=[], default_cols=[], rm_cols=['min', 'max', 'median'], keep_intrc=20,
                  to_sample=True, samp_sz=None, random_state=42, corr_thresh=0.9, tg_col=''):
    """This function automatically creates and selects interaction features from a given dataframe.
    Performs thorough analysis for retaining the appropriate interaction features."""
    df_xtnd, intrc_res = data.copy(), {}
    if intrc_feats:
        temp_df = data.copy()
        temp_df = temp_df[intrc_feats]
        polyf = PolynomialFeatures(interaction_only=True, include_bias=False)
        intrc_df = polyf.fit_transform(temp_df)
        intrc_cols = polyf.get_feature_names(intrc_feats)
        intrc_cols = ['::'.join(x.split()) for x in intrc_cols]
        intrc_df = pd.DataFrame(intrc_df, columns=intrc_cols)
        get_cols = list(set(intrc_cols)-set(intrc_feats))
        temp_df = intrc_df.copy()  # set temporary df to perform variable selection
        if to_sample:
            temp_df = temp_df.sample(n=samp_sz, random_state=random_state)
        temp_df = temp_df[get_cols]
        # +++++++++++++++++
        # Filtering the interaction columns
        cols_comb = [set(x) for x in combinations(rm_cols, 2)]
        drop_cols = []
        for col in get_cols:
            spl_cols = col.split('::')
            s0 = spl_cols[0].split("_")
            s1 = spl_cols[1].split("_")
            cond = set(s0).symmetric_difference(set(s1)) in cols_comb
            drop_cols += [col] if cond else []
        intrc_res['default_drop_cols'] = drop_cols
        temp_df = temp_df.drop(drop_cols, axis=1, errors='ignore')  # remove default columns
        # +++++++++++++++++
        # Now check sparsity to reduce dimensionality
        sp_res = sparsity_check(data=temp_df)
        intrc_res = {**intrc_res, **sp_res}  # updating the dictionary
        drop_cols = drop_cols + sp_res['nan_vars'] + sp_res['sparse_vars'] + sp_res['const_vars']
        temp_df = temp_df.drop(drop_cols, axis=1, errors='ignore')
        # +++++++++++++++++
        # Check mutual correlation to reduce dimensionality
        corr_res = del_hcor_cols(data=temp_df, corr_thresh=corr_thresh, reduce_df=False)
        intrc_res = {**intrc_res, **corr_res}
        corr_cols = set(corr_res['high_corr_vars']['Variable-1'])
        corr_cols = list(corr_cols - set(default_cols))
        drop_cols = drop_cols + corr_cols
        drop_cols = list(set(drop_cols))
        keep_cols = list(set(get_cols)-set(drop_cols))
        intrc_df_1 = intrc_df[keep_cols]

        intrc_res['keep_cols'] = keep_cols
        intrc_res['drop_cols'] = drop_cols
        intrc_res['final_intrc_df'] = intrc_df_1

        # +++++++++++++++++
        # Selecting the final set of interaction features based on F-scores
        df_xtnd.reset_index(drop=True, inplace=True)
        intrc_df_1.reset_index(drop=True, inplace=True)
        df_xtnd = pd.concat([df_xtnd, intrc_df_1], axis=1)

    # +++++++++++++++++
    # Label binarize and encode the boolean columns
    df_reduced = df_xtnd.copy()
    selct_cols = df_reduced.select_dtypes(exclude='object').columns.tolist()
    df_reduced = df_reduced[list(dict.fromkeys(tg_col+selct_cols))]
    lb = preprocessing.LabelBinarizer()
    le = preprocessing.LabelEncoder()
    bool_cols = df_reduced.select_dtypes(include='bool').columns
    if ~bool_cols.empty:
        df_reduced[bool_cols] = lb.fit_transform(df_reduced[bool_cols])
    df_reduced[tg_col] = le.fit_transform(df_reduced[tg_col])
    # +++++++++++++++++
    # Features selection through F-score
    feats_select = select_feats(data=df_reduced, tg_col=tg_col)
    feats_select.reset_index(drop=True, inplace=True)
    if intrc_feats:
        get_series = feats_select['Feat_names'].apply(lambda x: 'original' if x in data.columns else 'interaction')
        feats_select.insert(loc=1, column='Feat_type', value=get_series)
    intrc_res['feats_select'] = feats_select
    intrc_res['transf_df'] = df_reduced
    # +++++++++++++++++
    # Compute the reduced selection of top few interaction features
    if (intrc_feats and (keep_intrc is not None)):
        feats_1 = feats_select[feats_select['Feat_type']=='original']
        feats_2 = feats_select[feats_select['Feat_type']=='interaction']
        feats_reduced = pd.concat([feats_1,feats_2.iloc[:keep_intrc]],ignore_index=True)
        cols_1 = set(df_reduced.columns) - set(feats_reduced['Feat_names'])
        cols_1 = list(cols_1 - set(tg_col))
        reduced_intr_df = df_reduced.drop(cols_1,axis = 1)
        intrc_res['feats_reduced'] = feats_reduced
        intrc_res['reduced_intr_df'] = reduced_intr_df
    return intrc_res


def dtree_extract_rules(tree=None, feature_names=[], print_rules=False):
    """This function takes a sklearn dtree object and feature names as inputs, traverses the tree
    and extract the rules from it. The extracted rules are returned in the resultatnt dictionary."""
    tree_, tree_extract, pathto = tree.tree_, dict(), dict()
    feature_name = [feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!" for i in tree_.feature]
    global k
    k = 0

    def recurse(node, depth, parent):
        global k
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = round(tree_.threshold[node], 4)
            s = "{} <= {} ".format(name, threshold, node)
            if node == 0:
                pathto[node] = s
            else:
                pathto[node] = pathto[parent]+' & ' + s

            recurse(tree_.children_left[node], depth + 1, node)
            s = "{} > {}".format(name, threshold)
            if node == 0:
                pathto[node] = s
            else:
                pathto[node] = pathto[parent]+' & ' + s
            recurse(tree_.children_right[node], depth + 1, node)
        else:
            k += 1
            tree_val = tree_.value[node][0].tolist()
            tree_val = list(map(int, tree_val))
            get_class = tree.classes_[np.argmax(tree_val)]
            rules_str = "IF {0} THEN Value: {1}, Class = \'{2}\'".format(pathto[parent], tree_val, get_class)
            tree_extract[k] = rules_str
    recurse(0, 1, 0)
    if print_rules:
        # Print the resultant dictionary
        print('Rules extracted from the decision tree are as follwos:\n')
        print("\n".join("{}: {}\n".format(k, v) for k, v in tree_extract.items()))
    return tree_extract


def findElbowPoint(x=[], y=[]):
    """
    This function computes the elbow/knee point of a curve for given indices and values
    The indices and values should be of same lengths

    x: indices
    y: values of the curve
    """
    ind_val, values = x.copy(), y.copy()
    nPoints = len(values)
    allCoord = np.vstack((range(nPoints), values)).T
    # np.array([range(nPoints), values])
    firstPoint = allCoord[0]  # get the first point
    lineVec = allCoord[-1] - allCoord[0]  # get vector between first and last point - this is the line
    lineVecNorm = lineVec / np.sqrt(np.sum(lineVec**2))

    # find the distance from each point to the line:
    # vector between all points and first point
    vecFromFirst = allCoord - firstPoint

    # To calculate the distance to the line
    scalarProduct = np.sum(vecFromFirst * np.matlib.repmat(lineVecNorm, nPoints, 1), axis=1)
    vecFromFirstParallel = np.outer(scalarProduct, lineVecNorm)
    vecToLine = vecFromFirst - vecFromFirstParallel
    # distance to line is the norm of vecToLine
    distToLine = np.sqrt(np.sum(vecToLine ** 2, axis=1))
    # knee/elbow is the point with max distance value
    idxOfBestPoint = np.argmax(distToLine)
    find_elbow = {'elbow_index': ind_val[np.argmax(distToLine)],
                  'elbow_value': values[idxOfBestPoint]}
    return find_elbow


def prec_recall_generate(actual=None, probas_pred=None, thresh=None):
    """This function generates precision and recall values for given actual values, prediction probabilities
    and threshold. It returns the generated prec_recall, prediction and confusion matrix."""
    prec_recall_res = {}
    get_pred = pd.Series([True if y >= thresh else False for y in probas_pred])
    prec = precision_score(y_true=actual, y_pred=get_pred, average='binary')
    recall = recall_score(y_true=actual, y_pred=get_pred, average='binary')
    conf_mat = pd.crosstab(actual, get_pred, rownames=['Actual'], colnames=['Predicted'], margins=True)
    prec_recall_res = {'threshold': thresh, 'precision': prec, 'recall': recall,
                       'prediction': get_pred, 'conf_mat': conf_mat}
    return prec_recall_res
# Plot precision-recall curve
"""
plt.style.use('seaborn-darkgrid')
font_size = 14
plt.figure(figsize=(12,7))
plt.step(prec_recall['recall'], prec_recall['precision'], color='b', alpha=0.4,where='post')
plt.fill_between(prec_recall['recall'], prec_recall['precision'], color='b', alpha=0.4, step='post')

plt.xlabel('Recall',fontsize=font_size)
plt.ylabel('Precision',fontsize=font_size)
plt.title('Binary class Precision-Recall curve: XGBoost',fontsize=font_size)
plt.xticks(np.arange(0.0,1.02,0.2),fontsize=font_size)
plt.yticks(np.arange(0.2,1.02,0.2),fontsize=font_size)
plt.ylim([0.0, 1.0])
plt.xlim([0.0, 1.0])
plt.savefig('prec-recall_curve_xgb.png')
plt.show()
"""


def plot_learning_curve(estimator, X, y, title=None, ylim=None, cv=None, scoring=None, random_state=None,
                        verbose=0, figsize=None, font_size=None, n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5),
                        save_plot=False, plot_name='plot.png'):
    """
    Generate a simple plot of the test and training learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - An object to be used as a cross-validation generator.
          - An iterable yielding train/test splits.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : integer, optional
        Number of jobs to run in parallel (default 1).
    """
    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=figsize)
    plt.title(title, fontsize=font_size)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples",fontsize=font_size)
    plt.ylabel("Score", fontsize=font_size)
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, scoring=scoring, verbose=verbose, random_state=random_state,
        n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    # plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")
    plt.legend(loc="best")
    if save_plot:
        plt.savefig(plot_name)
    plt.show()
    return plt


# ================================================
# Apply grid search on 'class_weight' parameter of SVC
"""
grid_res = pd.DataFrame()
grids = list(np.arange(20,0.9,-0.1).round(2)) + ['balanced',None]
grids = ['balanced']
for pos_weight in grids:
    if(pos_weight not in ['balanced',None]): class_weight = {True:pos_weight,False:1}
    else: class_weight = pos_weight
    clf = LinearSVC(class_weight=class_weight,random_state=random_state)
    clf = clf.fit(feats_train[list(feats_train)[1:]],target_train)

    pred_test = pd.DataFrame(clf.predict(feats_test[list(feats_test)[1:]]), columns = list(target_test))
    conf_mat = pd.crosstab(target_test[tg_col[0]], pred_test[tg_col[0]], \
                               rownames=['Actual'], colnames=['Predicted'], margins=True)
    prec = round(precision_score(y_true=target_test, y_pred=pred_test, average='binary'),4)
    recall = round(recall_score(y_true=target_test, y_pred=pred_test, average='binary'),4)
    val_df = pd.DataFrame({'class_weight':[class_weight],'precision': prec, 'recall': recall},
                     index=[0],columns=['class_weight','precision','recall'])
    display((pos_weight,prec,recall))
    grid_res = grid_res.append(val_df).reindex(val_df.columns, axis=1)
grid_res = grid_res.reset_index(drop=True)
"""
# ================================================


def grid_search_classif(model_type=None, grid_params=None, feats_train=None, feats_test=None, target_train=None,
                        target_test=None, inter_display=True, disp_div=1000, early_break=False, break_thresh=1000):
    """This function performs grid search for parameters tuning of a classifier.
    Supplied are the model type, parametrs range, train, test dataframes and additional arguments.
    The function returns a dataframe of accuracy values together with the fit object for each grid value.

    - model_type = ['rf', 'gbm', 'xgb', 'dtree','logReg', 'svc']
    """
    # Perform grid search with supplied dict of parameters
    grid_res = pd.DataFrame()
    search_len = [row for row in product(*grid_params.values())].__len__()
    print('........Performing parameters-tuning through grid search for: {}'.format(model_type.upper()))
    print('........Total No. of searches : {}\n'.format(search_len))
    if model_type == 'rf':
        clf = RandomForestClassifier()
    elif model_type == 'gbm':
        clf = GradientBoostingClassifier()
    elif model_type == 'xgb':
        clf = XGBClassifier()
    elif model_type == 'dtree':
        clf = DecisionTreeClassifier()
    elif model_type == 'logReg':
        clf = LogisticRegression()
    else:
        clf = LinearSVC()
    # +++++++++++++++++
    # Perform grid search with the provided parameters range
    search_cntr = 1
    for row in product(*grid_params.values()):
        params = dict(zip(grid_params.keys(), row))
        clf = clf.set_params(**params).fit(feats_train[list(feats_train)[1:]], target_train)
        model_fit = deepcopy(clf)
        pred_test = pd.DataFrame(clf.predict(feats_test[list(feats_test)[1:]]), columns = list(target_test))
        model_acc = round(accuracy_score(target_test, pred_test), 4)
        model_f1 = round(f1_score(y_true=target_test, y_pred=pred_test, average='binary'), 4)
        model_prec = round(precision_score(y_true=target_test, y_pred=pred_test, average='binary'), 4)
        model_recall = round(recall_score(y_true=target_test, y_pred=pred_test, average='binary'), 4)
        # Apppend the current scores
        score_df = pd.DataFrame({'accuracy': model_acc, 'f1_score': model_f1, 'precision': model_prec,
                                 'recall': model_recall, 'fit_object': model_fit}, index=[0],
                                columns=['accuracy', 'f1_score', 'precision', 'recall', 'fit_object'])
        grid_res = grid_res.append(score_df).reindex(score_df.columns, axis=1)
        if inter_display & (not (search_cntr % disp_div)):
            print('No. of searches performed till now: {}'.format(search_cntr))
            display(score_df)
        if early_break & (search_cntr == break_thresh):
            break
        search_cntr += 1
    grid_res = grid_res.reset_index(drop=True)
    return grid_res


def create_bins(data, bin_range, labels='default', include_lowest=False, fill_value='default'):
    """This function create bins for a dataframe column.
    - `labels` : Can be one of -- None, 'default' or a list of labels
    - `fill_value` : Fills the left-out values after binning. It can be one of -- 'default', a string or 'False'
    """
    binned_data = data.copy()
    if labels == 'default':
        labels = ['Bin'+'.'+str(x)+'-'+str(y) for x, y in zip(bin_range[:-1], bin_range[1:])]
    binned_data = binned_data.apply(lambda x: pd.cut(x, bin_range, labels=labels, include_lowest=include_lowest))
    # Change the binned column to 'str' type
    if fill_value == 'default':
        fill_value = 'Bin.>' + str(bin_range[-1])
    if fill_value:
        binned_data = binned_data.apply(lambda x: x.cat.add_categories(fill_value))
        binned_data = binned_data.fillna(fill_value).astype(str)
        binned_data.iloc[:,0] = binned_data.iloc[:, 0].map({'Bin.-1-0': 'Bin.0'}).fillna(binned_data.iloc[:, 0])
    return binned_data


def generate_quarters(no_quarters=4, year=2018, check_yr=2018, check_qtr=4, to_display=True):
    """This function generates the desired number of quarters with dates"""
    get_quarters, i = [], 0
    while True:
        start_qt = check_qtr if year == check_yr else 4
        get_quarters = get_quarters + [pd.Period(freq='Q', year=year, quarter=quarter).strftime(
            '%Y-%m-%d') for quarter in list(range(start_qt, 0, -1))]
        if get_quarters.__len__() > no_quarters:
            break
        i, year = i+1, year-1
    get_quarters = get_quarters[:no_quarters]
    # +++++++++++++++++
    # Prepare obs_ranges for previous few quarters
    obs_qtrly = pd.DataFrame(columns=['obs_qtrly', 'qtr'])
    for i in range(1, no_quarters):
        d1 = pd.to_datetime(get_quarters[i-1])
        d2 = pd.to_datetime(get_quarters[i])
        obs_1 = ((d2 + timedelta(days=1)).strftime('%Y-%m-%d'), get_quarters[i-1])
        obs_2 = '{0}-Q{1}'.format(d1.year, d1.quarter)
        temp_df = pd.DataFrame([(obs_1, obs_2)], columns=obs_qtrly.columns)
        obs_qtrly = pd.concat([obs_qtrly, temp_df])
    obs_qtrly = obs_qtrly.reset_index(drop=True)
    # +++++++++++++++++
    # Display and return the generated quarters
    if to_display:
        display(get_quarters, obs_qtrly)
    return get_quarters, obs_qtrly


# ------------------------------------------------------#
# Some useful Python general tips & code snippets
# ------------------------------------------------------#
# Collage images in python
"""
from PIL import Image
img_list=['a.png','b.png','c.png']

# Make collage
all_images = [Image.open(x) for x in img_list]
widths, heights = zip(*(i.size for i in all_images))
total_width = sum(widths)
max_height = max(heights)

collage_img = Image.new('RGB', (total_width, max_height))

x_offset = 0
for img in all_images:
    collage_img.paste(img, (x_offset,0))
    x_offset += img.size[0]
display(collage_img)
collage_img.save('collage.png')
"""
# ================================================
# Get the arguments of a function as a tuple
"""
func_name.__code__.co_varnames
"""
## For loading a sub-function/sub-module from a .py script
"""
import inspect
from undecorated import undecorated ##[for stripping decorator from a function]
%load inspect.getsource(function_name)
# =================
For loading the base function that is decorated
%load inspect.getsource(base_func_name.__closure__[0].cell_contents)
%load inspect.getsource(undecorated(base_func_name))
help(undecorated(base_func_name)) #for console help
# =================
func_2 = base_func_name.__closure__[0].cell_contents
func_2 = undecorated(base_func_name)
"""
# ================================================
# Search and rename all occurences in a dataframe based on rename dict
# ================================================
"""
feats_rename = pd.read_excel(open('feats_renaming.xlsx','rb'))
feats_replace = tuple(zip(feats_rename['Original Feature'],feats_rename['Renamed Feature']))
cols = onhc_df.columns.tolist()
newcols=[]
for col in cols:
    for r in feats_replace:
        col = col.replace(*r)
    newcols = newcols + [col]
onhc_df.columns = newcols
"""
# ================================================
"""
# # Stop truncating columns in display
pd.set_option('display.max_columns', None)
# pd.reset_option('display.max_columns')
# pd.reset_option('all')
"""
"""
# # Install required packages
# !pip install pandas-profiling
# !pip install featuretools
# plotting a df through df.plot()
# plt.style.available
plt.style.use('seaborn')
get_fig = cl_groupped[['cluster',
                       'mean(package_ticket_description_dstcnt)',
                       'mean(package_ticket_num_days_mean)',
                       'mean(package_ticket_num_days_dstcnt)',
                       'median(package_ticket_num_days_dstcnt)']].\
plot(x='cluster',kind='bar',fontsize = 16,grid=False,legend=False,figsize = (20,14),subplots = True,
     color=('xkcd:aqua','xkcd:blue','xkcd:crimson','xkcd:magenta'),layout=(2,2),sharex=False,rot=0)
[(x.title.set_size(16),x.xaxis.label.set_fontsize(16))
 for x in get_fig.ravel()] #for setting title and label sizes for each subplot
get_fig = get_fig[0][0].get_figure()
get_fig.savefig('package_ticket_details.png')
"""

"""
# Writing/reading a dataframe as a compressed pickle file
df.to_pickle('omnicart_feat_init_01_5d.p.gzip', compression='gzip', protocol=pickle.HIGHEST_PROTOCOL)
df = pd.read_pickle('omnicart_raw_01_5d.p.gzip', compression='gzip')

## Save a dataframe as csv.zip
save_path="G:\\AIL Capability Development(00-KCS-0979)\\Ratnadip\\Cisco_Eugenie\\Exp_Results\\"
compression_opts = dict(method='zip',archive_name='dup_removed_us.csv')
dup_removed_df.to_csv(save_path+'dup_removed_us.zip',compression=compression_opts,
                      index = None, sep = ",",header=True)

# Save the dict to a pickle -- Normal
pickle.dump(dict, open('filename.p', "wb"), pickle.HIGHEST_PROTOCOL)
# Load results from saved pickle files
dict = pickle.load(open('filename.p', "rb"))

# Save the results dict to a pickle -- gzip
p_file = gzip.GzipFile('km_cluster_wfr.gz', 'wb')
p_file.write(pickle.dumps(kmeans_res, pickle.HIGHEST_PROTOCOL))
p_file.close()
# Load results from saved pickle files
p_file = gzip.GzipFile('km_cluster_wfr.gz', 'rb')
kmeans_res = pickle.loads(p_file.read())
p_file.close()

# Save the results dict to a pickle -- zip
zip_file = zipfile.ZipFile(save_path+save_name+'.zip', 'w',compression=zipfile.ZIP_DEFLATED)
zip_file.writestr(save_name+'.p',pickle.dumps(details_dict, pickle.HIGHEST_PROTOCOL))
zip_file.close()
######
# Load from zipped pickle
zip_file = zipfile.ZipFile(save_path+save_name+'.zip', 'r',compression=zipfile.ZIP_DEFLATED)
details_dict = pickle.loads(zip_file.read(save_name+'.p'))
zip_file.close()

## Saving relevant results in excel
file_name = "omnicart_01_5d_res-1.xlsx"
writer=pd.ExcelWriter(str(file_name))
get_corr.groupby("Variable-1",as_index=False, sort=False).head(10).to_excel(writer,index=False,sheet_name='corr_pairs')
get_rejvars.to_excel(writer,index=False,sheet_name='Rejctd_vars')
writer.save()
# writer.close()

# Reading data from an existing excel file
file_path = './'
file_name = "omnicart_6m_res-3.xlsx"
df_dtypes = pd.read_excel(open(str(file_path+file_name),'rb'),sheet_name='orig_feats')

# Saving results in existing excel
file_name = "omnicart_01_5d_res-1.xlsx"
book = load_workbook(file_name)
writer = pd.ExcelWriter(file_name, engine='openpyxl')
writer.book = book
df_final.describe().to_excel(writer,index=True,sheet_name='summary_stats')
writer.save()
writer.close()
"""
"""
###################################Summary statistics###################################
omnicart_final_01_5d = pd.read_pickle('omnicart_final_01_5d.p.gzip',compression='gzip')
# df = omnicart_final_01_5d.sample(frac = 0.2,random_state=random_state)
df_final = omnicart_final_01_5d

# Obtaining summary stats and Profile Report
# df_summary = pd_profiling.describe(df_final)
df_pfr = pd_profiling.ProfileReport(df_final)
df_pfr.to_file(outputfile="ProfileReport_final_01_5d.html")
get_rejvars = df_pfr.get_rejected_variables()
get_rejvars = pd.DataFrame(get_rejvars,columns=['Rejected variables'])

# Obtain the summary statistics
df_final.describe()
df_summary.keys()

# Obtain correlation and heatmap
df_corr = df_summary['correlations']['pearson']
# df_corr = df_final.corr()

# Plot correlation heatmap
f, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(df_corr, mask=np.zeros_like(df_corr, dtype=np.bool), cmap=sns.diverging_palette(220, 10, as_cmap=True),
            square=True, ax=ax)
plt.show()

# List highest correlation pairs
df_corr = df_final.corr()
get_corr = (df_corr.abs().where(np.triu(np.ones(df_corr.abs().shape), k=1).astype(np.bool)).stack())
get_corr = pd.DataFrame(get_corr).reset_index()
get_corr = get_corr.rename(columns = {get_corr.columns.values[0]:'Variable-1',
                           get_corr.columns.values[1]:'Variable-2',
                           get_corr.columns.values[2]:'Correlation'})

# Get correlations groupped by Correlation and Variable -1
get_corr = get_corr.groupby("Variable-1",as_index=False, sort=False).apply(
    lambda x: x.sort_values(["Correlation"], ascending = False)).reset_index(drop=True)
get_corr.groupby("Variable-1",as_index=False, sort=False).head(3)
# df_final.groupby(["label_new", "cart_total_amt_mean"]).size().reset_index(name="Count")
"""
"""
# settling infite values
df_final = df_final.replace(float('inf'), np.nan)
df_final = df_final.replace(-float('inf'), np.nan)
df_final = df_final.fillna(np.nan)
"""
"""
# For completely removing a directory (empty or non-empty)
shutil.rmtree('./saved_data/')
"""
"""
# Columns rearranging
df_cols = list(df)
df_cols.insert(1, df_cols.pop(-1))
df = df[df_cols]
"""
"""
# Columns slicing
df.iloc[0:m,0:n]
df.iloc[0:m,[n]]
"""
"""
# Dynamically save results for the cov type
globals()[''.join('gmm_res_{}'.format(cov))] = gmm_res
"""
"""
#Save dictionary items as variables
locals().update(dict)
"""
"""
# For reading data from/to clipboard
pd.read_clipboard()
df.to_clipboard()
"""
"""
# for pretty-printing dataframes/tables in console (e.g. spyder)
pip install tabulate
from tabulate import tabulate
print(tabulate(df,headers='keys',tablefmt='psql'))
print(df.to_markdown())
"""
# ------------------------------------------------------#
# Useful PySpark general tips & code snippets, Part-1
# ------------------------------------------------------#
# Instantiating SparkSession object with HiveSupport
"""
%livy2.pyspark
#%ETSpark2.pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import *
from pyspark.sql.functions import *

spark = SparkSession \
    .builder \
    .appName("Omnicart_Data_Prep") \
    .enableHiveSupport() \
    .getOrCreate()
"""

# Fetching data from Hive
"""
%livy2.pyspark
# %spark2.pyspark
spark.sql("use ai_ml_cart_abndmt")
df = spark.sql("select * from stg1_omnicart_agg_nov17_may18 as select")
# df = spark.sql("select * from stg1_omnicart_agg_nov17_may18 as select where cart_start_date <= '2017-11-05 00:00:00' ")
print((df.count(), len(df.columns)))
df.printSchema()
# 1m Full data count (without filtering 'Rejected' carts): (1619617, 90)
# 1m Data count after filtering out the 'Rejected' carts: (1463528, 90)
# 6m Data count keeping all the 'cart_status': (2003364, 100)
# Latest - 6m Data count keeping all the 'cart_status':
"""
"""
# Filter out the 'REJECTED carts'
df = df.where(col("cart_status").isin({"ACTIVE", "BOOKED"}))
print((df.count(), len(df.columns)))
"""

# Sampling of spark dataframe
"""
%livy2.pyspark
# %spark2.pyspark
# import pandas as pd
# import numpy as np
# import sys,os,json

random_state = 42
df_feat = df.sample(False,0.05,random_state)
print((df_feat.count(), len(df_feat.columns)))
"""

# Saving data to AWS S3 bucket
"""
%livy2.pyspark
filepath = "s3a://wdpr-ia-platform-datalake-latest/ML-Pilot-Projects/Cart-Abandonment/tmp/"
filename = "omnicart_6m_sampled_feats_1.csv.gz"
df_feat.repartition(1).write.format('com.databricks.spark.csv').\
options(mode='overwrite').\
options(codec='gzip').\
options(header='true').\
save(filepath+filename)

# df_feat.repartition(1).write.save(filepath + filename, format='csv', mode='overwrite', header=True, codec="gzip")
"""
# ------------------------------------------------------#
# Useful PySpark general tips & code snippets, Part-2
# ------------------------------------------------------#
# Package installation/updation
"""
python -m jupyterlab ## Opening JupyterLab from Anaconda cmd
## For opening a consloe to run specific lines of codes in Jupyter notebook
%qtconsole OR %qtconsole --style emacs/vim/etc.
"""
"""
pip install <package_name>
pip install <package_name> == <package_version>
pip install --user <package_name>
pip install --upgrade <package_name>
##############
## Install package with handling SSL Cert errors
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip setuptools
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package_name>
##############
## Install/upgrade through conda
conda config --set ssl_verify no #Don't verify SSL
conda update conda
conda update anaconda
conda install spyder=4.1.4

##################################################
## For highlighting selected texts in Jupyter
##################################################
https://anaconda.org/conda-forge/jupyter_highlight_selected_word
##############
Step-1: !conda install -c conda-forge jupyter_highlight_selected_word
            OR
        !pip install jupyter_highlight_selected_word
Step-2: !jupyter nbextension install --py jupyter_highlight_selected_word
Step-3: !jupyter nbextension enable jupyter_highlight_selected_word --py
##################################################
"""
# ------------------------------------------------------#
