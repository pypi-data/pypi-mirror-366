import pandas as pd
import numpy as np
import sys

def topsis_analysis(input_file, weights_str, impacts_str, output_file):
    """
    Perform TOPSIS analysis on the given data
    
    Parameters:
    input_file (str): Path to input CSV/Excel file
    weights_str (str): Comma-separated weights string
    impacts_str (str): Comma-separated impacts string (+/-)
    output_file (str): Path to output CSV file
    
    Returns:
    bool: True if analysis successful, False otherwise
    """
    try:
        # Read input file
        if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
            data = pd.read_excel(input_file, engine='openpyxl')
        else:
            data = pd.read_csv(input_file)
        
        # Parse weights and impacts
        weights = np.array([float(w.strip()) for w in weights_str.split(',')])
        impacts = [i.strip() for i in impacts_str.split(',')]
        
        # Validate inputs
        if not all(i in ['+', '-'] for i in impacts):
            raise ValueError("Impacts must be '+' or '-' only.")
        
        # Extract numeric data (from 2nd column onwards)
        numeric_data = data.iloc[:, 1:]
        
        if len(weights) != len(impacts) or len(weights) != len(numeric_data.columns):
            raise ValueError("Number of weights, impacts, and criteria must be equal")
        
        # Normalize the matrix
        normalized_matrix = numeric_data.apply(lambda x: x / np.sqrt((x**2).sum()), axis=0)
        
        # Calculate weighted normalized matrix
        weighted_matrix = normalized_matrix * weights
        
        # Find ideal best and worst solutions
        ideal_best = []
        ideal_worst = []
        
        for i, impact in enumerate(impacts):
            if impact == '+':
                ideal_best.append(weighted_matrix.iloc[:, i].max())
                ideal_worst.append(weighted_matrix.iloc[:, i].min())
            else:
                ideal_best.append(weighted_matrix.iloc[:, i].min())
                ideal_worst.append(weighted_matrix.iloc[:, i].max())
        
        # Calculate distances
        dist_ideal = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
        dist_anti_ideal = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))
        
        # Calculate TOPSIS score
        topsis_scores = dist_anti_ideal / (dist_anti_ideal + dist_ideal)
        
        # Calculate ranks
        ranks = topsis_scores.rank(method='min', ascending=False)
        
        # Create result dataframe
        result_df = data.copy()
        result_df['Topsis Score'] = topsis_scores
        result_df['Rank'] = ranks.astype(int)
        
        # Save result
        result_df.to_csv(output_file, index=False)
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 5:
        print("Usage: topsis <input_file> <weights> <impacts> <output_file>")
        sys.exit(1)
    
    input_file, weights_str, impacts_str, output_file = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    success = topsis_analysis(input_file, weights_str, impacts_str, output_file)
    
    if success:
        print(f"TOPSIS analysis completed successfully! Results saved to {output_file}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
