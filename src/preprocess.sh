data_raw="data/data_raw"
datasets="data/datasets"
medner_raw="${data_raw}/ner_medieval_multilingual"
medner="${datasets}/ner_medieval_multilingual"

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
        for split in train val test
        do
            mkdir "${medner}/${lang}/${dataset%?}/${split}"
            # divide each split by language and original dataset (grep), and then divide the sentences to respect a max sequence lenght when possible (sentence_split.py), and export dictionaries
            python3 data/sentence_split.py --input <(grep -A 1 "${tab}${lang}${tab}${dataset}" "${medner_raw}/${split}_set_all_17_03_2022.txt") --output-dir "${medner}/${lang}/${dataset%?}/${split}" #.txt" --dictionary "${medner}/${lang}/${dataset%?}/${split}.txt"
            if [ ! -s "${medner}/${lang}/${dataset%?}/${split}/plain.txt" ]
            then
                rm -rf "${medner}/${lang}/${dataset%?}/${split}/"
            fi
        done
    done
done
find ${medner} -type d -empty -exec rmdir '{}' ';' 2> /dev/null
