import pandas as pd


def collapse_data(filename):
    group_by = "dimensions,rock_chance,grass_grow_back,rand_catch,in_medias_res,number,die_of_hunger,preg_time,max_age,number,die_of_hunger,preg_time,max_age,rand_variance_trait,speed,slow_mode_sleep_time".split(sep=',')
    print(group_by)
    df = pd.read_csv(filename)
    df_group = df.groupby(group_by)['avg_speed_mouse'].aggregate(lambda x: sum(x)/len(x))#reset_index()
    #print(df_out.to_string())
    print(df_group)
"""
    new_df = pd.DataFrame(columns=['avg_speed_mouse', 'number_of_reps'])
    for name, group in df_group:
        group_average_speed = group['avg_speed_mouse'].mean()
        
        repetitions = group['number_of_reps'].sum()
        print(new_df)
        i+=1
"""
collapse_data("C:/Users/Thomas/PycharmProjects/Simulation/results.csv")
