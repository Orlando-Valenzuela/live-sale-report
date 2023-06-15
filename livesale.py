import os
import pandas as pd
import numpy as np
import re


class CSVProcessor:
    EXPECTED_HEADERS = [
        "Product Name",
        "Quantity Sold",
        "Current Stock Quantity",
        "live_sale_price",
        "Gross Sales",
        "Gross Sales (After Discounts)",
    ]

    def __init__(self, filename):
        self.filename = filename

    def load_csv(self):
        # Load CSV file into a pandas DataFrame
        self.dataframe = pd.read_csv(self.filename)
        # Fill null values and set data types
        self.dataframe["Quantity Sold"] = self.dataframe["Quantity Sold"].fillna(0).astype(int)
        self.dataframe["Current Stock Quantity"] = self.dataframe["Current Stock Quantity"].fillna(0).astype(int)
        self.dataframe["Gross Sales"] = self.dataframe["Gross Sales"].fillna(0.00).astype(float).round(2)
        self.dataframe["Gross Sales (After Discounts)"] = self.dataframe["Gross Sales (After Discounts)"].fillna(0.00).astype(float).round(2)
        self.dataframe["live_sale_price"] = self.dataframe["live_sale_price"].fillna(0.00).astype(float).round(2)

    def verify_csv(self):
        # Verify the DataFrame has all the expected headers
        assert set(CSVProcessor.EXPECTED_HEADERS).issubset(self.dataframe.columns), 'The CSV file does not have the expected headers'

    def preprocess_df(self):
        # Preprocess the Product Name column
        self.dataframe['Product Name'] = self.dataframe['Product Name'].astype(str).apply(lambda x: re.match("^[a-zA-Z0-9\s]*", x).group().upper())
        # Group by Product Name and sum numeric columns
        self.dataframe = self.dataframe.groupby('Product Name').agg(
            {"Quantity Sold": "sum",
             "Current Stock Quantity": "sum",
             "live_sale_price": "min",
             "Gross Sales": "sum",
             "Gross Sales (After Discounts)": "sum"}).reset_index()
        # Create Quantity Detail column
        self.dataframe['Quantity Detail'] = self.dataframe.apply(lambda row: f"{row['Quantity Sold']} of {row['Quantity Sold'] + row['Current Stock Quantity']}", axis=1)
        # Reorder columns
        self.dataframe = self.dataframe[["Product Name", "Quantity Detail", "Quantity Sold", "Current Stock Quantity", "live_sale_price", "Gross Sales", "Gross Sales (After Discounts)"]]

    def get_output_filename(self):
        # Ensure the Output directory exists
        os.makedirs('Output', exist_ok=True)
        # Prompt the user for the output filename
        output_filename = input('Enter the desired output filename (default is "output.csv"): ') or 'output.csv'
        output_filename = os.path.join('Output', output_filename)
        # Append a unique identifier if the file already exists in the Output folder
        if output_filename in os.listdir('Output'):
            base, ext = os.path.splitext(output_filename)
            i = 1
            while f'{base}({i}){ext}' in os.listdir('Output'):
                i += 1
            output_filename = f'{base}({i}){ext}'
        return output_filename

    def save_csv(self, output_filename):
        # Save the final DataFrame as a CSV file in the Output directory
        self.dataframe.to_csv(output_filename, index=False)


def find_csv_file():
    # Get the current directory
    current_directory = os.getcwd()
    # Find the first CSV file in the current directory
    for filename in os.listdir(current_directory):
        if filename.endswith('.csv'):
            return os.path.join(current_directory, filename)
    # If no CSV file found, raise an exception
    raise FileNotFoundError('No CSV file found in the current directory')


def main():
    # Find the CSV file in the current directory
    input_filename = find_csv_file()
    # Initialize a CSVProcessor object
    csv_processor = CSVProcessor(input_filename)
    # Load the CSV file
    csv_processor.load_csv()
    # Verify the CSV has the expected headers
    csv_processor.verify_csv()
    # Preprocess the DataFrame and group by Product Name
    csv_processor.preprocess_df()
    # Get the output filename
    output_filename = csv_processor.get_output_filename()
    # Save the final DataFrame as a CSV file
    csv_processor.save_csv(output_filename)


if __name__ == "__main__":
    main()