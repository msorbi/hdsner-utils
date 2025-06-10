#!/usr/bin/env python3
# split dataset sentences to limit sequence length
import argparse
import os
import random
import numpy as np
import json
from merge_labels import merge_iob_labels

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="input file")
    parser.add_argument("--output-dir", type=str, required=True, help="output directory")
    parser.add_argument("--split", type=str, required=True, help="dataset split (train|eval|test)")
    parser.add_argument("--classes", type=str, required=True, help="classes to consider, comma separated range including extremes, 1-based")
    parser.add_argument("--dictionary-size", type=int, default=10, help="size of dictionary sample to export, in percentage")
    parser.add_argument("--max-seq-length", type=int, default=512, help="maximum output sequence length, notes: splits occur only on end-tokens")
    parser.add_argument("--seq-end-tokens", type=str, default=".|;|,|Et|et|Le", help="end sequence tokens, case-sensitive, separated by |")
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
    return sorted(random.sample(dictionary, size))

def filter_classes(data, l, r):
    output = []
    sent = []
    tokens = 0
    sents = 0
    max_sent_len,msls = 0,0
    priors = {}
    for x in data:
        if len(x) <= 1:
            t = [[y[i] for y in sent] for i in range(l, r+1)]
            merged_labels = t[0] if l==r else merge_iob_labels(*t)
            tokens += len(sent)
            max_sent_len,msls = max((max_sent_len,msls), (len(sent),len(output)))
            for y,z in zip(sent, merged_labels):
                output.append([y[0],z])
                if '-' in z:
                    c = z.rsplit('-',1)[-1]
                    priors[c] = priors.get(c,0) + 1
            output.append(x)
            sent = []
            sents += 1
        else:
            sent.append(x)
    for k in priors.keys():
        priors[k] /= tokens
    stats = {
        "tokens": tokens,
        "sents": sents,
        "max_sent_len": max_sent_len,
        "msls": msls
    }
    return output, stats, priors

def split_sentences(data:list, seq_end_token:str, categories:list, max_seq_length:int) -> list:
    data_new = []
    sent = []
    categories = ["pers", "loc"]
    dictionary = {k:set() for k in categories}
    entries = {k:[] for k in categories}
    l = 0
    t = 0
    for i,row in enumerate(data):
        sent.append(row)
        if len(row) <= 1:
            if l>0 and l+t > max_seq_length:
                data_new.append([""])
            l = 0
            t = 0
            data_new.extend(sent)
            sent = []
        else:
            t += 1
            if row[0] == seq_end_token:
                if l + t <= max_seq_length:
                    l += t
                else:
                    if l > 0:
                        data_new.append([""]) # start new sequence
                    l = t
                t = 0
                data_new.extend(sent)
                sent = []
            fields = row
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
    return data_new, dictionary, entries

def main():
    args = parse_args()
    range_l, range_r = tuple(int(x) for x in args.classes.split(','))
    with open(args.input, "r") as fp:
        data = fp.readlines()
    data = [row.strip().split(args.field_delimiter) for row in data if row != "--\n"]
    categories = ["pers", "loc"]
    
    for seq_end_token in args.seq_end_tokens.split("|"):
        data, dictionary, entries = split_sentences(data, seq_end_token, categories, args.max_seq_length)

                
    data_new, stats, priors = filter_classes(data, range_l, range_r)
    data_new = "\n".join(args.field_delimiter.join(x) for x in data_new)
    with open(os.path.join(args.output_dir, f"{args.split}.txt"), "w") as fp:
        fp.write(data_new)
    if args.split == "train" and range_l == range_r:
        v = dictionary[categories[range_l-1]]
        v = sorted(v)
        d = sample(v, args.dictionary_size, args.seed)
        with open(os.path.join(args.output_dir, "dict.txt"), "w") as fp:
            fp.write("\n".join(d) + "\n")
    elif args.split == "val":
        with open(os.path.join(args.output_dir, "priors.json"), "w") as fp:
            json.dump(obj=priors, fp=fp)
    with open(os.path.join(args.output_dir, f"{args.split}-stats.json"), "w") as fp:
        json.dump(obj=stats, fp=fp)

if __name__ == "__main__":
    main()
