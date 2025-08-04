import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, message=".*FixedLocator.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*shapiro.*")
# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#####################################################################################

# Core imports
import os
import sys
import warnings

# Color and console utilities
class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Additional colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
def clear_console():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def colored_print(message, color=Colors.WHITE, bold=False):
    """Print colored message"""
    style = Colors.BOLD if bold else ""
    print(f"{style}{color}{message}{Colors.ENDC}")

def colored_input(prompt, color=Colors.CYAN, bold=True):
    """Get colored input from user"""
    style = Colors.BOLD if bold else ""
    return input(f"{style}{color}{prompt}{Colors.ENDC}")

def log_info(message):
    """Print info message in blue"""
    colored_print(f"INFO: {message}", Colors.OKBLUE)

def log_success(message):
    """Print success message in green"""
    colored_print(f"SUCCESS: {message}", Colors.OKGREEN)

def log_warning(message):
    """Print warning message in yellow"""
    colored_print(f"WARNING: {message}", Colors.WARNING)

def log_error(message):
    """Print error message in red"""
    colored_print(f"ERROR: {message}", Colors.FAIL)

def log_header(message):
    """Print header message in magenta"""
    colored_print(f"\n{'='*80}", Colors.MAGENTA, bold=True)
    colored_print(f"{message}", Colors.MAGENTA, bold=True)
    colored_print(f"{'='*80}\n", Colors.MAGENTA, bold=True)

def log_step(step_num, message):
    """Print step message in cyan"""
    colored_print(f"\n{message}", Colors.OKCYAN, bold=True)

def log_question(prompt):
    """Print question with proper spacing and color"""
    colored_print(f"\n", Colors.WHITE)  # Add space before question
    response = colored_input(f"  >>> {prompt}", Colors.YELLOW, bold=True)
    colored_print(f"", Colors.WHITE)  # Add space after question
    return response

def log_separator():
    """Print a separator line"""
    colored_print(f"{'-'*60}", Colors.CYAN)

# Data manipulation
import pandas as pd
import numpy as np
import itertools

# Statistical analysis
from scipy.stats import skew, chi2_contingency, pearsonr, spearmanr
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Data visualization
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

# Data preprocessing and validation
from sklearn.impute import SimpleImputer
from cerberus import Validator

# Hierarchical clustering
from scipy.cluster.hierarchy import linkage, leaves_list

# Tabular representation
from tabulate import tabulate
from tableone import TableOne

# Research and statistics
import researchpy as rp

# Utilities
import csv
from tqdm import tqdm
import subprocess
import textwrap
import importlib.util

#########################################################################################

