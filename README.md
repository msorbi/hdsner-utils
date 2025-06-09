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
`conda env create -n hdsner -f environment.yml` \
`conda activate hdsner`
## Data preparation
### Download data
`bash src/download.sh` # downloads data to `data/data_raw/`
### Preprocess data
`bash src/preprocess.sh` # creates supervised and distantly supervised datasets in `data/supervised/` and `data/distant/`
## Tag and evaluation with dictionary matching (default dictionary: 10% sample of train dictionary)
`bash src/tag_and_eval.sh` # tags will be produced in `data/output/` and scores in `results/`
