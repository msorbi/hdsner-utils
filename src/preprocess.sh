#!/bin/bash
# langs="FR lat es"
langs="FR" # using only French
datasets=""CBMA_" "CDBE_" "CODCAR-" "CODEA-" "CORHEN-" "HOME-""

medner_raw="data/data_raw/ner_medieval_multilingual"
medner_supervised="data/supervised/ner_medieval_multilingual"

# Parse arguments
DICT_SIZES=()
OTHER_ARGS=()
PARSE_DICT_SIZES=false
AFTER_SEPARATOR=false
for arg in "$@"; do
    if [ "$AFTER_SEPARATOR" = true ]; then
        # If we are after the -- separator, collect all remaining arguments
        OTHER_ARGS+=("$arg")
    elif [ "$arg" = "--" ]; then
        # Found the -- separator, set flag to start collecting other arguments
        AFTER_SEPARATOR=true
        PARSE_DICT_SIZES=false # Stop parsing dict sizes
    elif [ "$arg" = "--dictsizes" ]; then
        # Found the --dictsizes flag, set flag to start collecting dict sizes
        PARSE_DICT_SIZES=true
    elif [ "$PARSE_DICT_SIZES" = true ]; then
        # If we are parsing dict sizes, check if the argument is an integer
        if [[ "$arg" =~ ^[0-9]+$ ]]; then
            DICT_SIZES+=("$arg")
        else
            echo "Warning: '$arg' is not a valid integer for --dictsizes. Stopping parsing dictsizes."
            PARSE_DICT_SIZES=false # Stop parsing if a non-integer is found
        fi
    fi
done

mkdir -p "${medner_supervised}/"
tab=$'\t'

# split datasets
for lang in ${langs}
do
    rm -rf "${medner_supervised}/${lang}/"
    mkdir -p "${medner_supervised}/${lang}/"
    for dataset in ${datasets}
    do
        mkdir "${medner_supervised}/${lang}/${dataset%?}/"
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
            mkdir "${medner_supervised}/${lang}/${dataset%?}/${category}"
            for split in train val test
            do
                # divide each split by language, original dataset (grep), and category, and then divide the sentences to respect a max sequence lenght when possible (sentence_split.py), and export dictionaries
                python3 src/sentence_split.py \
                    --input <(egrep -A 1 "${tab}${lang}${tab}${dataset_grep}" "${medner_raw}/${split}_set_all_17_03_2022.txt") \
                    --output-dir "${medner_supervised}/${lang}/${dataset%?}/${category}"\
                    --split "${split}" \
                    --classes "${class_a},${class}" \
                    ${OTHER_ARGS[@]}
                if [ ! -s "${medner_supervised}/${lang}/${dataset%?}/${category}/train.txt" ]
                then
                    rm -rf "${medner_supervised}/${lang}/${dataset%?}/${category}/"
                    break
                fi
            done
        done
    done
done
find ${medner_supervised} -type d -empty -exec rmdir '{}' ';' 2> /dev/null

# build train splits with dictionary matching
for dict_size in ${DICT_SIZES[@]}
do
    medner_ds="data/distant-0.${dict_size}/ner_medieval_multilingual"
    rm -r "${medner_ds}"
    mkdir -p "`dirname ${medner_ds}`"
    cp -r "${medner_supervised}" "${medner_ds}"

    for lang in ${langs}
    do
        for dataset in ${datasets}
        do
            if [ -f "${medner_supervised}/${lang}/${dataset%?}/PERS/train.txt" ]
            then
                for category in PERS LOC
                do
                    category_lower="`echo ${category} | tr '[A-Z]' '[a-z]'`"
                    python3 src/tag.py \
                        --input "${medner_supervised}/${lang}/${dataset%?}/${category}/train.txt" \
                        --output "${medner_ds}/${lang}/${dataset%?}/${category}/train.txt" \
                        --dictionary-size "${dict_size}" \
                        --${category_lower}-dictionary "${medner_supervised}/${lang}/${dataset%?}/${category}/dict.txt"
                done
                python3 src/merge_labels.py \
                    --pers-input "${medner_ds}/${lang}/${dataset%?}/PERS/train.txt" \
                    --loc-input "${medner_ds}/${lang}/${dataset%?}/LOC/train.txt" \
                    --output "${medner_ds}/${lang}/${dataset%?}/MULTICLASS/train.txt"
            fi
        done
    done
done