def check_and_install_packages(packages):
    """
    Check if required packages are installed, and install them if they are missing.
    """
    import subprocess
    log_info("Checking required packages...")
    for package in packages:
        try:
            __import__(package)
            log_success(f"{package} is already installed")
        except ImportError:
            log_warning(f"{package} is not installed. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            log_success(f"{package} installed successfully")

########################################################################################

def data_info(data_copy, save_dir):
    """
    Displays and saves the DataFrame info in table format (pipe) to a text file.
    """
    os.makedirs(save_dir, exist_ok=True)
    info_buffer = []
    data_copy.info(buf=info_buffer.append)
    info_text = "\n".join(info_buffer)
    
    # Save to text file
    info_file_path = os.path.join(save_dir, "data_info.txt")
    with open(info_file_path, "w") as txt_file:
        txt_file.write(textwrap.indent(info_text, prefix="  ") + "\n")
    
    log_success(f"Data info saved in: {info_file_path}")
    
#---------------------------------------------------------------------------------------
def dataset_info_shap_datatypes_num_cat_count_duplecatedrows(df, save_dir):
    """
    Display and save customized dataset information including:
    - Shape: number of rows and columns
    - Range index: entries, min to max
    - Columns: total count of columns
    - Data types with counts of columns
    - Memory usage
    - Total duplicated rows
    - Missing values count and percentage
    - Count of numerical and categorical variables
    - Detailed list of duplicated rows (if any)
    """
    output_text = []
    missing_count = df.isnull().sum().sum()
    missing_percentage = (missing_count / df.size) * 100

    # Calculate the total number of duplicates
    duplicated_rows = df[df.duplicated(keep=False)]
    total_duplicates = duplicated_rows.shape[0]

    # Count numerical and categorical variables
    num_vars_count = df.select_dtypes(include=['number']).shape[1]
    cat_vars_count = df.select_dtypes(include=['object', 'category']).shape[1]

    # Print main title with color
    colored_print("\n DATASET INFORMATION \n", Colors.YELLOW, bold=True)

    
    # Prepare main info table
    info_data = {
        "Info": ["Total Shape", "Range Index", "Columns", "Memory Usage", "Total Duplicated Rows", "Missing Values Count", "Missing Values Percentage"],
        "Details": [
            f"{df.shape[0]} rows, {df.shape[1]} columns",
            f"{df.index.min()} to {df.index.max()}, {len(df)} entries",
            f"{df.shape[1]} columns",
            f"{df.memory_usage(deep=True).sum()} bytes",
            f"{total_duplicates} duplicates",
            f"{missing_count} missing values",
            f"{missing_percentage:.2f}% missing values"
        ]
    }
    info_table = pd.DataFrame(info_data)
    info_table_md = info_table.to_markdown(index=False, tablefmt="github")
    
    # Print main table
    colored_print(info_table_md, Colors.WHITE)
    
    # Save for file output
    output_text.append("\n=== Dataset Information ===\n")
    output_text.append(info_table_md)

    # Data types section
    colored_print("\n DATA TYPES WITH COUNTS OF COLUMNS \n", Colors.YELLOW, bold=True)

    
    data_types_count = df.dtypes.value_counts().reset_index()
    data_types_count.columns = ["Data Type", "Count of Columns"]
    data_types_md = data_types_count.to_markdown(index=False, tablefmt="github")
    
    # Print data types table
    colored_print(data_types_md, Colors.WHITE)
    
    # Save for file output
    output_text.append("\nData types with counts of columns:\n")
    output_text.append(data_types_md)

    # Variable counts section
    colored_print("\n NUMERICAL AND CATEGORICAL VARIABLE COUNTS \n", Colors.YELLOW, bold=True)
    
    var_counts_data = {
        "Variable Type": ["Numerical Variables", "Categorical Variables"],
        "Count": [num_vars_count, cat_vars_count]
    }
    var_counts_table = pd.DataFrame(var_counts_data)
    var_counts_md = var_counts_table.to_markdown(index=False, tablefmt="github")
    
    # Print variable counts table
    colored_print(var_counts_md, Colors.WHITE)
    
    # Save for file output
    output_text.append("\nNumerical and Categorical Variable Counts:\n")
    output_text.append(var_counts_md)

    # Duplicated rows section
    if not duplicated_rows.empty:
        colored_print("\n DETAILED LIST OF DUPLICATED ROWS \n", Colors.YELLOW, bold=True)
        
        duplicated_md = duplicated_rows.to_markdown(index=True, tablefmt="github")
        colored_print(duplicated_md, Colors.WHITE)
        
        # Save for file output
        output_text.append("\nDetailed list of duplicated rows (including indices):\n")
        output_text.append(duplicated_md)
    else:
        colored_print("\n NO DUPLICATED ROWS FOUND \n", Colors.OKGREEN, bold=True)
        
        # Save for file output
        output_text.append("\nNo duplicated rows found.\n")

    # Save to file
    output_file_path = os.path.join(save_dir, "dataset_info.txt")
    with open(output_file_path, 'w') as f:
        f.write("\n".join(output_text))

    log_success(f"Dataset information saved to: {output_file_path}")

########################################################################################

def save_and_remove_duplicates(df, save_dir):
    """
    Saves the duplicated rows to a CSV file and removes them from the DataFrame.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame.
    save_dir (str): The directory where the duplicated rows will be saved.

    Returns:
    pd.DataFrame: The DataFrame with duplicated rows removed.
    """
    # Identify duplicated rows
    duplicated_rows = df[df.duplicated(keep=False)]

    if not duplicated_rows.empty:
        # Save duplicated rows to a CSV file
        duplicates_file = os.path.join(save_dir, "duplicated_rows.csv")
        duplicated_rows.to_csv(duplicates_file, index=False)
        log_success(f"Duplicated rows saved to: {duplicates_file}")

        # Remove duplicated rows from the DataFrame
        df_cleaned = df.drop_duplicates(keep='first')
        log_success("Duplicated rows removed from the DataFrame.")
    else:
        log_info("No duplicated rows found.")
        df_cleaned = df.copy()

    return df_cleaned

#---------------------------------------------------------------------------------------
def analyze_missing_values(data_copy, save_dir):
    """
    Analyzes missing values in the given dataset by:
    1. Asking the user if they want to convert specific values to NaN.
    2. Saving total missing value percentage to a text file.
    3. Saving a statistical summary of missing values to a text file.
    4. Saving separate visualizations (matrix and bar plots).
    """
    # Create 'txt' folder inside the specified directory
    txt_dir = os.path.join(save_dir, "missing_values")
    os.makedirs(txt_dir, exist_ok=True)

    # Ask the user if they want to replace any specific values with NaN
    user_input = log_question("Do you want to convert any values to NaN? (y/n): ").strip().lower()
    
    if user_input == 'y':
        values_to_replace = log_question("Enter values to convert to NaN (comma-separated): ").strip().split(',')
        values_to_replace = [val.strip() for val in values_to_replace]
        data_copy.replace(values_to_replace, pd.NA, inplace=True)
        log_success(f"Converted values {values_to_replace} to NaN")

    # Calculate total missing value percentage
    missing_percentage = (data_copy.isnull().sum().sum() / data_copy.size) * 100
    missing_summary = f'Total Missing Percentage: {missing_percentage:.2f}%\n\n'

    # Get statistical summary of missing values
    missing_stats = data_copy.isna().sum().to_string()
    
    # Save missing values report to a text file
    report_file_path = os.path.join(txt_dir, "missing_values_report.txt")
    with open(report_file_path, "w") as file:
        file.write(missing_summary)
        file.write("Statistical Summary of Missing Values:\n")
        file.write(missing_stats)
    
    log_success(f"Missing values report saved at: {report_file_path}")

    # Optimize figure size based on the number of columns
    fig_width, fig_height = (50, 10) if data_copy.shape[1] > 100 else (20, 8)

    # Save missing data matrix plot separately
    plt.figure(figsize=(fig_width, fig_height))
    msno.matrix(data_copy, color=(0.27, 0.50, 0.70))
    plt.title('Missing Values Matrix', fontsize=16)
    matrix_plot_path = os.path.join(txt_dir, "missing_values_matrix.png")
    plt.savefig(matrix_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    log_success(f"Missing values matrix plot saved at: {matrix_plot_path}")

    # Save missing data bar plot separately
    plt.figure(figsize=(fig_width, fig_height))
    msno.bar(data_copy, color=sns.color_palette("Dark2", n_colors=data_copy.shape[1]))
    plt.title('Missing Values Bar Chart', fontsize=16)
    bar_plot_path = os.path.join(txt_dir, "missing_values_bar_chart.png")
    plt.savefig(bar_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    log_success(f"Missing values bar chart saved at: {bar_plot_path}")

    log_success("Missing values analysis completed successfully.")
#---------------------------------------------------------------------------------------
def auto_impute_missing_values(data_copy, save_dir):
    """
    Automatically imputes only the columns that contain missing values (NaN, None, pd.NA).
    
    Parameters:
    data_copy (pd.DataFrame): The DataFrame to modify in place.
    save_dir (str): The directory where the imputed data will be saved.

    Returns:
    pd.DataFrame: The DataFrame with missing values imputed.
    """

    #  Convert recognized missing values to NaN
    missing_values = ["", "NA", "NAN", "nan", None]
    data_copy.replace(missing_values, pd.NA, inplace=True)

    #  Ensure missing values are detected properly (Fixes 'boolean value of NA is ambiguous' issue)
    data_copy = data_copy.where(pd.notna(data_copy), other=None)

    #  Identify columns with missing values
    numeric_cols = [col for col in data_copy.select_dtypes(include=['number']).columns if data_copy[col].isnull().any()]
    categorical_cols = [col for col in data_copy.select_dtypes(include=['object', 'category']).columns if data_copy[col].isnull().any()]

    #  Apply imputations only for columns that have missing values
    if numeric_cols:
        num_imputer = SimpleImputer(strategy='mean')
        data_copy[numeric_cols] = num_imputer.fit_transform(data_copy[numeric_cols])
        log_success(f"Imputed {len(numeric_cols)} numerical columns with mean strategy")

    if categorical_cols:
        cat_imputer = SimpleImputer(strategy='most_frequent')
        data_copy[categorical_cols] = cat_imputer.fit_transform(data_copy[categorical_cols])
        log_success(f"Imputed {len(categorical_cols)} categorical columns with most frequent strategy")

    #  Save the imputed DataFrame
    imputed_file = os.path.join(save_dir, "imputed_data.csv")
    data_copy.to_csv(imputed_file, index=False)
    log_success(f"Imputed data saved to: {imputed_file}")

    return data_copy
    
########################################################################################

def detect_outliers(data, dtypes, save_dir):
    """
    Detects outliers in the specified data types using the IQR method and saves the summary.
    
    Parameters:
    data (pd.DataFrame): The input DataFrame to analyze.
    dtypes (list): List of data types to include in the outlier detection.
    save_dir (str): The directory where the outlier summary will be saved.

    Returns:
    pd.DataFrame: A DataFrame summarizing the outliers for each column, including the outlier count and percentage.
    """
    output_text = []

    data_copy = data.copy()
    outliers_summary = []

    for column in data_copy.select_dtypes(include=dtypes).columns:
        q1, q3 = data_copy[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers = data_copy[(data_copy[column] < (q1 - 1.5 * iqr)) | (data_copy[column] > (q3 + 1.5 * iqr))]
        outlier_count = len(outliers)
        outlier_percentage = (outlier_count / len(data_copy)) * 100
        outliers_summary.append([column, outlier_count, f"{outlier_percentage:.2f}%"])

    outliers_df = pd.DataFrame(outliers_summary, columns=['Column', 'Outlier Count', 'Percentage'])
    outliers_df.index.name = 'Index'  # Add index name for clarity

    output_text.append("\n Outliers Summary \n")
    output_text.append(outliers_df.to_markdown(index=True, tablefmt="github"))

    colored_print("\n".join(output_text), Colors.WHITE)

    output_file_path = os.path.join(save_dir, "outliers_summary.txt")
    with open(output_file_path, 'w') as f:
        f.write("\n".join(output_text))

    log_success(f"Outliers summary saved to: {output_file_path}")

    return outliers_df.reset_index()
    
#---------------------------------------------------------------------------------------
def detect_iqr_outliers_all(data_copy, save_dir, output_filename="iqr_outliers_report.csv"):
    """
    Detect outliers using the IQR method for all numerical columns in the dataset
    and save the results to a single CSV file inside an 'outliers' folder.
    """
    # Create the 'outliers' directory inside save_dir
    outliers_dir = os.path.join(save_dir, "outliers")
    os.makedirs(outliers_dir, exist_ok=True)
    output_path = os.path.join(outliers_dir, output_filename)

    # Extract numerical columns
    numerical_cols = data_copy.select_dtypes(include=['number']).columns.tolist()

    if not numerical_cols:
        log_warning("No numerical columns found in the dataset.")
        return

    results_list = []

    for column in numerical_cols:
        q1, q3 = data_copy[column].quantile([0.25, 0.75])  # Calculate Q1 and Q3
        iqr = q3 - q1  # Calculate IQR
        lower_bound = q1 - 1.5 * iqr  # Lower bound
        upper_bound = q3 + 1.5 * iqr  # Upper bound

        # Identify outliers
        outliers = data_copy[(data_copy[column] < lower_bound) | (data_copy[column] > upper_bound)][column]
        outlier_count = outliers.value_counts().to_dict()

        # Calculate distinct counts
        total_distinct_count = data_copy[column].nunique()
        outlier_distinct_count = outliers.nunique()

        # Get list of unique outliers
        outlier_list = ", ".join(map(str, outliers.unique()))

        # Store results
        results_list.append({
            'Column': column,
            'Q1': q1,
            'Q3': q3,
            'IQR_Range': iqr,
            'Lower_Bound': lower_bound,
            'Upper_Bound': upper_bound,
            'Total Distinct Count': total_distinct_count,
            'Outlier Distinct Count': outlier_distinct_count,
            'Outliers with val count': outlier_count,
            'Unique Outliers': outlier_list
        })

    # Convert the results to a DataFrame and save to CSV
    results_df = pd.DataFrame(results_list)
    results_df.to_csv(output_path, index=False)

    log_success(f"Outlier detection report saved successfully at: {output_path}")

#---------------------------------------------------------------------------------------
def numerical_features_boxplot_skew_kurto_outliers(data_copy, save_dir):
    """
    Analyzes numerical columns by generating box plots, calculating skewness, kurtosis,
    and detecting outliers, saving both visualizations and statistical summaries.
    """
    # Create 'outliers' folder inside the specified directory
    outliers_dir = os.path.join(save_dir, "outliers", "individual box plots")
    os.makedirs(outliers_dir, exist_ok=True)

    # Extract numerical columns
    numerical_cols = data_copy.select_dtypes(include=['number']).columns.tolist()

    if not numerical_cols:
        print("No numerical columns found in the dataset.")
        return

    # File to save the statistical report
    report_path = os.path.join(outliers_dir, "statistical_summary.txt")

    # Prepare summary table for outlier detection
    summary_data = []

    for column in numerical_cols:
        q1, q3 = data_copy[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = data_copy[(data_copy[column] < lower_bound) | (data_copy[column] > upper_bound)][column]

        summary_data.append([
            column, f"{q1:.2f}", f"{q3:.2f}", f"{iqr:.2f}",
            f"{lower_bound:.2f}", f"{upper_bound:.2f}",
            len(outliers), f"{(len(outliers) / len(data_copy)) * 100:.2f}%"
        ])

    # Convert summary data to DataFrame
    summary_df = pd.DataFrame(summary_data, columns=[
        "Column", "Q1", "Q3", "IQR", "Lower Bound", "Upper Bound", "Outliers Count", "Outliers Percentage"
    ])

    # Calculate skewness and kurtosis
    skewness = data_copy[numerical_cols].skew().reset_index()
    skewness.columns = ["Column", "Skewness"]
    
    kurtosis = data_copy[numerical_cols].kurt().reset_index()
    kurtosis.columns = ["Column", "Kurtosis"]

    # Merge skewness and kurtosis with summary statistics
    final_report = summary_df.merge(skewness, on="Column").merge(kurtosis, on="Column")

    # Save report to text file with structured table formatting
    with open(report_path, "w") as report_file:
        report_file.write("Outlier Detection Report\n")
        report_file.write("=" * 80 + "\n")
        report_file.write(tabulate(final_report, headers="keys", tablefmt="pipe"))
        report_file.write("\n\n")

    log_success(f"summary saved at: {report_path}")

    # Generate and save box plots in batches of 12 columns
    max_subplots_per_figure = 12
    figsize = (15, 15)  # Fixed figure size
    layout = (4, 4)     # Fixed layout

    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i:i + max_subplots_per_figure]

        # Generate box plots
        ax = data_copy[batch_cols].plot(
            kind="box",
            subplots=True,
            figsize=figsize,
            layout=layout,
            sharex=False,
            sharey=False,
            title=[f'Boxplot of {col}' for col in batch_cols]
        )

        plt.suptitle(f'Boxplots of Numerical Features (Batch {i // max_subplots_per_figure + 1})', fontsize=16, fontweight='bold')
        plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.95])

        # Save the figure
        plot_filename = os.path.join(outliers_dir, f'individual_box_plots_batch_{i // max_subplots_per_figure + 1}.png')
        plt.savefig(plot_filename, dpi=300)
        plt.close()

        log_success(f"Saved plot to: {plot_filename}")


########################################################################################

def data_table_range_min_max_distinct(data_copy, save_dir):
    """
    Prints a concise table with data type, range, distinct count, and index, organized by data type.
    Saves the results directly in save_dir.
    """
    result_lines = []
    result_lines.append("\n== Column Summary: ==\n")
    header = f"{'Index'.ljust(5)} {'Attribute'.ljust(30)} {'Data Type'.ljust(15)} {'Range'.ljust(30)} {'Distinct Count'}"
    separator = f"{'-'*5} {'-'*30} {'-'*15} {'-'*30} {'-'*15}"
    result_lines.append(header)
    result_lines.append(separator)
    
    index = 1
    for dtype in data_copy.dtypes.unique():
        dtype_columns = data_copy.select_dtypes(include=[dtype]).columns
        for col in dtype_columns:
            col_type = str(data_copy[col].dtype)
            distinct_count = data_copy[col].nunique()
            range_display = f"{data_copy[col].min()} - {data_copy[col].max()}" if col_type in ["int64", "float64"] else "N/A"
            result_lines.append(f"{str(index).ljust(5)} {col.ljust(30)} {col_type.ljust(15)} {range_display.ljust(30)} {distinct_count}")
            index += 1
    
    result_path = f"{save_dir}/column_summary.txt"
    with open(result_path, "w", encoding="utf-8") as f:
        f.write("\n".join(result_lines))
    
    log_success(f"Column summary saved to: {result_path}")
    
#---------------------------------------------------------------------------------------
def datatypes_wise_unique_mising(df, save_dir):
    """
    Generates a data overview table with columns for data type, column name, unique count,
    missing count, missing percentage, and missing value category, then saves it.
    """
    output_text = []

    missing_count = df.isnull().sum()
    missing_percentage = (missing_count / len(df)) * 100

    def categorize_missing_percentage(percentage):
        if percentage == 0:
            return "No Missing Values"
        elif 0 < percentage <= 5:
            return "Min (0-5%)"
        elif 5 < percentage <= 20:
            return "Moderate (5-20%)"
        elif 20 < percentage <= 50:
            return "High (20-50%)"
        else:
            return "Very High (50-100%)"

    missing_category = missing_percentage.apply(categorize_missing_percentage)

    output_text.append("\n Data Overview Table \n")
    for dtype, cols in df.dtypes.groupby(df.dtypes).groups.items():
        cols_list = list(cols)

        overview = pd.DataFrame({
            'Column Name': cols_list,
            'Data Type': [dtype] * len(cols),
            'Unique Count': df[cols_list].nunique().values,
            'Missing Count': missing_count[cols_list].values,
            'Missing Percentage': missing_percentage[cols_list].values,
            'Missing Value Category': missing_category[cols_list].values
        })

        output_text.append(f"\nOverview for Data Type: {dtype}\n")
        output_text.append(overview.to_markdown(index=True, tablefmt="github"))

    print("\n".join(output_text))

    output_file_path = os.path.join(save_dir, "data_overview.txt")
    with open(output_file_path, 'w') as f:
        f.write("\n".join(output_text))

    log_success(f"\nData overview table saved to: {output_file_path}")
    
#---------------------------------------------------------------------------------------
def researchpy_descriptive_stats(data_copy, save_dir):
    """
    Analyzes numerical and categorical columns in a dataset.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Numerical Analysis
    numerical_df = pd.concat(
        [rp.summary_cont(data_copy[col].dropna()).assign(Variable=col) for col in data_copy.select_dtypes(include=['float64', 'int64']).columns],
        ignore_index=True
    )
    numerical_output_path = os.path.join(save_dir, "numerical_analysis.csv")
    numerical_df.to_csv(numerical_output_path, index=False)

    # Categorical Analysis
    categorical_df = pd.concat(
        [rp.summary_cat(data_copy[col]).assign(Variable=col) for col in data_copy.select_dtypes(include=['object', 'category']).columns],
        ignore_index=True
    )
    categorical_output_path = os.path.join(save_dir, "categorical_analysis.csv")
    categorical_df.to_csv(categorical_output_path, index=False)

    print(f"Analysis complete. Results saved in: {save_dir}")

#---------------------------------------------------------------------------------------
def TableOne_groupby_column(data_copy, save_dir):
    """
    Analyzes numerical and categorical columns in a dataset using TableOne.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Automatically identify categorical and continuous columns
    categorical_columns = data_copy.select_dtypes(include=['object', 'category']).columns.tolist()
    continuous_columns = data_copy.select_dtypes(include=['number']).columns.tolist()
    all_columns = categorical_columns + continuous_columns
    
    # Ask the user for the type of report
    log_info("Choose report type:")
    colored_print("1: Single column report", Colors.YELLOW)
    colored_print("2: Multiple columns report", Colors.YELLOW)
    colored_print("3: All columns report", Colors.YELLOW)
    report_type = log_question("Enter your choice (1/2/3): ").strip()
    
    groupby_columns = []
    
    if report_type == "1":
        column_name = log_question(f"Enter a column name for grouping (available: {all_columns}): ").strip()
        if column_name in data_copy.columns:
            groupby_columns = [column_name]
        else:
            log_error(f"Column '{column_name}' not found. Exiting.")
            return
    
    elif report_type == "2":
        log_info(f"Available columns: {all_columns}")
        columns = log_question("Enter column names for grouping, separated by commas: ").strip().split(",")
        groupby_columns = [col.strip() for col in columns if col.strip() in data_copy.columns]
    
    elif report_type == "3":
        groupby_columns = all_columns
    
    else:
        log_error("Invalid choice. Exiting.")
        return
    
    log_separator()
    
    # Generate reports
    for groupby_column in groupby_columns:
        log_info(f"Generating report for grouping by: {groupby_column}")
        table = TableOne(data_copy,
                         columns=all_columns,
                         categorical=categorical_columns,
                         groupby=groupby_column,
                         pval=True,
                         isnull=True)
    
        # Save each grouping report as a CSV file
        csv_output_path = os.path.join(save_dir, f"summary_table_groupby_{groupby_column}.csv")
        table.to_csv(csv_output_path)
        log_success(f"Summary table for grouping by '{groupby_column}' saved as: {csv_output_path}")
    
    log_success("Reports generation completed.")
    
#---------------------------------------------------------------------------------------
def num_generate_summary_statistics_all(data, save_dir):
    """
    Generates a detailed summary statistics report for all numeric variables
    and displays them in a tabular format with the variable names as columns.
    The statistics' names are added as a separate column, and unique values count is included.
    """
    # Initialize an empty dictionary to store the summary statistics for each variable
    summary_stats_dict = {}

    # Loop through each numeric column in the dataset
    for variable in data.select_dtypes(include='number').columns:
        # Calculate the summary statistics
        summary_stats = {
            'Count': data[variable].count(),
            'Unique': data[variable].nunique(),
            'Mean': data[variable].mean(),
            'Std': data[variable].std(),
            'Min': data[variable].min(),
            '25%': data[variable].quantile(0.25),
            '50%': data[variable].median(),
            '75%': data[variable].quantile(0.75),
            'Max': data[variable].max(),
            'Mode': data[variable].mode()[0] if not data[variable].mode().empty else 'N/A',
            'Range': data[variable].max() - data[variable].min(),
            'IQR': data[variable].quantile(0.75) - data[variable].quantile(0.25),
            'Variance': data[variable].var(),
            'Skewness': data[variable].skew(),
            'Kurtosis': data[variable].kurt(),
            'Shapiro-Wilk Test Statistic': stats.shapiro(data[variable])[0],
            'Shapiro-Wilk Test p-value': stats.shapiro(data[variable])[1]
        }

        # Add the summary statistics to the dictionary with the variable name as the key
        summary_stats_dict[variable] = summary_stats

    # Convert the dictionary to a DataFrame
    summary_stats_df = pd.DataFrame(summary_stats_dict)

    # Reorder the rows as specified
    summary_stats_df = summary_stats_df.reindex([
        'Count', 'Unique', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max', 'Mode', 'Range',
        'IQR', 'Variance', 'Skewness', 'Kurtosis',
        'Shapiro-Wilk Test Statistic', 'Shapiro-Wilk Test p-value'
    ])

    # Insert the statistics names as the first column
    summary_stats_df.insert(0, 'Statistic', summary_stats_df.index)

    # Generate a bordered table using the 'github' format
    bordered_table = summary_stats_df.to_markdown(index=False, tablefmt="github")

    print("\nSummary Statistics for All Numeric Columns:\n")
    print(bordered_table)

    # Save the bordered table to a text file
    output_file_path = os.path.join(save_dir, "summary_statistics_all.txt")
    with open(output_file_path, 'w') as f:
        f.write("Summary Statistics for All Numeric Columns:\n\n")
        f.write(bordered_table)

    log_success(f"\nSummary statistics for all numeric columns saved to: {output_file_path}")

#---------------------------------------------------------------------------------------
def cat_generate_summary_statistics_all(df, save_dir):
    """
    Generates a detailed summary of categorical columns in the DataFrame and saves the results
    as a bordered table with variable names as columns.
    """
    # Initialize a dictionary to store the summary statistics for each variable
    summary_stats_dict = {
        'Statistic': [
            'Count', 
            'Unique', 
            'Top', 
            'Frequency', 
            'Top Percentage'
        ]
    }

    # Loop through each categorical column in the DataFrame
    for column in df.select_dtypes(include=['object']).columns:
        # Describe the column to get basic statistics
        desc = df[column].describe()

        # Add the summary statistics to the dictionary with the column name as the key
        summary_stats_dict[column] = [
            desc['count'],
            desc['unique'],
            desc['top'],
            desc['freq'],
            f"{(desc['freq'] / desc['count']) * 100:.2f}%"  # Percentage of top category
        ]

    # Convert the dictionary to a DataFrame
    categorical_stats_df = pd.DataFrame(summary_stats_dict)

    # Generate a bordered table using the 'github' format
    bordered_table = categorical_stats_df.to_markdown(index=False, tablefmt="github")

    print("\nCategorical Summary:\n")
    print(bordered_table)

    # Save the bordered table to a text file
    output_file_path = os.path.join(save_dir, "categorical_summary.txt")
    with open(output_file_path, 'w') as f:
        f.write("Categorical Summary:\n\n")
        f.write(bordered_table)

    log_success(f"\nCategorical summary saved to: {output_file_path}")

    
########################################################################################

def distinct_val_tabular_html_2000(data, output_file="distinct_values_count_by_dtype.html", display_limit=2000):
    """
    Displays the distinct value counts of all variables in a tabular format grouped by data type,
    ensuring that NaN values are shown as NaN, and saves it as an HTML file with a navigation pane
    that includes variable distinct counts. If a variable has more than `display_limit` distinct values,
    it will display only the top `display_limit` values but show the exact count in the title.
    """
    def generate_doc_map(grouped_columns, data):
        """
        Generates a document map (navigation pane) based on the grouped columns by data type,
        including the distinct values count for each variable.
        """
        doc_map_html = '<ul>'
        for dtype, variables in grouped_columns.items():
            doc_map_html += f"<li><strong>{dtype} ({len(variables)} variables)</strong><ul>"
            for variable in variables:
                distinct_count = data[variable].nunique(dropna=False)
                var_id = variable.replace(" ", "-")
                doc_map_html += f'<li><a href="#{var_id}">{variable} ({distinct_count})</a></li>'
            doc_map_html += "</ul></li>"
        doc_map_html += "</ul>"
        return doc_map_html

    def display_tabular_data_with_columns(variable, data, display_limit):
        """
        Displays the distinct value counts of a variable in a tabular format with an auto-calculated number of columns,
        ensuring that NaN values are shown as NaN and no empty columns are present. Displays only the top `display_limit`
        distinct values but shows the exact count in the title.
        """
        # Calculate value counts and prepare data for the table, including NaN values
        value_counts = data[variable].value_counts(dropna=False).sort_index()

        # Store the exact number of distinct values
        distinct_count = value_counts.shape[0]

        # Truncate the value counts if they exceed the display limit
        if len(value_counts) > display_limit:
            value_counts = value_counts.head(display_limit)

        # Ensure that NaN values are treated as NaN
        value_counts.index = value_counts.index.to_series().replace({pd.NA: 'NaN', float('nan'): 'NaN', None: 'NaN'})

        # Initialize the tabular data list
        tabular_data = []
        for value, count in value_counts.items():
            if pd.isna(value):
                value = 'NaN'
            else:
                # Format values to remove unnecessary decimal points
                value = f'{value:.6g}' if isinstance(value, float) else str(value)
            count = int(count)  # Ensure count is an integer to avoid decimals
            tabular_data.append([value, count])

        # Adjust the number of columns (Value_x, Count_x) to fit the data into a grid
        num_columns = 8  # For example, 8 pairs of Value and Count columns
        data_len = len(tabular_data)
        rows = (data_len + num_columns - 1) // num_columns

        # Create the rows for the tabular format
        formatted_table = []
        for i in range(rows):
            row = []
            for j in range(num_columns):
                idx = i + j * rows
                if idx < len(tabular_data):
                    row.extend(tabular_data[idx])
                else:
                    row.extend([None, None])  # Fill with NaN for empty cells
            formatted_table.append(row)

        # Convert the formatted table to a DataFrame
        col_names = []
        for i in range(len(formatted_table[0]) // 2):
            col_names.extend([f'Value_{i+1}', f'Count_{i+1}'])

        df = pd.DataFrame(formatted_table, columns=col_names)

        # Remove fully empty columns
        df = df.dropna(axis=1, how='all')

        # Replace any remaining None with 'NaN' for display
        df = df.fillna('NaN')

        # Convert count columns to integer type explicitly
        for col in df.columns:
            if 'Count' in col:
                df[col] = df[col].apply(lambda x: str(int(float(x))) if x != 'NaN' else x)

        # Return the final DataFrame in the desired format
        return df, distinct_count

    # Group columns by data type
    grouped_columns = data.columns.to_series().groupby(data.dtypes).groups

    # Generate the document map (navigation pane) HTML
    doc_map = generate_doc_map(grouped_columns, data)

    # Initialize a list to store HTML parts
    html_parts = []

    # Loop through each data type
    for dtype, variable_columns in grouped_columns.items():
        html_parts.append(f"<h1 id='{dtype}'>{dtype} ({len(variable_columns)} variables)</h1>\n")

        # Loop through each variable in the current dtype group
        for variable in variable_columns:
            var_id = variable.replace(" ", "-")
            # Create the tabular data for the current variable
            df, distinct_count = display_tabular_data_with_columns(variable, data, display_limit)

            # Add the title and DataFrame HTML to the html_parts list
            if distinct_count > display_limit:
                html_parts.append(f"<h2 id='{var_id}'>Distinct Values Counts for {variable}: {distinct_count} (Top {display_limit} displayed)</h2>\n")
            else:
                html_parts.append(f"<h2 id='{var_id}'>Distinct Values Counts for {variable}: {distinct_count}</h2>\n")
            
            html_parts.append(df.to_html(index=False, escape=False, border=0, justify='center', classes='data-table'))  # Align table center
            html_parts.append("<br><hr><br>")  # Add some space and a line break between variables

            # Add a page break after each large table
            if distinct_count > display_limit:
                html_parts.append('<div style="page-break-before: always;"></div>')

    # Combine all HTML parts into a single string
    full_html = "\n".join(html_parts)

    # Custom HTML template with navigation pane, light/dark mode, and without sticky headers
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #fdfdfd;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
                line-height: 1.6;
                color: #333;
                display: flex;
                height: 100vh;
                overflow: hidden;
                transition: background-color 0.3s, color 0.3s;
            }}
            body.dark-mode {{
                background-color: #2c2c2c;
                color: #d3d3d3;
            }}
            #doc-map {{
                width: 250px;
                height: 100vh;
                padding: 20px;
                background-color: #f0f0f0;
                color: #333;
                border-right: 1px solid #ccc;
                overflow-y: auto;
                flex-shrink: 0;
                position: relative;
                transition: width 0.2s, background-color 0.3s, color 0.3s;
            }}
            #doc-map.dark-mode {{
                background-color: #3b3b3b;
                color: #d3d3d3;
            }}
            #doc-map ul {{
                list-style-type: none;
                padding-left: 0;
                margin-left: 0;
            }}
            #doc-map ul ul {{
                margin-left: 20px;
            }}
            #doc-map li {{
                padding-left: 0;
            }}
            #doc-map a {{
                color: #007bff;
                text-decoration: none;
            }}
            #doc-map a.dark-mode {{
                color: #82cfff;
            }}
            #doc-map a:hover {{
                text-decoration: underline;
            }}
            #resizer {{
                width: 10px;
                cursor: ew-resize;
                background-color: #d1d5da;
                flex-shrink: 0;
            }}
            #content-wrapper {{
                flex-grow: 1;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}
            #content {{
                padding: 20px;
                background-color: #ffffff;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                height: 100vh;
                overflow-y: auto;
                word-wrap: break-word;
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                min-width: 0;
                position: relative;
                overflow-wrap: break-word;
                transition: background-color 0.3s, color 0.3s;
            }}
            #content.dark-mode {{
                background-color: #333333;
                color: #e4e6eb;
            }}
            table {{
                width: 100%;
                table-layout: fixed;
                border-collapse: collapse;
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
            th, td {{
                padding: 8px 12px;
                text-align: center;
                border: 1px solid #ddd;
                word-wrap: break-word;
                transition: background-color 0.3s, color 0.3s;
            }}
            th {{
                background-color: #e0e0e0;
                color: #333;
            }}
            td {{
                background-color: #ffffff;
            }}
            .data-table th {{
                background-color: #e0e0e0;
            }}
            .data-table td:nth-child(2n-1) {{
                background-color: #f0f8ff;  /* Light blue background for Value_ columns */
            }}
            .data-table td:nth-child(2n) {{
                background-color: #ffffff;  /* White background for Count_ columns */
            }}
            th.dark-mode {{
                background-color: #4a4a4a;
                color: #ffffff;
            }}
            .data-table td.dark-mode:nth-child(2n-1) {{
                background-color: #4a6072;  /* Darker blue background for Value_ columns in dark mode */
            }}
            .data-table td.dark-mode:nth-child(2n) {{
                background-color: #555555;  /* Darker background for Count_ columns in dark mode */
            }}
            pre, code {{
                background-color: #f6f8fa;
                padding: 16px;
                border-radius: 3px;
                overflow-x: auto;
                font-family: Consolas, "Courier New", monospace;
                font-size: 1em;
                word-wrap: break-word;
            }}
            pre.dark-mode, code.dark-mode {{
                background-color: #3a3b3c;
                color: #f5f6f7;
            }}
            .markdown-cell {{
                display: block;
                margin-bottom: 20px;
                word-wrap: break-word;
            }}
            .filename {{
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            #mode-toggle {{
                position: absolute;
                top: 10px;
                right: 20px;
                padding: 10px 20px;
                background-color: #444;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                z-index: 1000;
            }}
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function () {{
                var modeToggleButton = document.getElementById('mode-toggle');
                modeToggleButton.addEventListener('click', function() {{
                    document.body.classList.toggle('dark-mode');
                    document.getElementById('doc-map').classList.toggle('dark-mode');
                    document.getElementById('content').classList.toggle('dark-mode');
                    document.querySelectorAll('th, td').forEach(function(cell) {{
                        cell.classList.toggle('dark-mode');
                    }});
                    document.querySelectorAll('pre, code').forEach(function(cell) {{
                        cell.classList.toggle('dark-mode');
                    }});
                    document.querySelectorAll('#doc-map a').forEach(function(link) {{
                        link.classList.toggle('dark-mode');
                    }});
                }});

                // Enable resizing between ToC and content
                var resizer = document.getElementById('resizer');
                var leftPanel = document.getElementById('doc-map');
                var rightPanel = document.getElementById('content-wrapper');

                resizer.addEventListener('mousedown', function(e) {{
                    document.body.classList.add('resizing');
                    var startX = e.pageX;
                    var startWidth = leftPanel.offsetWidth;
                    var startRightWidth = rightPanel.offsetWidth;

                    function doDrag(e) {{
                        var newWidth = startWidth + (e.pageX - startX);
                        leftPanel.style.width = newWidth + 'px';
                        rightPanel.style.width = (startRightWidth - (e.pageX - startX)) + 'px';
                    }}

                    function stopDrag(e) {{
                        document.removeEventListener('mousemove', doDrag);
                        document.removeEventListener('mouseup', stopDrag);
                        document.body.classList.remove('resizing');
                    }}

                    document.addEventListener('mousemove', doDrag);
                    document.addEventListener('mouseup', stopDrag);
                }});
            }});
        </script>
    </head>
    <body>
        <div id="doc-map">
            {doc_map}
        </div>
        <div id="resizer"></div>
        <div id="content-wrapper">
            <div id="content">
                <button id="mode-toggle">Toggle Dark/Light Mode</button>
                {content}
            </div>
        </div>
    </body>
    </html>
    """

    # Insert the generated content into the custom HTML template
    html_content = html_template.format(content=full_html, doc_map=doc_map)

    # Write the full HTML to the output file
    with open(output_file, 'w') as file:
        file.write(html_content)

    print(f"Tabular data by data types has been saved to {output_file}")
    
########################################################################################

def analyze_relation(data_copy, save_dir):
    """
    Performs relationship analysis, including correlation, chi-square tests, and VIF calculation.
    It makes a temporary copy of `data_copy` and encodes categorical targets without modifying the original dataset.
    """
    os.makedirs(save_dir, exist_ok=True)
    results_dir = os.path.join(save_dir, "relation_analysis")
    os.makedirs(results_dir, exist_ok=True)

    warnings.filterwarnings("ignore")

    #  Step 1: Ask for target variable
    def process_target():
        target_available = log_question("Is there a target variable? (y/n): ").lower()
        
        if target_available == 'y':
            target_var = log_question("Enter the target variable name: ").strip()
            if target_var in data_copy.columns:
                return target_var
            else:
                log_warning(f"Target variable '{target_var}' not found in the dataset. Skipping target-based analysis.")
                return None
        return None

    #  Step 2: Generate Clustered Correlation Heatmap
    def generate_clustered_correlation_heatmap():
        log_info("Generating clustered correlation heatmap...")
        correlation_matrix = data_copy.select_dtypes(include=['int64', 'float64']).corr()
        linkage_matrix = linkage(1 - correlation_matrix, method="average")
        clustered_order = leaves_list(linkage_matrix)
        clustered_corr = correlation_matrix.iloc[clustered_order, clustered_order]

        plt.figure(figsize=(12, 10))
        sns.heatmap(clustered_corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        plt.title("Clustered Correlation Heatmap of Numerical Features", fontsize=16, pad=20)
        heatmap_path = os.path.join(results_dir, "clustered_heatmap.png")
        plt.savefig(heatmap_path)
        plt.close()
        log_success(f"Heatmap saved at {heatmap_path}")

    #  Step 3: Get Target Variable
    target_var = process_target()

    # If no target variable, generate heatmap and exit
    if target_var is None:
        generate_clustered_correlation_heatmap()
        return

    log_separator()

    #  Step 4: Create a Temporary Copy for Encoding (Original Data Unchanged)
    temp_data = data_copy.copy()
    target_series = temp_data[target_var].copy()

    #  Step 5: Encode Target Variable if Categorical
    if target_series.dtype == 'object' or target_series.dtype.name == 'category':
        unique_values = target_series.unique()

        #  If binary (e.g., "yes"/"no"), map to 0 and 1
        if len(unique_values) == 2:
            mapping = {unique_values[0]: 0, unique_values[1]: 1}
            temp_data[target_var] = target_series.map(mapping)
            log_success(f"Converted categorical target '{target_var}' using mapping: {mapping}")
        else:
            log_warning(f"Target variable '{target_var}' has more than two categories. Skipping correlation analysis.")
            generate_clustered_correlation_heatmap()
            return

    #  Step 6: Chi-Square Test for Categorical Variables
    log_info("Performing chi-square test for categorical variables...")
    cat_vars = temp_data.select_dtypes(include=['object', 'category']).columns
    chi_square_results = []
    for col in tqdm(cat_vars, desc="Chi-Square Tests"):
        contingency_table = pd.crosstab(temp_data[col], temp_data[target_var])
        p_value = round(chi2_contingency(contingency_table)[1], 2)
        chi_square_results.append({'Categorical Variable': col, 'p-value': p_value})
    categorical_table = pd.DataFrame(chi_square_results)

    #  Step 7: Correlation Analysis for Numerical Variables
    log_info("Performing correlation analysis for numerical variables...")
    num_vars = temp_data.select_dtypes(include=['int64', 'float64']).columns
    correlation_results = []
    for col in tqdm(num_vars, desc="Correlation Analysis"):
        if col != target_var:
            pearson_corr = round(pearsonr(temp_data[col], temp_data[target_var])[0], 2)
            spearman_corr = round(spearmanr(temp_data[col], temp_data[target_var])[0], 2)
            correlation_results.append({'Numerical Variable': col, 'Pearson': pearson_corr, 'Spearman': spearman_corr})
    numerical_table = pd.DataFrame(correlation_results)

    #  Step 8: Variance Inflation Factor (VIF)
    log_info("Calculating Variance Inflation Factor (VIF)...")
    vif_data = temp_data.select_dtypes(include=['int64', 'float64']).dropna()
    vif_table = pd.DataFrame()
    vif_table['Variable'] = vif_data.columns
    vif_table['VIF'] = [round(variance_inflation_factor(vif_data.values, i), 2) for i in range(vif_data.shape[1])]

    #  Step 9: Save Results
    categorical_table.to_csv(os.path.join(results_dir, "categorical_analysis.csv"), index=False)
    numerical_table.to_csv(os.path.join(results_dir, "numerical_analysis.csv"), index=False)
    vif_table.to_csv(os.path.join(results_dir, "vif_analysis.csv"), index=False)

    txt_path = os.path.join(results_dir, "analysis_results.txt")
    with open(txt_path, 'w') as txt_file:
        txt_file.write("Chi-Square Analysis for Categorical Variables:\n")
        txt_file.write(textwrap.indent(categorical_table.to_markdown(tablefmt="pipe", index=False), prefix="  ") + "\n\n")

        txt_file.write("Correlation Analysis for Numerical Variables:\n")
        txt_file.write(textwrap.indent(numerical_table.to_markdown(tablefmt="pipe", index=False), prefix="  ") + "\n\n")

        txt_file.write("Variance Inflation Factor (VIF):\n")
        txt_file.write(textwrap.indent(vif_table.to_markdown(tablefmt="pipe", index=False), prefix="  ") + "\n")

    log_success(f"Results saved in CSV and TXT format at {results_dir}")


    
########################################################################################
################################## visualization #######################################
########################################################################################

def calculate_statistics(data):
    """
    Calculates various statistics for a numerical dataset.
    """
    stats = {
        'Count': data.count(),
        'Mean': data.mean(),
        'Trimmed Mean (IQR)': iqr_trimmed_mean(data),
        'MAD': mad(data),
        'Std': data.std(),
        'Min': data.min(),
        '25%': data.quantile(0.25),
        '50%': data.median(),
        '75%': data.quantile(0.75),
        'Max': data.max(),
        'Mode': data.mode()[0] if not data.mode().empty else 'N/A',
        'Range': data.max() - data.min(),
        'IQR': data.quantile(0.75) - data.quantile(0.25),
        'Variance': data.var(),
        'Skewness': data.skew(),
        'Kurtosis': data.kurt()
    }
    return stats

def iqr_trimmed_mean(data):
    """
    Calculates the trimmed mean using the IQR method.
    """
    q1, q3 = np.percentile(data.dropna(), [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    trimmed_data = data[(data >= lower_bound) & (data <= upper_bound)]
    return trimmed_data.mean()

def mad(data):
    """
    Computes the Mean Absolute Deviation (MAD).
    """
    return np.mean(np.abs(data - data.mean()))

def num_var_analysis(data, attribute, target=None):
    """
    Analyzes a numerical variable and generates summary statistics.
    If a target is provided, computes grouped statistics as well.
    """
    var_summary = calculate_statistics(data[attribute])
    
    if target:
        grouped_summary = {
            group: calculate_statistics(group_data)
            for group, group_data in data.groupby(target)[attribute]
        }
        summary_table = pd.DataFrame(var_summary, index=['Overall']).T
        for group, stats in grouped_summary.items():
            group_df = pd.DataFrame(stats, index=[f"{target}: {group}"]).T
            summary_table = summary_table.join(group_df)
    else:
        summary_table = pd.DataFrame(var_summary, index=['Overall']).T

    summary_table.index.name = 'Statistic'
    return summary_table

def plot_summary_num_hist_box_optional_target(data, save_dir):
    """
    Automates numerical variable analysis and visualization, saving results in a single folder.
    """
    vis_dir = os.path.join(save_dir, "visualization", "plot_summary_num_hist_box_optional_target")
    os.makedirs(vis_dir, exist_ok=True)
    
    numerical_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if not numerical_cols:
        print("No numerical columns found in the dataset.")
        return
 
    target_input = log_question("Do you want to analyze variables with a target variable? (y/n): ").strip().lower()
    target = None
    if target_input == 'y':
        target = log_question("Enter the target variable name: ").strip()
        if target not in data.columns:
            print(f"Target variable '{target}' not found in the dataset. Proceeding without target variable.")
            target = None
    
    report_file_path = os.path.join(vis_dir, "numerical_analysis_summary.txt")
    
    with open(report_file_path, "w") as report_file:
        report_file.write("Numerical Variable Analysis Report\n")
        report_file.write("=" * 120 + "\n\n")
        
        for variable in tqdm(numerical_cols, desc="Processing Numerical Variables", unit="variable"):
            analysis_result = num_var_analysis(data, variable, target)
            
            report_file.write(f"\n### Analysis for '{variable}' {'by ' + target if target else ''} ###\n")
            report_file.write(analysis_result.to_markdown(tablefmt="github"))
            report_file.write("\n\n")
            
            individual_file_path = os.path.join(vis_dir, f"{variable}_analysis.txt")
            with open(individual_file_path, "w") as individual_file:
                individual_file.write(f"Analysis for '{variable}' {'by ' + target if target else ''}\n")
                individual_file.write("=" * 80 + "\n")
                individual_file.write(analysis_result.to_markdown(tablefmt="github"))
            
            if target:
                fig, axes = plt.subplots(1, 2, figsize=(18, 6))
                sns.histplot(data, x=variable, hue=target, bins=30, palette='Set1', kde=True, ax=axes[0])
                axes[0].set_title(f'Histogram of {variable} by {target} with KDE')
                sns.boxplot(x=target, y=variable, data=data, hue=target, palette='Set2', legend=False, ax=axes[1])
                axes[1].set_title(f'Box Plot of {variable} by {target}')
                plt.tight_layout()
                plot_filename = os.path.join(vis_dir, f'{variable}_by_{target}.png')
            else:
                plt.figure(figsize=(9, 6))
                sns.histplot(data[variable], bins=30, kde=True, color='skyblue', edgecolor='black', alpha=0.7)
                plt.title(f'Histogram of {variable} with KDE')
                plt.xlabel(variable)
                plt.ylabel('Frequency')
                plot_filename = os.path.join(vis_dir, f'{variable}_histogram.png')
            plt.savefig(plot_filename, dpi=300)
            plt.close()

    
#---------------------------------------------------------------------------------------
def plot_num_kde_subplot(data_copy, save_dir, layout_title="KDE Plots of Numerical Variables"):
    """
    Generate and save KDE plots for all numerical variables in a dataset in batches of 12 subplots.
    """
    # Create 'plot_num_kde_subplot' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_num_kde_subplot")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract numerical columns
    numerical_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()

    if not numerical_cols:
        print("No numerical columns found in the dataset.")
        return

    # Set subplot limits
    max_subplots_per_figure = 12

    # Process columns in batches of max_subplots_per_figure
    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i:i + max_subplots_per_figure]
        rows = (len(batch_cols) + 2) // 3
        cols = min(3, len(batch_cols))

        plt.figure(figsize=(cols * 7, rows * 5))

        for j, col in enumerate(batch_cols):
            plt.subplot(rows, cols, j + 1)
            sns.histplot(data_copy[col], bins=20, kde=True, color='skyblue', edgecolor='black', alpha=0.7)

            # Add statistical markers
            stats = {
                'Mean': (data_copy[col].mean(), 'darkred'),
                'Median': (data_copy[col].median(), 'darkgreen'),
                'Mode': (data_copy[col].mode()[0] if not data_copy[col].mode().empty else np.nan, 'darkblue'),
                'Min': (data_copy[col].min(), 'darkmagenta'),
                '25%': (data_copy[col].quantile(0.25), 'darkorange'),
                '75%': (data_copy[col].quantile(0.75), 'darkcyan'),
                'Max': (data_copy[col].max(), 'darkviolet')
            }

            for stat, (value, color) in stats.items():
                plt.axvline(value, color=color, linestyle='--', linewidth=2, label=f'{stat}: {value:.2f}')

            # Plot formatting
            plt.title(f'Distribution and KDE of {col}', fontsize=14)
            plt.xlabel(col, fontsize=12)
            plt.ylabel('Density', fontsize=12)
            plt.legend(loc='upper right', fontsize=10, frameon=False)
            plt.grid(False)

        # Set title for the figure
        plt.suptitle(f'{layout_title} (Batch {i // max_subplots_per_figure + 1})', fontsize=16, fontweight='bold')
        plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.95])

        # Save the figure inside 'plot_num_kde_subplot' folder
        plot_filename = os.path.join(vis_dir, f'kde_plots_batch_{i // max_subplots_per_figure + 1}.png')
        plt.savefig(plot_filename, dpi=300)
        plt.close()

        log_success(f"Saved plot to: {plot_filename}")
    
#---------------------------------------------------------------------------------------
def plot_num_box_plots_all(data_copy, save_dir, layout_title="Box Plots of Numerical Variables"):
    """
    Generate and save box plots for all numerical variables in a dataset in batches of 12 subplots.
    """
    # Create 'plot_num_box_plots_all' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_num_box_plots_all")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract numerical columns
    numerical_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()

    if not numerical_cols:
        print("No numerical columns found in the dataset.")
        return

    # Set subplot limits
    max_subplots_per_figure = 12

    # Process columns in batches of max_subplots_per_figure
    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i:i + max_subplots_per_figure]
        rows = (len(batch_cols) + 2) // 3
        cols = min(3, len(batch_cols))

        plt.figure(figsize=(cols * 7, rows * 5))

        for j, col in enumerate(batch_cols):
            plt.subplot(rows, cols, j + 1)
            sns.boxplot(x=data_copy[col], color='skyblue', fliersize=5, linewidth=2)

            # Add statistical markers
            stats = {
                'Mean': (data_copy[col].mean(), 'darkred'),
                'Median': (data_copy[col].median(), 'darkgreen'),
                'Min': (data_copy[col].min(), 'darkblue'),
                '25%': (data_copy[col].quantile(0.25), 'darkorange'),
                '75%': (data_copy[col].quantile(0.75), 'darkcyan'),
                'Max': (data_copy[col].max(), 'darkviolet')
            }

            for stat, (value, color) in stats.items():
                plt.axvline(value, color=color, linestyle='--', linewidth=2, label=f'{stat}: {value:.2f}')

            # Plot formatting
            plt.title(f'Box Plot of {col}', fontsize=14)
            plt.xlabel(col, fontsize=12)
            plt.legend(loc='upper right', fontsize=10, frameon=False)
            plt.grid(False)

        # Set title for the figure
        plt.suptitle(f'{layout_title} (Batch {i // max_subplots_per_figure + 1})', fontsize=16, fontweight='bold')
        plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.95])

        # Save the figure inside 'plot_num_box_plots_all' folder
        plot_filename = os.path.join(vis_dir, f'box_plots_batch_{i // max_subplots_per_figure + 1}.png')
        plt.savefig(plot_filename, dpi=300)
        plt.close()

        log_success(f"Saved plot to: {plot_filename}")

#---------------------------------------------------------------------------------------
def plot_num_qq_subplot(data_copy, save_dir, layout_title="QQ Plots of Numerical Variables"):
    """
    Generate and save QQ plots for all numerical variables in a dataset in batches of 12 subplots.
    """
    # Create 'plot_num_qq_subplot' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_num_qq_subplot")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract numerical columns
    numerical_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()

    if not numerical_cols:
        print("No numerical columns found in the dataset.")
        return

    # Set subplot limits
    max_subplots_per_figure = 12

    # Process columns in batches of max_subplots_per_figure
    for i in range(0, len(numerical_cols), max_subplots_per_figure):
        batch_cols = numerical_cols[i:i + max_subplots_per_figure]
        rows = (len(batch_cols) + 2) // 3
        cols = min(3, len(batch_cols))

        plt.figure(figsize=(cols * 7, rows * 5))

        for j, col in enumerate(batch_cols):
            plt.subplot(rows, cols, j + 1)

            # Generate QQ plot with custom marker and line
            (osm, osr), (slope, intercept, r) = stats.probplot(data_copy[col], dist="norm", plot=None)
            plt.scatter(osm, osr, s=10, color='blue', alpha=0.6)  # Adjust point style
            plt.plot(osm, slope * osm + intercept, 'r-', linewidth=2)  # Red line for theoretical quantiles

            # Formatting
            plt.title(f'QQ Plot of {col}', fontsize=14)
            plt.xlabel('Theoretical Quantiles', fontsize=12)
            plt.ylabel(f'Quantiles of {col}', fontsize=12)
            plt.grid(False)

        # Set title for the figure
        plt.suptitle(f'{layout_title} (Batch {i // max_subplots_per_figure + 1})', fontsize=16, fontweight='bold')
        plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.95])

        # Save the figure inside 'plot_num_qq_subplot' folder
        plot_filename = os.path.join(vis_dir, f'qq_plots_batch_{i // max_subplots_per_figure + 1}.png')
        plt.savefig(plot_filename, dpi=300)
        plt.close()

        log_success(f"Saved plot to: {plot_filename}")

#---------------------------------------------------------------------------------------
def analyze_categorical_variable(data, attribute, target=None, save_dir=None, all_summaries=[]):
    """
    Analyze and plot a categorical variable, optionally grouped by a target variable.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Create a summary table for the categorical variable
    counts = data[attribute].value_counts().to_frame()
    counts.columns = ["Count"]
    percentages = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    counts["Percentage"] = percentages

    if target:
        grouped_counts = data.groupby([attribute, target]).size().unstack(fill_value=0)
        grouped_counts.columns = grouped_counts.columns.astype(str)
        grouped_counts['Total'] = grouped_counts.sum(axis=1)
        grouped_percentages = (grouped_counts.div(grouped_counts['Total'], axis=0) * 100).round(2)
        grouped_percentages.columns = [f"% {col}" for col in grouped_percentages.columns]
        final_table = pd.concat([grouped_counts, grouped_percentages], axis=1)
        total_counts = grouped_counts.sum().to_frame().T
        total_counts.index = ['Total']
        total_percentages = (total_counts.div(total_counts['Total'], axis=0) * 100).round(2)
        total_percentages.columns = [f"% {col}" for col in total_percentages.columns]
        final_table = pd.concat([final_table, pd.concat([total_counts, total_percentages], axis=1)])
    else:
        final_table = counts

    final_table.reset_index(inplace=True)
    final_table.rename(columns={'index': attribute.capitalize()}, inplace=True)
    table_path = os.path.join(save_dir, f"{attribute}_summary.txt")
    with open(table_path, "w") as file:
        file.write(final_table.to_markdown(index=False, tablefmt="pipe"))

    all_summaries.append(f"\n### {attribute.capitalize()} Summary ###\n")
    all_summaries.append(final_table.to_markdown(index=False, tablefmt="pipe"))

    plt.figure(figsize=(10, 6))
    sns.countplot(data=data, x=attribute, palette="viridis")
    plt.title(f"{attribute.capitalize()} Distribution")
    for p in plt.gca().patches:
        height = p.get_height()
        if height > 0:
            plt.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5), textcoords='offset points')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plot_path1 = os.path.join(save_dir, f"{attribute}_distribution.png")
    plt.savefig(plot_path1, dpi=300)
    plt.close()

    if target:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=data, x=attribute, hue=target, palette="viridis", dodge=True)
        plt.title(f"{attribute.capitalize()} by {target.capitalize()}")
        for p in plt.gca().patches:
            height = p.get_height()
            if height > 0:
                plt.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                             ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5), textcoords='offset points')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plot_path2 = os.path.join(save_dir, f"{attribute}_with_{target}.png")
        plt.savefig(plot_path2, dpi=300)
        plt.close()

