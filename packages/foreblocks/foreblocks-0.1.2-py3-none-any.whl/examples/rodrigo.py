import os
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn

# Get the current working directory of the notebook
notebook_dir = os.getcwd()

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(notebook_dir, "."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from torch.jit import script
from torch.utils.data import DataLoader, TensorDataset

from foreblocks import ForecastingModel, LSTMDecoder, LSTMEncoder, Trainer
from foreblocks.att import AttentionLayer
from foreblocks.blocks import GRU
from foreblocks.blocks.fourier import FNO1DLayer, FourierFeatures
from foreblocks.blocks.graph import LatentGraphNetwork
from foreblocks.tf.embeddings import LearnablePositionalEncoding
from foreblocks.tf.transformer import TransformerDecoder, TransformerEncoder

# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%

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


# df = pd.read_csv('df_demmand_without_category_2025_05_13.csv')


# %%

# # read df_demmand_without_category_2025_05_13.csv
# import pandas as pd
# df = pd.read_csv('df_demmand_without_category_2025_05_13.csv')
# from foreblocks import TimeSeriesPreprocessor

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt


# # Generate synthetic time series data
# np.random.seed(42)
# n_samples = 200
# timestamps = df.date

# # convert df to numpy
# data = df.drop(columns=['date']).values
# # Create preprocessor with various techniques enabled
# preprocessor = TimeSeriesPreprocessor(
#     normalize=True,
#     differencing=False,
#     detrend=True,
#     apply_ewt=True,
#     window_size=24,
#     horizon=12,
#     remove_outliers=True,
#     outlier_threshold=2.5,
#     outlier_method="iqr",
#     impute_method="iterative",
#     ewt_bands=5,
#     trend_imf_idx=0,
#     log_transform=False,
#     filter_window=5,
#     filter_polyorder=2,
#     apply_filter=True,
#     self_tune=True,
#     apply_imputation=True,
#     generate_time_features=False,
# )

# # Fit and transform the data
# X, y, processed_data = preprocessor.fit_transform(data, time_stamps=timestamps)

# # Visualize the results
# plt.figure(figsize=(15, 10))

# plt.subplot(3, 1, 1)
# plt.title('Original Data with Outliers and Missing Values')
# plt.plot(data)

# plt.subplot(3, 1, 2)
# plt.title('Processed Data')
# print("Processed data shape:", processed_data.shape)
# plt.plot(processed_data)

# plt.subplot(3, 1, 3)
# plt.title('EWT Components')
# ewt_components = preprocessor.get_ewt_components()
# if ewt_components:
#     for i, imf in enumerate(ewt_components[0].T):
#         plt.plot(imf, label=f'IMF {i}')
#     plt.legend()

# plt.tight_layout()
# plt.show()

# print(f"Input sequence shape: {X.shape}")
# print(f"Target sequence shape: {y.shape}")

# %%
# # load the processed data
# # save X and y to pickle
# import pickle
# with open('X.pkl', 'wb') as f:
#     pickle.dump(X, f)
# with open('y.pkl', 'wb') as f:
#     pickle.dump(y, f)

# %%

# load X and y from pickle
with open("examples/X.pkl", "rb") as f:
    X = pickle.load(f)
with open("examples/y.pkl", "rb") as f:
    y = pickle.load(f)
with open("examples/time.pkl", "rb") as f:
    time_feat = pickle.load(f)

# %%


# Parameters
input_size = X.shape[2]  # Number of features
hidden_size = 64
num_layers = 2
output_size = X.shape[2]  # Number of features
target_len = 12
seq_len = 24
total_len = 300  # Total synthetic time series length


# fourier_preprocessor = LatentCorrelationGraphLayer(
#     #conv_type='sgconv',
#     input_size=input_size,          # Input dimension
#     output_size=hidden_size,        # Output dimension (same as hidden_size)
# )
preprocessor = LatentGraphNetwork(
    input_size=input_size,
    output_size=input_size,
    hidden_size=input_size,
    strategy="vanilla",
    aggregation="mean",
)

# preprocessor = FourierFeatures(
#     input_size=input_size,
#     output_size=input_size,
#     num_frequencies=8,
# )
# 1. Create encoder and decoder
# encoder = LSTMEncoder(input_size, hidden_size, num_layers)
# decoder = LSTMDecoder(output_size, hidden_size, output_size, num_layers)

model_params = {
    "input_processor_output_size": input_size,
    "hidden_size": 64,
    "nhead": 4,
    "num_encoder_layers": 1,
    "num_decoder_layers": 1,
    "dropout": 0.1,
    "dim_feedforward": 2048,
    "seq_len": 24,
    "target_len": 12,
    "total_len": 1000,
    "input_size": input_size,
    "output_size": output_size,
}

from foreblocks.third_party.flash_softpick_attn import parallel_softpick_attn


def warmup_softpick(device, d_model=512, n_heads=4, seq_len=16):
    q = torch.randn(
        1, seq_len, n_heads, d_model // n_heads, device=device, dtype=torch.float16
    )
    k = q.clone()
    v = q.clone()
    _ = parallel_softpick_attn(q, k, v, head_first=False)


from foreblocks.blocks.nha import NHA

embedding_size = 12  # Size of the output embeddings
# 1. Create the NHA input preprocessor
nha_preprocessor = NHA(
    input_dim=input_size,  # Input dimension
    embedding_dim=embedding_size,  # Output embedding dimension
    hidden_dim=12,  # Hidden dimension for processing
    num_blocks=2,  # Number of hierarchical blocks
    num_levels_per_block=3,  # Number of hierarchical levels per block
    kernel_size=3,  # Kernel size for convolutions
    attention_heads=4,  # Number of attention heads
    dropout=0.1,  # Dropout probability
)

from foreblocks.blocks.famous import TimesBlock, TimesBlockPreprocessor

times_wrapper = TimesBlockPreprocessor(d_model=input_size)
# warmup_softpick(device=torch.device("cuda"))

pos_encoder = LearnablePositionalEncoding(512)
pos_decoder = LearnablePositionalEncoding(512)

encoder = TransformerEncoder(
    input_size=model_params.get("input_processor_output_size", 1),
    nhead=model_params.get("nhead", 4),
    num_layers=model_params.get("num_encoder_layers", 1),
    dropout=model_params.get("dropout", 0.1),
    dim_feedforward=model_params.get("dim_feedforward", 2048),
    use_moe=True,
    pos_encoder=pos_encoder,
    att_type="autocor",
)

# Create transformer decoder
decoder = TransformerDecoder(
    input_size=model_params.get("input_processor_output_size", 1),
    output_size=output_size,
    nhead=model_params.get("nhead", 4),
    num_layers=model_params.get("num_decoder_layers", 1),
    dropout=model_params.get("dropout", 0.1),
    dim_feedforward=model_params.get("dim_feedforward", 2048),
    informer_like=True,
    use_moe=True,
    # att_type="prob_sparse",
    pos_encoder=pos_decoder,
)

# from foreblocks.blocks.mamba import MambaDecoder, MambaEncoder

# encoder = MambaEncoder(
#     input_size=input_size, hidden_size=hidden_size, num_layers=num_layers
# )
# decoder = MambaDecoder(
#     input_size=output_size,
#     hidden_size=hidden_size,
#     num_layers=num_layers,
#     output_size=output_size,
# )


# attention_module = AttentionLayer(
#     method="mha",
#     attention_backend="flash",
#     encoder_hidden_size=hidden_size,
#     decoder_hidden_size=hidden_size,
#     nhead=16,
# )

total_epochs = 500


# create scheduled_sampling_fn for teacher forcing
def scheduled_sampling_fn(epoch):
    # Use a linear decay from 1.0 to 0.0 over the epochs
    tf_ratio = max(0.0, 0.95 - (epoch / total_epochs))

    return tf_ratio


outprocessor = nn.Sequential(
    GRU(input_size=output_size, hidden_size=32, output_size=output_size),
)

print("Using timewrapper")
outnorm = nn.LayerNorm(output_size)
model = ForecastingModel(
    encoder=encoder,
    decoder=decoder,
    target_len=target_len,
    forecasting_strategy="seq2seq",
    model_type="informer-like",
    scheduled_sampling_fn=scheduled_sampling_fn,
    output_size=output_size,
    # attention_module=attention_module,
    input_preprocessor=times_wrapper,
    output_block=outprocessor,
    # output_normalization=outnorm,
    input_skip_connection=False,
)

# model = script(model)  # Convert to TorchScript for optimization
trainer = Trainer(
    model,
    optimizer=torch.optim.Adam(model.parameters(), lr=0.001),
    criterion=nn.MSELoss(),
)


train_size = int(0.8 * len(X))
X_train, Y_train = X[:train_size], y[:train_size]
X_val, Y_val = X[train_size:], y[train_size:]

X_train = torch.tensor(X_train, dtype=torch.float32)
Y_train = torch.tensor(Y_train, dtype=torch.float32)
Y_val = torch.tensor(Y_val, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)
time_train = torch.tensor(time_feat[:train_size], dtype=torch.float32)

# create DataLoader

train_dataset = TensorDataset(X_train, Y_train, time_train)
print(time_train.shape)
train_loader = DataLoader(train_dataset, batch_size=1024, shuffle=True)
data = trainer.train(train_loader, epochs=100)
metrics = trainer.metrics(X_val, Y_val)


# %%
X = torch.tensor(X, dtype=torch.float32)
fig = trainer.plot_prediction(X_val, Y_val, full_series=X, offset=train_size)


# %%
