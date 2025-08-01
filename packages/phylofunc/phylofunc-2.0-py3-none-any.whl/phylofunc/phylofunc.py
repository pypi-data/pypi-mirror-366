# This code is PhyloFunc package to calculate PhyloFunc distance for human gut microbiome dataset
import pkgutil
import time
import pandas as pd
from Bio import Phylo
import io
import numpy as np


# Name internal nodes of phylogenetic tree
def assign_names(tree):
    node_count = 0
    for clade in tree.find_clades(order='postorder'):
        if not clade.name:
            node_count += 1
            clade.name = f"Node{node_count}"
    return tree, node_count


# Recursively collect leaf nodes and their data
def collect_leaf_nodes(clade, composition_table):
    if clade.is_terminal() or clade.name == "None":
        return pd.DataFrame()

    leaf_data = composition_table[composition_table['Taxon'].isin(
        [sub_clade.name for sub_clade in clade.get_terminals() if sub_clade.name != "None"]
    )].copy()

    if not leaf_data.empty:
        leaf_data.loc[:, 'Taxon'] = clade.name

    return leaf_data


# Recursively collect information about all branches of the tree
def collect_branches(clade, all_branches):
    if clade.is_terminal():
        return
    branches = generate_branches(clade)
    # Ensure that each entry in branches has exactly 4 elements
    all_branches.extend(branches)
    for child_clade in clade.clades:
        collect_branches(child_clade, all_branches)


# Process a phylogenetic tree clade to obtain information about its branches, including the predecessor, successor, and branch length.
def generate_branches(clade):
    branches = []
    for child in clade.clades:
        if child.branch_length is not None:
            branches.append([
                clade.name if clade.name else clade.clades[0].name,
                child.name if child.name else child.clades[0].name,
                child.count_terminals(),
                child.branch_length
            ])
    return branches


def validate_sample_data(sample_data):
    # Required columns: 'Taxon', 'Function', and at least two numeric columns for sample data
    required_columns = {'Taxon', 'Function'}
    if not required_columns.issubset(sample_data.columns):
        return False, f"Sample data error: Missing required columns {required_columns - set(sample_data.columns)}."
    if sample_data.shape[1] < 4:  # Ensuring there are data columns
        return False, "Sample data error: Insufficient columns. Expected additional columns for data values."
    for col in sample_data.columns[2:]:
        if not pd.api.types.is_numeric_dtype(sample_data[col]):
            return False, f"Sample data error: Expected numeric values in column '{col}'."
    return True, ""


def validate_mgyg_taxa(tree, sample_data):
    # Get the names of the leaf nodes in the tree that start with "MGYG"
    leaf_names = {clade.name for clade in tree.get_terminals() if clade.name and clade.name.startswith("MGYG")}
    # Find the "MGYG" taxa in the sample data
    sample_taxa = set(sample_data[sample_data['Taxon'].str.startswith("MGYG")]['Taxon'].unique())
    # Identify missing and extra taxa
    missing_taxa = sample_taxa - leaf_names
    found_taxa = sample_taxa & leaf_names
    # extra_taxa = leaf_names - sample_taxa

    # Drop rows from sample_data for missing "MGYG" taxa
    if missing_taxa:
        print(
            f"In the leaf nodes of the phylogenetic tree, {len(found_taxa)} taxa were successfully identified, "
            f"while {len(missing_taxa)} taxa could not be located. "
            f"The unfound taxa are as follows: {missing_taxa}. "
            f"Corresponding rows in the taxon-function table associated with these missing taxa were removed to calculate PhyloFunc distances.")
        sample_data = sample_data[
            ~sample_data['Taxon'].isin(missing_taxa)].copy()
    else:
        print("All 'MGYG' taxa in the sample data are present as leaf nodes in the tree.")
    return sample_data
    # Inform about any extra taxa in the tree not present in sample data
    # if extra_taxa:
    #     print(f"Note: Additional 'MGYG' taxa in the tree not present in sample data: {extra_taxa}")


