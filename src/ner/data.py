import json
import re
import torch
import src.ner.constant as C
from torch.utils.data import Dataset
from allennlp.modules.elmo import batch_to_ids

DIGIT_PATTERN = re.compile('\d')


def bio_to_bioes(labels):
    """Convert a sequence of BIO labels to BIOES labels.
    :param labels: A list of labels.
    :return: A list of converted labels.
    """
    label_len = len(labels)
    labels_bioes = []
    for idx, label in enumerate(labels):
        next_label = labels[idx + 1] if idx < label_len - 1 else 'O'
        if label == 'O':
            labels_bioes.append('O')
        elif label.startswith('B-'):
            if next_label.startswith('I-'):
                labels_bioes.append(label)
            else:
                labels_bioes.append('S-' + label[2:])
        else:
            if next_label.startswith('I-'):
                labels_bioes.append(label)
            else:
                labels_bioes.append('E-' + label[2:])
    return labels_bioes


def process_data(tokens, token_vocab, char_vocab, fallback_vocab,
                 fallback=False, max_char_len=50, min_char_len=4,
                 gpu=False):
    token_num = len(tokens)
    pad = C.PAD_INDEX
    batch_token_ids, batch_char_ids, batch_elmo_ids = [], [], []
    spans = [str(i) for i in range(token_num)]

    # numberize tokens
    if fallback:
        token_ids = []
        for token in tokens:
            if token in token_vocab:
                token_ids.append(token_vocab[token])
            else:
                token_lower = token.lower()
                token_zero = re.sub(DIGIT_PATTERN, '0', token_lower)
                if token_lower in fallback_vocab:
                    token_ids.append(token_vocab[fallback_vocab[token_lower]])
                elif token_zero in fallback_vocab:
                    token_ids.append(token_vocab[fallback_vocab[token_zero]])
                else:
                    token_ids.append(C.UNK_INDEX)
    else:
        token_ids = [token_vocab.get(token, C.UNK_INDEX)
                     for token in tokens]
    # numberize characters
    char_ids = [
        [char_vocab.get(c, C.UNK_INDEX) for c in t][:max_char_len]
        for t in tokens]
    char_ids = [x + [pad] * (max_char_len - len(x)) for x in char_ids]
    elmo_ids = batch_to_ids([tokens])[0].tolist()


    if gpu:
        batch_token_ids = torch.cuda.LongTensor([token_ids])
        batch_char_ids = torch.cuda.LongTensor(char_ids)
        seq_lens = torch.cuda.LongTensor([token_num])
        batch_elmo_ids = torch.cuda.LongTensor([elmo_ids])
    else:
        batch_token_ids = torch.LongTensor([token_ids])
        batch_char_ids = torch.LongTensor(char_ids)
        seq_lens = torch.LongTensor([token_num])
        batch_elmo_ids = torch.LongTensor([elmo_ids])

    return (batch_token_ids, batch_char_ids, batch_elmo_ids,
            seq_lens, [tokens], [spans])





class BioDataset(Dataset):
    def __init__(self,
                 span_col=0,
                 token_col=1,
                 label_col=-1,
                 separator=' ',
                 max_seq_len=-1,
                 min_char_len=4,
                 max_char_len=50,
                 gpu=False,
                 test_mode=False):
        self.span_col = span_col
        self.token_col = token_col
        self.label_col = label_col
        self.separator = separator

        self.max_seq_len = max_seq_len
        self.min_char_len = min_char_len
        self.max_char_len = max_char_len
        self.gpu = gpu
        self.test_mode = test_mode
        self.data = []

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)

    def process(self, bio_str,
                vocabs, fallback=False):
        self.data = []
        token_vocab = vocabs['token']
        char_vocab = vocabs['char']
        fallback_vocab = vocabs['fallback']
        sentences = bio_str.strip().split('\n\n')
        for sentence in sentences:
            lines = sentence.split('\n')
            tokens, spans = [], []
            for line in lines:
                segments = line.split(self.separator)
                tokens.append(segments[self.token_col].strip())
                spans.append(segments[self.span_col])
            # numberize tokens
            if fallback:
                token_ids = []
                for token in tokens:
                    if token in token_vocab:
                        token_ids.append(token_vocab[token])
                    else:
                        token_lower = token.lower()
                        token_zero = re.sub(DIGIT_PATTERN, '0', token_lower)
                        if token_lower in fallback_vocab:
                            token_ids.append(token_vocab[fallback_vocab[token_lower]])
                        elif token_zero in fallback_vocab:
                            token_ids.append(token_vocab[fallback_vocab[token_zero]])
                        else:
                            token_ids.append(C.UNK_INDEX)
            else:
                token_ids = [token_vocab.get(token, C.UNK_INDEX)
                             for token in tokens]
            # numberize characters
            char_ids = [
                [char_vocab.get(c, C.UNK_INDEX) for c in t][:self.max_char_len]
                for t in tokens]
            elmo_ids = batch_to_ids([tokens])[0].tolist()
            self.data.append((token_ids, char_ids, elmo_ids,
                         tokens, spans))

    def batch_process(self, batch):
        pad = C.PAD_INDEX
        # sort instances in decreasing order of sequence lengths
        # batch.sort(key=lambda x: len(x[0]), reverse=True)
        batch = sorted(enumerate(batch), key=lambda x: len(x[1][0]),
                       reverse=True)
        ori_indices = [i[0] for i in batch]
        batch = [i[1] for i in batch]
        # sequence lengths
        seq_lens = [len(x[0]) for x in batch]
        max_seq_len = max(seq_lens)
        # character lengths
        max_char_len = self.min_char_len
        for seq in batch:
            for chars in seq[1]:
                if len(chars) > max_char_len:
                    max_char_len = len(chars)
        # padding sequences
        batch_token_ids = []
        batch_char_ids = []
        batch_elmo_ids = []
        batch_tokens = []
        batch_spans = []
        for inst in batch:
            token_ids, char_ids, elmo_ids, tokens, spans = inst
            seq_len = len(token_ids)
            pad_num = max_seq_len - seq_len
            batch_token_ids.append(token_ids + [pad] * pad_num)
            batch_char_ids.extend(
                # pad each word
                [x + [pad] * (max_char_len - len(x)) for x in char_ids] +
                # pad each sequence
                [[pad] * max_char_len for _ in range(pad_num)])
            batch_tokens.append(tokens)
            batch_spans.append(spans)
            batch_elmo_ids.append(elmo_ids + [[pad] * C.ELMO_MAX_CHAR_LEN
                                              for _ in range(pad_num)])

        if self.gpu:
            batch_token_ids = torch.cuda.LongTensor(batch_token_ids)
            batch_char_ids = torch.cuda.LongTensor(batch_char_ids)
            seq_lens = torch.cuda.LongTensor(seq_lens)
            batch_elmo_ids = torch.cuda.LongTensor(batch_elmo_ids)
        else:
            batch_token_ids = torch.LongTensor(batch_token_ids)
            batch_char_ids = torch.LongTensor(batch_char_ids)
            seq_lens = torch.LongTensor(seq_lens)
            batch_elmo_ids = torch.LongTensor(batch_elmo_ids)

        return (batch_token_ids, batch_char_ids, batch_elmo_ids,
                seq_lens, batch_tokens, batch_spans, ori_indices)


