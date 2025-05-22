base="data/data_raw"
medner="${base}/ner_medieval_multilingual"

mkdir -p "${medner}/"
tab=$'\t'
for split in train val test
do
    wget -P "${medner}/" "https://gitlab.com/magistermilitum/ner_medieval_multilingual/-/raw/main/large_datasets/${split}_set_all_17_03_2022.txt"
done