# Perform a PhyloFunc distance for one pair of sample
def PhyloFunc_distance(tree_file=None, sample_file=None, sample_data=None):
    # Validate tree file format (must be .nwk)
    if tree_file and not tree_file.endswith('.nwk'):
        print("Error: The tree file should be a .nwk file.")
        return
    start_time = time.time()

    # Use cache to avoid reloading the tree and branches multiple times
    if not hasattr(PhyloFunc_distance, 'cache'):
        PhyloFunc_distance.cache = {}
    cache_key = tree_file if tree_file is not None else 'default_tree'
    if cache_key in PhyloFunc_distance.cache:
        precomputed = PhyloFunc_distance.cache[cache_key]
        tree, branch_df = precomputed['tree'], precomputed['branch_df']
    else:
        # Read phylogenetic tree; load default tree if no file provided
        if tree_file is None:
            tree_data = pkgutil.get_data(__name__, 'data/bac120_iqtree_v2.0.1.nwk')
            tree = Phylo.read(io.StringIO(tree_data.decode('utf-8')), "newick")
        else:
            tree = Phylo.read(tree_file, "newick")
        # Assign names to internal nodes and extract tree branch information
        tree, _ = assign_names(tree)
        if not tree.root.name:
            tree.root.name = "Root"
        all_branches = []
        collect_branches(tree.root, all_branches)
        branch_df = pd.DataFrame(all_branches,
                                 columns=["Precedent", "Consequent", "Number_of_child_nodes", "Length"]).dropna()

        PhyloFunc_distance.cache[cache_key] = {'tree': tree, 'branch_df': branch_df}

    # Load sample data (use default if no file provided)
    if sample_data is None:
        if sample_file is None:
            sample_data_bytes = pkgutil.get_data(__name__, 'data/Taxon_Function_distance.csv')
            sample_data = pd.read_csv(io.StringIO(sample_data_bytes.decode('utf-8')), sep=',')
        else:
            sample_data = pd.read_csv(sample_file, sep=',')


    is_valid, error_msg = validate_sample_data(sample_data)
    if not is_valid: print(error_msg); return

    # Validate and adjust MGYG taxa matching in the tree
    sample_data = validate_mgyg_taxa(tree, sample_data.copy())


    s1_name, s2_name = sample_data.columns[2], sample_data.columns[3]

    grouped_sum_tax = sample_data.groupby('Taxon')[[s1_name, s2_name]].sum()
    leaf_tax_comp = grouped_sum_tax.div(grouped_sum_tax.sum(), axis=1).fillna(0)

    grouped_func_tax = sample_data.groupby(['Taxon', 'Function'])[[s1_name, s2_name]].sum()
    leaf_func_comp = grouped_func_tax.div(grouped_func_tax.sum(), axis=1).fillna(0).reset_index()

    # Build dictionaries for functional and taxon composition
    func_compositions = {name: df for name, df in leaf_func_comp.groupby('Taxon')}
    tax_compositions = leaf_tax_comp.copy()

    # Traverse tree nodes to compute functional/taxon composition for internal nodes
    for clade in tree.find_clades(order='postorder'):
        if not clade.is_terminal():
            child_names = [child.name for child in clade.clades]

            # Merge functional composition from child nodes
            child_func_comps = [func_compositions[name] for name in child_names if name in func_compositions]
            if child_func_comps:
                parent_func_comp = pd.concat(child_func_comps).groupby('Function').sum().reset_index()
                parent_func_comp['Taxon'] = clade.name
                func_compositions[clade.name] = parent_func_comp

            parent_tax_comp = tax_compositions.loc[tax_compositions.index.isin(child_names)].sum()
            parent_tax_comp.name = clade.name
            tax_compositions = pd.concat([tax_compositions, parent_tax_comp.to_frame().T])

    # Combine functional composition for all nodes
    all_nodes_func_comp = pd.concat(func_compositions.values(), ignore_index=True)
    extend_taxon_composition_merge_all_nodes = tax_compositions.reset_index().rename(columns={'index': 'Taxon'})

    # Compute weighted functional composition percentage
    wfc_percentage = all_nodes_func_comp.groupby(['Taxon', 'Function'])[[s1_name, s2_name]].sum()
    total_by_Taxon = wfc_percentage.groupby('Taxon')[[s1_name, s2_name]].sum().replace(0, np.nan)
    wfc_percentage = wfc_percentage.div(total_by_Taxon, level=0).reset_index().fillna(0)

    # Calculate min/max for each function between the two samples
    min_vals = wfc_percentage[[s1_name, s2_name]].min(axis=1)
    max_vals = wfc_percentage[[s1_name, s2_name]].max(axis=1)
    min_sums = min_vals.groupby(wfc_percentage['Taxon']).sum()
    max_sums = max_vals.groupby(wfc_percentage['Taxon']).sum()


    # Compute functional difference (dist)
    with np.errstate(divide='ignore', invalid='ignore'):
        sample_pair_dists = (1 - min_sums / max_sums).fillna(0)
    sample_pair_dists.name = 'dist'


    abundances = extend_taxon_composition_merge_all_nodes.set_index('Taxon')
    weights = branch_df.set_index('Consequent')['Length']
    weights.name = 'weight'

    # Merge all data for final calculation
    final_df = pd.merge(sample_pair_dists, abundances, left_index=True, right_index=True)
    final_df = pd.merge(final_df, weights, left_index=True, right_index=True, how='left').fillna({'weight': 1.0})

    # Compute final PhyloFunc distance
    PhyloFunc = (final_df['dist'] * final_df['weight'] * final_df[s1_name] * final_df[s2_name]).sum()


    print(f'The optimized PhyloFunc distance between "{s1_name}" and "{s2_name}" is {PhyloFunc}.')
    print(f"Finish, time consumed: {time.time() - start_time:.2f} seconds")


