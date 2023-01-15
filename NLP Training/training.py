from os import chdir
import spacy
from tqdm import tqdm
import rapidjson as json
# from spacy import training
from spacy.tokens import DocBin

# TODO create a constants file for managing outputs and setting
infile = r"output/training_output.json"

# train data
TRAIN_DATA = json.load(open(infile))

# use absolute dir location
NLP_LOCATION = ""   # PUT SPACY FOLDER LOCATION HERE ("NLP Folder location")
nlp = spacy.load(NLP_LOCATION)

db = DocBin()

for text, annot in tqdm(TRAIN_DATA):
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annot["entities"]:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            pass
        else:
            ents.append(span)

    chdir(NLP_LOCATION)
    db.to_disk("/train.spacy")


#TODO after train.spacy is generated use to
#TODO run cli spacy -> python -m spacy train config.cfg --paths.train ./train.spacy --pthas.dev ./dev.spacy