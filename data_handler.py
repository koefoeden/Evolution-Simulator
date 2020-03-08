import pandas as pd
import os


class Analyzer:
    def __init__(self, data_file):
        # read data
        self.df = pd.read_csv(data_file)

        #determine groupings
        self.group_by_list = list(self.df)
        self.group_by_list.remove('avg_speed_mouse')

        #make group object
        self.df_grouped = self.df.groupby(self.group_by_list)

        self.df_average_speed = self.df_grouped['avg_speed_mouse'].mean()
        self.df_non_na_count = self.df_grouped['avg_speed_mouse'].count().reset_index(name='non_NA_count')
        #self.df_grouped['full_count'] =
        missing_values = self.df_grouped.apply(lambda x: x.count(), axis=1)
        print(missing_values)

        self.df_na_count = self.get_na_count()

        self.df_merged = pd.merge(self.df_average_speed, self.df_non_na_count, on=self.group_by_list)
        self.df_final = pd.merge(self.df_merged, self.df_na_count, on=self.group_by_list)
        #self.df_final2 = self.df_final.transform()

        self.df_average_speed.to_csv("results/avg_speed_groups.csv")
        self.df_na_count.to_csv("results/NA_count.csv")
        self.df_non_na_count.to_csv("results/non_NA_count.csv")
        self.df_merged.to_csv('results/merged.csv')
        self.df_final.to_csv('results/final.csv', index=False)

    def get_na_count(self):
        group_by_dataframe_list = [self.df[elm] for elm in self.group_by_list]
        df2 = self.df.avg_speed_mouse.isnull().groupby(group_by_dataframe_list).sum().astype(int).reset_index(name='NA_count')
        return df2

if __name__ == "__main__":
    analyzer = Analyzer("results/data_new_analysis.csv")