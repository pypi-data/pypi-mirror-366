import math
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import levene, sem, shapiro
from scipy import stats
from scipy.stats import friedmanchisquare
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.stattools import durbin_watson

from skbio import TreeNode
from skbio.diversity import alpha, beta_diversity
from skbio.stats import subsample_counts


def rarefaction(otus, seed = 23):
    
    # Define depth
    depth = otus.sum(axis=1).min()

    # Apply rarefaction
    rarefied_data = np.array([subsample_counts(row, depth, seed = seed) for row in otus.values])

    return rarefied_data


def alpha_diversity(otus, metrics, includes_ids = False, rarefy = True, seed = 23):

    # Check for errors in input:

    # Input data must have nonzero dimensions
    if otus.shape[0] == 0 or otus.shape[1] == 0:
        raise ValueError(f"otus must have nonzero dimensions")
    
    # Alpha diversity metrics input must include at least 1 value
    if metrics == []:
        raise ValueError("There must be at least one metric input")
    
    # List of OTU columns
    columns = otus.columns

    # If input data includes IDs for each row they are removed for calculations
    if includes_ids:
        ids = columns[0]
        ids_values = otus[ids]
        columns = columns[1:]
    
    # Select only OTU data columns
    otu_data = otus[columns]

    # Verify that all values are numeric
    numeric_values = otu_data.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all()

    # Only numeric values are valid
    if numeric_values == False:
        raise ValueError("Only numeric OTU read values are valid")
    
    # Rarefy otu observations if indicated
    if rarefy:
        otu_data = rarefaction(otu_data, seed)

    # Create a DF with each of the desired Alpha diversity metrics
    alpha_diversities = pd.DataFrame(columns=metrics)

    # List of metric supported
    valid_metrics = [
        'shannon',
        'sv-richness',
        'heip_e',
        'simpson'
    ]

    # Check if all desired metrics are valid
    for metric in metrics:
        if metric not in valid_metrics:
            raise ValueError(f"The metric {metric} recieved as an input is not valid")
    
    # For each metric, calculate the diversity using the respective funciton
    for metric in metrics:
        metric_values = []

        if metric == 'shannon':
            metric_values = [alpha.shannon(row) for row in otu_data]
        
        if metric == 'sv-richness':
            metric_values = [alpha.sobs(row) for row in otu_data]

        if metric == 'heip_e':
            metric_values = [alpha.heip_e(row) for row in otu_data]

        if metric == 'simpson':
            metric_values = [alpha.simpson(row) for row in otu_data]
        
        alpha_diversities[metric] = metric_values

    # If input data originally included IDs they are included in the return df
    if includes_ids:
        alpha_diversities['Sample_ID'] = ids_values
        complete_columns = ['Sample_ID'] + metrics
        alpha_diversities = alpha_diversities[complete_columns]

    return alpha_diversities


