# hdsner-utils
Distantly Supervised Named Entity Recognition for Historical Documents - Utils
## Description
This repository uses the datasets from [Multilingual Named Entity Recognition for Medieval Charters using
Stacked Embeddings and BERT-based Models](https://gitlab.com/magistermilitum/ner_medieval_multilingual) to provide tools to:
- build NER gazetteers based on their tags
- randomly sample the gazetteers
- re-tag the datasets using the sample with dictionary matching
- evaluate the new tags  
## Environment setup
```bash
conda env create -n hdsner -f environment.yml
conda activate hdsner
```
## Data preparation
### Download data
```bash
bash src/download.sh
```
Downloads data to `data/data_raw/`
### Preprocess data
```bash
bash src/preprocess.sh --dictsizes 10 20 40 60 80 100
```
Creates supervised and distantly supervised datasets in `data/supervised/`, `data/distant-0.10/`, and `data/distant-0.20/`

## Tag and evaluation with dictionary matching
```bash
bash src/tag_and_eval.sh
```
Tags will be produced in `output/` and scores in `results/hdsner_report_(val|test).json`