def plot_summary_cat_bar_optional_target(data, save_dir):
    """
    Fully automated analysis for all categorical variables, asking for a target variable.
    """
    vis_dir = os.path.join(save_dir, "visualization", "plot_summary_cat_bar_optional_target")
    os.makedirs(vis_dir, exist_ok=True)

    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()

    if not categorical_cols:
        print("No categorical columns found in the dataset.")
        return

    target_input = log_question("Do you want to analyze variables with a target variable? (y/n): ").strip().lower()
    target = None
    if target_input == 'y':
        target = log_question("Enter the target variable name: ").strip()
        if target not in data.columns:
            print(f"Target variable '{target}' not found in the dataset. Proceeding without target variable.")
            target = None

    all_summaries = []

    for attribute in tqdm(categorical_cols, desc="Processing Categorical Variables", unit="variable", leave=False):
        if attribute != target:
            analyze_categorical_variable(data, attribute, target, vis_dir, all_summaries)

    consolidated_report_path = os.path.join(vis_dir, "all_categorical_summaries.txt")
    with open(consolidated_report_path, "w") as consolidated_file:
        consolidated_file.write("### Consolidated Categorical Variable Analysis ###\n")
        consolidated_file.write("=" * 120 + "\n\n")
        consolidated_file.write("\n\n".join(all_summaries))

    
