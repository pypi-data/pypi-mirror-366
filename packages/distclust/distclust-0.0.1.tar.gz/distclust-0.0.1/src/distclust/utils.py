import numpy as np
from scipy.spatial import distance
import random
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'
from sklearn.metrics import silhouette_score
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import time
import json
from scipy.cluster import hierarchy


def merge_list(list_of_list):
    list_final = []
    for i in list_of_list:
        list_final += i
    return list(set(list_final))


def density_calc(list_base, list_point):
    n = len(list_point)
    list_base = list(set(list_base))
    list_density = []
    list_point_final = []
    for i in list_base:
        if i in list_point:
            list_density.append(list_point.count(i) / n)
            list_point_final.append(i)
        else:
            list_density.append(0)  # changed
    return list_point_final, list_density


def density_calc_list(list_of_list, list_base):
    list_density = []
    for i in list_of_list:
        list_density.append(np.array([density_calc(list_base, i)[1]]).transpose())
    return list_density


def create_blank_dataset_with_metadata(m):
    data = {
        'system num': [],
        'data points': [],
    }

    for i in range(1, m + 1):
        data[f'{i - 1}'] = []
    data[f'label'] = []
    blank_dataset = pd.DataFrame(data)

    return blank_dataset


def fill_dataset_with_records(dataset, records):
    for record in records:
        dataset = pd.concat([dataset, pd.DataFrame([record])], ignore_index=True)
    return dataset


def make_record(list_of_list, list_p):
    records_to_be_added = []
    for i in range(len(list_of_list)):
        records_to_be_added.append({'system num': i, 'data points': list_of_list[i], 'p': list_p[i]})

    return records_to_be_added


def fill_ot_distance(df, Xi, cost_matrix, num_of_iterations, lambda_pen):
    for i in range(len(df)):
        for j in range(i):
            OT_plan_test = ot.bregman.sinkhorn(df['p'][i].transpose().tolist()[0], df['p'][j].transpose().tolist()[0],
                                               cost_matrix, lambda_pen, method='sinkhorn', numItermax=num_of_iterations,
                                               stopThr=1e-09, verbose=False, log=False, warn=True, warmstart=None)
            OT_cost_test = np.multiply(OT_plan_test, cost_matrix).sum() - lambda_pen * entropy(OT_plan_test)
            df.loc[j, str(i)] = OT_cost_test


def calc_barycenter(df, cost_matrix, lambda_value):
    list_p_cluster = [i.transpose()[0] for i in df['p']]
    matrix_p = np.column_stack(list_p_cluster)
    return ot.barycenter(matrix_p, cost_matrix, lambda_value, weights=None, method='sinkhorn', numItermax=200,
                         stopThr=0.0001, verbose=False, log=False, warn=True)


def condensed_creator(arr):
    m = arr.shape[0]

    # Extract upper triangle indices
    upper_triangle_indices = np.triu_indices(m, k=1)

    # Use the indices to get the upper triangle elements
    upper_triangle_elements = arr[upper_triangle_indices]

    # Convert the elements to a list if needed
    upper_triangle_list = upper_triangle_elements.tolist()

    # Print or use the resulting list as needed
    return upper_triangle_list


def plot_dendrogram(df, save_file=False):
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()

    scaled_matrix = matrix_final
    np.fill_diagonal(scaled_matrix, 0)

    matrix_final = condensed_creator(scaled_matrix)
    linkage_matrix = linkage(matrix_final, method='complete')

    plt.figure(figsize=(10, 7))
    dendrogram(linkage_matrix, color_threshold=-np.inf, above_threshold_color='gray')
    plt.xlabel('Systems')  # Set the x-axis label to 'System'
    plt.xticks([])  # Remove x-axis tick labels
    plt.ylabel('Distance')
    if save_file:
        plt.savefig('plot_dendrogram.png', format='png', dpi=1000)
    plt.show()


