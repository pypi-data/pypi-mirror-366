import os
from tqdm.auto import tqdm, trange
import pandas as pd
import argparse
import pathlib
from esm import Alphabet, FastaBatchedDataset, ProteinBertModel, pretrained, MSATransformer
import pickle
import matplotlib.pyplot as plt
import argparse
import tempfile
import shutil
from contextlib import nullcontext
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
with getattr(torch.serialization, "add_safe_globals", nullcontext):
    torch.serialization.add_safe_globals([argparse.Namespace])

# step 1
def to_fasta(from_csv_path, to_fasta_path):
    df = pd.read_csv(from_csv_path)
    seq_list = df['Sequence'].tolist()
    number = len(seq_list) + 1
    name = [i for i in range(1, number)]

    with open(to_fasta_path, 'w') as fasta_file:
        for i in name:
            fasta_lines = '>' + str(i)
            seq_lines = seq_list[i - 1]
            fasta_file.write(fasta_lines + '\n' + seq_lines + '\n')

# step 2
def get_embedding(model_location, fasta_file, output_dir, toks_per_batch=4096, truncation_seq_length=1022, include='mean', repr_layers=[-1]):
    assert os.path.exists(fasta_file)
    fasta_file = pathlib.Path(fasta_file)
    output_dir = pathlib.Path(output_dir)
    model, alphabet = pretrained.load_model_and_alphabet(model_location)
    model.eval()
    if isinstance(model, MSATransformer):
        raise ValueError("This script currently does not handle models with MSA input (MSA Transformer).")
    if torch.cuda.is_available():
        model = model.cuda()
        print("Transferred model to GPU")

    dataset = FastaBatchedDataset.from_file(fasta_file)
    batches = dataset.get_batch_indices(toks_per_batch, extra_toks_per_seq=1)
    data_loader = torch.utils.data.DataLoader(dataset, collate_fn=alphabet.get_batch_converter(truncation_seq_length), batch_sampler=batches)
    print(f"Read {fasta_file} with {len(dataset)} sequences")

    output_dir.mkdir(parents=True, exist_ok=True)
    return_contacts = "contacts" in include

    assert all(-(model.num_layers + 1) <= i <= model.num_layers for i in repr_layers)
    repr_layers = [(i + model.num_layers + 1) % (model.num_layers + 1) for i in repr_layers]

    with torch.no_grad():
        for batch_idx, (labels, strs, toks) in enumerate(data_loader):
            print(f"Processing {batch_idx + 1} of {len(batches)} batches ({toks.size(0)} sequences)")
            if torch.cuda.is_available():
                toks = toks.to(device="cuda", non_blocking=True)

            out = model(toks, repr_layers=repr_layers, return_contacts=return_contacts)

            logits = out["logits"].to(device="cpu")
            representations = {layer: t.to(device="cpu") for layer, t in out["representations"].items()}
            if return_contacts:
                contacts = out["contacts"].to(device="cpu")

            for i, label in enumerate(labels):
                output_file = output_dir / f"{label}.pt"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                result = {"label": label}
                truncate_len = min(truncation_seq_length, len(strs[i]))
                if "per_tok" in include:
                    result["representations"] = {layer: t[i, 1 : truncate_len + 1].clone() for layer, t in representations.items()}
                if "mean" in include:
                    result["mean_representations"] = {layer: t[i, 1 : truncate_len + 1].mean(0).clone() for layer, t in representations.items()}
                if "bos" in include:
                    result["bos_representations"] = {layer: t[i, 0].clone() for layer, t in representations.items()}
                if return_contacts:
                    result["contacts"] = contacts[i, : truncate_len, : truncate_len].clone()

                torch.save(result, output_file)

# step 3

def _safe_torch_load(path, **kw):
    ctx = getattr(torch.serialization, "safe_globals", nullcontext)([argparse.Namespace])
    with ctx:
        return torch.load(path, **kw)

def load_embeding(from_folder_path, from_csv_path, to_device):
    folder_path = from_folder_path
    csv_file_path = from_csv_path
    device = torch.device('cuda' if torch.cuda.is_available() and to_device == 'cuda' else 'cpu')
    print(f"Running on {device}")

    file_names = sorted([f for f in os.listdir(folder_path) if f.endswith('.pt')], key=lambda x: int(x.split('.')[0]))
    mean_representations_list = []

    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        # mean_representation = torch.load(file_path,  map_location=device, weights_only=True)['mean_representations'][36].numpy().tolist()
        loaded = _safe_torch_load(file_path, map_location="cpu", weights_only=True)
        tensor36 = loaded["mean_representations"][36]          
        mean_representation = tensor36.numpy().tolist()
        mean_representations_list.append(mean_representation)

    mean_representations_df = pd.DataFrame(mean_representations_list)
    additional_data_df = pd.read_csv(csv_file_path)

    if len(mean_representations_df) != len(additional_data_df):
        raise ValueError("The number of rows in the additional data CSV does not match the number of .pt files")

    final_df = pd.concat([additional_data_df['Sequence'], mean_representations_df], axis=1)
    return final_df

