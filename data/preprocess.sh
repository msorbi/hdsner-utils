base="data/data_raw"
medner="${base}/ner_medieval_multilingual"

mkdir -p "${medner}/"
tab=$'\t'
for lang in FR lat es
do
    rm -rf "${medner}/${lang}/"
    mkdir -p "${medner}/${lang}/"
    for dataset in 'CBMA_' 'CDBE_' 'CODCAR-' 'CODEA-' 'CORHEN-' 'Fervaques_' 'Navarre_' 'S_Denis_'
    do
        mkdir "${medner}/${lang}/${dataset%?}/"
        for split in train val test
        do
            grep -A 1 "${tab}${lang}${tab}${dataset}" "${medner}/${split}_set_all_17_03_2022.txt" > "${medner}/${lang}/${dataset%?}/${split}.txt"
            if [ ! -s "${medner}/${lang}/${dataset%?}/${split}.txt" ]
            then
                rm "${medner}/${lang}/${dataset%?}/${split}.txt"
            fi
        done
    done
done
find ${medner} -type d -empty -exec rmdir '{}' ';' 2> /dev/null
