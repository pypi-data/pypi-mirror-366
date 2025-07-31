#!/bin/bash
#SBATCH -p gpu
#SBATCH --mem=32g
#SBATCH --gres=gpu:rtx2080:1
#SBATCH -c 2
#SBATCH --output=example_1.out

source activate generative_structures

#mpnn part
folder_with_pdbs="/u/ilanm/ophiuchus/notebooks/samples/"
output_dir="/u/ilanm/ophiuchus/notebooks/output_mpnn"
if [ ! -d $output_dir ]
then
    mkdir -p $output_dir
fi

path_for_parsed_chains=$output_dir"/parsed_pdbs.jsonl"

python /u/ilanm/ProteinMPNN/helper_scripts/parse_multiple_chains.py --input_path=$folder_with_pdbs --output_path=$path_for_parsed_chains

python /u/ilanm/ProteinMPNN/protein_mpnn_run.py \
        --jsonl_path $path_for_parsed_chains \
        --out_folder $output_dir \
        --num_seq_per_target 2 \
        --sampling_temp "0.1" \
        --seed 37 \
        --batch_size 1


#omegafold
output_fold="/u/ilanm/ophiuchus/notebooks/output_fold/"
if [ ! -d $output_fold ]
then
    mkdir -p $output_fold
fi

for FILE in $output_dir/seqs/*; do omegafold $FILE $output_fold --device cuda:1; done
