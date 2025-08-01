import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
from scipy.cluster.hierarchy import dendrogram
import pandas as pd
import warnings
from scipy.cluster import hierarchy

warnings.filterwarnings("ignore", category=FutureWarning)  # Ignore FutureWarnings from pandas
from .utils import modal_filter_numba



# Function to plot a dendrogram for hierarchical clustering
def plot_dendrogram(linkage_matrix,title='Dendrogram of Treatment Sequences'):
    """
    Plot a dendrogram based on the hierarchical clustering of treatment sequences.

    Parameters:
    linkage_matrix (numpy.ndarray): The linkage matrix containing the hierarchical clustering information.
    title (str): The title of the plot.

    Returns:
    None
    """
    # Create a figure for the dendrogram
    plt.figure(figsize=(10, 6))
    dendrogram(linkage_matrix)  # Plot the dendrogram
    plt.title(title)  # Add a title
    plt.xlabel('Patients')  # Label for the x-axis
    plt.ylabel('Distance')  # Label for the y-axis
    plt.show()  # Display the plot

# Function to plot a clustermap with a custom legend
def plot_clustermap(data, id_col, label_to_encoded, colors, alphabet, states, linkage_matrix, mode=None,title="Clustermap of individuals"):
    """
    Plot a clustermap of the treatment sequences with a custom legend.

    Parameters:
    data (pd.DataFrame): The dataset containing treatment sequences.
    id_col (str): The column name for patient IDs.
    label_to_encoded (dict): Mapping of labels to encoded values.
    colors (str): Colormap for the heatmap.
    alphabet (list): List of unique treatment states.
    states (list): List of state labels corresponding to the alphabet.
    linkage_matrix (numpy.ndarray): The linkage matrix containing the hierarchical clustering information.
    title (str): The title of the plot.

    Returns:
    None
    """
    data = data.drop(id_col, axis=1).replace(label_to_encoded)

    # Generate the clustermap
    clustermap = sns.clustermap(
        data,
        cmap=colors,
        metric='precomputed',
        method='ward',
        row_linkage=linkage_matrix,
        row_cluster=True, 
        col_cluster=False,
        dendrogram_ratio=(0.15, 0.05), 
        cbar=False
    )

    # # Remove the gap between dendrogram and heatmap
    # clustermap.ax_row_dendrogram.set_position([
    #     clustermap.ax_row_dendrogram.get_position().x0 - 0.05,
    #     clustermap.ax_row_dendrogram.get_position().y0,
    #     clustermap.ax_row_dendrogram.get_position().width,
    #     clustermap.ax_heatmap.get_position().height
    # ])
    # clustermap.ax_heatmap.set_position([
    #     clustermap.ax_heatmap.get_position().x0,
    #     clustermap.ax_heatmap.get_position().y0,
    #     clustermap.ax_heatmap.get_position().width,
    #     clustermap.ax_heatmap.get_position().height
    # ])

    # Customize the plot
    xticks = clustermap.ax_heatmap.get_xticks()
    xtick_labels = [data.columns[int(i)] if int(i) < len(data.columns) else "" for i in xticks]
    clustermap.ax_heatmap.set_xticklabels(xtick_labels, rotation=45, ha='right')
    clustermap.ax_heatmap.set_yticks([])
    clustermap.ax_heatmap.set_yticklabels([])
    clustermap.ax_heatmap.set_title(title)
    clustermap.cax.set_visible(False)

    # Add a legend for treatment states
    if mode == 'unidimensional':
        viridis_colors_list = [plt.cm.viridis(i) for i in np.linspace(0, 1, len(alphabet))]
        legend_handles = [plt.Rectangle((0, 0), 1, 1, color=viridis_colors_list[i], label=alphabet[i]) for i in range(len(alphabet))]
        clustermap.ax_heatmap.legend(
            handles=legend_handles,
            labels=states,
            loc='center left',
            bbox_to_anchor=(1.005, 0.5),
            borderaxespad=0.0,
            ncol=1,
            title='Events'
        )
    elif mode == 'multidimensional':
        # Calculate colorbar position so its top left aligns with the top right of the heatmap
        heatmap_bbox = clustermap.ax_heatmap.get_position()
        cbar_width = 0.02
        cbar_height = 0.18
        cbar_x = heatmap_bbox.x1 # right edge of heatmap
        cbar_y = heatmap_bbox.y1 - cbar_height - 0.01 # align top
        cbar_pos = [cbar_x, cbar_y, cbar_width, cbar_height]
        cbar = clustermap.figure.colorbar(plt.cm.ScalarMappable(cmap=colors), cax=plt.axes(cbar_pos))
        cbar.set_label('Phenotype Intensity', rotation=270, labelpad=15)
    else:
        raise ValueError("Invalid mode. Choose either 'unidimensional' or 'multidimensional'.")   
    
    # Use clustermap's own figure for layout adjustment to avoid UserWarning
    #clustermap.figure.tight_layout()
    # Optionally, adjust subplots for better spacing
    clustermap.figure.subplots_adjust(right=0.90)
   
    plt.show()

