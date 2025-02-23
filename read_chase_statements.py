import re
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber
import pandas as pd
import os
import csv

class BankData:
    def __init__(self):
        self.filepath = 'input_data/'

    def run_all(self, file):
        """Transfer, payment, purchase different types"""

        # Define a regular expression pattern to match the date format
        date_pattern = re.compile(r'\b\d{1,2} [A-Za-z]{3} \d{4}\b')

        # Use pdfplumber to read pdf
        transactions = []
        with pdfplumber.open(file) as pdf:
            for page_number in range(len(pdf.pages)):
                page = pdf.pages[page_number]
                text = page.extract_text()

                # Split the text into lines and process each line
                lines = text.split('\n')
                for line in lines:
                    parts = line.split()
                    if date_pattern.match(line):
                        date = " ".join(parts[:3])
                        description = " ".join(parts[3:-2])
                        amount = parts[-2]
                        balance = parts[-1]
                        transactions.append([date, description, amount, balance])

            # create a df and add data
            columns = ['Date', 'Description', 'Amount', 'Balance']
            df = pd.DataFrame(transactions, columns=columns)

            # Remove the pound sign from the 'Amount' column
            df['Balance'] = pd.to_numeric(df['Balance'].str.replace('£', ''), errors='coerce')

            # Remove pound sign and commas from 'Amount' and convert to numeric
            df['Amount'] = pd.to_numeric(df['Amount'].str.replace('£', '').str.replace(',', ''), errors='coerce')

            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])

            return df

    def get_filtered_statements(self):
        """Generate filtered dataframe"""
        files_list = os.listdir(self.filepath)
        combined_df = pd.DataFrame()
        for file_name in files_list:
            file_path = os.path.join(self.filepath, file_name)
            if file_path.lower().endswith('.pdf'):
                df = self.run_all(file_path)
            # Append the current DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        combined_df['Month'] = combined_df['Date'].dt.month
        combined_df['Year'] = combined_df['Date'].dt.year

        # Define the strings you want to filter
        with open('strings_to_filter.csv', 'r') as strings:
            csv_reader = csv.reader(strings)
            list_of_rows = list(csv_reader)
        strings_to_filter = [item for sublist in list_of_rows for item in sublist]

        # Heat map plot
        filtered_df =  combined_df[~combined_df['Description'].str.contains('|'.join(strings_to_filter), case=False) & (combined_df['Amount'] < 0)]
        return filtered_df

    def generate_plots(self, filtered_df):
        """Generate plots"""
        monthly_spending = filtered_df.pivot_table(values='Amount', index='Month', columns='Year', aggfunc='sum')
        plt.figure(figsize=(12, 6))
        sns.heatmap(monthly_spending, annot=True, fmt=".2f", linewidths=.5)
        plt.title('Monthly Spending Heatmap')
        plt.savefig('output_images/bank_spending_heat_map.png')
        plt.close()

        # Save df to csv
        filtered_df.to_csv('output_data/bank_data.csv', index=False, encoding='utf-8')

        # Monthly plot
        monthly_summary = filtered_df.resample('ME', on='Date')['Amount'].sum()
        monthly_summary.plot(title='Monthly Spending Trend', marker='o')
        plt.xlabel('Month')
        plt.ylabel('Total Amount Spent')
        plt.grid()
        plt.savefig('output_images/bank_spending_over_time.png')
        plt.close()

        # Group spending by description and sum the costs
        category_spending = filtered_df.groupby('Description')['Amount'].sum()
        category_spending = category_spending.abs()
        sorted_category_spending = category_spending.sort_values(ascending=True)
        category_spending.to_csv('output_data/category_spending.csv', index=True, encoding='utf-8')

        # Create the bar plot with horizontal bars
        plt.figure(figsize=(10, 30))
        bars = plt.barh(sorted_category_spending.index, sorted_category_spending, color='blue', edgecolor='black')
        # Add data labels to each bar
        for bar in bars:
            plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2,
                    f'{bar.get_width():.0f}',
                    va='center', ha='left', fontsize=10, color='black')
        plt.xlabel('Spending')
        plt.ylabel('Categories', fontsize=8)
        plt.title('Category-wise Spending')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('output_images/bank_spending_bar_chart.png')
        plt.close()

bank_data = BankData()
filtered_df = bank_data.get_filtered_statements()
bank_data.generate_plots(filtered_df)