#---------------------------------------------------------------------------------------
def plot_cat_pie_charts_subplot(data_copy, save_dir, layout_title="Pie Charts of Categorical Variables"):
    """
    Generate and save pie charts for all categorical variables in a dataset in batches of 12 subplots.
    """
    # Create 'plot_cat_pie_charts_subplot' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_cat_pie_charts_subplot")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract categorical columns
    categorical_cols = data_copy.select_dtypes(include=['object', 'category']).columns.tolist()

    if not categorical_cols:
        print("No categorical columns found in the dataset.")
        return

    # Set subplot limits
    max_subplots_per_figure = 12

    # Process columns in batches of max_subplots_per_figure
    for i in range(0, len(categorical_cols), max_subplots_per_figure):
        batch_cols = categorical_cols[i:i + max_subplots_per_figure]
        rows = (len(batch_cols) + 2) // 3
        cols = min(3, len(batch_cols))

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5))
        axes = axes.flatten()

        for j, col in enumerate(batch_cols):
            series = data_copy[col].value_counts()
            sizes = series.values / series.sum() * 100
            colors = plt.cm.tab20c(np.linspace(0, 1, len(series)))
            wedges, _, autotexts = axes[j].pie(sizes, autopct='%1.1f%%', startangle=90, colors=colors)

            for text in autotexts:
                text.set_color('white')
                text.set_fontsize(12)

            axes[j].set_title(f'Distribution of {col}', fontsize=14)
            legend_labels = [f'{label} ({size:.1f}%)' for label, size in zip(series.index, sizes)]
            axes[j].legend(wedges, legend_labels, title=col, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))

        # Remove unused subplots
        for k in range(len(batch_cols), len(axes)):
            fig.delaxes(axes[k])

        # Set title for the figure
        fig.suptitle(f'{layout_title} (Batch {i // max_subplots_per_figure + 1})', fontsize=16, fontweight='bold')
        plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.95])

        # Save the figure inside 'plot_cat_pie_charts_subplot' folder
        plot_filename = os.path.join(vis_dir, f'pie_charts_batch_{i // max_subplots_per_figure + 1}.png')
        plt.savefig(plot_filename, dpi=300)
        plt.close()

        log_success(f"Saved plot to: {plot_filename}")

    