# Calculate PhyloFunc distance matrix for all samples
def PhyloFunc_matrix(tree_file=None, sample_file=None, sample_data=None):

    start_time = time.time()

    # Use cache to avoid reloading tree structure repeatedly
    if not hasattr(PhyloFunc_matrix, 'cache'):
        PhyloFunc_matrix.cache = {}
    cache_key = tree_file if tree_file is not None else 'default_tree'

    if cache_key in PhyloFunc_matrix.cache:
        precomputed_data = PhyloFunc_matrix.cache[cache_key]
        tree, tree_with_names, node_count, branch_df, clades, taxon_weights = (
            precomputed_data['tree'], precomputed_data['tree_with_names'], precomputed_data['node_count'],
            precomputed_data['branch_df'], precomputed_data['clades'], precomputed_data['taxon_weights']
        )
    else:
        # Read phylogenetic tree (use default if no file provided)
        if tree_file is None:
            tree_data_bytes = pkgutil.get_data('phylofunc', 'data/bac120_iqtree_v2.0.1.nwk')
            tree = Phylo.read(io.StringIO(tree_data_bytes.decode('utf-8')), "newick")
        else:
            if not tree_file.endswith('.nwk'):
                raise ValueError("Error: The tree file should be a .nwk file.")
            tree = Phylo.read(tree_file, "newick")

        # Assign internal node names, extract branch info, and record weights
        tree_with_names, node_count = assign_names(tree)
        if not tree_with_names.root.name:
            tree_with_names.root.name = "Root"
        all_branches = []
        collect_branches(tree_with_names.root, all_branches)
        branch_df = pd.DataFrame(all_branches,
                                 columns=["Precedent", "Consequent", "Number_of_child_nodes", "Length"]).dropna()
        clades = [clade for clade in tree_with_names.find_clades() if not clade.is_terminal()]
        taxon_weights = branch_df.set_index('Consequent')['Length'].to_dict()
        if f'Node{node_count}' not in taxon_weights:
            taxon_weights[f'Node{node_count}'] = 1.0


        PhyloFunc_matrix.cache[cache_key] = {
            'tree': tree, 'tree_with_names': tree_with_names, 'node_count': node_count,
            'branch_df': branch_df, 'clades': clades, 'taxon_weights': taxon_weights
        }

    # Load sample data (use default if not provided)
    if sample_data is None:
        if sample_file is None:
            sample_data_bytes = pkgutil.get_data('phylofunc', 'data/Taxon_Function_matrix.csv')
            sample_data = pd.read_csv(io.StringIO(sample_data_bytes.decode('utf-8')), sep=',')
        else:
            sample_data = pd.read_csv(sample_file, sep=',')

    is_valid, error_msg = validate_sample_data(sample_data)
    if not is_valid: raise ValueError(error_msg)

    sample_data = validate_mgyg_taxa(tree, sample_data.copy())
    if sample_data.empty: return None

    Taxon_col_name, Function_col_name = 'Taxon', 'Function'
    Intensity_cols = sample_data.columns[2:]

    # Compute normalized abundance at Taxon level
    grouped_sum_tax = sample_data.groupby(Taxon_col_name)[Intensity_cols].sum()
    tax_composition = grouped_sum_tax.div(grouped_sum_tax.sum(), axis=1).reset_index()

    # Compute weighted composition at Taxon-Function level
    weighted_function_composition = sample_data.groupby([Taxon_col_name, Function_col_name])[Intensity_cols].sum()
    weighted_function_composition = weighted_function_composition.div(weighted_function_composition.sum(),
                                                                      axis=1).reset_index()

    all_weighted_function_data = [weighted_function_composition]
    all_taxon_composition_data = [tax_composition]

    # Traverse internal nodes to collect function and taxon data
    for clade in clades:
        clade_func_data = collect_leaf_nodes(clade, weighted_function_composition)
        if not clade_func_data.empty: all_weighted_function_data.append(
            clade_func_data.groupby('Function')[Intensity_cols].sum().reset_index().assign(Taxon=clade.name))
        clade_tax_data = collect_leaf_nodes(clade, tax_composition)
        if not clade_tax_data.empty: all_taxon_composition_data.append(
            clade_tax_data.groupby('Taxon')[Intensity_cols].sum().reset_index().assign(Taxon=clade.name))

    # Merge function and taxon data for all nodes
    weighted_function_composition_all = pd.concat(all_weighted_function_data, ignore_index=True)
    extend_taxon_composition_merge_all_nodes = pd.concat(all_taxon_composition_data, ignore_index=True)

    # Compute functional composition percentage
    wfc_percentage = weighted_function_composition_all.groupby([Taxon_col_name, Function_col_name])[
        Intensity_cols].sum()
    total_by_Taxon = wfc_percentage.groupby(Taxon_col_name)[Intensity_cols].sum().replace(0, np.nan)
    wfc_percentage = wfc_percentage.div(total_by_Taxon, level=0).reset_index().fillna(0)

    # Generate normalized functional matrix
    wfc_percentage_indexed = wfc_percentage.set_index([Taxon_col_name, Function_col_name])[Intensity_cols]
    group_sums = wfc_percentage_indexed.groupby(level='Taxon').transform('sum')
    normalized_function_profiles = wfc_percentage_indexed.div(group_sums).fillna(0)

    taxon_abundances = extend_taxon_composition_merge_all_nodes.set_index(Taxon_col_name)[Intensity_cols]

    sample_names = Intensity_cols.tolist()
    num_samples = len(sample_names)
    distance_matrix = pd.DataFrame(np.zeros((num_samples, num_samples)), index=sample_names, columns=sample_names)

    # Compute PhyloFunc distance for every sample pair
    for i in range(num_samples):
        for j in range(i + 1, num_samples):
            s1_col, s2_col = sample_names[i], sample_names[j]
            s1_profiles = normalized_function_profiles[s1_col]
            s2_profiles = normalized_function_profiles[s2_col]

            # Compute min and max for functional composition
            min_profiles = np.minimum(s1_profiles.values, s2_profiles.values)
            max_profiles = np.maximum(s1_profiles.values, s2_profiles.values)

            # Aggregate differences by taxon
            min_sums = pd.Series(min_profiles, index=s1_profiles.index).groupby(level='Taxon').sum()
            max_sums = pd.Series(max_profiles, index=s1_profiles.index).groupby(level='Taxon').sum()

            # Compute functional difference (dist)
            with np.errstate(divide='ignore', invalid='ignore'):
                sample_pair_dists = 1 - (min_sums / max_sums.replace(0, np.nan))
            sample_pair_dists = sample_pair_dists.fillna(0)

            common_taxa = sample_pair_dists.index.intersection(taxon_weights.keys()).intersection(
                taxon_abundances.index)

            current_phylofunc_distance = 0
            if not common_taxa.empty:
                # Compute final PhyloFunc distance
                dists = sample_pair_dists.loc[common_taxa].values
                weights_vals = np.array([taxon_weights[t] for t in common_taxa])
                abund1 = taxon_abundances.loc[common_taxa, s1_col].values
                abund2 = taxon_abundances.loc[common_taxa, s2_col].values
                current_phylofunc_distance = (dists * weights_vals * abund1 * abund2).sum()

            # Write distance into matrix
            distance_matrix.iloc[i, j] = distance_matrix.iloc[j, i] = current_phylofunc_distance

            print(f'The PhyloFunc distance between "{s1_col}" and "{s2_col}" is {current_phylofunc_distance}.')

    print(f"Finish, time consumed: {time.time() - start_time:.2f} seconds")
    return distance_matrix
