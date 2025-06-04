#!/bin/bash
# langs="FR lat es"
langs="FR" # using only French
dataset_names=""CBMA_" "CDBE_" "CODCAR-" "CODEA-" "CORHEN-" "HOME-""

data_raw="data/data_raw"
datasets="data/datasets"
medner_raw="${data_raw}/ner_medieval_multilingual"
medner_ds="${datasets}/ner_medieval_multilingual"

mkdir -p "${medner_raw}/"
tab=$'\t'

# split datasets
for lang in ${langs}
do
    rm -rf "${medner_raw}/${lang}/"
    mkdir -p "${medner_raw}/${lang}/"
    for dataset in ${dataset_names}
    do
        mkdir "${medner_raw}/${lang}/${dataset%?}/"
        class=0
        for category in PERS LOC MULTICLASS
        do
            let class=class+1
            if [ "${category}" == "MULTICLASS" ]
            then
                class_a=1
                let class=class-1
            else
                class_a=${class}
            fi
            if [ "$dataset" == "HOME-" ]
            then
                dataset_grep="(Fervaques_|Navarre_|S_Denis_)"
            else
                dataset_grep="${dataset}"
            fi
            mkdir "${medner_raw}/${lang}/${dataset%?}/${category}"
            for split in train val test
            do
                # divide each split by language, original dataset (grep), and category, and then divide the sentences to respect a max sequence lenght when possible (sentence_split.py), and export dictionaries
                python3 src/sentence_split.py \
                    --input <(egrep -A 1 "${tab}${lang}${tab}${dataset_grep}" "${medner_raw}/${split}_set_all_17_03_2022.txt") \
                    --output-dir "${medner_raw}/${lang}/${dataset%?}/${category}"\
                    --split "${split}" \
                    --classes "${class_a},${class}"
                if [ ! -s "${medner_raw}/${lang}/${dataset%?}/${category}/train.txt" ]
                then
                    rm -rf "${medner_raw}/${lang}/${dataset%?}/${category}/"
                    break
                fi
            done
        done
    done
done
find ${medner_raw} -type d -empty -exec rmdir '{}' ';' 2> /dev/null

# build train splits with dictionary matching
rm -r "${medner_ds}"
mkdir -p "`dirname ${medner_ds}`"
cp -r "${medner_raw}" "${medner_ds}"

for lang in ${langs}
do
    for dataset in ${datasets}
    do
        if [ -f "${medner_raw}/${lang}/${dataset%?}/PERS/train.txt" ]
        then
            for category in PERS LOC
            do
                category_lower="`echo ${category} | tr '[A-Z]' '[a-z]'`"
                python3 src/tag.py \
                    --input "${medner_raw}/${lang}/${dataset%?}/${category}/train.txt" \
                    --output "${medner_ds}/${lang}/${dataset%?}/${category}/train.txt" \
                    --${category_lower}-dictionary "${medner_raw}/${lang}/${dataset%?}/${category}/dict.txt"
            done
            python3 src/merge_labels.py \
                --pers-input "${medner_ds}/${lang}/${dataset%?}/PERS/train.txt" \
                --loc-input "${medner_ds}/${lang}/${dataset%?}/LOC/train.txt" \
                --output "${medner_ds}/${lang}/${dataset%?}/MULTICLASS/train.txt"
        fi
    done
done
