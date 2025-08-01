import numpy as np
from pkg_resources import resource_filename

data_folder = resource_filename(__name__, "/data/")
test_data_file = data_folder + "test_data.csv"

# Load Fits and Groups
named_Groups = np.load(data_folder + "original_Dodd23_Groups.npy")
group_mean = np.load(data_folder + "original_Dodd23_Group_Mean_ELzLp.npy")
group_covar = np.load(data_folder + "original_Dodd23_Group_Covar_ELzLp.npy")
g_name_to_index = {g: ind for (ind, g) in enumerate(named_Groups)}
