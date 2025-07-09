#!/usr/bin/env python3
# convert IOB from class index to class name
# B is set when changing class

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="../data/hdsner_report.json", help="input file")
    parser.add_argument("--output", type=str, default=None, help="output file, defaults to stdout")
    parser.add_argument("--classes", type=str, default="PERS,LOC", help="1-based comma-separated ordered class list")
    parser.add_argument("--field-delimiter", type=str, default=" ", help="IOB field delimiter")
    args = parser.parse_args()
    args.classes = ["O"] + args.classes.split(",")
    return args

def main():
    args = parse_args()
    with open(args.input, "r") as fp:
        data = fp.read()
    data = data.split("\n")
    output = []
    p = 0
    for row in data:
        fields = row.split(args.field_delimiter)
        if len(fields) < 2:
            p = 0
        else:
            c = int(fields[1])
            if c == 0:
                fields[1] = args.classes[0]
            else:
                fields[1] = "{}-{}".format("I" if c==p else "B", args.classes[c])
            p = c
        output.append(" ".join(fields))
    output = "\n".join(output)
    if args.output is None:
        print(output)
    else:
        with open(args.output, "w") as fp:
            fp.write(output)

if __name__ == "__main__":
    main()
