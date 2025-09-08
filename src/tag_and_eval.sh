#!/bin/bash
# tag using ditionaries exported in during preprocess.sh
# script for supervised case - full dictionaries
for dict_size in 10 20 40 60 80 100
do
    dict_size_lab=`python3 -c "print(f'{${dict_size}/100:.2f}')"`
    python3 src/tag_all.py \
        --input-dir "data/distant-${dict_size_lab}/ner_medieval_multilingual/FR/" \
        --output-dir "output/distant-${dict_size_lab}/ner_medieval_multilingual/FR/"
    # eval
    python3 src/eval_all.py \
        --true-dir "data/supervised/ner_medieval_multilingual/FR/" \
        --pred-dir "output/distant-${dict_size_lab}/ner_medieval_multilingual/FR/" \
        --results-dir "results/distant-${dict_size_lab}/ner_medieval_multilingual/FR/distant-${dict_size_lab}-" \
        --n 1
done

for split in val test
do
    find results/ -name MULTICLASS -exec echo "{}/$split.json" ';' | python3 src/eval_summary.py --output "results/hdsner_report_${split}.json" "--dataset-pos=-3"
done