########################################################################################
###################################### V/S #############################################
########################################################################################

def plot_pair_scatter_numerical_vs_numerical(data_copy, save_dir):
    """
    Analyzes numerical columns by creating scatter plots with regression lines,
    optionally using a target variable for color encoding, and saves plots into
    organized subfolders based on the first column of each pair.
    """
    # Ask if there is a target variable for coloring
    use_hue = log_question("Do you have a target variable for coloring the scatter plots? (y/n): ").strip().lower()
    hue_column = None

    if use_hue == 'y':
        hue_column = log_question("Enter the target variable name (column): ").strip()
        if hue_column not in data_copy.columns:
            print(f"Column '{hue_column}' not found in dataset. Skipping hue.")
            hue_column = None

    # Create 'plot_scatter_plots_numerical_vs_numerical' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_scatter_plots_numerical_vs_numerical")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract numerical columns
    numerical_cols = data_copy.select_dtypes(include=['number']).columns.tolist()

    if not numerical_cols:
        print("No numerical columns found in the dataset.")
        return

    # Create all possible pairs of numerical columns
    NumericalVSNumerical_pairs = list(itertools.product(numerical_cols, repeat=2))

    # Group pairs by the first element in each pair
    grouped_pairs = {}
    for pair in NumericalVSNumerical_pairs:
        key = pair[0]
        if key not in grouped_pairs:
            grouped_pairs[key] = []
        grouped_pairs[key].append(pair)

    # Function to create subplots for a given set of pairs
    def create_subplots(df, current_pairs, save_path, hue_column):
        num_pairs = len(current_pairs)
        cols = 3
        rows = (num_pairs // cols) + (num_pairs % cols > 0)

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5))
        axes = axes.flatten()

        for i, (var1, var2) in enumerate(current_pairs):
            if hue_column:
                sns.scatterplot(data=df, x=var1, y=var2, hue=hue_column, palette='coolwarm', ax=axes[i])
            else:
                sns.scatterplot(data=df, x=var1, y=var2, ax=axes[i])
                
            sns.regplot(data=df, x=var1, y=var2, scatter=False, color="green", ax=axes[i], ci=None)
            axes[i].set_title(f'{var1} vs. {var2}')
            axes[i].set_xlabel(var2)
            axes[i].set_ylabel(var1)

        # Hide any remaining empty axes
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    # Generate plots and save to respective folders with progress tracking
    for col, pairs in tqdm(grouped_pairs.items(), desc="Generating plots", unit="column"):
        col_dir = os.path.join(vis_dir, col)
        os.makedirs(col_dir, exist_ok=True)

        # Split pairs into batches of 12 for better visualization
        max_plots_per_file = 12
        for i in range(0, len(pairs), max_plots_per_file):
            batch_pairs = pairs[i:i + max_plots_per_file]
            plot_filename = os.path.join(col_dir, f'{col}_batch_{i // max_plots_per_file + 1}.png')
            create_subplots(data_copy, batch_pairs, plot_filename, hue_column)

