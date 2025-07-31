# import sys
# sys.path.insert(1, '/storage/coda1/p-ssinha338/0/shared/InSTAnT/InSTAnT/InSTAnT/')
from InSTAnT import Instant
import pandas as pd
import numpy as np
import subprocess
from ..io import read_h5ad, write_h5ad
from ._bicluster import LargeAverageSubmatrices, _log_combs, _expand_bicluster_rows, _expand_bicluster, _get_sprawl_score, _submatrix_score, _get_null_score
from sklearn.preprocessing import scale
from itertools import combinations
import timeit
import random
import sys
from datetime import timedelta
from sklearn.utils import check_array



def run_instant(adata_st, distance_threshold, threads, n_vertices = None, alpha_cpb = 0.001, alpha_fsm = 0.001, filename = None, remove_file = True, is_sliced = True):
    '''
    Run Instant on the spatial data to find colocalized gene pairs.
    Arguments
    ----------
    adata_st : AnnData
        Anndata object containing spatial transcriptomics data.
    distance_threshold : float
        Distance threshold for PP-Test.
    threads : int
        Number of threads to use.
    n_vertices : int
        Number of vertices to use for the FSM.
    alpha_cpb : float
        Significance level for the CPB.
    alpha_fsm : float
        Significance level for the FSM.
    filename : str
        Name of the file to save the preprocessed data. By defualt, file will be saved as .cellSP_st.h5ad and deleted post completion.
    remove_file : bool
        If True, the file will be deleted post completion.
    '''
    print("Running InSTAnT...")
    if filename == None:
        filename = f".cellSP_st_{random.randint(0,int(1e7))}.h5ad"
        write_h5ad(adata_st, filename)
    obj = Instant(distance_threshold = distance_threshold, threads = threads)
    obj.load_preprocessed_data(filename)
    if 'absZ' in adata_st.uns["transcripts"].columns:
        if is_sliced:
            obj.run_ProximalPairs3D_slice(distance_threshold = distance_threshold, min_genecount = 20)
        else:
            df_temp = adata_st.uns["transcripts"].copy()
            adata_st.uns["transcripts"]['absZ'] = adata_st.uns["transcripts"]['absZ_raw']
            obj.run_ProximalPairs3D(distance_threshold = distance_threshold, min_genecount = 20)
            adata_st.uns['transcripts'] = df_temp
    else:
        obj.run_ProximalPairs(distance_threshold = distance_threshold, min_genecount = 20)
    obj.run_GlobalColocalization(high_precision = True, alpha_cellwise = alpha_cpb)
    if n_vertices != None:
        obj.run_fsm(n_vertices = n_vertices, alpha = alpha_fsm)
    adata_st = read_h5ad(filename)
    if remove_file:
        subprocess.run(["rm", filename])
    return adata_st 


def analyse_fsm(adata_st, top_k, n_vertices, distance_threshold, alpha = 0.01):
    '''
    Analyse the results of the FSM.
    Arguments
    ----------
    adata_st : AnnData
        Anndata object containing spatial transcriptomics data.
    top_k : int
        Number of top cliques to select to consider.
    distance_threshold : float
        Distance threshold used for PP-Test.
    n_vertices : int
        Number of vertices to use for the FSM.
    alpha : float
        Significance level for the CPB and FSM.
    '''
    df_topk = adata_st.uns[f"nV{n_vertices}_cliques"].iloc[:top_k]
    cell_ids = adata_st.obs_names.values
    rows = []
    for _, i in df_topk.iterrows():
        gene_indexes = [list(adata_st.uns['geneList']).index(x) for x in i.Vertices.split(",")]
        uids = []
        for n, cell in enumerate(adata_st.uns[f"pp_test_d{distance_threshold}_pvalues"]):
            if all([cell[i][j] < alpha for i, j in list(combinations(gene_indexes, 2))]):
                uids.append(cell_ids[n])
        if len(uids) >= 5:
            rows.append([i.Vertices, len(uids), ','.join(uids)])
    df_topk = pd.DataFrame(rows, columns = ["genes", "#cells", "uIDs"])
    adata_st.uns[f"instant_fsm"] = df_topk
    return adata_st

