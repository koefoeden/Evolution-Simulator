import pandas as pd
import matplotlib.pyplot as plt

class Analyzer:
    def __init__(self, grouped_results_name):
        self.grouped_results = grouped_results_name
        self.df = pd.read_csv(self.grouped_results)
        self.decide_optimal_parameters()
        self.df_filtered = self.make_filtered_grouped_results()
        self.make_plots()

    def decide_optimal_parameters(self):
        self.df["harmonic_mean"] = 2*(self.df["non_NA_fraction_owls"]*self.df["non_NA_fraction_mice"])/(self.df["non_NA_fraction_owls"]+self.df["non_NA_fraction_mice"])
        sorted_df = self.df.sort_values(by="harmonic_mean", ascending=False)
        #filtered_df = sorted_df[sorted_df["harmonic_mean" ]]
        sorted_df.to_csv("../results/sorted.csv")

    def make_filtered_grouped_results(self):
        filtered_owls_df = self.df.loc[self.df['non_NA_fraction_owls'] > 0.75]
        filtered_total_df = filtered_owls_df.loc[filtered_owls_df['non_NA_fraction_mice'] > 0.75]
        filtered_total_df.to_csv('../results/filtered.csv', index=False)
        return filtered_total_df




    def make_plots(self):
        df_single_config = self.df[(self.df["m_die_of_hunger"]==3) & (self.df["m_preg_time"]==2)]
        df_single_config.plot.scatter(x="rand_variance_trait", y="avg_speed_mouse")
        plt.savefig("../results/plots/my_plot.pdf")


if __name__=='__main__':
    analyzer = Analyzer("../results/grouped_results.csv")