def beta_diversities(otus, metrics, tree_string, includes_ids = False, rarefy = True, seed = 23):

    #Check for errors in input:
    # Input data must have dimensions greater than 0
    if otus.shape[0] == 0 or otus.shape[1] == 0:
        raise ValueError(f"otus must have nonzero dimensions")
    
    # Beta diversity metrics input must include at least 1 value
    if metrics == []:
        raise ValueError("Select at least 1 metric")

    # List of columns
    columns = otus.columns

    # If input data includes IDs for each row they are removed for calculations
    if includes_ids:
        ids = columns[0]
        ids_values = otus[ids]
        columns = columns[1:]
    
    # Select only OTU data columns
    otu_data = otus[columns]

    # Verify that all values are numeric
    numeric_values = otu_data.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all()

    # Only numeric values are valid
    if numeric_values == False:
        raise ValueError("Only numeric OTU read values are valid")
    
    # Verify that tree string is not empty
    if tree_string == "" or tree_string == None:
        raise ValueError("pSTreeString is empty")
    
    # Rarefy OTU observations if the user desires
    if rarefy:
        otu_data = rarefaction(otu_data, seed)

    # Create the tree based on input data 
    input_tree = TreeNode.read([tree_string])

    # Create a DF with each of the desired Alpha diversity metrics
    beta_diversities = []

    # List of supported metrics
    valid_metrics = [
        'weighted_unifrac',
        'unweighted_unifrac'
    ]

    for metric in metrics:
        if metric not in valid_metrics:
            raise ValueError(f"The metric {metric} recieved as an input is not valid")
    
    # For each selected metric calculate the respective values
    for metric in metrics:
        print('Calculating',metric)
        if metric == 'weighted_unifrac': ##Scikit does NOT normalize wieghted by default (in literature they seem to do)
            unifrac_result = beta_diversity(metric, otu_data, taxa = columns, tree = input_tree, normalized = True)
        else:
            unifrac_result = beta_diversity(metric, otu_data, taxa = columns, tree = input_tree)

        unifrac_matrix = unifrac_result.data
        unifrac_vector = convert_matrix_vector(unifrac_matrix)
        beta_diversities.append(unifrac_vector)


    return beta_diversities


def convert_vector_beta_matrix(vector):

    # We must get the n of the matrix using the vectors length
    elements = len(vector)

    # Check vector dimensions
    if elements < 1:
        raise ValueError('The vector must have at least 1 element to convert it into a matrix')
    
    # Compute the number of observations there are
    discriminant = 1 + 8*elements
    discriminant_root = math.sqrt(discriminant)

    n = (1 + discriminant_root) // 2

    n = int(n)

    start = 0
    finish = n-2
    window = n-1

    # Fill the matrix using the vector's elements
    matrix = np.zeros((n,n))

    for i in range(n-1):
        row_act = vector[start:finish+1]
        matrix[i, i+1:] = row_act
        window = window - 1
        start = finish + 1
        finish = finish + window

    complete_matrix = matrix + matrix.T

    return complete_matrix


def convert_matrix_vector(matrix):

    # Get the number of observations
    n = matrix.shape[0]
    rows = []

    # Fill the vector with the upper triangle elements of the matrix
    for i in range(n):
        row_act = matrix[i]
        elements = row_act[i+1:]
        rows.append(elements)

    vector = np.concatenate(rows)
    return vector
    

def create_graphic(Y, X, graphic_type, save_file = False, file_name = ""):
    
    # ---- Input check ---
    if graphic_type not in [1,2,3]:
        raise ValueError('Graph type input not allowed')

    # Y must have more than 1 observation
    if Y.shape[0] == 0:
        raise ValueError('Y must have nonzero dimensions')

    # Create a [Y,X] df for creating the carts
    complete_data = pd.concat([Y, X], axis = 1)
    complete_variables = complete_data.columns
    
    # TYPE 1: Y vs numeric - Linegraph
    if graphic_type == 1:
        graph = sns.lmplot(
            data = complete_data,
            x = complete_variables[1],
            y = complete_variables[0],
            scatter_kws={'alpha': 0.3}, 
            height = 5
        )
        graph.set_axis_labels(complete_variables[1], complete_variables[0])
        
    # TYPE 2: Y vs 1 categoric - Violinplot
    if graphic_type == 2:
        graph = sns.violinplot(
                data = complete_data, 
                x = complete_variables[1], 
                y = complete_variables[0], 
                hue = complete_variables[1],
                inner = "quart",
                fill = False)
        graph.set(xlabel=complete_variables[1], ylabel=complete_variables[0])

    # TYPE 3: Y vs numeric with categories - Multiple linegraph
    if graphic_type == 3:
        if X.shape[0] == 0 or X.shape[1] == 0:
            raise TypeError('X must have nonzero dimensions')  
        graph = sns.lmplot(
                data = complete_data,
                x = complete_variables[1],
                y = complete_variables[0],
                hue = complete_variables[2],
                scatter_kws={'alpha': 0.3} 
        )
        graph.set_axis_labels(complete_variables[1], complete_variables[0])

    # Save file if needed
    if save_file:
        if file_name == "":
            raise ValueError("File is set to be saved, however there is no file name")
        complete_path = file_name + '.png'
        
        if graphic_type == 2:
            plt.savefig(complete_path, dpi=300)  # Extract figure from Axes
        else:
            graph.savefig(complete_path, dpi=300)


