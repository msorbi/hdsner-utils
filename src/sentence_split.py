#!/usr/bin/env python3
# split dataset sentences to limit sequence length
import argparse
import os
import random

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="input file")
    parser.add_argument("--output-dir", type=str, required=True, help="output directory")
    parser.add_argument("--dictionary-sizes", type=str, default="100,33,10", help="sizes of dictionary samples to export, in percentage, comma-separated")
    parser.add_argument("--max-seq-length", type=int, default=512, help="maximum output sequence length, notes: splits occur only on end-token, only tokens with label O are used as end")
    parser.add_argument("--seq-end-token", type=str, default=".", help="end sequence token, default \".\"")
    parser.add_argument("--field-delimiter", type=str, default="\t", help="field delimiter, default TAB")
    parser.add_argument("--seed", type=int, default=42, help="random seed for dictionary sampling")
    args = parser.parse_args()
    return args

def detokenize(tokens:list) -> tuple:
    if not tokens:
        return "", []
    s = [tokens[0]]
    p = len(tokens[0])
    token_pos = [(0, p)]
    for x in tokens[1:]:
        if x and x[0].isalnum() and s[-1] != "\n" and (not s[-1] or s[-1][-1] != "'"):
            s.append(" ")
            p += 1
        s.append(x)
        q = p + len(x)
        token_pos.append((p,q))
        p = q
    return "".join(s), token_pos

def join(tokens:list) -> str:
    return detokenize(tokens)[0]

def sample(dictionary:list, percentage:int, seed:int) -> list:
    size = (len(dictionary)*percentage) // 100
    random.seed(42)
    return random.sample(dictionary, size)

def main():
    args = parse_args()
    with open(args.input, "r") as fp:
        data = fp.readlines()
    data += ["--\n"] # placeholder
    data_new = []
    sent = []
    plain = []
    dictionary = {"pers":set(), "loc":set()}
    entries = {"pers":[], "loc":[]}
    l = 0
    t = 0
    for i,row in enumerate(data):
        if row == "--\n":
            continue
        t += 1
        sent.append(row)
        if row.startswith(args.field_delimiter.join([args.seq_end_token,"O","O",""])) and data[i+1][0].isupper():
            if l + t <= args.max_seq_length:
                l += t
            else:
                if l > 0:
                    data_new.extend(["\n"]) # start new sequence
                    plain.append("\n")
                l = t
            t = 0
            data_new.extend(sent)
            plain.extend([x.split(args.field_delimiter,1)[0] for x in sent])
            sent = []
        if args.field_delimiter not in row:
            l = 0
            t = 0
            data_new.extend(sent)
            plain.extend([x.split(args.field_delimiter,1)[0] for x in sent])
            sent = []
        else:
            fields = row.split(args.field_delimiter)
            for f in fields[1:3]:
                type_ = f[2:].lower()
                if f.startswith("B-"):
                    if entries[type_]:
                        entry = join(entries[type_])
                        if len(entry) > 2:
                            dictionary[type_].add(entry)
                    entries[type_] = [fields[0]]
                elif f.startswith("I-"):
                    entries[type_].append(fields[0])
                
    data_new.extend(sent)
    plain.extend([x.split(args.field_delimiter,1)[0] for x in sent])
    with open(os.path.join(args.output_dir, "tags.txt"), "w") as fp:
        fp.write("".join(data_new))
    with open(os.path.join(args.output_dir, "plain.txt"), "w") as fp:
        fp.write(join(plain))
    dictionary_sizes = [int(x) for x in args.dictionary_sizes.split(",")]
    for k,v in dictionary.items():
        v = sorted(v)
        for size in dictionary_sizes:
            d = sample(v, size, args.seed)
            with open(os.path.join(args.output_dir, f"{k}-{str(size).rjust(3,'0')}.txt"), "w") as fp:
                fp.write("\n".join(d) + "\n")

if __name__ == "__main__":
    main()
