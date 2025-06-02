#!/usr/bin/env python3
import argparse
import os
import sys
from tag import tag

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default="data/datasets/ner_medieval_multilingual/FR/", help="input dataset directory")
    parser.add_argument("--output-dir", type=str, default="output/ner_medieval_multilingual/FR/", help="output directory")
    parser.add_argument("--dictionary-size", type=int, default=10, help="size of dictionary samples to use, in percentage, dictionaries must exist")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    dictionary_size = str(args.dictionary_size).rjust(3,"0")
    inputs = os.walk(args.input_dir)
    files = {k:v for k,_,v in inputs}
    for k,v in files.items():
        if "tags.txt" in v:
            train_dir = os.path.join(
                os.path.dirname(k),
                "train"
            )
            output_dir = os.path.join(
                args.output_dir,
                os.path.relpath(
                    k,
                    args.input_dir
                )
            )
            os.makedirs(output_dir, exist_ok=True)
            tag_kwargs = {
                "input": os.path.join(k,"tags.txt"),
                "pers_dictionary": os.path.join(train_dir, f"pers-{dictionary_size}.txt"),
                "loc_dictionary": os.path.join(train_dir, f"loc-{dictionary_size}.txt"),
                "output": os.path.join(output_dir, "tags.txt")
            }
            output = tag(**tag_kwargs)

if __name__ == "__main__":
    main()