def silhouette_score_agglomerative(df):
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()
    min_val = np.min(matrix)
    max_val = np.max(matrix)
    scaled_matrix = (matrix_final - min_val)
    np.fill_diagonal(scaled_matrix, 0)
    silhouette_score_list = []
    for i in range(2, len(df)):
        index_list = cluster_list_creator(df, i)
        silhouette_score_list.append(silhouette_score(scaled_matrix, index_list, metric='precomputed'))
    return silhouette_score_list


def entropy(matrix):
    matrix = np.array(matrix)
    non_zero_entries = matrix[matrix > 0]
    entropy_value = -np.sum(non_zero_entries * np.log(non_zero_entries))

    return entropy_value


def cluster_list_creator(df, num_of_clusters):
    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    matrix_final = matrix + matrix.transpose()

    min_val = np.min(matrix)
    max_val = np.max(matrix)
    scaled_matrix = matrix_final
    np.fill_diagonal(scaled_matrix, 0)
    matrix_final = condensed_creator(scaled_matrix)

    linkage_matrix = linkage(matrix_final, method='complete')

    height = np.shape(linkage_matrix)[0]
    list_linkage = [[i] for i in range(len(df))]
    for i in range(height):
        list_linkage.append(list_linkage[int(linkage_matrix[i][0])] + list_linkage[int(linkage_matrix[i][1])])

    list_linkage_inverse = list_linkage[::-1]
    list_final = list_linkage_inverse[num_of_clusters - 1:]
    list_index = []
    for i in range(len(df)):
        for j in list_final:
            if i in j:
                list_index.append(list_final.index(j))
                break

    return list_index


def calculate_OT_cost(p, q, reg, cost_matrix, num_iterations, stop_theshold):
    p = np.array([p]).T
    q = np.array([q]).T
    Xi = np.exp(-cost_matrix / reg)
    v_n = np.ones((Xi.shape[1], 1))
    v_old = v_n
    for _ in range(num_iterations):
        v_n = q / (Xi.T @ (p / (Xi @ v_n)))
        if np.linalg.norm(v_n - v_old) < stop_theshold:
            break
        v_old = v_n
    diag_u = np.diagflat((p / (Xi @ v_n)))
    diag_v = np.diagflat(v_n)
    OT_plan = diag_u @ Xi @ diag_v
    OT_cost = np.multiply(OT_plan, cost_matrix).sum()
    return OT_plan


def fill_ot_distance(df, num_of_iterations, lambda_pen, stop_theshold):
    for i in range(len(df)):  # Here we iterate among rows, and below we shall calculate the densities
        for j in range(i + 1):
            cost_matrix = distance.cdist(df['data points'][i], df['data points'][j])
            min_time = time.time()
            OT_plan_test = calculate_OT_cost(df['p'][i], df['p'][j], lambda_pen, cost_matrix, num_of_iterations,
                                             stop_theshold)
            OT_cost_test = np.multiply(OT_plan_test, cost_matrix).sum()  # yakhoda
            max_time = time.time()
            df.loc[j, str(i)] = OT_cost_test


def normalize_tuples(list_of_lists):
    num_dimensions = len(list_of_lists[0][0])  # Get the number of dimensions from the first tuple

    # Extract all values for each dimension
    all_values = [[] for _ in range(num_dimensions)]
    for sublist in list_of_lists:
        for i, t in enumerate(sublist):
            for j in range(num_dimensions):
                all_values[j].append(t[j])

    # Compute the minimum and maximum values for each dimension
    min_values = [min(dim_values) for dim_values in all_values]
    max_values = [max(dim_values) for dim_values in all_values]

    # Normalize each dimension of each tuple
    normalized_list_of_lists = []
    for sublist in list_of_lists:
        normalized_sublist = []
        for t in sublist:
            normalized_t = tuple(
                (t[j] - min_values[j]) / (max_values[j] - min_values[j]) for j in range(num_dimensions))
            normalized_sublist.append(normalized_t)
        normalized_list_of_lists.append(normalized_sublist)

    return normalized_list_of_lists


