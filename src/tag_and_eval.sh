#!/bin/bash
# tag
python3 src/tag_all.py \
    --input-dir data/datasets/ner_medieval_multilingual/FR/ \
    --output-dir output/ner_medieval_multilingual/FR/ \
    --dictionary-size 10 # see --dictionary-sizes parameter of src/sentence_split.py to create additional dictionaries
# eval
python3 src/eval_all.py \
    --true-dir "data/datasets/ner_medieval_multilingual/FR/" \
    --pred-dir "output/ner_medieval_multilingual/FR/" \
    --results-dir "results/ner_medieval_multilingual/FR/" 
