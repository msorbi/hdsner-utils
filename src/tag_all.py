#!/usr/bin/env python3
import argparse
import os
import sys
from tag import tag
from merge_labels import merge_files

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default="data/supervised/ner_medieval_multilingual/FR/", help="input dataset directory")
    parser.add_argument("--output-dir", type=str, default="data/output/ner_medieval_multilingual/FR/", help="output directory")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    inputs = os.walk(args.input_dir)
    # walk = {k:(v,w) for k,v,w in inputs}
    # for base_dir,(subdirs,files) in walk.items():
    for base_dir,subdirs,files in inputs:
        if "MULTICLASS" in subdirs:
            subdirs = [x for x in subdirs if x!="MULTICLASS"]
            output_dir = os.path.join(
                args.output_dir,
                os.path.relpath(
                    base_dir,
                    args.input_dir
                )
            )
            for split in ["train", "val", "test"]:
                for category in subdirs:
                    os.makedirs(os.path.join(output_dir, category), exist_ok=True)
                    tag_kwargs = {
                        "input": os.path.join(base_dir, category, f"{split}.txt"),
                        f"{category.lower()}_dictionary": os.path.join(base_dir, category, f"dict.txt"),
                        "output": os.path.join(output_dir, category, f"{split}.txt")
                    }
                    output = tag(**tag_kwargs)
                os.makedirs(os.path.join(output_dir, "MULTICLASS"), exist_ok=True)
                merge_files(
                    pers_input=os.path.join(output_dir, "PERS", f"{split}.txt"),
                    loc_input=os.path.join(output_dir, "LOC", f"{split}.txt"),
                    output=os.path.join(output_dir, "MULTICLASS", f"{split}.txt"),
                )
            

if __name__ == "__main__":
    main()