def list_of_lists_to_json(list_of_lists):
    json_data = {}

    for idx, lst in enumerate(list_of_lists):
        json_data[idx + 1] = {
            'id': idx + 1,
            'data points': lst
        }

    json_output = json.dumps(json_data, indent=4)

    return json_output


def json_content_to_list_of_lists(json_content):
    json_data = json.loads(json_content)

    list_of_lists = []
    for key in sorted(json_data.keys(), key=int):
        list_of_lists.append([tuple(item) for item in json_data[key]['data points']])

    return list_of_lists


def list_to_array(*lst):
    r""" Convert a list if in numpy format """
    lst_not_empty = [a for a in lst if len(a) > 0 and not isinstance(a, list)]

    if len(lst_not_empty) == 0:
        type_as = np.zeros(0)

    else:
        type_as = lst_not_empty[0]
    if len(lst) > 1:
        return [np.from_numpy(np.array(a), type_as=type_as)
                if isinstance(a, list) else a for a in lst]
    else:
        if isinstance(lst[0], list):
            return np.from_numpy(np.array(lst[0]), type_as=type_as)
        else:
            return lst[0]


def geometricBar(weights, alldistribT):
    """return the weighted geometric mean of distributions"""
    weights, alldistribT = list_to_array(weights, alldistribT)
    assert (len(weights) == alldistribT.shape[1])
    return np.exp(np.dot(np.log(alldistribT), weights.T))


def geometricMean(alldistribT):
    """return the  geometric mean of distributions"""
    alldistribT = list_to_array(alldistribT)
    return np.exp(np.mean(np.log(alldistribT), axis=1))


def barycenter_sinkhorn(A, M, reg, weights=None, numItermax=1000,
                        stopThr=1e-4, verbose=False, log=False, warn=True):
    A, M = list_to_array(A, M)

    if weights is None:
        weights = np.ones((A.shape[1],), dtype=A.dtype) / A.shape[1]
    else:
        assert (len(weights) == A.shape[1])

    if log:
        log_dict = {'err': []}

    K = np.exp(-M / reg)

    err = 1

    UKv = np.dot(K, (A.T / np.sum(K, axis=0)).T)
    u = (geometricMean(UKv) / UKv.T).T
    for ii in range(numItermax):

        v = (A / np.dot(K, u))
        ps = np.tile(geometricBar(weights, UKv), (A.shape[1], 1)).T
        UKv = u * np.dot(K.T, v)
        u = ps / np.dot(K, v)

        if ii % 10 == 1:
            err = np.sum(np.std(UKv, axis=1))

            if log:
                log_dict['err'].append(err)

            if err < stopThr:
                break
            if verbose:
                if ii % 200 == 0:
                    print('{:5s}|{:12s}'.format('It.', 'Err') + '\n' + '-' * 19)
                print('{:5d}|{:8e}|'.format(ii, err))
    else:
        if warn:
            warnings.warn("Sinkhorn did not converge. You might want to "
                          "increase the number of iterations `numItermax` "
                          "or the regularization parameter `reg`.")
    if log:
        log_dict['niter'] = ii
        return geometricBar(weights, UKv), log_dict
    else:
        return geometricBar(weights, UKv)


def calc_barycenter(df, cost_matrix, lambda_value):
    list_p_cluster = [i for i in df['p']]
    matrix_p = np.column_stack(list_p_cluster)
    return barycenter_sinkhorn(matrix_p, cost_matrix, lambda_value, weights=None, numItermax=200, stopThr=0.0001,
                               verbose=False, log=False, warn=True)


def dataframe_to_json(df, columns=None):
    """
    Convert a pandas DataFrame to a JSON format where each row index maps to a dictionary
    of column names and their corresponding values.

    Parameters:
    df (pandas.DataFrame): The DataFrame to convert.

    Returns:
    str: JSON string representing the DataFrame.
    """
    # Convert DataFrame to dictionary format
    if columns == None:
        df_dict = df.to_dict(orient='index')
    else:
        df_dict = df[columns].to_dict(orient='index')
    for row in df_dict.values():
        for key, value in row.items():
            if isinstance(value, np.ndarray):
                row[key] = value.tolist()
    # Convert dictionary to JSON
    json_result = json.dumps(df_dict, indent=4)

    return json_result


