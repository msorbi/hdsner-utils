#!/usr/bin/env python3
import argparse
import json
from pprint import pprint
from seqeval.metrics import classification_report

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--true", type=str, required=True, help="true IOB tag file")
    parser.add_argument("--pred", type=str, required=True, help="predicted IOB tag file")
    parser.add_argument("--output", type=str, required=True, help="output file (json)")
    parser.add_argument("--mode", type=str, default=None, help="seqeval.metrics.classification_report mode (None|\"strict\")")
    parser.add_argument("--n", type=int, default=2, help="number of predictions per token (columns in the files, PERS and LOC by default)")
    parser.add_argument("--field-delimiter", type=str, default="\t", help="tag file field delimiter")

    args = parser.parse_args()
    return args 

def parse_tags(data:str, n, field_delimiter) -> list:
    data = [[x.split(field_delimiter) for x in y.strip().split("\n")] for y in data.strip().split("\n\n")]
    tags = []
    for y in data:
        for category in range(1, 1+n):
            tags.append([x[category] for x in y])
    return tags

def eval(true_file, pred_file, output_file, mode=None, n=2, field_delimiter="\t"):
    with open(true_file, "r") as fp:
        data = fp.read()
    true = parse_tags(data, n, field_delimiter)
    with open(pred_file, "r") as fp:
        data = fp.read()
    pred = parse_tags(data, n, field_delimiter)
    report = classification_report(
        y_true=true,
        y_pred=pred,
        output_dict=True,
        mode=mode,
        digits=4
    )
    for d in report.values():
        for k,v in d.items():
            d[k] = v.item()
    with open(output_file, "w") as fp:
        json.dump(obj=report, fp=fp)
    return report

def main():
    args = parse_args()
    report = eval(args.true, args.pred, args.output, args.mode, args.n, args.field_delimiter)
    pprint(report)



if __name__ == "__main__":
    main()
