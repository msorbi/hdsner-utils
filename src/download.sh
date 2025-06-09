base="data/data_raw"
medner="${base}/ner_medieval_multilingual"

mkdir -p "${medner}/"
tab=$'\t'
for split in train val test
do
    filename="${split}_set_all_17_03_2022.txt"
    if [ ! -f "${medner}/${filename}" ]
    then
        wget -P "${medner}/" "https://gitlab.com/magistermilitum/ner_medieval_multilingual/-/raw/18046c490a9b911d7fa047804234f232f2a48335/large_datasets/${filename}"
    fi
done