def bicluster_instant(adata_st, distance_threshold, num_biclusters = 'auto', randomized_searches = 50000, scale_data = True, alpha = 0.001, cell_threshold = 5, gene_threshold = 3, threads = 1, expand = True, topk = None, oc = 0.667): #, randomized_searches = 50000
    '''
    Perform LAS biclustering on InSTAnT PP-test p-values to find spatial gene expression patterns.
    Arguments
    ----------
    adata_st : AnnData
        AnnData object containing spatial transcriptomics data with PP-test p-values computed.
    distance_threshold : float
        Distance threshold used to define spatial proximity between cells for the PP-test.
    num_biclusters : int or str, default='auto'
        Number of biclusters to detect. If 'auto', the algorithm determines an optimal number.
    randomized_searches : int, default=50000
        Number of randomized searches to perform in the LAS biclustering algorithm.
    scale_data : bool, default=True
        Whether to z-score the input data before biclustering.
    alpha : float, default=0.001
        Significance level for conditional permutation-based (CPB) tests.
    cell_threshold : int, default=5
        Minimum number of cells required for a valid bicluster.
    gene_threshold : int, default=3
        Minimum number of genes required for a valid bicluster.
    threads : int, default=1
        Number of threads to use for parallel computation.
    expand : bool, default=True
        Whether to expand biclusters by including additional nearby or correlated entries.
    topk : int or None, default=None
        If specified, restrict analysis to the top-k most significant gene-pairs.
    oc : float, default=0.667
        Overlap coefficient threshold for merging overlapping biclusters.
    '''
    if 'cpb_results' in adata_st.uns.keys():
        cpb_results = adata_st.uns['cpb_results'].reset_index()
        cpb_results = cpb_results[cpb_results.p_val_cond <= alpha]
        if topk != None:
            cpb_results = cpb_results.iloc[:topk]
    else:
        raise ValueError("CPB results not found in adata_st.uns. Please run `run_instant` first.")
    print("Bi-clustering InSTAnT CPB results...")
    start = timeit.default_timer()
    pval_matrix = np.ones((adata_st.n_obs, len(cpb_results.g1g2)))
    pp_pvalues = adata_st.uns[f'pp_test_d{distance_threshold}_pvalues'].copy()
    geneList = list(adata_st.uns['geneList'])
    gene_pairs = cpb_results.g1g2.values
    for n, i in cpb_results.reset_index().iterrows():
        index1 = geneList.index(i.gene_id1)
        index2 = geneList.index(i.gene_id2)
        for pos, cell in enumerate(pp_pvalues):
            assert cell[index1, index2] == cell[index1][index2]
            pval_matrix[pos][n] = cell[index1][index2] if cell[index1][index2] != 0 else sys.float_info.min
    pval_matrix = -np.log10(pval_matrix.copy())
    gene_pairs = [f"({x.split(',')[0]},{x.split(',')[1][1:]})" for x in gene_pairs]
    gene_pairs_array = np.array(gene_pairs)
    model = LargeAverageSubmatrices(num_biclusters = num_biclusters, randomized_searches = randomized_searches, scale_data = scale_data, threads = threads)
    if num_biclusters == 'auto':
        null_score = _get_null_score(pval_matrix, threads = threads)
        biclustering = model.run(pval_matrix, null_score)
    else:
        biclustering = model.run(pval_matrix)
    df_pval = pd.DataFrame(pval_matrix, columns = [','.join(x) for x in gene_pairs])
    df_pval.index = adata_st.obs_names
    df_pval_scaled = df_pval.copy()
    df_pval_scaled[:] = scale(df_pval)
    pval_matrix_scaled = scale(pval_matrix)
    uids = adata_st.obs_names.values
    # row_log_combs = _log_combs(pval_matrix.shape[0])[1:] # self._log_combs(num_rows)[1:] discards the case where the bicluster has 0 rows
    # col_log_combs = _log_combs(pval_matrix.shape[1])[1:] # self._log_combs(num_cols)[1:] discards the case where the bicluster has 0 columns
    # col_range = np.arange(1, pval_matrix.shape[1] + 1)
    rows = []
    for bicluster in biclustering.biclusters:
        if len(bicluster.cols) >= 2:
            bicluster_pairs = gene_pairs_array[bicluster.cols]
            bicluster_genes = list(set(gene for pair in bicluster_pairs for gene in pair.strip("()").split(',')))
            bicluster.rows = _expand_bicluster_rows(pval_matrix_scaled, bicluster.rows, bicluster.cols)
            bicluster_cells = uids[bicluster.rows]
            calculated_score = _submatrix_score(pval_matrix_scaled.shape[0], pval_matrix_scaled.shape[1], len(bicluster.rows), len(bicluster.cols), np.mean(pval_matrix_scaled[bicluster.rows][:, bicluster.cols]))#_get_sprawl_score(bicluster.rows, pval_matrix_scaled, col_range, col_log_combs, row_log_combs)
            rows.append([','.join(map(str, bicluster_pairs)),','.join(map(str, bicluster_genes)), ','.join(map(str, bicluster_cells)), len(bicluster_cells), 0, calculated_score])
    df_results = pd.DataFrame(rows, columns=['gene-pairs', 'genes', 'uIDs', '#cells', 'combined', "LAS score"])
    df_results['LAS score'] = df_results['LAS score'].astype('str')
    score_issues = []
    if expand:
        while True:
            original_length = len(df_results)
            df_results, score_issues = _expand_bicluster(df_results, pval_matrix, pval_matrix_scaled, list(uids), score_issues, mode = "instant", gene_pairs = gene_pairs, oc = oc)
            if len(df_results) == original_length:
                break
    df_results = df_results[df_results.uIDs.apply(lambda x: len(x.split(',')) > cell_threshold)]
    df_results = df_results[df_results['genes'].apply(lambda x: len(x.split(',')) >= gene_threshold)]
    adata_st.uns[f'instant_biclustering'] = df_results.reset_index(drop=True)
    print("InSTAnT CPB Bi-clustering time:", timedelta(seconds=timeit.default_timer() - start))
    return adata_st