# step 4
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_rate)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h_0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        c_0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h_0, c_0))
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out

def get_predicted_mic_csv(new_data, from_csv_path, scaler_data_path, model_path, result_path, to_device):
    device = torch.device('cuda' if torch.cuda.is_available() and to_device == 'cuda' else 'cpu')
    print(f"Running on {device}")

    X_new = new_data.iloc[:, 1:].values
    with open(scaler_data_path, 'rb') as f:
        scaler = pickle.load(f)
    X_new = scaler.transform(X_new)

    X_new = torch.tensor(X_new, dtype=torch.float32)

    new_dataset = TensorDataset(X_new.unsqueeze(1))
    new_loader = DataLoader(new_dataset, batch_size=64, shuffle=False)

    model = LSTMModel(input_size=X_new.size(1), hidden_size=128, num_layers=2, output_size=1, dropout_rate=0.7).to(device)
    model_state_dict = _safe_torch_load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(model_state_dict)
    model.eval()

    new_predictions = []
    with torch.no_grad():
        for X_batch in new_loader:
            X_batch = X_batch[0].to(device)
            outputs = model(X_batch)
            new_predictions.extend(outputs.squeeze().cpu().numpy())

    new_predictions = pd.DataFrame(new_predictions, columns=['Predicted Values'])
    df_info  = pd.read_csv(from_csv_path)
    df_merged = pd.concat([df_info, new_predictions], axis=1)
     # df_merged.to_csv(result_path, index=False)

    return df_merged





def get_predicted_mic(sequences: list[str],model_location: str,scaler_path: str,lstm_model_path: str,
                          device: str = 'cuda',batch_size: int = 1,truncation_seq_length: int = 1022,
                          include: str = 'mean', repr_layers: list = [-1]):
    tmp = tempfile.mkdtemp()
    fasta = os.path.join(tmp, "input.fasta")
    with open(fasta, 'w') as f:
        for idx, seq in enumerate(sequences, start=1):
            f.write(f">{idx}\n{seq}\n")

    try:
        tqdm.write("Generating embeddings with ESM model...")
        get_embedding(model_location=model_location,fasta_file=fasta,output_dir=tmp,toks_per_batch=4096,
            truncation_seq_length=truncation_seq_length,include=include,repr_layers=repr_layers)
        
        tqdm.write("Writing temporary CSV for feature loader...")
        tmp_csv = os.path.join(tmp, "seq.csv")
        pd.DataFrame({"Sequence": sequences}).to_csv(tmp_csv, index=False)
        
        tqdm.write("Loading embeddings into feature DataFrame...")
        feature_df = load_embeding(from_folder_path=tmp,from_csv_path=tmp_csv,to_device=device)

        X = feature_df.iloc[:, 1:].values
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        X_scaled = scaler.transform(X)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(device)
        ds = TensorDataset(X_tensor.unsqueeze(1))
        loader = DataLoader(ds, batch_size=batch_size, shuffle=False)

        tqdm.write("Loading LSTM regression model...")
        lstm = LSTMModel(input_size=X_scaled.shape[1],hidden_size=128, num_layers=2,output_size=1, dropout_rate=0.7).to(device)
        state = _safe_torch_load(lstm_model_path, map_location=device, weights_only=True)
        lstm.load_state_dict(state)
        lstm.eval()

        preds = []
        tqdm.write("Predicting MIC values...")
        for (xb,) in tqdm(loader, desc="LSTM Batches", unit="batch"):
            xb = xb.to(device)
            with torch.no_grad():
                out = lstm(xb)                 
            batch_vals = out.squeeze(-1).cpu().tolist()
            if isinstance(batch_vals, float):
                preds.append(batch_vals)
            else:
                preds.extend(batch_vals)

        return pd.DataFrame({"Sequence": sequences,"Predicted Values": preds})

    finally:
        shutil.rmtree(tmp)

if __name__ == '__main__':
    pass
    
    
    
    
    
    
