"""
	1.	Function Definition: The core logic is wrapped in a function generate_unconditional_sequences that takes total_sequences, batch_size, and output_file as arguments.
	2.	Command-Line Interface: The script uses argparse to handle command-line arguments, making it easy to run from the command line.
	3.	File Writing: The function saves the generated sequences to a CSV file specified by the user.
"""

import random
import csv

from evodiff.generate import generate_oaardm
from evodiff.pretrained import OA_DM_640M,OA_DM_38M, MSA_OA_DM_MAXSUB
import os
from evodiff.utils import Tokenizer, download_model
from evodiff.collaters import D3PMCollater, OAMaskCollater, ESMOAMaskCollater, D3PMCollaterMSA, ESMOAMaskCollaterMSA
from typing import Dict, List, Any
from evodiff.generate_msa import generate_msa
import os
import random
import re
import pandas as pd
from evodiff.generate_msa import generate_query_oadm_msa_simple


def generate_unconditional_sequences(
    total_sequences: int,
    model_name="OA_DM_38M", 
    batch_size=1,
    to_device: str = 'cuda'
) -> List[Dict[str, Any]]:
    """
    total_sequences: (int) The total number of sequences you want to generate.
    batch_size: (int) The batch size for sequence generation.
    model_name: (str) The name of the model to use for sequence generation.
    to_device: (str) Device to run the model, cuda or cpu.
    """
    loader_map = {"OA_DM_38M": OA_DM_38M, "OA_DM_640M": OA_DM_640M}
    checkpoint_loader = loader_map[model_name]
    checkpoint = checkpoint_loader()
    model, collater, tokenizer, scheme = checkpoint
    model.to(to_device)

    sequences_data: List[Dict[str, Any]] = []
    seq_id = 0
    while seq_id < total_sequences:
        seq_len = random.randint(15, 35)
        _, gen_seqs = generate_oaardm(
            model, tokenizer, seq_len,
            batch_size=batch_size, device=to_device
        )
        for s in gen_seqs:
            sequences_data.append({"ID": seq_id, "Sequence": s})
            seq_id += 1
            if seq_id >= total_sequences:
                break
    return sequences_data

def generate_unconditional_msa_sequences(
    total_sequences: int,
    model_name='MSA_OA_DM_MAXSUB',
    batch_size=1,  
    n_sequences=16,
    to_device: str = 'cuda'
) -> List[Dict[str, Any]]:

    """
    Generates AMP sequences using EvoDiff Unconditional Generation with MSA_OA_DM_MAXSUB and saves them to a CSV file.

    Args:
        total_sequences (int): Total number of sequences to generate.
        batch_size (int): Batch size for sequence generation.
        n_sequences (int): Number of sequences to generate in each batch.
        output_csv_file (str): Path to the output CSV file.
        to_device: (str) Device to run the model, cuda or cpu.
    """
    loader_map = {"MSA_OA_DM_MAXSUB": MSA_OA_DM_MAXSUB}
    checkpoint_loader = loader_map[model_name]
    checkpoint = checkpoint_loader()
    model, collater, tokenizer, scheme = checkpoint
    model.to(to_device)
    
    sequences_data = []
    sequence_id_counter = 0

    for _ in range(total_sequences):
        seq_len = random.randint(15, 35)  # Randomly choose a length between 15 and 35
        _, untokenized = generate_msa(model, tokenizer, batch_size=batch_size, n_sequences=n_sequences, seq_length=seq_len, penalty_value=1, device=to_device,
                                      start_query=False, start_msa=False, data_top_dir='../data', selection_type='MaxHamming', out_path='../ref/')
        for generated_sequence in untokenized:
            seq_tem = str(generated_sequence)
            seq_tem = seq_tem[3:seq_len + 3]
            seq_tem = seq_tem[:-1]

            # Store each sequence's data in a dictionary
            sequence_data = {
                "ID": sequence_id_counter,
                "Sequence": seq_tem
            }
            sequences_data.append(sequence_data)
            sequence_id_counter += 1
            

            # Break if total sequences reached
            if sequence_id_counter >= total_sequences:
                break
        # Break the outer loop as well when total sequences reached
        if sequence_id_counter >= total_sequences:
            break
    return sequences_data

def generate_conditional_msa_sequences(
    directory_path: str,
    total_sequences: int,
    model_name='MSA_OA_DM_MAXSUB',
    max_retries=5,  
    n_sequences=16,
    to_device: str = 'cuda'
) -> List[Dict[str, Any]]:
    """
    Generates AMP sequences using EvoDiff Conditional Generation with MSA_OA_DM_MAXSUB and saves the results to a CSV file.

    Args:
        directory_path (str): Path to the directory containing MSA files.
        output_csv_file (str): Path to the output CSV file.
        max_retries (int): Maximum number of retries for each file (default: 5).
        to_device: (str) Device to run the model, cuda or cpu.
        total_sequences: (int) The total number of sequences you want to generate.
    """
    loader_map = {"MSA_OA_DM_MAXSUB": MSA_OA_DM_MAXSUB}
    checkpoint_loader = loader_map[model_name]
    checkpoint = checkpoint_loader()
    model, collater, tokenizer, scheme = checkpoint
    model.to(to_device)
    
    output_data = []

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".a3m"):
            path_to_msa = os.path.join(directory_path, filename)
            
            # Read the file to determine the number of sequences
            with open(path_to_msa, 'r') as file:
                sequences = [line.strip() for line in file if line.startswith(">")]
                n_sequences = len(sequences) - 1
                if n_sequences > 64:
                    n_sequences = 64
            
            # Read the first sequence (reference sequence)
            with open(path_to_msa, 'r') as file:
                msa_content = file.read()
                reference_sequence = re.search(r"^>[^\n]*\n([^>]*)", msa_content, re.MULTILINE).group(1).replace('\n', '')
                reference_length = len(reference_sequence.replace('-', ''))  # Remove gaps and get length

            # Run the model 5 times with random seq_length each time
            for _ in range(total_sequences):
                retries = 0
                while retries < max_retries:
                    try:
                        seq_length = random.randint(15, 35)
                        selection_type = 'MaxHamming'  # or 'random'; MSA subsampling scheme
                        
                        # Running the model
                        tokenized_sample, generated_sequence = generate_query_oadm_msa_simple(
                            path_to_msa, model, tokenizer, n_sequences, seq_length, device=to_device, selection_type=selection_type)
                        
                        clean_generated_sequence = re.sub('[!-]', '', generated_sequence[0][0])
                        generated_length = len(clean_generated_sequence)

                        output_data.append([filename, n_sequences, reference_sequence, reference_length, clean_generated_sequence, generated_length])
                        break  # Break out of the retry loop if successful
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        retries += 1
                        if retries == max_retries:
                            print(f"Failed to process {filename} after {max_retries} retries.")
                        else:
                            print(f"Retrying {filename} ({retries}/{max_retries})...")

    return output_data# Return only the 5th element of output_data



if __name__ == "__main__":
    pass


    



    
