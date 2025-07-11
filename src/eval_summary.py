#!/usr/bin/env python3
# summarize evaluation outputs
# evaluations are provided as filenames to the standard input, one per line
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="../data/hdsner_report.json", help="output JSON file")
    parser.add_argument("--dataset-pos", type=int, default=-2, help="position of the dataset name in the input path after split")
    args = parser.parse_args()
    return args

def main():
    import sys
    import json
    args = parse_args()
    summary = {}
    for f in sys.stdin:
        with open(f.strip(), 'r') as fp:
            x = json.load(fp)
        summary[f.strip().split('/')[args.dataset_pos]] = x
    with open(args.output, 'w') as fp:
        json.dump(obj=summary, fp=fp)

if __name__ == "__main__":
    main()