def anova_test(Y, data, X_columns, alpha = 0.05):
    
    # INPUT CHECKS

    # Y variable - Nonzero dimensions
    if Y.shape[0] == 0:
        raise ValueError("Objetive variable must have nonzero dimensions")

    # Convert objetive variable input into a DF
    objective_variable_df = pd.DataFrame(Y)
    objective_columns = objective_variable_df.columns

    # Objective variable - Only 1 variable
    if len(objective_columns) > 1:
        raise ValueError("Y must have only 1 column")

    
    # Data input - consistent dimensions
    if data.shape[0] == 0 or data.shape[1] == 0:
        raise ValueError("Dataset must have nonzero dimensions")
    
    # Desired analysis variables - At least 1 variable
    if len(X_columns) == []:
        raise ValueError("X_columns must be a non-empty array")
    
    # Variables in Explicative Variables input
    explicative_columns = data.columns

    
    # Desired variables must exist in input data
    for desired_variable in X_columns:
        if desired_variable not in explicative_columns:
            raise ValueError(f"Desired explicative variable {desired_variable} does not exist in data")

    # Select only the desired variables from the explicative variables input
    explicative_data = data[X_columns]    
        
    # Dimension consistency check
    if objective_variable_df.shape[0] != data.shape[0]:
        raise ValueError("Y and dataset must have the same number of observations")
    
    # Alpha value check
    if alpha < 0 or alpha >=1:
        raise ValueError('Alpha must be a positive decimal smaller than 1')
    
    
    # ACTUAL ANALYSIS

    # Input line for ANOVA
    formula = f"{objective_columns[0]} ~ " + " + ".join([f"C({variable})" for variable in X_columns])

    # Concat objective and explicative variables
    complete_data = pd.concat([objective_variable_df, explicative_data], axis= 1)
    
    # ANOVA
    model = ols(formula, data = complete_data).fit()
    anova_T = sm.stats.anova_lm(model, typ=1)

    # Format output similar to R
    anova_T['Mean Sq'] = anova_T['sum_sq'] / anova_T['df']
    anova_T = anova_T.rename(columns={'df': 'Df', 'sum_sq': 'Sum Sq', 'F': 'F value', 'PR(>F)': 'Pr(>F)'})
    anova_T = anova_T[['Df', 'Sum Sq', 'Mean Sq', 'F value', 'Pr(>F)']]

    # Print formatted output
    for col in ['Sum Sq', 'Mean Sq', 'F value']:
        anova_T[col] = anova_T[col].round(4)
    print("\nAnalysis of Variance Table\n")
    print(anova_T)

    print('\n')
    #Verify ANOVA Assumptions

    # 1. Homocedasticity - Levene's Test

    # We must create the group-specific tag for each observation
    print("Levene's Test for Homocedasticity. H0: There is no hetecedasticity")
    complete_data['Group_Tag'] = complete_data[X_columns].astype(str).agg('_'.join, axis = 1)


    # Now with each observation with a group tag, we compile each group
    groups = [complete_data[complete_data.columns[0]][  complete_data['Group_Tag'] == g] for g in complete_data['Group_Tag'].unique()]
    levene_stat, levene_p = levene(*groups)
    print('\tLevene statistic:',levene_stat)
    print('\tLevene statistic p-value:',levene_p)

    print('\n')

    # 2. Error Normality - Shapiro test
    print('Shapiro Test for Error Normality. H0: Population is distributed normally')
    shapiro_stat, shapiro_p = shapiro(model.resid)
    print('\tShapiro statistic:',shapiro_stat)
    print('\tShapiro statistic p-value:',shapiro_p)

    print('\n')

    # 3. Independence - Durbin-Watson Test
    print('Durbin-Watson Test for Independence. DW >= 2 indicates no autocorrelation')
    dw_stat = durbin_watson(model.resid)
    print("Durbin-Watson statistic:", dw_stat)

    # Output messages
    if levene_p > alpha and shapiro_p > alpha and dw_stat >= 2:
        print("\nThe ANOVA Model satisfies all assumptions")
    else:
        print("\nThe ANOVA Model does not satisfy all assumptions. Consider trying one of the following transformations:")
        print(" sqrt(y), ln(y), 1/y, 1/sqrt(y)")
        print("\n")

        # If there is only one explicative variable, non-parametric tests are suggested
        if len(X_columns) == 1:
            print("Alternatively, you could also try one of the non-parametric tests implemented in the package:")
            print("- Kruskall-Wallis H Test (kruskal_wallis_test): Groups can have different number of observations. It tests for same median between groups")
            print("- Friedmant Test (friedman_test): If all groups have the same number of observations. It tests for groups having the same distribution")


