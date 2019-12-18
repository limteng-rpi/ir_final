import torch
from src.ner.model import LstmCnnOutElmo


def load_lstm_cnn_elmo_model(model_file, elmo_option, elmo_weight,
                             gpu=False, device=0):
    """Load the LSTM-CNN+ELMo model from file.

    :param model_file: Path to the model file.
    :param elmo_option: ELMo option file.
    :param elmo_weight: ELMo weight file.
    :param gpu: Use GPU.
    :param device: GPU device index.
    :return: Model object and a dict of vocabs.
    """
    map_location = 'cuda:{}'.format(device) if gpu else 'cpu'

    state = torch.load(model_file, map_location=map_location)
    params = state['params']
    model = LstmCnnOutElmo(
        vocabs=state['vocabs'],
        elmo_option=elmo_option,
        elmo_weight=elmo_weight,
        lstm_hidden_size=params['lstm_size'],
        parameters=state['model_params'],
        output_bias=not params['no_out_bias']
    )
    model.load_state_dict(state['model'])
    if gpu:
        torch.cuda.set_device(device)
        model.cuda(device=device)

    return model, state['vocabs']


def convert_result(results, to_bio=True, separator=' ', conf=True):
    """Convert model output to BIO format.

    :param results: Model output.
    :param to_bio: Convert BIOES to BIO.
    :param separator: Delimiter character.
    :param conf: Confidence value
    :return: BIO formatted string.
    """
    def bioes_2_bio_tag(tag):
        if tag.startswith('S-'):
            tag = 'B-' + tag[2:]
        elif tag.startswith('E-'):
            tag = 'I-' + tag[2:]
        return tag

    bio_str = ''
    if conf:
        for p_b, t_b, l_b, s_b, c_b in results:
            for p_s, t_s, l_s, s_s, c_s in zip(p_b, t_b, l_b, s_b, c_b):
                p_s = p_s[:l_s]
                c_s = c_s[:l_s]
                for p, t, s, c in zip(p_s, t_s, s_s, c_s):
                    if to_bio:
                        p = bioes_2_bio_tag(p)
                    c = c.item()
                    bio_str += separator.join(
                        [str(i) for i in [t, s, c, p]]) + '\n'
                bio_str += '\n'
    else:
        for p_b, t_b, l_b, s_b in results:
            for p_s, t_s, l_s, s_s in zip(p_b, t_b, l_b, s_b):
                p_s = p_s[:l_s]
                for p, t, s in zip(p_s, t_s, s_s):
                    if to_bio:
                        p = bioes_2_bio_tag(p)
                    bio_str += separator.join(
                        [str(i) for i in [t, s, p]]) + '\n'
                bio_str += '\n'

    return bio_str


def plain2bio(input_str):
    """Convert plain text to BIO format.
    :param input_str: Input data string.
    :return: BIO formatted string.
    """
    sents = [s for s in input_str.strip().splitlines() if s]

    bio_sents = []
    for sent in sents:
        tokens = [t for t in sent.split(' ') if t]
        bio_sents.append('\n'.join(['{} {} O'.format(
            t, '{}-{}'.format(len(bio_sents), i))
            for i, t in enumerate(tokens)]))
    return '\n\n'.join(bio_sents)


def restore_order(items, indices):
    items_new = []
    for item in items:
        item = sorted([(i, v) for v, i in zip(item, indices)],
                      key=lambda x: x[0])
        item = [v for i, v in item]
        items_new.append(item)
    return items_new