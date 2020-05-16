'''Parses txt files with stanza (CoreNLP)

Usage:
    stanza_parse.py <i> <o>  [options]

Arguments:
    <i>             An path of a txt or a folder with txt to parse
    <o>             The folder path where the JSON files containing the parse are gonna be stored
    --cores CORES   The number of cores to use in a parallel setting [default: 1:int]
'''
import json

import stanza
from argopt import argopt
from joblib import Parallel, delayed
from tqdm import tqdm
import re
from stanza.models.common.doc import Document, Sentence, Token

from src.utils import get_files

NLP = stanza.Pipeline(lang='fr', package=None, processors={'tokenize': 'partut', 'lemma': 'partut',
                                                           "mwt": "partut",
                                                           'pos': 'partut', 'depparse': 'default',
                                                           'ner': "WikiNER"},
                      use_gpu=False)


#
# NLP = stanza.Pipeline(lang='fr', processors="tokenize,lemma,pos,mwt,depparse", use_gpu=False)
# NER = stanza.Pipeline(lang='fr',  processors='tokenize,ner',
#                       pos_batch_size=3000)

def parse(doc_path: str, max_read_bytes=350000):
    fields = ['id', 'text', 'lemma', 'upos', 'xpos', 'feats', 'head',
              'deprel', 'deps', 'misc', 'ner', 'start_char', 'end_char', 'type']
    tqdm.write(f"Parsing file {doc_path}")
    json_path = doc_path[:-4] + ".json"

    try:
        with open(doc_path) as filo:
            content = filo.read(max_read_bytes)
        content = re.sub(r"[^\n]\n[^\n]", "\n\n", content)
        doc: Document = NLP(content)
        sentences = []
        for s in doc.sentences:
            s: Sentence = s
            tokens = []
            for t in s.tokens:
                t: Token = t
                tokens.append(t.to_dict(fields=fields))
            sentences.append(tokens)
        with open(json_path, "w") as filo:
            json.dump(sentences, filo, indent=4)
        return 1
    except Exception as e:
        tqdm.write(f"Could not parse file {doc_path}: {str(e)}")
        return 0

if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    file_path = parser.i
    output_folder = parser.o
    n_jobs = int(parser.cores)

    doc_paths = get_files(file_path, extension="txt")
    tqdm.write(f"Got {len(doc_paths)} files to process")
    if n_jobs > 1:
        success_parsed = Parallel(n_jobs=n_jobs)(
            delayed(parse)(path) for path in tqdm(doc_paths))
    else:
        success_parsed = []
        for path in tqdm(doc_paths):
            success_parsed.append(parse(path))

    tqdm.write(f"I successfully transformed {str(sum(success_parsed))}  of {len(success_parsed)} files")
#
# for sent in doc.sentences:
#     for word in sent.words:
#         print(f'word: {word.text}\tupos: {word.upos}\txpos: {word.xpos}\tfeats: {word.feats if word.feats else "_"}')
# # print(*[f'word: {word.text}\tupos: {word.upos}\txpos: {word.xpos}\tfeats: {word.feats if word.feats else "_"}' for sent in doc.sentences for word in sent.words], sep='\n')
# print(*[f'token: {token.text}\tner: {token.ner}' for sent in doc_ner.sentences for token in sent.tokens], sep='\n')
