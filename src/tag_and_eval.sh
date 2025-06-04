#!/bin/bash
# tag using ditionaries exported in during preprocess.sh
python3 src/tag_all.py \
    --input-dir data/data_raw/ner_medieval_multilingual/FR/ \
    --output-dir output/ner_medieval_multilingual/FR/ \
# eval
python3 src/eval_all.py \
    --true-dir "data/data_raw/ner_medieval_multilingual/FR/" \
    --pred-dir "output/ner_medieval_multilingual/FR/" \
    --results-dir "results/ner_medieval_multilingual/FR/" \
    --n 1