# Function to plot the inertia diagram for determining the optimal number of clusters
def plot_inertia(linkage_matrix, n_points=10,title="Inertia Diagram (Elbow Method)"):
    """
    Plot the inertia diagram to help determine the optimal number of clusters.

    Parameters:
    linkage_matrix (numpy.ndarray): The linkage matrix from hierarchical clustering.
    n_points (int): Number of last merges to plot (default is 10).
    title (str): The title of the plot.

    Returns:
    None
    """
    # Extract the last n_points merges
    num_merges = linkage_matrix.shape[0]
    n_points = min(n_points, num_merges)
    last = linkage_matrix[-n_points:, 2]  # Distances of the last merges
    last_rev = last[::-1]  # Reverse the order for plotting
    idxs = np.arange(2, len(last) + 2)  # Cluster indices

    # Plot the inertia diagram
    plt.figure(figsize=(10, 6))
    plt.step(idxs, last_rev, c="black", linewidth=2)  # Step plot for inertia
    plt.scatter(idxs, last_rev, c="red", label="Inertia points")  # Highlight points

    # Customize the plot
    plt.xlabel("Number of clusters")  # Label for the x-axis
    plt.ylabel("Inertia (distance)")  # Label for the y-axis
    plt.title(title)  # Add a title
    plt.legend()  # Add a legend
    plt.grid(True, linestyle="--", alpha=0.6)  # Add a grid for better readability
    plt.show()

