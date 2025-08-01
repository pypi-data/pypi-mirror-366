"""
Module pour les algorithmes de clustering de trajectoires.

Ce module contient des fonctions pour calculer les matrices de substitution,
les matrices de distances, et effectuer un clustering hiérarchique.
"""


import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)  # Ignore FutureWarnings from pandas
from scipy.cluster.hierarchy import linkage, fcluster, leaves_list
from scipy.spatial.distance import squareform, pdist, cityblock
import Levenshtein
from tslearn.metrics import dtw, dtw_path_from_metric, gak
import tqdm
import logging
import timeit
from trajectoryclusteringanalysis.optimal_matching import optimal_matching_fast # Import de la version Cython optimisée
import kmedoids
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def compute_substitution_cost_matrix(sequences, alphabet, method='constant', custom_costs=None):
    """
    Calcule une matrice de coûts de substitution pour les séquences.

    Args:
        sequences (list): Liste des séquences à analyser.
        alphabet (list): Liste des états possibles.
        method (str): Méthode pour calculer les coûts ('constant', 'custom', 'frequency').
        custom_costs (dict): Coûts personnalisés pour les substitutions (optionnel).

    Returns:
        pd.DataFrame: Matrice de coûts de substitution.
    """
    num_states = len(alphabet)
    substitution_matrix = np.zeros((num_states, num_states))

    if method == 'constant':
        for i in range(num_states):
            for j in range(num_states):
                if i != j:
                    substitution_matrix[i, j] = 2

    elif method == 'custom':
        for i in range(num_states):
            for j in range(num_states):
                if i != j:
                    state_i = alphabet[i]
                    state_j = alphabet[j]
                    try:
                        key = state_i + ':' + state_j
                        cost = custom_costs[key]
                    except:
                        key = state_j + ':' + state_i  
                        cost = custom_costs[key]
                    substitution_matrix[i, j] = cost

    elif method == 'frequency':
        substitution_frequencies = np.zeros((num_states, num_states))

        for sequence in sequences:
            sequence = [char if char != 'nan' else '-' for char in sequence.split('-')]
            for i in range(len(sequence) - 1):
                state_i = alphabet.index(sequence[i])
                state_j = alphabet.index(sequence[i + 1])
                substitution_frequencies[state_i, state_j] += 1

        substitution_probabilities = substitution_frequencies / substitution_frequencies.sum(axis=1, keepdims=True)

        for i in range(num_states):
            for j in range(num_states):
                if i != j:
                    substitution_matrix[i, j] = 2 - substitution_probabilities[i, j] - substitution_probabilities[j, i]

    substitution_cost_matrix = pd.DataFrame(substitution_matrix, index=alphabet, columns=alphabet)
    return substitution_cost_matrix

def replace_labels(sequence, label_to_encoded):
    """
    Replaces sequence labels with their encoded values.

    Parameters:
    - sequence: Sequence to be encoded.
    - label_to_encoded: Dictionary mapping labels to encoded values.

    Returns:
    - Encoded sequence.
    """
    try:
        vectorized_replace = np.vectorize(label_to_encoded.__getitem__)
        return vectorized_replace(sequence)
    except KeyError as e:
        raise ValueError(f"Label {e} not found in label_to_encoded mapping.")
    #vectorized_replace = np.vectorize(label_to_encoded.get)
    #return vectorized_replace(sequence)

