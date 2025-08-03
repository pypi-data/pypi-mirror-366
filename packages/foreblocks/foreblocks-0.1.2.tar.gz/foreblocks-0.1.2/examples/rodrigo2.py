import os
import sys

total_epochs = 500


# create scheduled_sampling_fn for teacher forcing
def scheduled_sampling_fn(epoch):
    tf_ratio = max(0.0, 0.8 - (epoch / total_epochs))
    return tf_ratio


# Get the current working directory of the notebook
notebook_dir = os.getcwd()

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(notebook_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# # # # read df_demmand_without_category_2025_05_13.csv
# import pandas as pd

# df = pd.read_csv('df_demmand_without_category_2025_05_13.csv')


# read df_demmand_without_category_2025_05_13.csv
import pandas as pd

df = pd.read_csv("df_demmand_without_category_2025_05_13.csv")

# import itemrplot
import itermplot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from foreblocks.preprocessing import TimeSeriesPreprocessor

# Generate synthetic time series data
np.random.seed(42)
n_samples = 200
timestamps = df.date

# convert df to numpy
data = df.drop(columns=["date"]).values
# Create preprocessor with various techniques enabled
preprocessor = TimeSeriesPreprocessor(
    normalize=True,
    differencing=False,
    detrend=True,
    apply_ewt=True,
    window_size=24,
    horizon=12,
    remove_outliers=True,
    outlier_threshold=2.5,
    outlier_method="iqr",
    impute_method="iterative",
    ewt_bands=5,
    trend_imf_idx=0,
    log_transform=False,
    filter_window=5,
    filter_polyorder=2,
    apply_filter=True,
    self_tune=True,
    apply_imputation=True,
    generate_time_features=True,
)

# Fit and transform the data
X, y, processed_data, time_feats = preprocessor.fit_transform(
    data, time_stamps=timestamps
)

# Visualize the results
plt.figure(figsize=(15, 10))

plt.subplot(3, 1, 1)
plt.title("Original Data with Outliers and Missing Values")
plt.plot(data)

plt.subplot(3, 1, 2)
plt.title("Processed Data")
print("Processed data shape:", processed_data.shape)
plt.plot(processed_data)

plt.subplot(3, 1, 3)
plt.title("EWT Components")
ewt_components = preprocessor.get_ewt_components()
if ewt_components:
    for i, imf in enumerate(ewt_components[0].T):
        plt.plot(imf, label=f"IMF {i}")
    plt.legend()

plt.tight_layout()
plt.show()

print(f"Input sequence shape: {X.shape}")
print(f"Target sequence shape: {y.shape}")