def taxonomy_df(taxonomic_data):

    # Check taxonomic_data dimensions
    if taxonomic_data.shape[1] < 1 or taxonomic_data.shape[0] < 1:
        raise ValueError('Input table must have non-zero dimensions')
    
    # Remove the final semicolon at the end of Taxonomy column
    taxonomic_data['Taxonomy'] = taxonomic_data['Taxonomy'].str.rstrip(";")

    # Split taxonomy using ";"
    taxonomy_split = taxonomic_data['Taxonomy'].str.split(";", expand = True)

    # Rename the columns using the according level name
    taxonomy_split.columns = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

    # Remove the __ in each value (if its not unclassified)
    taxonomy_split = taxonomy_split.apply(lambda col: col.map(lambda x: x[3:] if isinstance(x, str) and "__" in x else x))

    # Create the output df
    complete_matrix = pd.concat([taxonomic_data.drop(columns = ['Taxonomy']), taxonomy_split], axis = 1)

    return complete_matrix


def multi_level_factors(otus, otu_taxonomy, Y, Y_name, levels, classification = False, includes_ids = False, max_rows = 10, relative = True, seed = 23, save_file = False, file_name = ""):

    # Verify inputs
    if otus.shape[0] == 0 or otus.shape[1] == 0:
        raise ValueError("otus data must have non-zero dimensions")
    
    if otu_taxonomy.shape[0] == 0 or otu_taxonomy.shape[1] == 0:
        raise ValueError("otu_taxonomy data must have non-zero dimensions")
    
    if len(Y) == 0:
        raise ValueError('Y must have multiple values')

    if Y_name == "" or Y_name == None:
        raise ValueError("Y_name cannot be empty or None. It is needed for the figure's title")
    
    if len(Y) != otus.shape[0]:
        raise ValueError('Objective variable observations must have the same number of rows and otus data')
    
    if levels == []:
        raise ValueError('levels must have at least one value')

    if save_file and file_name == "":
        raise ValueError("If graph is to be saved, then it must have a file name")
    
    # Taxonomy classification columns
    taxonomy_columns = otu_taxonomy.columns

    # Check if selected levels are actual taxonomic levels
    for level in levels:
        if level not in taxonomy_columns:
            raise ValueError(f"{level} it not a column in otu_taxonomy")
        
    # Create a OTU data variable
    otu_data = otus

    # If ID column comes in the data, remove it
    if includes_ids:
        otu_data = otu_data.drop(columns = ['ID'])
    
    # If relative abundances are desired, transform the data into relative abundances
    if relative:
        #Total observations
        otu_data = relative_abundances(otu_data)

    # Create the grid of graphs
    grid_rows = math.ceil(len(levels)/2)
    fig, axes = plt.subplots(nrows=grid_rows, ncols=2, figsize=(12, 6 * grid_rows))
    axes = axes.flatten()

    # Create list of importance DFs for keepsake
    importances_df_list = []

    # Now for each desired level: create a df that groups OTU values by each value of the level
    for i, level in enumerate(levels):
        
        print("Estimating model for", level)

        # Using that level_df. Create a RF model vs the objective
        level_df = create_level_df(otu_data, otu_taxonomy, level)
        level_p = level_df.shape[1]
        if classification:
            rf_model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state = seed, max_features="sqrt")
        else:
            rf_model = RandomForestRegressor(n_estimators=100, max_depth=3, random_state = seed, max_features="sqrt")
        
        rf_model.fit(level_df, Y)
        importances = rf_model.feature_importances_
        importance_df = pd.DataFrame({
            "Feature": level_df.columns,
            "Importance": importances
        }).sort_values(by = "Importance", ascending=False)

        importance_df.columns = [level, "Importance"]
        importances_df_list.append(importance_df)
        min_shown = min(importance_df.shape[0], max_rows)

        graph_importances = importance_df.head(min_shown)
        ax = axes[i]
        ax.barh(graph_importances[level], graph_importances["Importance"], color="skyblue")
        ax.set_xlabel("Importance Score")
        ax.set_ylabel(level)
        ax.set_title(f"{level} Importance")
        ax.invert_yaxis()  # Invert y-axis to show highest importance at the top

    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])
    fig.suptitle(f"Taxonomic Level Importance for Predicting {Y_name}", fontsize=16, fontweight="bold", y = 1.005)
    plt.tight_layout()

    # Save image if needed
    if save_file:
        complete_path = file_name + ".png"
        plt.savefig(complete_path, dpi = 400, bbox_inches = "tight")
    plt.show()
    
    return importances_df_list


