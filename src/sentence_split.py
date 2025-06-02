#!/usr/bin/env python3
# split dataset sentences to limit sequence length
import argparse
import os
import random
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="input file")
    parser.add_argument("--output-dir", type=str, required=True, help="output directory")
    parser.add_argument("--split", type=str, required=True, help="dataset split (train|eval|test)")
    parser.add_argument("--classes", type=str, required=True, help="classes to consider, comma separated range including extremes, 1-based")
    parser.add_argument("--dictionary-size", type=int, default=10, help="size of dictionary sample to export, in percentage")
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
    return sorted(random.sample(dictionary, size))

def filter_classes(data, l, r):
    # # merge single class predictions into a single multiclass prediction
    # # in case of span overlaps, consider the one that begins earlier
    # #   if tie, consider the longest one
    # #   if tie, take the first class
    # # TODO: fix
    # lens = []
    # for c in range(l,r):
    #     tlens = []
    #     t = 0
    #     for x in sent[::-1]:
    #         if len(x) > 1:
    #             if x[c].startswith("B"):
    #                 t += 1
    #             elif x[c].startswith("I"):
    #                 t += 1
    #             else:
    #                 t = 0
    #         else:
    #             x[0] = ""
    #             x.extend([""]*r)
    #             t = 0
    #         tlens.append(t)
    #         if t and x[c].startswith("B"):
    #             t = 0
    #     lens.append(tlens[::-1])
    # idx = np.array(lens).argmax(axis=0)
    # sent_new = []
    # c = l
    # t = 0
    # for i,x in enumerate(sent):
    #     if t <= 0:
    #         if i==0 or lens[idx[i]][i-1] < 2:
    #             c = idx[i]+l
    #         else:
    #             c = 1-idx[i] + l
    #         t = lens[c-l][i]
    #     t -= 1
    #     sent_new.append([x[0], x[c]] if x[0] else [''])
    # return sent_new
    if l == r:
        return [[x[0],x[l]] if len(x)>1 else [x[0]] for x in data]
    output = []
    sent = []
    for x in data:
        if len(x) <= 1:
            t = [[]]*3
            for i in range(3):
                t[i] = [y[i] for y in sent]
            merged_labels = merge_iob_labels(*t)
            for y,z in zip(sent, merged_labels):
                output.append([y[0],z])
            output.append(x)
            sent = []
        else:
            sent.append(x)
    return output

def merge_iob_labels(tokens, pers_labels, loc_labels):
    """
    Merge two IOB label sequences (PERS and LOC) into a single sequence based on specified rules.

    Parameters:
    - tokens: List of token strings.
    - pers_labels: List of IOB labels for the PERS class.
    - loc_labels: List of IOB labels for the LOC class.

    Returns:
    - merged_labels: List of merged IOB labels.
    """
    n = len(tokens)
    merged_labels = ['O'] * n
    i = 0

    while i < n:
        # Determine if a PERS span starts at position i
        if pers_labels[i].startswith('B-'):
            pers_start = i
            pers_end = i + 1
            while pers_end < n and pers_labels[pers_end].startswith('I-'):
                pers_end += 1
        else:
            pers_start = pers_end = None

        # Determine if a LOC span starts at position i
        if loc_labels[i].startswith('B-'):
            loc_start = i
            loc_end = i + 1
            while loc_end < n and loc_labels[loc_end].startswith('I-'):
                loc_end += 1
        else:
            loc_start = loc_end = None

        # Decide which span to select based on the rules
        if pers_start is not None and loc_start is not None:
            if pers_start < loc_start:
                selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
            elif loc_start < pers_start:
                selected_start, selected_end, selected_type = loc_start, loc_end, 'LOC'
            else:  # Starts are equal
                pers_length = pers_end - pers_start
                loc_length = loc_end - loc_start
                if pers_length > loc_length:
                    selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
                elif loc_length > pers_length:
                    selected_start, selected_end, selected_type = loc_start, loc_end, 'LOC'
                else:
                    selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
        elif pers_start is not None:
            selected_start, selected_end, selected_type = pers_start, pers_end, 'PERS'
        elif loc_start is not None:
            selected_start, selected_end, selected_type = loc_start, loc_end, 'LOC'
        else:
            i += 1
            continue

        # Assign labels to the merged sequence
        merged_labels[selected_start] = f'B-{selected_type}'
        for j in range(selected_start + 1, selected_end):
            merged_labels[j] = f'I-{selected_type}'

        # Advance the index to the end of the selected span
        i = selected_end

    return merged_labels

        