#---------------------------------------------------------------------------------------
def plot_pair_heatmaps_categorical_vs_categorical(data_copy, save_dir):
    """
    Analyzes categorical columns by creating heatmaps for pairwise comparisons
    and saves them into organized subfolders based on the first column of each pair.
    """
    # Create 'plot_pair_heatmaps_categorical_vs_categorical' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_pair_heatmaps_categorical_vs_categorical")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract categorical columns
    categorical_cols = data_copy.select_dtypes(include=['object', 'category']).columns.tolist()

    if not categorical_cols:
        print("No categorical columns found in the dataset.")
        return

    # Create all possible pairs of categorical columns
    CategoricalVSCategorical_pairs = list(itertools.product(categorical_cols, repeat=2))

    # Function to group pairs by the first element in each pair
    def group_pairs_by_first_element(pairs):
        grouped_pairs = {}
        for pair in pairs:
            key = pair[0]
            if key not in grouped_pairs:
                grouped_pairs[key] = []
            grouped_pairs[key].append(pair)
        return grouped_pairs

    # Group the pairs
    grouped_pairs = group_pairs_by_first_element(CategoricalVSCategorical_pairs)

    # Function to create subplots for a given set of pairs
    def create_subplots(df, current_pairs, save_path):
        num_pairs = len(current_pairs)
        cols = 3
        rows = (num_pairs // cols) + (num_pairs % cols > 0)

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5))
        axes = axes.flatten()

        for i, (var1, var2) in enumerate(current_pairs):
            var1_order = df[var1].unique()
            var2_order = df[var2].unique()
            contingency_table = pd.crosstab(df[var1], df[var2]).loc[var1_order, var2_order]
            sns.heatmap(contingency_table, annot=True, fmt="d", cmap="YlGnBu", ax=axes[i])
            axes[i].set_title(f'{var1} vs. {var2}')
            axes[i].set_xlabel(var2)
            axes[i].set_ylabel(var1)

        # Hide any remaining empty axes
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    # Generate and save plots with progress tracking
    for col, pairs in tqdm(grouped_pairs.items(), desc="Generating categorical heatmaps", unit="column"):
        col_dir = os.path.join(vis_dir, col)
        os.makedirs(col_dir, exist_ok=True)

        # Split pairs into batches of 12 for better visualization
        max_plots_per_file = 12
        for i in range(0, len(pairs), max_plots_per_file):
            batch_pairs = pairs[i:i + max_plots_per_file]
            plot_filename = os.path.join(col_dir, f'{col}_batch_{i // max_plots_per_file + 1}.png')
            create_subplots(data_copy, batch_pairs, plot_filename)
    
