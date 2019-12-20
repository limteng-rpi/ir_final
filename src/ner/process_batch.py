import os
import torch
import tqdm
import src.crawl.news.news.settings as settings
from pymongo import MongoClient
from nltk import word_tokenize
from src.ner.util import load_lstm_cnn_elmo_model
from src.ner.data import process_data

# MODEL_DIR = '/shared/nas/data/m1/yinglin8/projects/ir_final'
DATA_PATH = ''
MAX_SENTENCE_LEN = 128
GPU = 2
USE_GPU = GPU >= 0
FALLBACK = True

if USE_GPU:
    torch.cuda.set_device(GPU)

print('Loading name tagging model')
model, vocabs = load_lstm_cnn_elmo_model(
    os.path.join(DATA_PATH, 'eng.nam.mdl'),
    os.path.join(DATA_PATH, 'eng.original.5.5b.json'),
    os.path.join(DATA_PATH, 'eng.original.5.5b.hdf5'),
    gpu=USE_GPU, device=GPU
)
token_vocab = vocabs['token']
char_vocab = vocabs['char']
fallback_vocab = vocabs['fallback']
label_itos = {i: s for s, i in vocabs['label'].items()}


def pred2mention(tokens, preds):
    mentions = []
    cur_mention = None
    for i, (token, pred) in enumerate(zip(tokens, preds)):
        if pred == 'O':
            prefix = tag = 'O'
        else:
            prefix, tag = pred.split('-')

        if prefix == 'B':
            if cur_mention:
                mentions.append(cur_mention)
            cur_mention = [i, i + 1, [token], tag]
        elif prefix == 'S':
            if cur_mention:
                mentions.append(cur_mention)
            cur_mention = None
            mentions.append([i, i + 1, [token], tag])
        elif prefix == 'I':
            if cur_mention is None:
                cur_mention = [i, i + 1, [token], tag]
            elif cur_mention[-1] == tag:
                cur_mention[1] = i + 1
                cur_mention[2].append(token)
            else:
                mentions.append(cur_mention)
                cur_mention = [i, i + 1, [token], tag]
        elif prefix == 'E':
            if cur_mention is None:
                mentions.append([i, i + 1, [token], tag])
            elif cur_mention[-1] == tag:
                cur_mention[1] = i + 1
                cur_mention[2].append(token)
                mentions.append(cur_mention)
                cur_mention = None
            else:
                mentions.append(cur_mention)
                mentions.append([i, i + 1, [token], tag])
                cur_mention = None
        else:
            if cur_mention:
                mentions.append(cur_mention)
            cur_mention = None
    if cur_mention:
        mentions.append(cur_mention)

    mentions = [(i, j, ' '.join(ts), t) for i, j, ts, t in mentions]
    return mentions

def tagging(model, text):
    (
        token_ids, char_ids, elmo_ids, seq_lens, tokens, spans
    ) = process_data(text,
                     token_vocab=token_vocab,
                     char_vocab=char_vocab,
                     fallback_vocab=fallback_vocab,
                     fallback=FALLBACK,
                     gpu=USE_GPU)
    preds = model.predict(token_ids, elmo_ids, seq_lens)
    preds = [[label_itos[l] for l in ls] for ls in preds][0]
    mentions = pred2mention(text, preds)
    return mentions


with MongoClient(host=settings.DB_HOST, port=settings.DB_PORT) as client:
    data_col = client['data']['news']
    waitlist_col = client['data']['waitlist']
    result_col = client['result']['ner']

    total_num = waitlist_col.estimated_document_count()
    progress = tqdm.tqdm(total=total_num, ncols=75)
    for pending_doc in waitlist_col.find():
        progress.update(1)
        url = pending_doc['url']
        doc = data_col.find_one({'url': url})
        if doc and result_col.find_one({'url': url}) is None:
            sents = doc['sentences']
            # results = []
            doc_mentions = []
            for sent in sents:
                tokens = [t for t in word_tokenize(sent) if t]
                if len(tokens) == 0 or len(tokens) > MAX_SENTENCE_LEN:
                    # results.append([])
                    continue
                mentions = tagging(model, tokens)
                # results.append(mentions)
                doc_mentions.extend([[text, tag] for _, _, text, tag in mentions])
            # print(doc_mentions)
            result_col.insert_one({
                'url': url,
                'mentions': doc_mentions
            })

            # delete waitlist entry
            waitlist_col.delete_one({'url': url})
    progress.close()