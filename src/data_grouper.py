import pandas as pd


class Grouper:
    def __init__(self, data_file):
        # read data
        self.df_results = pd.read_csv(data_file)
        self.df_grouped_results = self.make_grouped_results()
        self.df_grouped_results.to_csv('../results/grouped_results.csv', index=False)

    def make_grouped_results(self):
        # determine groupings
        column_list = list(self.df_results)
        remove_list = ['avg_speed_mouse', 'avg_speed_owl']
        group_by_list = [x for x in column_list if x not in remove_list]

        # make group object
        df_config_groups = self.df_results.groupby(group_by_list)

        """
        # Get average speed, and non-NA and full count within each group.
        #self.df_results[['avg_speed_mouse', 'avg_speed_owl']] = df_config_groups[['avg_speed_mouse', 'avg_speed_owl']].mean()
        #self.df_results['non_NA_count_mice'] = df_config_groups['avg_speed_mouse'].count()
        #self.df_results['non_NA_count_owls'] = df_config_groups['avg_speed_owl'].count()
        #self.df_results['repetitions'] = df_config_groups['avg_speed_mouse'].size()

        #self.df_results['non_NA_fraction_mice'] = self.df_results['non_NA_count_mice'] / self.df_results['repetitions']
        #self.df_results['non_NA_fraction_owls'] = self.df_results['non_NA_count_owls'] / self.df_results['repetitions']

        #df_final_rounded = self.df_results.round(2)
        """

        # Get average speed, and non-NA and full count within each group.
        df_average_speeds = df_config_groups[['avg_speed_mouse', 'avg_speed_owl']].mean()
        df_non_na_count_mice = df_config_groups['avg_speed_mouse'].count().reset_index(name='non_NA_count_mice')
        df_non_na_count_owls = df_config_groups['avg_speed_owl'].count().reset_index(name='non_NA_count_owls')

        df_full_count = df_config_groups['avg_speed_mouse'].size().reset_index(name='repetitions')

        # merge columns and calculate NA-fraction
        df_merged = pd.merge(df_average_speeds, df_non_na_count_mice, on=group_by_list)
        df_merged2 = pd.merge(df_merged, df_non_na_count_owls, on=group_by_list)

        df_final = pd.merge(df_merged2, df_full_count, on=group_by_list)
        df_final['non_NA_fraction_mice'] = df_final['non_NA_count_mice']/df_final['repetitions']
        df_final['non_NA_fraction_owls'] = df_final['non_NA_count_owls']/df_final['repetitions']

        df_final_rounded = df_final.round(2)


        return df_final_rounded


if __name__ == "__main__":
    grouper = Grouper("../results/automatic_testing.csv")