#---------------------------------------------------------------------------------------
def plot_pair_box_vilon_numerical_vs_categorical(data_copy, save_dir):
    """
    Analyzes numerical vs categorical variables by creating boxplots and violin plots,
    and saves them into organized subfolders based on categorical variables.
    """
    # Create 'plot_box_violin_numerical_vs_categorical' folder inside the specified directory
    vis_dir = os.path.join(save_dir, "visualization", "plot_box_violin_numerical_vs_categorical")
    os.makedirs(vis_dir, exist_ok=True)

    # Extract numerical and categorical columns
    numerical_cols = data_copy.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data_copy.select_dtypes(include=['object', 'category']).columns.tolist()

    if not numerical_cols or not categorical_cols:
        print("No numerical or categorical columns found in the dataset.")
        return

    # Create all possible numerical vs categorical pairs
    NumVsCat_pairs = list(itertools.product(numerical_cols, categorical_cols))

    # Group pairs by categorical variables
    grouped_pairs = {}
    for num_var, cat_var in NumVsCat_pairs:
        if cat_var not in grouped_pairs:
            grouped_pairs[cat_var] = []
        grouped_pairs[cat_var].append((num_var, cat_var))

    # Function to create subplots for a given set of pairs
    def create_subplots(df, current_pairs, save_path):
        num_pairs = len(current_pairs)
        cols = 3
        rows = (num_pairs // cols) + (num_pairs % cols > 0)

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5))
        axes = axes.flatten()

        for i, (num_var, cat_var) in enumerate(current_pairs):
            sns.boxplot(x=cat_var, y=num_var, data=df, ax=axes[i], hue=cat_var, palette="Set3", legend=False, boxprops=dict(alpha=0.7))
            sns.violinplot(x=cat_var, y=num_var, data=df, ax=axes[i], hue=cat_var, palette="Set3", legend=False, inner=None, alpha=0.3)
            axes[i].set_title(f'{num_var} by {cat_var}')
            axes[i].tick_params(axis='x', rotation=90)

        # Hide any remaining empty axes
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    # Generate plots and save to respective folders with progress tracking
    for cat_var, pairs in tqdm(grouped_pairs.items(), desc="Generating numerical vs categorical plots", unit="category"):
        cat_dir = os.path.join(vis_dir, cat_var)
        os.makedirs(cat_dir, exist_ok=True)

        # Split pairs into batches of 12 for better visualization
        max_plots_per_file = 12
        for i in range(0, len(pairs), max_plots_per_file):
            batch_pairs = pairs[i:i + max_plots_per_file]
            plot_filename = os.path.join(cat_dir, f'{cat_var}_batch_{i // max_plots_per_file + 1}.png')
            create_subplots(data_copy, batch_pairs, plot_filename)
            

########################################################################################

def combine_files(directory, csv_file_name):
    """
    Combines specific text files into a single output file with a name based on the CSV file
    and deletes the individual text files after combining.
    
    Parameters:
    directory (str): The directory containing the text files.
    csv_file_name (str): The name of the original CSV file.
    """
    files_to_concatenate = [
        "dataset_info.txt",
        "data_overview.txt",
        "categorize_columns.txt",
        "outliers_summary.txt",
        "summary_statistics_all.txt",
        "categorical_summary.txt"
    ]

    # Get the base name of the CSV file without extension
    base_csv_name = os.path.splitext(csv_file_name)[0]

    # Create the output file name using the CSV file's base name
    output_file_name = f"{base_csv_name}_data_overview.txt"
    output_file_path = os.path.join(directory, output_file_name)

    with open(output_file_path, 'w') as outfile:
        for filename in files_to_concatenate:
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                # Remove the .txt extension only for files listed in files_to_concatenate
                title = filename[:-4]  # Remove the last four characters (".txt")
                outfile.write(f"### {title}\n\n")
                with open(file_path, 'r') as infile:
                    outfile.write(infile.read())
                outfile.write("\n\n")  # Add a newline to separate contents

                # Delete the individual file after adding its contents to the combined file
                os.remove(file_path)
                log_info(f"Deleted file: {file_path}")

    log_success(f"Combined file created at: {output_file_path}")