def compute_distance_matrix(data, sequences, label_to_encoded, metric='hamming', substitution_cost_matrix=None, alphabet=None, indel_cost=None, id=None):
    """
    Calcule une matrice de distances entre les séquences.

    Args:
        data (pd.DataFrame): Données d'entrée.
        sequences (list): Liste des séquences.
        label_to_encoded (dict): Mapping des labels vers des valeurs encodées.
        metric (str): Métrique de distance ('hamming', 'levenshtein', etc.).
        substitution_cost_matrix (pd.DataFrame): Matrice de coûts de substitution (optionnel).
        alphabet (list): Liste des états possibles (optionnel).

    Returns:
        np.ndarray: Matrice de distances.
    """
    logging.info(f"Calculating distance matrix using metric: {metric}...")
    start_time = timeit.default_timer()
    if sequences is None:
        pass
    else: 
        n = len(sequences)
    
    if metric == 'euclidean':   
        # Compute Euclidean distance
        if id in data.columns:
            data = data.drop(columns=[id])  # Drop the 'id' column if it exists
        distance_matrix = pdist(data, metric=metric)

    elif metric == 'hamming':
        # Compute Hamming distance
        distance_matrix = squareform(np.array(pdist(data.replace(label_to_encoded).drop(columns=['id']), metric=metric)))

    elif metric == 'levenshtein':
        # Compute Levenshtein distance
        distance_matrix = np.zeros((len(data), len(data)))
        for i in tqdm.tqdm(range(len(sequences))):
            for j in range(i + 1, len(sequences)):
                seq1, seq2 = sequences[i], sequences[j]                  
                distance = Levenshtein.distance(seq1, seq2)
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance

    elif metric == 'optimal_matching':
        # Compute Optimal Matching distance
        if substitution_cost_matrix is None:
            logging.error("Substitution cost matrix not found. Please compute the substitution cost matrix first.")
            raise ValueError("Substitution cost matrix not found. Please compute the substitution cost matrix first.")
        distance_matrix = np.zeros((len(data), len(data)))
         # Ensure substitution_cost_matrix is a NumPy array for .values access
        sub_matrix_values = substitution_cost_matrix.values if isinstance(substitution_cost_matrix, pd.DataFrame) else substitution_cost_matrix
        
        current_indel_cost = indel_cost
        if current_indel_cost is None:
            # Heuristic: indel cost is half the max substitution cost
            current_indel_cost = np.max(sub_matrix_values) / 2
            print(f"Calculated indel cost: {current_indel_cost} (from max sub_cost: {np.max(sub_matrix_values)})")
        else:
            print(f"User-provided indel cost: {current_indel_cost}")

        print("substitution cost matrix: \n", substitution_cost_matrix)
        alphabet_dict = {char: i for i, char in enumerate(alphabet)}
        #indel_cost = np.max(substitution_cost_matrix.values)/2
        sequences_idx = [np.array([alphabet_dict[s] for s in seq], dtype=np.int32) for seq in sequences]
        for i in tqdm.tqdm(range(len(sequences))):
            for j in range(i + 1, len(sequences)):
                seq1_idx, seq2_idx = sequences_idx[i], sequences_idx[j]
                normalized_dist = optimal_matching_fast(seq1_idx, seq2_idx, sub_matrix_values, indel_cost=current_indel_cost)           
                distance_matrix[i, j] = normalized_dist
                distance_matrix[j, i] = normalized_dist

    elif metric == 'dtw':
        # Compute Dynamic Time Warping (DTW) distance
        distance_matrix = np.zeros((len(data), len(data)))
        for i in tqdm.tqdm(range(len(sequences))):
            for j in range(i + 1, len(sequences)):
                seq1, seq2 = replace_labels(sequences[i], label_to_encoded), replace_labels(sequences[j], label_to_encoded)
                distance = dtw(seq1, seq2)
                max_length = max(len(seq1), len(seq2))
                normalized_dist = distance / max_length
                distance_matrix[i, j] = normalized_dist
                distance_matrix[j, i] = normalized_dist

    elif metric == 'dtw_path_from_metric':
        # Compute DTW distance using a custom metric
        distance_matrix = np.zeros((len(data), len(data)))
        for i in tqdm.tqdm(range(len(sequences))):
            for j in range(i + 1, len(sequences)):
                seq1, seq2 = replace_labels(sequences[i], label_to_encoded), replace_labels(sequences[j], label_to_encoded)
                #distance = dtw_path_from_metric(seq1, seq2, metric=np.abs(seq1 - seq2))
                distance, _ = dtw_path_from_metric(seq1, seq2, metric=cityblock)
                max_length = max(len(seq1), len(seq2))
                normalized_dist = distance / max_length
                distance_matrix[i, j] = normalized_dist
                distance_matrix[j, i] = normalized_dist

    elif metric == 'gak':
        # Compute Global Alignment Kernel (GAK) distance
        distance_matrix = np.zeros((len(data), len(data)))
        for i in tqdm.tqdm(range(len(sequences))):
            for j in range(i + 1, len(sequences)):
                seq1, seq2 = replace_labels(sequences[i], label_to_encoded), replace_labels(sequences[j], label_to_encoded)
                distance = gak(seq1, seq2)
                max_length = max(len(seq1), len(seq2))
                normalized_dist = distance / max_length
                distance_matrix[i, j] = normalized_dist
                distance_matrix[j, i] = normalized_dist

    c_time = timeit.default_timer() - start_time
    logging.info(f"Time taken for computation: {c_time:.2f} seconds")
    assert(np.allclose(distance_matrix, distance_matrix.T)), "Distance matrix is not symmetric"
    return distance_matrix