def cluster_distributions(dist_file, reg=0.5, n_clusters=None, calculate_barycenter=False, stop_theshold=10 ** -9,
                          num_of_iterations=1000, plt_dendrogram=True):
    list_sim_outputs_raw = json_content_to_list_of_lists(dist_file)
    list_base = merge_list(list_sim_outputs_raw)
    list_sim_outputs = []
    p_list = []
    for i in list_sim_outputs_raw:
        list_sim_outputs.append(density_calc(i, i)[0])
        p_list.append(density_calc(i, i)[1])

    normalized_list_sim_outputs = normalize_tuples(list_sim_outputs)
    m = len(normalized_list_sim_outputs)
    blank_df = create_blank_dataset_with_metadata(m)
    df = fill_dataset_with_records(blank_df, make_record(normalized_list_sim_outputs, p_list))
    # Display the filled dataset
    df['data points real'] = list_sim_outputs
    fill_ot_distance(df, num_of_iterations, reg, stop_theshold)
    if plt_dendrogram:
        plot_dendrogram(df, save_file=False)
    sil_values = silhouette_score_agglomerative(df)
    #     print(df['47'][0])
    if n_clusters == None:  # if cluster_num is none then max_silhouette index will be considered, else the number that is wanted
        n_clusters = sil_values.index(max(sil_values)) + 2

    columns_to_filter = [str(i) for i in range(len(df))]
    df_filter = df[columns_to_filter]
    filled_df = df_filter.fillna(0)
    matrix = filled_df.values
    diagonal = np.diagonal(matrix)
    matrix_final = matrix + matrix.transpose()
    np.fill_diagonal(matrix_final, 0)
    # Below we get the linkage matrix, which will be used in many parts
    upper_triangle_flat = matrix_final[np.triu_indices_from(matrix_final, k=1)]
    Z = hierarchy.linkage(upper_triangle_flat, method='complete')
    clusters = hierarchy.fcluster(Z, n_clusters, criterion='maxclust')
    df['cluster'] = clusters
    print(clusters.tolist())

    # Here the dataset for clusters is generated
    blank_df_clusters = create_blank_dataset_with_metadata(n_clusters)
    records_to_be_added = []
    for i in range(1, n_clusters + 1):
        records_to_be_added.append({'cluster num': i, 'p': 0})
    df_clusters = fill_dataset_with_records(blank_df_clusters, records_to_be_added)

    list_p_cluster_new = []
    list_sup_cluster_new = []
    list_sup_cluster_real_new = []
    for i in range(1, len(df_clusters) + 1):
        df_test = df[df['cluster'] == i]
        list_column = df_test['data points']
        list_sim_outputs_cluster = list_column.tolist()
        list_base_cluster = merge_list(list_sim_outputs_cluster)

        list_column_real = df_test['data points real']
        list_sim_outputs_cluster_real = list_column_real.tolist()
        list_base_cluster_real = merge_list(list_sim_outputs_cluster_real)

        cost_matrix_cluster = distance.cdist(list_base_cluster, list_base_cluster)
        density_list_cluster = density_calc_list(list_sim_outputs_cluster, list_base_cluster)
        df_test['p'] = density_list_cluster
        list_p_cluster_new.append(calc_barycenter(df_test, cost_matrix_cluster, reg))
        list_sup_cluster_new.append(list_base_cluster)
        list_sup_cluster_real_new.append(list_base_cluster_real)

    df_clusters['p'] = list_p_cluster_new
    df_clusters['data points'] = list_sup_cluster_new
    df_clusters['data points real'] = list_sup_cluster_real_new
    json_inputs = dataframe_to_json(df, ['system num', 'data points real', 'cluster'])
    json_barycenters = dataframe_to_json(df_clusters, ['data points real', 'p'])

    return json_inputs, json_barycenters
