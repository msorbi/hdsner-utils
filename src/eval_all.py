#!/usr/bin/env python3
import argparse
import os
import sys
from eval import eval

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--true-dir", type=str, default="data/datasets/ner_medieval_multilingual/FR/", help="input dataset directory")
    parser.add_argument("--pred-dir", type=str, default="output/ner_medieval_multilingual/FR/", help="output directory")
    parser.add_argument("--results-dir", type=str, default="results/ner_medieval_multilingual/FR/", help="output directory")
    parser.add_argument("--mode", type=str, default=None, help="seqeval.metrics.classification_report mode (None|\"strict\")")
    parser.add_argument("--n", type=int, default=2, help="number of predictions per token (columns in the files, PERS and LOC by default)")
    parser.add_argument("--field-delimiter", type=str, default="\t", help="tag file field delimiter")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    truth = os.walk(args.true_dir)
    files = {k:v for k,_,v in truth}
    for k,v in files.items():
        if "tags.txt" in v:
            pred_dir = os.path.join(
                args.pred_dir,
                os.path.relpath(
                    k,
                    args.true_dir
                )
            )
            results_dir = os.path.join(
                args.results_dir,
                os.path.relpath(
                    k,
                    args.true_dir
                )
            )
            os.makedirs(results_dir, exist_ok=True)
            eval_kwargs = {
                "true_file": os.path.join(k,"tags.txt"),
                "pred_file": os.path.join(pred_dir, "tags.txt"),
                "output_file": os.path.join(results_dir, "scores.json"),
                "mode": args.mode,
                "n": args.n,
                "field_delimiter": args.field_delimiter
            }
            print(eval_kwargs, file=sys.stderr)
            output = eval(**eval_kwargs)

if __name__ == "__main__":
    main()