# Function to plot heatmaps for each cluster
def plot_cluster_heatmaps(data, id_col, label_to_encoded, colors, alphabet, states, clusters, leaf_order, sorted=True, mode=None,title='Heatmaps of Treatment Sequences by Cluster'):
    """
    Plot heatmaps for each cluster, ensuring the data is sorted by leaves_order.

    Parameters:
    data (pd.DataFrame): The dataset containing treatment sequences.
    id_col (str): The column name for patient IDs.
    label_to_encoded (dict): Mapping of labels to encoded values.
    colors (str): Colormap for the heatmap.
    alphabet (list): List of unique treatment states.
    states (list): List of state labels corresponding to the alphabet.
    clusters (numpy.ndarray): The cluster assignments for each patient.
    leaf_order (list): The order of leaves from the hierarchical clustering.
    sorted (bool): Whether to sort the data within each cluster. Default is True.
    title (str): The title of the plot.

    Returns:
    None
    """
    data = data.drop(id_col, axis=1).replace(label_to_encoded)
    
    # Reorder data based on leaf order
    if leaf_order is None or len(leaf_order) == 0:
        reordered_data = data.copy()
        reordered_clusters = clusters
    else:
        leaves_order = leaf_order
        reordered_data = data.iloc[leaves_order]
        reordered_clusters = clusters[leaves_order]

    # Group data by clusters and preserve order within clusters
    unique_clusters = np.unique(reordered_clusters)
    cluster_data = {}
    for cluster_label in unique_clusters:
        cluster_indices = np.where(reordered_clusters == cluster_label)[0]
        cluster_df = reordered_data.iloc[cluster_indices]
        if sorted:
            # Optionally sort rows within each cluster by all columns for consistency
            cluster_df = cluster_df.sort_values(by=list(cluster_df.columns))
        cluster_data[cluster_label] = cluster_df

    heights = [len(cluster_df) if len(cluster_df) > 0 else 1 for cluster_df in cluster_data.values()]
    num_clusters = len(cluster_data)
    fig, axs = plt.subplots(
        num_clusters, 1,
        # figsize=(min(num_clusters * 3, 10),
         #         max(sum(heights) * 0.2, 4)),
        sharex=True,
        gridspec_kw={'height_ratios': heights}
    )
    # Ensure axs is always iterable
    if num_clusters == 1:
        axs = [axs]
    if num_clusters == 2:
        axs = np.array([axs])
    
    # elif     
    
    plt.subplots_adjust(hspace=2, wspace=0.5)
        
    if mode == 'unidimensional':
        plt.suptitle(title, fontsize=16, y=1.02)
        for cluster_label, (cluster_df, ax) in enumerate(zip(cluster_data.items(), axs)):
            #sns.heatmap(cluster_df[1].drop(id_col, axis=1).replace(label_to_encoded), cmap=colors, cbar=False, ax=ax, yticklabels=False)
            heatmap_data = cluster_df[1]
            heatmap_data = heatmap_data.infer_objects(copy=True)
            sns.heatmap(heatmap_data,
                        cmap=colors,
                        cbar=False, 
                        ax=ax, 
                        yticklabels=False)
            ax.tick_params(axis='x', rotation=45)
            ax.text(1.05, 0.5, f'cluster {cluster_label+1} (n={len(cluster_df[1])})', transform=ax.transAxes, ha='left', va='center')
        axs[-1].set_xlabel('Time in months')
        
        # Add a legend for treatment states
        viridis_colors_list = [plt.cm.viridis(i) for i in np.linspace(0, 1, len(alphabet))]
        legend_handles = [plt.Rectangle((0, 0), 1, 1, color=viridis_colors_list[i], label=alphabet[i]) for i in range(len(alphabet))]
        plt.legend(handles=legend_handles, labels=states, loc='lower right', ncol=1, title='Events')
        

    elif mode == 'multidimensional':
        # vmin, vmax = 0, 1
        #title = 'Heatmaps of Phenotypes Intensity by Cluster'
        plt.suptitle(title, y=1.)
        for cluster_label, (cluster_df, ax) in enumerate(zip(cluster_data.items(), axs)):
            heatmap_data = cluster_df[1]
            heatmap_data = heatmap_data.infer_objects(copy=True)
            sns.heatmap(heatmap_data,
                        cmap=colors,
                        cbar=False,
                        ax=ax,
                        yticklabels=False)
            ax.tick_params(axis='x')
            ax.text(1.05, 0.5, f'cluster {cluster_label+1} (n={len(cluster_df[1])})', transform=ax.transAxes, ha='left', va='center')
        axs[-1].set_xlabel('Phenotypes')

    else:
        raise ValueError("Invalid mode. Choose either 'unidimensional' or 'multidimensional'.")

   # plt.tight_layout()
    plt.show()

# Function to plot the percentage of patients under each state over time
def plot_treatment_percentage(data, id_col, alphabet, states, clusters=None,title='Percentage of Patients under Each State Over Time'):
    """
    Plot the percentage of patients under each state over time using line plots.
    If clusters are provided, plot the treatment percentages for each cluster.

    Parameters:
    data (pd.DataFrame): The dataset containing treatment sequences.
    id_col (str): The column name for patient IDs.
    alphabet (list): List of unique treatment states.
    states (list): List of state labels corresponding to the alphabet.
    clusters (numpy.ndarray): Cluster assignments for each patient (optional).
    title (str): The title of the plot.

    Returns:
    None
    """
    viridis_colors_list = [plt.cm.viridis(i) for i in np.linspace(0, 1, len(alphabet))]

    if clusters is None:
        # Plot for the entire dataset
        df = data.drop(id_col, axis=1, errors='ignore').copy()
        plt.figure(figsize=(15, 8))
        
        for treatment, treatment_label, color in zip(alphabet, states, viridis_colors_list):
            treatment_data = df[df.eq(treatment).any(axis=1)]
            months = treatment_data.columns
            percentages = (treatment_data.apply(lambda x: x.value_counts().get(treatment, 0)) / len(treatment_data)) * 100
            percentages = percentages.fillna(0)
            plt.plot(months, percentages, label=f'{treatment_label}', color=color, marker='o')

        plt.xticks(months[::2], rotation=90, ha='right')
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Percentage of Patients')
        plt.legend(title=None)

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

    else:
        num_clusters = len(np.unique(clusters))
        num_rows = (num_clusters + 1) // 2  
        num_cols = min(2, num_clusters)
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 10))

        if num_clusters == 2:
            axs = np.array([axs])
        if num_clusters % 2 != 0:
            fig.delaxes(axs[-1, -1])

        for cluster_label in range(1,num_clusters+1):
            cluster_indices = np.where(clusters == cluster_label)[0]
            cluster_data = data.iloc[cluster_indices].drop(id_col, axis=1, errors='ignore')

            row = (cluster_label-1) // num_cols
            col = (cluster_label-1) % num_cols
            ax = axs[row, col]

            for treatment, treatment_label, color in zip(alphabet, states, viridis_colors_list):
                treatment_data = cluster_data[cluster_data.eq(treatment).any(axis=1)]
                months = treatment_data.columns
                percentages = (treatment_data.apply(lambda x: x.value_counts().get(treatment, 0)) / len(treatment_data)) * 100
                percentages = percentages.fillna(0)
                ax.plot(months, percentages, label=f'{treatment_label}', color=color, marker='o')

            #ax.set_xticks(months[::2])
            #ax.set_xticklabels(months[::2], rotation=90, ha='right')
            ax.set_title(f'Cluster {cluster_label}')
            ax.set_xlabel('Time')
            ax.set_ylabel('Percentage of Patients')
            ax.legend(title='State')
            ax.grid(True, linestyle='--', alpha=0.6)
            xticks_positions = range(0, len(months), 2)
            ax.set_xticks(xticks_positions)
            ax.set_xticklabels([months[i] for i in xticks_positions], rotation=45, ha='right')

        plt.tight_layout()
        plt.show()
        
