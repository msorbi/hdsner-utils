data_raw="data/data_raw"
datasets="data/datasets"
medner_raw="${data_raw}/ner_medieval_multilingual"
medner="${data_raw}/ner_medieval_multilingual"

mkdir -p "${medner}/"
tab=$'\t'

# split datasets
for lang in FR lat es
do
    rm -rf "${medner}/${lang}/"
    mkdir -p "${medner}/${lang}/"
    for dataset in 'CBMA_' 'CDBE_' 'CODCAR-' 'CODEA-' 'CORHEN-' 'Fervaques_' 'Navarre_' 'S_Denis_'
    do
        mkdir "${medner}/${lang}/${dataset%?}/"
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
            mkdir "${medner}/${lang}/${dataset%?}/${category}"
            for split in train val test
            do
                # divide each split by language and original dataset (grep), and then divide the sentences to respect a max sequence lenght when possible (sentence_split.py), and export dictionaries
                python3 src/sentence_split.py \
                    --input <(grep -A 1 "${tab}${lang}${tab}${dataset}" "${medner_raw}/${split}_set_all_17_03_2022.txt") \
                    --output-dir "${medner}/${lang}/${dataset%?}/${category}"\
                    --split "${split}" \
                    --classes "${class_a},${class}"
                if [ ! -s "${medner}/${lang}/${dataset%?}/${category}/train.txt" ]
                then
                    rm -rf "${medner}/${lang}/${dataset%?}/${category}/"
                    break
                fi
            done
        done
    done
done
find ${medner} -type d -empty -exec rmdir '{}' ';' 2> /dev/null