def create_level_df(otus, otu_taxonomy, level):

    # Get all unique values in the desired level
    level_names = otu_taxonomy[level].unique()

    # Data frame that will include the summed values
    level_df = pd.DataFrame(columns=level_names)

    # Dictionary that will have name in the level : list of otus
    name_otus_dict = {}

    # For each name in the level, get the list of OTUS
    for name in level_names:
        
        # Otu list
        selected_otus = otu_taxonomy[otu_taxonomy[level] == name]
        otu_list = selected_otus['OTU'].tolist()

        name_otus_dict[name] = otu_list

    # For each name in the level, get the summed valud of the OTUs and insert that result into the ouput df
    for name in level_names:
        filtered_otus = otus[name_otus_dict[name]]
        filtered_summs = filtered_otus.sum(axis = 1)
        level_df[name] = filtered_summs


    return level_df


def single_specific_level_factors(otus, otu_taxonomy, Y, Y_name, level, specific, classification = False, includes_ids = False, max_rows = 10, relative = True, seed = 23, save_file = False, file_name = ""):
    
    # Verify inputs
    if otus.shape[0] == 0 or otus.shape[1] == 0:
        raise ValueError("otus data must have non-zero dimensions")
    
    if otu_taxonomy.shape[0] == 0 or otu_taxonomy.shape[1] == 0:
        raise ValueError("otu_taxonomy data must have non-zero dimensions")
    
    if len(Y) == 0:
        raise ValueError('Y must have multiple values')

    if Y_name == "" or Y_name == None:
        raise ValueError("Y_name cannot be empty or None. It is needed for the figure's title")
    
    if len(Y) != otus.shape[0]:
        raise ValueError('Objective variable observations must have the same number of rows and otus data')
    
    if level == "":
        raise ValueError('level cannot be empty')
    
    if specific == "":
        raise ValueError("specific cannot be empty")

    if save_file and file_name == "":
        raise ValueError("If graph is to be saved, then it must have a file name")
    
    taxonomy_columns = otu_taxonomy.columns

    if level not in taxonomy_columns:
        raise ValueError("level does not exist in the taxonomy data frame columns")
    
    # Once checks are done. First step is to get the list of OTUs belonging to the specific taxon in the level
    filtered_taxonomy_df = otu_taxonomy[otu_taxonomy[level] == specific]
    filtered_otus = filtered_taxonomy_df['OTU'].tolist()

    if len(filtered_otus) == 0:
        raise ValueError('The specific value has no matches in the selected taxonomic level')
    
    # Now otu data can be filtered
    otu_data = otus

    if includes_ids:
        otu_data = otu_data.drop(columns = ['ID'])

    # Select relative abundances if desired
    if relative:
        #Total observations
        otu_data = relative_abundances(otu_data)
    
    # List of otus belonging to specific in level
    filtered_otu_data = otu_data[filtered_otus]

    #N ow we can do out respective model
    if classification:
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state = seed, max_features="sqrt")
    else:
        rf_model = RandomForestRegressor(n_estimators=100, max_depth=3, random_state = seed, max_features="sqrt")

    rf_model.fit(filtered_otu_data, Y)
    importances = rf_model.feature_importances_
    importance_df = pd.DataFrame({
            "Feature": filtered_otu_data.columns,
            "Importance": importances
        }).sort_values(by = "Importance", ascending=False)
    
    importance_df.columns = ['OTU', 'Importance']
    number_rows = min((importance_df.shape[0], max_rows))

    graph_importances = importance_df.head(number_rows)


    plt.figure(figsize=(9,5))
    plt.barh(graph_importances['OTU'], graph_importances['Importance'], color="skyblue")
    plt.xlabel("Importance")
    plt.ylabel("OTU")
    plt.title(f"{level} Taxon - {specific} OTU Importance for Predicting {Y_name}")
    plt.gca().invert_yaxis()

    if save_file:
        complete_path = file_name + '.png'
        plt.savefig(complete_path, dpi = 400, bbox_inches = "tight")

    plt.tight_layout()
    plt.show()


    return importance_df


