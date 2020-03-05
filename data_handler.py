import pandas as pd

group_by_list = """dimensions
rock_chance
grass_grow_back
rand_catch
in_medias_res
number
die_of_hunger
preg_time
max_age
number
die_of_hunger
preg_time
max_age
rand_variance_trait
speed""".split(sep='\n')


class Analyzer:
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
        self.average_data()
        self.get_na_count()
        self.get_na_count()

    def average_data(self):
        df_group = self.df.groupby(group_by_list)['avg_speed_mouse'].mean()  # agg('sum')
        df_group.to_csv("avg_speed_groups.csv")

    def get_na_count(self):
        df2 = self.df.avg_speed_mouse.isnull().groupby([self.df['die_of_hunger'], self.df['preg_time']]).sum().astype(int).reset_index(name='count')
        df2.to_csv("NA_count.csv")

    def get_non_na_count(self):
        df_group = self.df.groupby(group_by_list)['avg_speed_mouse'].count()
        df_group.to_csv("non_NA_count.csv")


"""
    new_df = pd.DataFrame(columns=['avg_speed_mouse', 'number_of_reps'])
    for name, group in df_group:
        group_average_speed = group['avg_speed_mouse'].mean()
        
        repetitions = group['number_of_reps'].sum()
        print(new_df)
        i+=1
"""

if __name__ == "__main__":
    analyzer = Analyzer("results_data_analysis.csv")
    analyzer.get_na_count("results_data_analysis.csv")
    analyzer.get_non_na_count("results_data_analysis.csv")
    analyzer.average_data("results_data_analysis.csv")