def distinct_val_tabular_html_2000(data, output_file="distinct_values_count_by_dtype.html", display_limit=2000):
    """
    Displays the distinct value counts of all variables in a tabular format grouped by data type,
    ensuring that NaN values are shown as NaN, and saves it as an HTML file with a navigation pane
    that includes variable distinct counts. If a variable has more than `display_limit` distinct values,
    it will display only the top `display_limit` values but show the exact count in the title.
    """
    def generate_doc_map(grouped_columns, data):
        """
        Generates a document map (navigation pane) based on the grouped columns by data type,
        including the distinct values count for each variable.
        """
        doc_map_html = '<ul>'
        for dtype, variables in grouped_columns.items():
            doc_map_html += f"<li><strong>{dtype} ({len(variables)} variables)</strong><ul>"
            for variable in variables:
                distinct_count = data[variable].nunique(dropna=False)
                var_id = variable.replace(" ", "-")
                doc_map_html += f'<li><a href="#{var_id}">{variable} ({distinct_count})</a></li>'
            doc_map_html += "</ul></li>"
        doc_map_html += "</ul>"
        return doc_map_html

    def display_tabular_data_with_columns(variable, data, display_limit):
        """
        Displays the distinct value counts of a variable in a tabular format with an auto-calculated number of columns,
        ensuring that NaN values are shown as NaN and no empty columns are present. Displays only the top `display_limit`
        distinct values but shows the exact count in the title.
        """
        # Calculate value counts and prepare data for the table, including NaN values
        value_counts = data[variable].value_counts(dropna=False).sort_index()

        # Store the exact number of distinct values
        distinct_count = value_counts.shape[0]

        # Truncate the value counts if they exceed the display limit
        if len(value_counts) > display_limit:
            value_counts = value_counts.head(display_limit)

        # Ensure that NaN values are treated as NaN
        value_counts.index = value_counts.index.to_series().replace({pd.NA: 'NaN', float('nan'): 'NaN', None: 'NaN'})

        # Initialize the tabular data list
        tabular_data = []
        for value, count in value_counts.items():
            if pd.isna(value):
                value = 'NaN'
            else:
                # Format values to remove unnecessary decimal points
                value = f'{value:.6g}' if isinstance(value, float) else str(value)
            count = int(count)  # Ensure count is an integer to avoid decimals
            tabular_data.append([value, count])

        # Adjust the number of columns (Value_x, Count_x) to fit the data into a grid
        num_columns = 8  # For example, 8 pairs of Value and Count columns
        data_len = len(tabular_data)
        rows = (data_len + num_columns - 1) // num_columns

        # Create the rows for the tabular format
        formatted_table = []
        for i in range(rows):
            row = []
            for j in range(num_columns):
                idx = i + j * rows
                if idx < len(tabular_data):
                    row.extend(tabular_data[idx])
                else:
                    row.extend([None, None])  # Fill with NaN for empty cells
            formatted_table.append(row)

        # Convert the formatted table to a DataFrame
        col_names = []
        for i in range(len(formatted_table[0]) // 2):
            col_names.extend([f'Value_{i+1}', f'Count_{i+1}'])

        df = pd.DataFrame(formatted_table, columns=col_names)

        # Remove fully empty columns
        df = df.dropna(axis=1, how='all')

        # Replace any remaining None with 'NaN' for display
        df = df.fillna('NaN')

        # Convert count columns to integer type explicitly
        for col in df.columns:
            if 'Count' in col:
                df[col] = df[col].apply(lambda x: str(int(float(x))) if x != 'NaN' else x)

        # Return the final DataFrame in the desired format
        return df, distinct_count

    # Group columns by data type
    grouped_columns = data.columns.to_series().groupby(data.dtypes).groups

    # Generate the document map (navigation pane) HTML
    doc_map = generate_doc_map(grouped_columns, data)

    # Initialize a list to store HTML parts
    html_parts = []

    # Loop through each data type
    for dtype, variable_columns in grouped_columns.items():
        html_parts.append(f"<h1 id='{dtype}'>{dtype} ({len(variable_columns)} variables)</h1>\n")

        # Loop through each variable in the current dtype group
        for variable in variable_columns:
            var_id = variable.replace(" ", "-")
            # Create the tabular data for the current variable
            df, distinct_count = display_tabular_data_with_columns(variable, data, display_limit)

            # Add the title and DataFrame HTML to the html_parts list
            if distinct_count > display_limit:
                html_parts.append(f"<h2 id='{var_id}'>Distinct Values Counts for {variable}: {distinct_count} (Top {display_limit} displayed)</h2>\n")
            else:
                html_parts.append(f"<h2 id='{var_id}'>Distinct Values Counts for {variable}: {distinct_count}</h2>\n")
            
            html_parts.append(df.to_html(index=False, escape=False, border=0, justify='center', classes='data-table'))  # Align table center
            html_parts.append("<br><hr><br>")  # Add some space and a line break between variables

            # Add a page break after each large table
            if distinct_count > display_limit:
                html_parts.append('<div style="page-break-before: always;"></div>')

    # Combine all HTML parts into a single string
    full_html = "\n".join(html_parts)

    # Custom HTML template with navigation pane, light/dark mode, and without sticky headers
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #fdfdfd;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
                line-height: 1.6;
                color: #333;
                display: flex;
                height: 100vh;
                overflow: hidden;
                transition: background-color 0.3s, color 0.3s;
            }}
            body.dark-mode {{
                background-color: #2c2c2c;
                color: #d3d3d3;
            }}
            #doc-map {{
                width: 250px;
                height: 100vh;
                padding: 20px;
                background-color: #f0f0f0;
                color: #333;
                border-right: 1px solid #ccc;
                overflow-y: auto;
                flex-shrink: 0;
                position: relative;
                transition: width 0.2s, background-color 0.3s, color 0.3s;
            }}
            #doc-map.dark-mode {{
                background-color: #3b3b3b;
                color: #d3d3d3;
            }}
            #doc-map ul {{
                list-style-type: none;
                padding-left: 0;
                margin-left: 0;
            }}
            #doc-map ul ul {{
                margin-left: 20px;
            }}
            #doc-map li {{
                padding-left: 0;
            }}
            #doc-map a {{
                color: #007bff;
                text-decoration: none;
            }}
            #doc-map a.dark-mode {{
                color: #82cfff;
            }}
            #doc-map a:hover {{
                text-decoration: underline;
            }}
            #resizer {{
                width: 10px;
                cursor: ew-resize;
                background-color: #d1d5da;
                flex-shrink: 0;
            }}
            #content-wrapper {{
                flex-grow: 1;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}
            #content {{
                padding: 20px;
                background-color: #ffffff;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                height: 100vh;
                overflow-y: auto;
                word-wrap: break-word;
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                min-width: 0;
                position: relative;
                overflow-wrap: break-word;
                transition: background-color 0.3s, color 0.3s;
            }}
            #content.dark-mode {{
                background-color: #333333;
                color: #e4e6eb;
            }}
            table {{
                width: 100%;
                table-layout: fixed;
                border-collapse: collapse;
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
            th, td {{
                padding: 8px 12px;
                text-align: center;
                border: 1px solid #ddd;
                word-wrap: break-word;
                transition: background-color 0.3s, color 0.3s;
            }}
            th {{
                background-color: #e0e0e0;
                color: #333;
            }}
            td {{
                background-color: #ffffff;
            }}
            .data-table th {{
                background-color: #e0e0e0;
            }}
            .data-table td:nth-child(2n-1) {{
                background-color: #f0f8ff;  /* Light blue background for Value_ columns */
            }}
            .data-table td:nth-child(2n) {{
                background-color: #ffffff;  /* White background for Count_ columns */
            }}
            th.dark-mode {{
                background-color: #4a4a4a;
                color: #ffffff;
            }}
            .data-table td.dark-mode:nth-child(2n-1) {{
                background-color: #4a6072;  /* Darker blue background for Value_ columns in dark mode */
            }}
            .data-table td.dark-mode:nth-child(2n) {{
                background-color: #555555;  /* Darker background for Count_ columns in dark mode */
            }}
            pre, code {{
                background-color: #f6f8fa;
                padding: 16px;
                border-radius: 3px;
                overflow-x: auto;
                font-family: Consolas, "Courier New", monospace;
                font-size: 1em;
                word-wrap: break-word;
            }}
            pre.dark-mode, code.dark-mode {{
                background-color: #3a3b3c;
                color: #f5f6f7;
            }}
            .markdown-cell {{
                display: block;
                margin-bottom: 20px;
                word-wrap: break-word;
            }}
            .filename {{
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            #mode-toggle {{
                position: absolute;
                top: 10px;
                right: 20px;
                padding: 10px 20px;
                background-color: #444;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                z-index: 1000;
            }}
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function () {{
                var modeToggleButton = document.getElementById('mode-toggle');
                modeToggleButton.addEventListener('click', function() {{
                    document.body.classList.toggle('dark-mode');
                    document.getElementById('doc-map').classList.toggle('dark-mode');
                    document.getElementById('content').classList.toggle('dark-mode');
                    document.querySelectorAll('th, td').forEach(function(cell) {{
                        cell.classList.toggle('dark-mode');
                    }});
                    document.querySelectorAll('pre, code').forEach(function(cell) {{
                        cell.classList.toggle('dark-mode');
                    }});
                    document.querySelectorAll('#doc-map a').forEach(function(link) {{
                        link.classList.toggle('dark-mode');
                    }});
                }});

                // Enable resizing between ToC and content
                var resizer = document.getElementById('resizer');
                var leftPanel = document.getElementById('doc-map');
                var rightPanel = document.getElementById('content-wrapper');

                resizer.addEventListener('mousedown', function(e) {{
                    document.body.classList.add('resizing');
                    var startX = e.pageX;
                    var startWidth = leftPanel.offsetWidth;
                    var startRightWidth = rightPanel.offsetWidth;

                    function doDrag(e) {{
                        var newWidth = startWidth + (e.pageX - startX);
                        leftPanel.style.width = newWidth + 'px';
                        rightPanel.style.width = (startRightWidth - (e.pageX - startX)) + 'px';
                    }}

                    function stopDrag(e) {{
                        document.removeEventListener('mousemove', doDrag);
                        document.removeEventListener('mouseup', stopDrag);
                        document.body.classList.remove('resizing');
                    }}

                    document.addEventListener('mousemove', doDrag);
                    document.addEventListener('mouseup', stopDrag);
                }});
            }});
        </script>
    </head>
    <body>
        <div id="doc-map">
            {doc_map}
        </div>
        <div id="resizer"></div>
        <div id="content-wrapper">
            <div id="content">
                <button id="mode-toggle">Toggle Dark/Light Mode</button>
                {content}
            </div>
        </div>
    </body>
    </html>
    """

    # Insert the generated content into the custom HTML template
    html_content = html_template.format(content=full_html, doc_map=doc_map)

    # Write the full HTML to the output file
    with open(output_file, 'w') as file:
        file.write(html_content)

    log_success(f"Tabular data by data types has been saved to {output_file}")

def main(file_path, save_dir):
    """
    Main function to execute the full data analysis workflow.

    Steps:
    1. Check and install required packages
    2. Detect delimiter and load dataset
    3. Create a copy of the dataset
    4. Perform dataset information and overview analysis
    5. Detect and handle duplicates (Optional)
    6. Handle missing values (Optional)
    7. Detect outliers and analyze numerical & categorical features
    8. Generate summary statistics
    9. Perform relation analysis (Chi-square, Correlation, VIF)
    10. Generate visualizations (Histograms, KDE, Boxplots, QQ plots)
    11. Perform scatter plots, categorical comparisons, and heatmaps
    12. Combine all reports into a single file
    13. Handle any errors gracefully
    """

    # Updated required packages based on the provided imports
    required_packages = [
        'pandas', 'numpy', 'scipy', 'statsmodels', 'seaborn', 'matplotlib', 'missingno', 
        'tableone', 'researchpy', 'cerberus', 'tqdm', 'tabulate', 'sklearn'
    ]

    # Clear console and start
    clear_console()
    log_header("AUTOMATED CSV DATA ANALYSIS TOOL")

    # Step 1: Check and install packages
    log_step(1, "Checking and installing required packages")
    check_and_install_packages(required_packages)

    try:
        # Step 2: Detect the delimiter
        log_step(2, "Detecting delimiter and loading dataset")
        with open(file_path, 'r') as f:
            first_line = f.readline()
            delimiter = ',' if ',' in first_line else (';' if ';' in first_line else None)

        if not delimiter:
            log_warning("Delimiter not detected automatically.")
            log_info("Displaying top 5 rows of the data to help determine the correct delimiter.")
            temp_df = pd.read_csv(file_path, nrows=5)
            colored_print(str(temp_df.head()), Colors.WHITE)
            delimiter = log_question("Please enter the delimiter manually (e.g., ',', ';', '\\t'): ").strip()

        # Step 3: Load dataset and create a copy
        data = pd.read_csv(file_path, delimiter=delimiter)
        data_copy = data.copy()
        log_success(f"Dataset loaded successfully! Shape: {data.shape}")

        log_separator()

        # Step 4: Dataset information and overview
        log_step(4, "Generating dataset information and overview")
        dataset_info_shap_datatypes_num_cat_count_duplecatedrows(data_copy, save_dir)
        data_table_range_min_max_distinct(data_copy, save_dir)        
        datatypes_wise_unique_mising(data_copy, save_dir)

        # Step 5: Detect and handle duplicates (Optional)
        log_step(5, "Duplicate detection and removal")
        run_save_remove_duplicates = log_question("Do you want to remove duplicates? (y/n): ").strip().lower()
        
        if run_save_remove_duplicates == 'y':
            data_copy = save_and_remove_duplicates(data_copy, save_dir)

        # Step 6: Handle missing values (Optional)
        log_step(6, "Missing values analysis and imputation")
        run_missing_values_analysis = log_question("Do you want to analyze missing values? (y/n): ").strip().lower()
        
        if run_missing_values_analysis == 'y':
            analyze_missing_values(data_copy, save_dir)

        run_auto_impute = log_question("Do you want to auto-impute missing values? (y/n): ").strip().lower()
        
        if run_auto_impute == 'y':
            data_copy = auto_impute_missing_values(data_copy, save_dir)

        # Step 7: Detect outliers and analyze numerical & categorical features
        log_step(7, "Outlier detection and feature analysis")
        detect_outliers(data_copy, ['int64', 'float64'], save_dir)
        detect_iqr_outliers_all(data_copy, save_dir)
        numerical_features_boxplot_skew_kurto_outliers(data_copy, save_dir)

        # Step 8: Generate summary statistics
        log_step(8, "Generating summary statistics")
        researchpy_descriptive_stats(data_copy, save_dir)
        TableOne_groupby_column(data_copy, save_dir)
        num_generate_summary_statistics_all(data_copy, save_dir)
        cat_generate_summary_statistics_all(data_copy, save_dir)  # Fixed variable name
        distinct_val_tabular_html_2000(data_copy, os.path.join(save_dir, "distinct_values_count_by_dtype.html"))

        # Step 9: Perform relation analysis (Chi-square, Correlation, VIF)
        log_step(9, "Relationship analysis (Correlation, Chi-square, VIF)")
        analyze_relation(data_copy, save_dir)

        # Step 10: Generate visualizations (Histograms, KDE, Boxplots, QQ plots)
        log_step(10, "Generating visualizations")
        plot_summary_num_hist_box_optional_target(data_copy, save_dir)
        plot_num_kde_subplot(data_copy, save_dir)
        plot_num_box_plots_all(data_copy, save_dir)
        plot_num_qq_subplot(data_copy, save_dir)
        
        plot_summary_cat_bar_optional_target(data_copy, save_dir)  # Fixed variable name
        plot_cat_pie_charts_subplot(data_copy, save_dir)

        # Step 11: Perform scatter, heatmaps, box, plots, comparisons
        log_step(11, "Generating comparison plots")
        plot_pair_scatter_numerical_vs_numerical(data_copy, save_dir)
        plot_pair_heatmaps_categorical_vs_categorical(data_copy, save_dir)
        plot_pair_box_vilon_numerical_vs_categorical(data_copy, save_dir)  # Removed `.txt`

        # Step 12: Combine all reports into a single file
        log_step(12, "Combining reports")
        combine_files(save_dir, os.path.basename(file_path))

    except Exception as e:
        # Step 13: Handle errors
        log_error(f"An error occurred: {e}")
        import traceback
        log_error(f"Detailed error: {traceback.format_exc()}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        log_error("Usage: python auto_data_analysis.py <path_to_csv_file> <output_directory>")
        colored_print("Example: python auto_data_analysis.py data.csv ./output", Colors.YELLOW)
    else:
        file_path = sys.argv[1]
        save_dir = sys.argv[2]
        main(file_path, save_dir)
