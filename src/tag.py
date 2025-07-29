#!/usr/bin/env python3
import argparse
import os
import spacy
import spacy_lookup #import Entity
from typing import List, Tuple, Dict
from sentence_split import detokenize, sample

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="original IOB tag file")
    parser.add_argument("--output", type=str, required=True, help="output IOB tag file")
    parser.add_argument("--pers-dictionary", type=str, default="/dev/null", help="person dictionary text file")
    parser.add_argument("--loc-dictionary", type=str, default="/dev/null", help="location dictionary text file")
    parser.add_argument("--dictionary-size", type=int, default=100, help="size of dictionary sample to use, in percentage")
    parser.add_argument("--seed", type=int, default=42, help="random seed for dictionary sampling")
    args = parser.parse_args()
    return args

def generate_iob(
    text: str,
    token_positions: List[Tuple[int, int]],
    entities: List[Dict[str, object]],
    categories: List[str]
):
    """
    Generate an IOB-formatted list from a given text, token positions, and NER entities.

    Parameters:
    - text: The input text.
    - token_positions: A list of (start, end) character offsets for tokens.
    - entities: Output from lexifuzz_ner.ner.find_entity, with dicts like:
    - categories: Entity categories list
    """
    # Create a map from each character position to its entity label
    char_labels = {k:['O'] * len(text) for k in categories}
    for ent in entities:
        start = ent['start']
        end = ent['end']
        category = ent['category'].upper()
        char_labels[category][start] = f'B-{category}'
        for i in range(start + 1, end):
            char_labels[category][i] = f'I-{category}'
    output = []
    for start, end in token_positions:
        token = text[start:end]
        tags = [char_labels[category][start] for category in categories]
        output.append("\t".join([token]+tags))
    output.append("")
    return output

def tag(**kwargs) -> list:
    categories = [x for x in ["PERS", "LOC"] if kwargs.get(f"{x.lower()}_dictionary","/dev/null") != "/dev/null"]
    dictionary = {}
    with open(kwargs["input"], "r") as fp:
        data = fp.read()
    tags = [detokenize([x.split("\t",1)[0] for x in y.split("\n")]) for y in  data.strip().split("\n\n")]

    nlp = {}
    for category in categories:
        with open(kwargs[f"{category.lower()}_dictionary"], "r") as fp:
            data = fp.read()
        sampled_dict = sample(data.strip().split("\n"), kwargs["dictionary_size"], kwargs["seed"])
        with open(os.path.join(os.path.dirname(kwargs["output"]), "dict.txt"), "w") as fp:
            fp.write("\n".join(sampled_dict) + "\n")
        dictionary[category] = spacy_lookup.Entity(sampled_dict)
        nlp[category] = spacy.blank("fr")
        nlp[category].add_pipe(dictionary[category], last=True)
    
    output = []
    for text, token_pos in tags:
        ner = []
        for category in categories:
            for ent in nlp[category](text).ents:
                ner.append({'start': ent.start_char, 'end': ent.end_char, 'category': category})
        output.extend(generate_iob(text, token_pos, ner, categories))

    with open(kwargs["output"], "w") as fp:
        fp.write("\n".join(output))
    
    return output

def main():
    args = parse_args()
    kwargs = dict(args._get_kwargs())
    output = tag(**kwargs)

if __name__ == "__main__":
    main()