def hierarchical_clustering(tca_instance, distance_matrix, method='ward', optimal_ordering=True):
    """
    Effectue un clustering hiérarchique sur une matrice de distances.

    Args:
        tca_instance (TCA): Instance de la classe TCA.
        distance_matrix (np.ndarray): Matrice de distances.
        method (str): Méthode de linkage ('ward', 'single', etc.).
        optimal_ordering (bool): Optimiser l'ordre des feuilles (par défaut: True).

    Returns:
        np.ndarray: Matrice de linkage.
    """
    logging.info(f"Computing the linkage matrix using method: {method}...")
    condensed_distance_matrix = squareform(distance_matrix)
    linkage_matrix = linkage(condensed_distance_matrix, method=method, optimal_ordering=optimal_ordering)
    logging.info("Linkage matrix computed successfully")
    tca_instance.leaf_order = leaves_list(linkage_matrix)
    return linkage_matrix

def assign_clusters(linkage_matrix, num_clusters):
    """
    Assigne des étiquettes de clusters aux données.

    Args:
        linkage_matrix (np.ndarray): Matrice de linkage.
        num_clusters (int): Nombre de clusters à assigner.

    Returns:
        np.ndarray: Étiquettes des clusters.
    """
    clusters = fcluster(linkage_matrix, num_clusters, criterion='maxclust')
    return clusters

def k_medoids_clustering_faster(distance_matrix, num_clusters, method='fasterpam', init='random', max_iter=300, random_state=None, **kwargs):
    '''
    Performs K-Medoids clustering on a precomputed distance matrix.

    Args:
        distance_matrix (np.ndarray): Square distance matrix.
        num_clusters (int): The desired number of clusters.
        method (str, optional): The method to use for KMedoids.
            "fasterpam" (default), "fastpam1", "pam", "alternate", "fastermsc", "fastmsc", "pamsil" or "pammedsil".
        init (string, "random" (default), "first" or "build") – initialization method.
        max_iter (int, optional): Maximum number of iterations. Defaults to 300.
        random_state (int, RandomState instance or None, optional):
            Determines random number generation for centroid initialization.
            Use an int to make the randomness deterministic. Defaults to None.
        **kwargs: Additional keyword arguments to pass to KMedoids.

    Returns:
        kmedoids.KMedoids: the results containing:
            - cluster_centers : None for 'precomputed'
            - medoid_indices : The indices of the medoid rows in X.
            - labels : Labels of each point.
            - inertia : Sum of distances of samples to their closest cluster center.
    '''
    if not isinstance(distance_matrix, np.ndarray):
        raise TypeError("distance_matrix must be a NumPy array.")
    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        distance_matrix = squareform(distance_matrix)  # Ensure it's a square matrix
    if not isinstance(num_clusters, int) or num_clusters <= 0: # Ensure num_clusters is positive int
        raise ValueError("num_clusters must be a positive integer.")
    if num_clusters > distance_matrix.shape[0]:
        raise ValueError("num_clusters cannot be greater than the number of samples.")

    logging.info(f"Performing K-Medoids clustering with {num_clusters} clusters...")
    kmedoids_model = kmedoids.KMedoids(
        n_clusters=num_clusters,
        metric='precomputed',  # Crucial for using a distance matrix
        method=method,
        init=init,
        max_iter=max_iter,
        random_state=random_state,
        **kwargs
    ).fit(distance_matrix)  # Fit the model to the distance matrix
    # KMedoids expects the distance matrix itself as input to fit/fit_predict
    labels = kmedoids_model.labels_ + 1  # Adjust labels to start from 1
    medoid_indices = kmedoids_model.medoid_indices_
    inertia = kmedoids_model.inertia_
    logging.info("K-Medoids clustering completed.")
    return labels, medoid_indices, inertia