# Function to plot the percentage of patients under each state over time using bar plots
def bar_treatment_percentage(data, id_col, alphabet, states, clusters=None,title='Bar Plot of Percentage of Patients under Each State Over Time'):
    """
    Plot the percentage of patients under each state over time using bar plots.
    If clusters are provided, plot the treatment percentages for each cluster.

    Parameters:
    data (pd.DataFrame): The dataset containing treatment sequences.
    id_col (str): The column name for patient IDs.
    alphabet (list): List of unique treatment states.
    states (list): List of state labels corresponding to the alphabet.
    clusters (numpy.ndarray): Cluster assignments for each patient (optional).
    title (str): The title of the plot.

    Returns:
    None
    """
    viridis_colors_list = [plt.cm.viridis(i) for i in np.linspace(0, 1, len(alphabet))]
    
    if clusters is None:
        df = data.drop(id_col, axis=1).copy()

        status_counts = df.apply(pd.Series.value_counts).fillna(0)
        #status_counts.T.plot.bar(stacked=True, color=[viridis_colors_list[i] for i in range(len(alphabet))], ax=ax)
        cumulative_values = np.zeros(len(df.columns))  # Initialisation des valeurs cumulées
        plt.figure(figsize=(15, 8))

        for treatment, treatment_label, color in zip(alphabet,states, viridis_colors_list):
            treatment_data = df[df.eq(treatment).any(axis=1)]
            months = treatment_data.columns
            percentages = (treatment_data.apply(lambda x: x.value_counts().get(treatment, 0)) / len(treatment_data)) * 100
            percentages = percentages.fillna(0)
            plt.bar(months, percentages, bottom=cumulative_values, label=f'{treatment_label}', color=color,)
            plt.xticks(months[::2], rotation=90)
            cumulative_values += percentages

     
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Number of Patients')
        plt.legend(title=None)
        plt.tight_layout()
        plt.show()

    else:
        num_clusters = len(np.unique(clusters))
        num_rows = (num_clusters + 1) // 2  
        num_cols = min(2, num_clusters)

        fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 10), squeeze=False)

        if num_clusters % 2 != 0:
            fig.delaxes(axs[-1, -1])
        for cluster_label in range(1,num_clusters+1):
            cluster_indices = np.where(clusters == cluster_label)[0]
            cluster_data = data.iloc[cluster_indices].drop(id_col, axis=1, errors='ignore')
            row = (cluster_label-1) // num_cols
            col = (cluster_label-1) % num_cols
            ax = axs[row, col]
            cumulative_values = np.zeros(len(cluster_data.columns)) 
            for treatment, treatment_label, color in zip(alphabet, states, viridis_colors_list):
                treatment_data = cluster_data[cluster_data.eq(treatment).any(axis=1)]
                months = treatment_data.columns
                percentages = (treatment_data.apply(lambda x: x.value_counts().get(treatment, 0)) / len(treatment_data)) * 100
                percentages = percentages.fillna(0)
                ax.bar(months, percentages, bottom=cumulative_values, label=f'{treatment_label}', color=color)
                cumulative_values += percentages 

            ax.set_title(f'Cluster {cluster_label}')
            ax.set_xlabel('Time')
            ax.set_ylabel('Percentage of Patients')
            ax.legend(title='State')
            xticks_positions = range(0, len(months), 2)
            ax.set_xticks(xticks_positions)
            ax.set_xticklabels([months[i] for i in xticks_positions], rotation=90)

        plt.tight_layout()
        plt.show()