def multiple_specific_level_factors(otus, otu_taxonomy, Y, Y_name, level, specifics, classification = False, includes_ids = False, max_rows = 10, relative = True, seed = 23, save_file = False, file_name = ""):
    
    # Verify inputs
    if otus.shape[0] == 0 or otus.shape[1] == 0:
        raise ValueError("otus data must have non-zero dimensions")
    
    if otu_taxonomy.shape[0] == 0 or otu_taxonomy.shape[1] == 0:
        raise ValueError("otu_taxonomy data must have non-zero dimensions")
    
    if len(Y) == 0:
        raise ValueError('Y must have multiple values')

    if Y_name == "" or Y_name == None:
        raise ValueError("Y_name cannot be empty or None. It is needed for the figure's title")
    
    if len(Y) != otus.shape[0]:
        raise ValueError('Objective variable observations must have the same number of rows and otus data')
    
    if level == "":
        raise ValueError('level cannot be empty')
    
    if specifics == []:
        raise ValueError("specifics cannot be empty")

    if save_file and file_name == "":
        raise TypeError("If graph is to be saved, then it must have a file name")
    
    taxonomy_columns = otu_taxonomy.columns

    if level not in taxonomy_columns:
        raise ValueError("level does not exist in the taxonomy data frame columns")
    
    # Once checks are done. First step is to get the list of OTUs belonging to the specific taxon in the level
    filtered_taxonomy_df = otu_taxonomy[otu_taxonomy[level].isin(specifics)]
    filtered_otus = filtered_taxonomy_df['OTU'].tolist()

    if len(filtered_otus) == 0:
        raise ValueError('The specifics value has no matches in the selected taxonomic level')
    

    # Now otu data can be filtered
    otu_data = otus

    if includes_ids:
        otu_data = otu_data.drop(columns = ['ID'])

    # Select relative abundances if desired
    if relative:
        otu_data = relative_abundances(otu_data)
    
    # List of otus belonging to pSpecific in level
    filtered_otu_data = otu_data[filtered_otus]

    # Now we can do out respective model
    if classification:
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state = seed, max_features="sqrt")
    else:
        rf_model = RandomForestRegressor(n_estimators=100, max_depth=3, random_state = seed, max_features="sqrt")

    rf_model.fit(filtered_otu_data, Y)
    importances = rf_model.feature_importances_
    importance_df = pd.DataFrame({
            "Feature": filtered_otu_data.columns,
            "Importance": importances
        }).sort_values(by = "Importance", ascending=False)
    
    importance_df.columns = ['OTU', 'Importance']
    number_rows = min((importance_df.shape[0], max_rows))

    graph_importances = importance_df.head(number_rows)


    plt.figure(figsize=(9,5))
    plt.barh(graph_importances['OTU'], graph_importances['Importance'], color="skyblue")
    plt.xlabel("Importance")
    plt.ylabel("OTU")
    plt.title(f"{level} Taxon - OTU Importance for Predicting {Y_name}")
    plt.gca().invert_yaxis()

    if save_file:
        complete_path = file_name + '.png'
        plt.savefig(complete_path, dpi = 400, bbox_inches = "tight")

    plt.tight_layout()
    plt.show()


    return importance_df