def vectorize_sequences_by_state_frequency(sequences, alphabet,normalize=False):
    """
    Vectorizes sequences by counting the frequency of each state from the alphabet.

    Args:
        sequences (list of np.ndarray or list of lists): 
            A list where each element is a sequence (np.array or list of states).
        alphabet (list): 
            A list of unique states that can appear in the sequences. 
            The order of states in the alphabet determines the order in the output vector.

    Returns:
        np.ndarray: 
            A 2D NumPy array where each row corresponds to a sequence and each column 
            corresponds to a state in the alphabet. The values are the frequencies of states.
    """
    if not isinstance(sequences, list):
        raise TypeError("Input 'sequences' must be a list of sequences.")
    if not isinstance(alphabet, list):
        raise TypeError("Input 'alphabet' must be a list.")
    if not all(isinstance(state, (str, int, float)) for state in alphabet): # Assuming states are simple types
        raise ValueError("Alphabet should contain simple data types (strings, numbers).")
    if len(set(alphabet)) != len(alphabet):
        raise ValueError("Alphabet should not contain duplicate states.")

    alphabet_map = {state: i for i, state in enumerate(alphabet)}
    num_sequences = len(sequences)
    num_states = len(alphabet)
    
    vectorized_data = np.zeros((num_sequences, num_states), dtype=int)
    
    for i, seq in enumerate(sequences):
        if not isinstance(seq, (np.ndarray, list)):
            logging.warning(f"Sequence at index {i} is not a list or numpy array, skipping.")
            continue
        for state in seq:
            if state in alphabet_map:
                vectorized_data[i, alphabet_map[state]] += 1
            # else:
            #     logging.warning(f"State '{state}' in sequence {i} not found in alphabet. It will be ignored.")
    if normalize:
        vectorized_data = vectorized_data / vectorized_data.sum(axis=1, keepdims=True)          
    return vectorized_data


