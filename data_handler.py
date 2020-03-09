import pandas as pd
import os


class Analyzer:
    def __init__(self, data_file):
        # read data
        self.df = pd.read_csv(data_file)

        # determine groupings
        self.column_list = list(self.df)
        self.remove_list = ['avg_speed_mouse', 'avg_speed_owl']
        self.group_by_list = [x for x in self.column_list if x not in self.remove_list]

        # make group object
        self.df_config_groups = self.df.groupby(self.group_by_list)

        # Get average speed, and non-NA and full count within each group.
        self.df_average_speeds = self.df_config_groups[['avg_speed_mouse', 'avg_speed_owl']].mean()
        self.df_non_na_count_mice = self.df_config_groups['avg_speed_mouse'].count().reset_index(name='non_NA_count_mice')
        self.df_non_na_count_owls = self.df_config_groups['avg_speed_owl'].count().reset_index(name='non_NA_count_owls')

        self.df_full_count = self.df_config_groups['avg_speed_mouse'].size().reset_index(name='repetitions')

        # merge columns and calculate NA-fraction
        self.df_merged = pd.merge(self.df_average_speeds, self.df_non_na_count_mice, on=self.group_by_list)
        self.df_merged2 = pd.merge(self.df_merged, self.df_non_na_count_owls, on=self.group_by_list)

        self.df_final = pd.merge(self.df_merged2, self.df_full_count, on=self.group_by_list)
        self.df_final['NA_fraction_mice'] = 1 - (self.df_final['non_NA_count_mice']/self.df_final['repetitions'])
        self.df_final['NA_fracion_owls'] = 1 - (self.df_final['non_NA_count_owls']/self.df_final['repetitions'])

        self.df_final_rounded = self.df_final.round(2)

        # print to csv
        self.df_final_rounded.to_csv('results/final.csv', index=False)


if __name__ == "__main__":
    analyzer = Analyzer("results/data_new_analysis.csv")