def friedman_test(Y, X, alpha = 0.05):
    
    # Check inputs
    if len(Y) != len(X):
        raise ValueError('Input vectors must be of the same size')
    
    if len(Y) < 1:
        raise ValueError('Objective variable must have at least 1 observation')
    

    if len(X) < 1: 
        raise ValueError('Explicative variable must have at least 1 observation')
    
    if alpha < 0:
        raise ValueError('alpha must be a non negative decimal')
    
    if alpha >= 1:
        raise ValueError('alpha must be a postive decimal smaller than 1')

    # Create a df for the information
    data = pd.DataFrame(columns=['X','Y'])
    data['X' ] = X
    data['Y'] = Y

    # Create the list of lists for each value of each class in X
    class_observations = []

    unique_classes = data['X'].unique()
    
    for unique_class in unique_classes:
        current_df = data[data['X'] == unique_class]
        class_observations.append(current_df[current_df['X']==unique_class]['Y'].to_list())

    # Check that all classes have the same number of observations
    current_number = len(class_observations[0])

    for unique_class in class_observations:
        if len(unique_class) != current_number:
            raise ValueError('All classes must have the same number of observations')

    # Create the friedman test
    friedman = friedmanchisquare(*class_observations)

    # Get the statistic
    te = round(float(friedman.statistic),4)

    # Get the p-value
    p_value = round(float(friedman.pvalue),4)

    # Print the output
    print(f"Friedman test result, using alpha = {alpha}")
    print('Null Hipothesis: All groups have the same distribution')
    print(f"  Friedman Statistic: {te}")
    print(f"  p-value: {p_value}")

    if p_value < alpha:
        print("The p-value is lower than alpha, therefore, the null hipothesis is rejected")
    else:
        print("The p-value is greater than alpha, therefore, the null hipothesis is accepted")


def kruskal_wallis_test(Y, X, alpha = 0.05):
    
    # Check inputs
    if len(Y) != len(X):
        raise ValueError('Input vectors must be of the same size')
    
    if len(Y) < 1:
        raise ValueError('Objective variable must have at least 1 observation')
    
    if len(X) < 1: 
        raise ValueError('Explicative variable must have at least 1 observation')
    
    if alpha < 0:
        raise ValueError('alpha must be a non negative decimal')
    
    if alpha >= 1:
        raise ValueError('alpha must be a postive decimal smaller than 1')

    # Create a df for the information
    data = pd.DataFrame(columns=['X','Y'])
    data['X' ] = X
    data['Y'] = Y

    # Create the list of lists for each value of each class in X
    class_observations = []

    unique_classes = data['X'].unique()
    
    for unique_class in unique_classes:
        current_df = data[data['X'] == unique_class]
        class_observations.append(current_df[current_df['X']==unique_class]['Y'].to_list())


    # Create the friedman test
    kruskal = stats.kruskal(*class_observations)

    # Get the statistic
    te = round(float(kruskal.statistic),4)

    # Get the p-value
    p_value = round(float(kruskal.pvalue),4)

    # Print the output
    print(f"Krukall-Wallis-H test result, using alpha = {alpha}")
    print('Null Hipothesis: The population median of all the groups are equal')
    print(f"  Kruskall-Wallis-H Statistic: {te}")
    print(f"  p-value: {p_value}")

    if p_value < alpha:
        print("The p-value is lower than alpha, therefore, the null hipothesis is rejected")
    else:
        print("The p-value is greater than alpha, therefore, the null hipothesis is accepted")


