import pandas as pd
import matplotlib.pyplot as plt

class Analyzer:
    def __init__(self, grouped_results_name):
        self.grouped_results = grouped_results_name
        self.make_filtered_grouped_results()


    def make_filtered_grouped_results(self):
        df = pd.read_csv(self.grouped_results)
        filtered_owls_df = df.loc[df['NA_fraction_owls'] < 0.25]
        filtered_total_df = filtered_owls_df.loc[filtered_owls_df['NA_fraction_mice'] < 0.25]
        filtered_total_df.to_csv('../results/filtered.csv', index=False)

    def make_plots(self):



if __name__=='__main__':
    analyzer = Analyzer("../results/grouped_results.csv")