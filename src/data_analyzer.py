class Analyzer:

    def get_filtered_grouped_results(self):
        df = self.grouped_dataframe
        filtered_df = df.loc[df['NA_fraction_owls'] < 0.5]
        return filtered_df

if __name__=='__main__':
    analyzer = Analyzer()
    analyzer.get_filtered_grouped_results().to_csv('../results/filtered.csv', index=False)