def plot_discovered_phenotypes(reordered_phenotypes, rank, labels, colors=['#E81313', '#54C45E', '#1071E5'], title="Discovered phenotype"):
    """
    Plot the discovered phenotypes with a custom legend.

    Parameters:
    phenotypes (numpy.ndarray): The discovered phenotypes.
    colors (list): List of colors for each phenotype.
    states (list): List of state labels corresponding to the events.
    title (str): The title of the plot.

    Returns:
    None
    """
    for i in range(rank):
        if rank == 3 :
            # Create a colormap based on the base color
            base_color = colors[i % len(colors)]
            cmap = mcolors.LinearSegmentedColormap.from_list(f"custom_cmap_{i}", ["white", base_color])
        else:
            cmap = 'binary' 

        # Plot the phenotype matrix with the custom colormap
        plt.imshow(reordered_phenotypes[i].detach().numpy(), vmin=0, vmax=1, cmap=cmap, interpolation='none')
        plt.ylabel("Events")
        plt.xticks(range(reordered_phenotypes[i].shape[1]), range(reordered_phenotypes[i].shape[1]))
        plt.xlabel("Time")
        plt.title(f"{title} {i + 1}")
        plt.yticks(range(reordered_phenotypes[i].shape[0]), labels)
        plt.show()

def plot_input_matrix(tensor, id, labels, figsize=(12, 8), fontsize=12, title="Input Matrix of One Individual"):
    """
    Plot the input matrix of a tensor with patient IDs as labels.

    Parameters:
    tensor (torch.Tensor): The input tensor to be plotted.
    id (list): List of patient IDs corresponding to the rows of the tensor.
    figsize (tuple): Size of the figure for the plot.
    fontsize (int): Font size for the labels.
    title (str): The title of the plot.

    Returns:
    None
    """

    plt.figure(figsize=figsize)
    plt.imshow(tensor[id], vmin=0, vmax=1, cmap="binary", interpolation='none')
    plt.title(title, fontsize=fontsize)
    plt.xlabel("Time", fontsize=fontsize)
    plt.ylabel("Events", fontsize=fontsize)
    plt.xticks(np.arange(0, tensor[id].shape[1], 2))
    plt.yticks(range(tensor[id].shape[0]), labels, fontsize=fontsize-2)
    plt.tight_layout()  
    # fig, axs = plt.subplots(figsize=figsize)
    # axs.imshow(tensor[id], vmin=0, vmax=1, cmap="binary", interpolation='none')
    # axs.set_title("Input matrix of one individual", fontsize=fontsize) 
    # axs.set_xlabel("Time", fontsize=fontsize)
    # axs.set_ylabel("Events", fontsize=fontsize)
    # axs.set_xticks(np.arange(0, tensor[id].shape[1], 2)) 
    # axs.set_yticks(range(tensor[id].shape[0]))
    # axs.set_yticklabels(labels, fontsize=fontsize-2)
    # plt.tight_layout()
    plt.show()

def plot_discovered_pathways(reordered_pathways, id, figsize=(12, 8), fontsize=12,title="Discovered pathway of one individual"): 
    """
    """
    plt.figure(figsize=figsize) 
    plt.imshow(reordered_pathways[id].detach().numpy(), vmin=0, vmax=1, cmap="binary", interpolation="nearest")
    plt.ylabel("Phenotypes", fontsize=fontsize)
    plt.yticks(range(reordered_pathways[0].shape[0]), range(1, reordered_pathways[0].shape[0]+1), fontsize=fontsize-2)
    plt.xlabel("Time", fontsize=fontsize)
    plt.xticks(np.arange(0, reordered_pathways[id].shape[1], 2))
    plt.title(title, fontsize=fontsize)
    plt.show()   
    
