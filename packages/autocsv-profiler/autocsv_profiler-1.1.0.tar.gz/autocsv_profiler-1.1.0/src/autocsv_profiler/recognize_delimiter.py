import sys
import csv
import subprocess


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

def colored_print(message, color=Colors.WHITE, bold=False):
    """Print colored message"""
    style = Colors.BOLD if bold else ""
    print(f"{style}{color}{message}{Colors.ENDC}")

def log_success(message):
    """Print success message in green"""
    colored_print(f"SUCCESS: {message}", Colors.OKGREEN, bold=True)

def install_missing_packages():
    """Installs missing required packages if not already installed."""
    required_packages = ["pandas"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing package: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def detect_delimiter(csv_file):
    common_delimiters = [',', ';', '\t', '|', ':']

    with open(csv_file, 'r') as file:
        sample = file.read(1024)  # Read a sample of the file to detect the delimiter

    for delimiter in common_delimiters:
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            if delimiter == dialect.delimiter:
                return delimiter
        except csv.Error:
            continue

    # If the Sniffer fails, we'll manually count the delimiter occurrences
    for delimiter in common_delimiters:
        with open(csv_file, 'r') as file:
            sample_lines = file.readlines(5)  # Read first few lines
            counts = [line.count(delimiter) for line in sample_lines]
            if max(counts) > 0 and all(count == counts[0] for count in counts):
                return delimiter

    raise ValueError("Could not determine delimiter")

def print_csv_head(csv_file):
    try:
        with open(csv_file, 'r') as file:
            lines = [next(file).strip() for _ in range(5)]
            print("\n".join(lines))
    except Exception as e:
        print(f"Error reading the CSV file: {e}")

if __name__ == "__main__":
    install_missing_packages()  # Ensure required packages are installed

    if len(sys.argv) != 2:
        print("Usage: python recognize_delimiter.py <csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    try:
        delimiter = detect_delimiter(csv_file_path)
        log_success(f"Detected delimiter: {delimiter}")
    except ValueError as e:
        print(f"Error detecting delimiter: {e}")
        print("Printing the first few lines of the file for manual inspection:")
        print_csv_head(csv_file_path)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