# def merge_iob_labels(tokens, pers_labels, loc_labels):
#     """
#     Merge two IOB label sequences (PERS and LOC) into a single sequence based on specified rules.

#     Parameters:
#     - tokens: List of token strings.
#     - pers_labels: List of IOB labels for the PERS class.
#     - loc_labels: List of IOB labels for the LOC class.

#     Returns:
#     - merged_labels: List of merged IOB labels.
#     """
#     def extract_spans(labels, label_type):
#         """
#         Extract spans from IOB labels.

#         Returns a list of tuples: (start_idx, end_idx, label_type)
#         """
#         spans = []
#         start = None
#         for i, label in enumerate(labels):
#             if label == f'B-{label_type}':
#                 if start is not None:
#                     spans.append((start, i, label_type))
#                 start = i
#             elif label == f'I-{label_type}':
#                 if start is None:
#                     start = i
#             else:
#                 if start is not None:
#                     spans.append((start, i, label_type))
#                     start = None
#         if start is not None:
#             spans.append((start, len(labels), label_type))
#         return spans

#     # Extract spans for both label types
#     pers_spans = extract_spans(pers_labels, 'PERS')
#     loc_spans = extract_spans(loc_labels, 'LOC')

#     # Combine spans and sort based on the rules
#     all_spans = pers_spans + loc_spans
#     all_spans.sort(key=lambda x: (x[0], -(x[1]-x[0]), x[2] != 'PERS'))

#     # Initialize merged labels with 'O'
#     merged_labels = ['O'] * len(tokens)
#     occupied = set()

#     for start, end, label_type in all_spans:
#         if any(i in occupied for i in range(start, end)):
#             continue  # Overlaps with an already assigned span
#         for i in range(start, end):
#             occupied.add(i)
#             prefix = 'B-' if i == start else 'I-'
#             merged_labels[i] = f'{prefix}{label_type}'

#     return merged_labels


def main():
    args = parse_args()
    range_l, range_r = tuple(int(x) for x in args.classes.split(','))
    with open(args.input, "r") as fp:
        data = fp.readlines()
    data += ["--\n"] # placeholder
    data_new = []
    sent = []
    categories = ["pers", "loc"]
    dictionary = {k:set() for k in categories}
    entries = {k:[] for k in categories}
    l = 0
    t = 0
    for i,row in enumerate(data):
        if row == "--\n":
            continue
        t += 1
        sent.append(row.strip().split(args.field_delimiter))
        if row.startswith(args.field_delimiter.join([args.seq_end_token,"O","O",""])) and data[i+1][0].isupper():
            if l + t <= args.max_seq_length:
                l += t
            else:
                if l > 0:
                    data_new.append([""]) # start new sequence
                l = t
            t = 0
            data_new.extend(sent)
            sent = []
        if args.field_delimiter not in row:
            l = 0
            t = 0
            data_new.extend(sent)
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
    data_new = filter_classes(data_new, range_l, range_r)
    data_new = "\n".join(args.field_delimiter.join(x) for x in data_new)
    with open(os.path.join(args.output_dir, f"{args.split}.txt"), "w") as fp:
        fp.write(data_new)
    if args.split == "train" and range_l == range_r:
        v = dictionary[categories[range_l-1]]
        v = sorted(v)
        d = sample(v, args.dictionary_size, args.seed)
        with open(os.path.join(args.output_dir, "dict.txt"), "w") as fp:
            fp.write("\n".join(d) + "\n")

if __name__ == "__main__":
    main()