def kmeans_on_frequency(self, num_clusters, random_state=None,normalize=False, **kmeans_kwargs):
        """
        Performs K-Means clustering on a vectorized representation of sequences.

        The sequences are first converted into numerical vectors based on the frequency
        of each state from the alphabet. Then, scikit-learn's KMeans is applied.

        Args:
            num_clusters (int): The desired number of clusters.
            random_state (int, RandomState instance or None, optional):
                Determines random number generation for centroid initialization.
                Use an int to make the randomness deterministic. Defaults to None.
            normalize (bool): If True, normalizes the frequency vectors to sum to 1.
            **kmeans_kwargs: Additional keyword arguments to pass to sklearn.cluster.KMeans.
                             Example: n_init=10, max_iter=300.

        Returns:
                returns a tuple containing:
                  - 'labels': Labels of each point (adjusted to start from 1).
                  - 'cluster_centers': Coordinates of cluster centers (vectors of state frequencies).
                  - 'inertia': Sum of squared distances of samples to their closest cluster center.

        """
        logging.info(f"Performing K-Means clustering with {num_clusters} clusters...")
        
        # 1. Vectorize sequences
        vectorized_data = vectorize_sequences_by_state_frequency(list(self.sequences), self.alphabet,normalize=normalize)
        
        if vectorized_data.shape[0] == 0:
            logging.error("No data to cluster after vectorization.")
            raise ValueError("Vectorized data is empty, cannot perform K-Means.")
        if num_clusters > vectorized_data.shape[0]:
            logging.warning(f"Number of clusters ({num_clusters}) is greater than the number of samples ({vectorized_data.shape[0]}). Setting num_clusters to number of samples.")
            num_clusters = vectorized_data.shape[0]

        # 2. Apply KMeans
        # Set default n_init if not provided, to suppress FutureWarning in scikit-learn >= 1.4
        if 'n_init' not in kmeans_kwargs and hasattr(KMeans(), 'n_init'): # Check if n_init is an attribute
             # Get default n_init value from a temporary KMeans instance if possible
            try:
                default_n_init = KMeans().n_init
                if default_n_init == 'auto': # 'auto' is deprecated in favor of explicit 10
                    kmeans_kwargs['n_init'] = 10 
                else:
                    kmeans_kwargs['n_init'] = default_n_init
            except AttributeError: # Fallback if n_init is not easily retrievable or behaves unexpectedly
                 kmeans_kwargs['n_init'] = 10
        
        kmeans = KMeans(n_clusters=num_clusters, random_state=random_state, **kmeans_kwargs)
        kmeans.fit(vectorized_data)
        
        logging.info("K-Means clustering completed.")
        
        return kmeans.labels_ + 1, kmeans.cluster_centers_,kmeans.inertia_


def kmeans_on_wide_format(data, num_clusters, label_to_encoded=None, random_state=None, normalize=False,  **kmeans_kwargs):
    """
    Performs KMeans clustering directly on wide-format (fixed-column encoded) sequences.

    Args:
        num_clusters (int): Number of desired clusters.
        label_to_encoded (dict, optional): Dictionary to encode labels. If None, uses self.label_to_encoded if available.
        random_state (int, optional): Random seed.
        **kmeans_kwargs: Additional arguments for sklearn.cluster.KMeans.

    Returns:
        dict: Dictionary containing:
            - 'labels': Cluster labels (starting at 1),
            - 'cluster_centers': Cluster centers,
            - 'inertia': Model inertia,

    """
    logging.info(f"Performing KMeans clustering on wide-format data with {num_clusters} clusters.")

    # Replace NaN with a special value (e.g., 'MISSING')
    data_no_nan = data.drop(columns=['id']).fillna('MISSING')

    # Optionally, add 'MISSING' to label_to_encoded if not present
    if label_to_encoded is not None and 'MISSING' not in label_to_encoded:
        label_to_encoded = label_to_encoded.copy()
        label_to_encoded['MISSING'] = -1
    # Prepare data: encode
    encoded_matrix = np.vstack([
        replace_labels(seq, label_to_encoded)
        for seq in data_no_nan.values
    ])

    if normalize:
        scaler = StandardScaler()
        encoded_matrix = scaler.fit_transform(encoded_matrix)
   

    if num_clusters > encoded_matrix.shape[0]:
        logging.warning(f"num_clusters ({num_clusters}) > number of samples ({encoded_matrix.shape[0]}). Adjusting.")
        num_clusters = encoded_matrix.shape[0]

    # Set n_init if not provided
    if 'n_init' not in kmeans_kwargs and hasattr(KMeans(), 'n_init'):
        try:
            default_n_init = KMeans().n_init
            if default_n_init == 'auto':
                kmeans_kwargs['n_init'] = 10
            else:
                kmeans_kwargs['n_init'] = default_n_init
        except Exception:
            kmeans_kwargs['n_init'] = 10

    # Clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=random_state, **kmeans_kwargs)
    kmeans.fit(encoded_matrix)

    logging.info("KMeans on wide format completed.")

    return kmeans.labels_ + 1, kmeans.cluster_centers_,kmeans.inertia_