def plot_reconstructed_matrix(reconstructed_matrix, id, labels, figsize=(12, 8), fontsize=12,title="Reconstructed matrix of one individual"):
    """
    Plot the reconstructed matrix of a tensor with patient IDs as labels.

    Parameters:
    reconstructed_matrix (torch.Tensor): The reconstructed matrix to be plotted.
    id (list): List of patient IDs corresponding to the rows of the tensor.
    labels (list): List of event labels corresponding to the rows of the tensor.
    figsize (tuple): Size of the figure for the plot.
    fontsize (int): Font size for the labels.
    title (str): The title of the plot.

    Returns:
    None
    """
    plt.figure(figsize=figsize)
    plt.imshow(reconstructed_matrix[id].detach().numpy(), vmin=0, vmax=1, cmap="binary", interpolation='none')
    plt.title(title, fontsize=fontsize)
    plt.xlabel("Time", fontsize=fontsize)
    plt.ylabel("Events", fontsize=fontsize)
    plt.xticks(np.arange(0, reconstructed_matrix[id].shape[1], 2))
    plt.yticks(range(reconstructed_matrix[id].shape[0]), labels, fontsize=fontsize-2)
    # fig, axs = plt.subplots(figsize=(16, 12))
    # axs.imshow(X_pred.detach().numpy(), vmin=0, vmax=1, cmap="binary", interpolation='none')
    # axs.set_title("Reconstructed matrix of one patient", fontsize=12) 
    # axs.set_xlabel("Time", fontsize=12)
    # axs.set_ylabel("Care Events", fontsize=12)
    # axs.set_xticks(np.arange(0, T, 2)) 
    # axs.set_yticks(range(X[id].shape[0]))
    # axs.set_yticklabels(label_encoder.inverse_transform(range(X[id].shape[0])), fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_filtered_heatmap(data, id_col, label_to_encoded, cmap, alphabet, states, labels=None, linkage_matrix=None, kernel_size=(10, 7),title=None):
    """
    Display a heatmap of numerical sequences, optionally filtered with a modal filter,
    and optionally reordered using K-Medoids or hierarchical clustering.

    Parameters:
    - data (pd.DataFrame): Original dataset with patient sequences.
    - id_col (str): Name of the patient ID column.
    - label_to_encoded (dict): Dictionary mapping labels to numerical codes.
    - cmap (str): Colormap to use for heatmap (e.g., "viridis").
    - alphabet (list): List of state letters (for legend).
    - states (list): List of full state names (for legend).
    - labels (np.ndarray, optional): Cluster labels from K-Medoids.
    - linkage_matrix (np.ndarray, optional): Linkage matrix from hierarchical clustering.
    - kernel_size (tuple): Size of modal filter kernel; (0,0) disables filtering.
    - title (str): The title of the plot.

    Returns:
    - None
    """
    df_numeriques = data.drop(id_col, axis=1).replace(label_to_encoded)

    if labels is not None:
        df_numeriques['cluster_kmedoids'] = labels
        df_reordered = df_numeriques.sort_values(by='cluster_kmedoids').drop(columns='cluster_kmedoids')
    elif linkage_matrix is not None:
        from scipy.cluster import hierarchy
        leaves_order = list(hierarchy.leaves_list(linkage_matrix))
        df_reordered = df_numeriques.iloc[leaves_order]
    else:
        raise ValueError("Either 'labels' or 'linkage_matrix' must be provided to reorder the data.")

    if kernel_size != (0, 0):
        df_to_plot = modal_filter_numba(df_reordered, kernel_size)
        if title is None:
            title = f"Heatmap of Numerical Sequences (modal filter, kernel={kernel_size})"
    else:
        df_to_plot = df_reordered.copy()
        if title is None:
            title = "Heatmap of Numerical Sequences"

    plt.figure(figsize=(15, 8))
    sns.heatmap(df_to_plot, cmap=cmap, cbar=False)
    plt.xlabel("Time")
    plt.ylabel("Patients")
    plt.xticks(rotation=90)
    plt.yticks([])
    plt.title(title)

    viridis_colors_list = [plt.cm.viridis(i) for i in np.linspace(0, 1, len(alphabet))]
    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=viridis_colors_list[i], label=alphabet[i]) for i in range(len(alphabet))]
    plt.legend(handles=legend_handles, labels=states, loc='upper right', ncol=1, title='Statuts')
    plt.tight_layout()
    plt.show()