def tax_breakdown(otu_taxonomy, otu_list, max_depth = ""):
    
    # Input check
    if len(otu_list) < 1:
        raise ValueError('The Input of OTUs must have at least 1 element')
    
    otu_tax = otu_taxonomy[otu_taxonomy['OTU'].isin(otu_list)]

    # List of unique kingdoms
    kingdoms = otu_tax['Kingdom'].unique()

    # First level: kingdom
    for kingdom in kingdoms:
        kingdom_df = otu_tax[otu_tax['Kingdom'] == kingdom]
        print(f"-{kingdom}: {kingdom_df.shape[0]}")
        
        # Second level: Phylum
        phylums = kingdom_df['Phylum'].unique()

        for phylum in phylums:

            if max_depth == "Kingdom":
                break
            phylum_df = kingdom_df[kingdom_df['Phylum'] == phylum]
            print(f"\t-{phylum}: {phylum_df.shape[0]}")

            # Third level: Class
            classes_act = phylum_df['Class'].unique()

            for class_act in classes_act:

                if max_depth == "Phylum":
                    break
                class_df = phylum_df[phylum_df['Class'] == class_act]
                print(f"\t\t-{class_act}: {class_df.shape[0]}")


                # Fourth level: Order
                orders = class_df['Order'].unique()

                for order in orders:
                    if max_depth == "Class":
                        break
                    order_df = class_df[class_df['Order'] == order]
                    print(f"\t\t\t-{order}: {order_df.shape[0]}")


                    # Fifth level: Family
                    families = order_df['Family'].unique()

                    for family in families:
                        if max_depth == "Order":
                            break
                        family_df = order_df[order_df['Family'] == family]
                        print(f"\t\t\t\t-{family}: {family_df.shape[0]}")

                        # Sixth level: Genus
                        genuses = family_df['Genus'].unique()

                        for genus in genuses:
                            if max_depth == "Family":
                                break
                            genus_df = family_df[family_df['Genus'] == genus]
                            print(f"\t\t\t\t\t-{genus}: {genus_df.shape[0]}")

                            # Seventh level: Species
                            specieses = genus_df['Species'].unique()

                            for species in specieses:
                                if max_depth == "Genus":
                                    break
                                species_df = genus_df[genus_df['Species'] == species]
                                print(f"\t\t\t\t\t\t-{species}: {species_df.shape[0]}")


def relative_abundances(otus):
    
    total_otus = otus.sum(axis = 1)

    # In case there is an individual with 0 OTUS
    total_otus.replace(0, 1, inplace = True)

    otu_data = otus.div(total_otus, axis = 0)

    return otu_data


__all__ = [
    "rarefaction",
    "alpha_diversity",
    "beta_diversities",
    "convert_vector_beta_matrix",
    "convert_matrix_vector",
    "create_graphic",
    "anova_test",
    "taxonomy_df",
    "multi_level_factors",
    "single_specific_level_factors",
    "multiple_specific_level_factors",
    "friedman_test",
    "kruskal_wallis_test",
    "tax_breakdown",
    "relative_abundances",
    "create_level_df"
]