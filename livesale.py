import os
import pandas as pd
import numpy as np
import re

class CSVProcessor:
    EXPECTED_HEADERS = ["Product Name", "Quantity Sold", "Current Stock Quantity", "live_sale_price", "Gross Sales", "Gross Sales (After Discounts)"]

    @staticmethod
    def load_first_csv():
        # List all CSV files in the current directory
        csv_files = [f for f in os.listdir() if f.endswith('.csv')]
        assert csv_files, 'No CSV files found in the current directory'

        # Load the first CSV file into a pandas DataFrame
        input_dataframe = pd.read_csv(csv_files[0])
        # Fill null values and set data types
        input_dataframe["Quantity Sold"] = input_dataframe["Quantity Sold"].fillna(0).astype(int)
        input_dataframe["Current Stock Quantity"] = input_dataframe["Current Stock Quantity"].fillna(0).astype(int)
        input_dataframe["Gross Sales"] = input_dataframe["Gross Sales"].fillna(0.00).astype(float).round(2)
        input_dataframe["Gross Sales (After Discounts)"] = input_dataframe["Gross Sales (After Discounts)"].fillna(0.00).astype(float).round(2)
        input_dataframe["live_sale_price"] = input_dataframe["live_sale_price"].fillna(0.00).astype(float).round(2)
        return input_dataframe

    @staticmethod
    def verify_csv(input_dataframe):
        # Verify the DataFrame has all the expected headers
        assert set(CSVProcessor.EXPECTED_HEADERS).issubset(input_dataframe.columns), 'The CSV file does not have the expected headers'

    @staticmethod
    def preprocess_df(input_dataframe):
        # Preprocess the Product Name column
        input_dataframe['Product Name'] = input_dataframe['Product Name'].astype(str).apply(lambda x: re.match("^[a-zA-Z0-9\s]*", x).group().upper())

        # Group by Product Name and sum numeric columns
        summed_dataframe = input_dataframe.groupby('Product Name').sum().reset_index()[["Product Name", "Quantity Sold", "Current Stock Quantity", "Gross Sales", "Gross Sales (After Discounts)"]]

        # Group by Product Name and get minimum live_sale_price
        min_price_dataframe = input_dataframe.groupby('Product Name').min().reset_index()[["Product Name", "live_sale_price"]]

        # Merge the summed and minimum price dataframes
        grouped_dataframe = pd.merge(summed_dataframe, min_price_dataframe, on='Product Name')

        # Create Quantity Detail column
        grouped_dataframe['Quantity Detail'] = grouped_dataframe['Quantity Sold'].astype(str) + ' of ' + (grouped_dataframe['Quantity Sold'] + grouped_dataframe['Current Stock Quantity']).astype(str)

        # Reorder columns
        grouped_dataframe = grouped_dataframe[["Product Name", "Quantity Detail", "Quantity Sold", "Current Stock Quantity", "live_sale_price", "Gross Sales", "Gross Sales (After Discounts)"]]

        # Add two empty rows after each row
        empty_rows = pd.DataFrame(index=pd.Index(['', '']*len(grouped_dataframe))).reset_index(drop=True)
        final_dataframe = pd.concat([grouped_dataframe, empty_rows]).sort_index(kind='mergesort').reset_index(drop=True)

        # Replace NaN values with an empty string
        final_dataframe.replace(np.nan, '', inplace=True)

        return final_dataframe

    @staticmethod
    def get_output_filename():
        # Prompt the user for the output filename
        output_filename = input('Enter the desired output filename (default is "output.csv"): ') or 'output.csv'
        # Append a unique identifier if the file already exists in the Output folder
        if output_filename in os.listdir('./Output'):
            base, ext = os.path.splitext(output_filename)
            i = 1
            while f'{base}({i}){ext}' in os.listdir('./Output'):
                i += 1
            output_filename = f'{base}({i}){ext}'
        return output_filename

    @staticmethod
    def save_csv(final_dataframe, output_filename):
        # Ensure the Output directory exists
        os.makedirs('./Output', exist_ok=True)
        # Save the final DataFrame as a CSV file in the Output directory
        final_dataframe.to_csv(f'Output/{output_filename}', index=False)

def main():
    # Load the first CSV file in the current directory
    input_dataframe = CSVProcessor.load_first_csv()
    # Verify the CSV has the expected headers
    CSVProcessor.verify_csv(input_dataframe)
    # Preprocess the DataFrame and group by Product Name
    final_dataframe = CSVProcessor.preprocess_df(input_dataframe)
    # Get the output filename from the user
    output_filename = CSVProcessor.get_output_filename()
    # Save the final DataFrame as a CSV file
    CSVProcessor.save_csv(final_dataframe, output_filename)

if __name__ == "__main__":
    main()