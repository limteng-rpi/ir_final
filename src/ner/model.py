import math
import torch
import src.ner.constant as C
import torch.nn as nn
import torch.nn.utils.rnn as R

from src.ner.module import Linear, CRF, CharCNN, CharCNNHW, CharCNNFF, LSTM
from allennlp.modules.elmo import Elmo


class LstmCnnOutElmo(nn.Module):

    def __init__(self,
                 vocabs,
                 elmo_option, elmo_weight,
                 lstm_hidden_size,
                 lstm_dropout=0.5, feat_dropout=0.5, elmo_dropout=0.5,
                 parameters=None,
                 output_bias=True,
                 elmo_finetune=False,
                 tag_scheme='bioes'
                 ):
        super(LstmCnnOutElmo, self).__init__()

        self.vocabs = vocabs
        self.label_size = len(self.vocabs['label'])
        # input features
        self.word_embed = nn.Embedding(parameters['word_embed_num'],
                                        parameters['word_embed_dim'],
                                        padding_idx=C.PAD_INDEX)

        self.elmo = Elmo(elmo_option, elmo_weight,
                         num_output_representations=1,
                         requires_grad=elmo_finetune,
                         dropout=elmo_dropout)
        self.elmo_dim = self.elmo.get_output_dim()

        self.word_dim = self.word_embed.embedding_dim
        self.feat_dim = self.word_dim
        # layers
        self.lstm = LSTM(input_size=self.feat_dim,
                         hidden_size=lstm_hidden_size,
                         batch_first=True,
                         bidirectional=True)
        self.output_linear = Linear(self.lstm.output_size + self.elmo_dim,
                                    self.label_size, bias=output_bias)
        self.crf = CRF(vocabs['label'], tag_scheme=tag_scheme)
        self.feat_dropout = nn.Dropout(p=feat_dropout)
        self.lstm_dropout = nn.Dropout(p=lstm_dropout)

    def forward_nn(self, token_ids, elmo_ids, lens, return_hidden=False):
        # word representation
        word_in = self.word_embed(token_ids)
        feats = self.feat_dropout(word_in)

        # LSTM layer
        lstm_in = R.pack_padded_sequence(feats, lens.tolist(), batch_first=True)
        lstm_out, _ = self.lstm(lstm_in)
        lstm_out, _ = R.pad_packed_sequence(lstm_out, batch_first=True)
        lstm_out = self.lstm_dropout(lstm_out)

        # ELMo output
        elmo_out = self.elmo(elmo_ids)['elmo_representations'][0]
        combined_out = torch.cat([lstm_out, elmo_out], dim=2)

        # output linear layer
        linear_out = self.output_linear(combined_out)
        if return_hidden:
            return linear_out, combined_out.tolist()
        else:
            return linear_out, None

    def predict(self, token_ids, elmo_ids, lens):
        self.eval()
        logits, lstm_out = self.forward_nn(token_ids, elmo_ids, lens,
                                           return_hidden=False)
        logits_padded = self.crf.pad_logits(logits)
        _scores, preds = self.crf.viterbi_decode(logits_padded, lens)

        preds = preds.data.tolist()
        self.train()
        return preds