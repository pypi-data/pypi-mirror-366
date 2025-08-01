#!/usr/bin/env python3

import sys
import time
import torch
import argparse
import numpy as np
from torch.nn import Sequential, Tanh, Module

from koi.lstm import LSTMStack
from koi.utils import void_ptr
from koi.decode import beam_search, to_str

from bonito.nn import Convolution, Permute
from bonito.util import match_names, accuracy, decode_ref


class PushNVTX(Module):
    def __init__(self, emission):
        super(PushNVTX, self).__init__()
        self.emission = emission

    def forward(self, x):
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_push(self.emission)
        return x


class PopNVTX(Module):
    def __init__(self):
        super(PopNVTX, self).__init__()

    def forward(self, x):
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        return x


class LinearCRFEncoder(Module):

    def __init__(self, insize, n_base, state_len, scale=None, blank_score=None):
        super().__init__()
        self.n_base = n_base
        self.state_len = state_len
        self.blank_score = blank_score
        size = (n_base + 1) * n_base**state_len if blank_score is None else n_base**(state_len + 1)
        self.linear = torch.nn.Linear(insize, size)
        self.activation = Tanh()
        self.scale = scale

    def forward(self, x):
        scores = self.linear(x)
        if self.activation is not None:
            scores = self.activation(scores)
        if self.scale is not None:
            scores = scores * self.scale
        return scores


class Model(Module):

    def __init__(self, chunksize, batchsize, features=96, statelen=3, stride=5, ks=19, quantize=False):
        super().__init__()

        self.scale = 5
        self.blank = 2.0
        self.stride = stride
        self.feature = features
        self.statelen = statelen

        self.encoder = Sequential(
            Convolution(1, 4, 5, stride=1, padding=5//2, activation='swish'),
            Convolution(4, 16, 5, stride=1, padding=5//2, activation='swish'),
            Convolution(16, features, ks, stride=stride, padding=ks//2, activation='swish'),
            Permute([0, 2, 1]),
            LSTMStack((1, 0, 1, 0, 1), features, batchsize, chunksize // stride, quantized=quantize),
            LinearCRFEncoder(
                features, n_base=4, state_len=statelen, scale=self.scale, blank_score=self.blank
            )
        )

    def forward(self, x):
        return self.encoder(x)


def main(args):

    chunks = np.load(args.data + 'chunks.npy')
    targets = np.load(args.data + 'references.npy')
    raw_data = torch.from_numpy(chunks)[:args.batchsize].half().cuda().unsqueeze(dim=1)
    chunksize = raw_data.shape[-1]

    model = Model(chunksize, args.batchsize, quantize=args.quantize)
    weights = torch.load(args.weights)
    model.encoder.load_state_dict({
        k2: weights[k1] for k1, k2 in match_names(weights, model.encoder).items()
    })

    model.eval()
    model = model.half()
    model.to(args.device)

    torch.cuda.synchronize(); t1 = time.time()

    for i in range(args.repeat):
        scores = model(raw_data)
        sequences, qstrings, moves = beam_search(scores)

    torch.cuda.synchronize(); t2 = time.time(); duration = t2 - t1

    seqs = [to_str(seq) for seq in sequences]
    qstrings = [to_str(qs) for qs in qstrings]
    refs = [decode_ref(target, 'NACGT') for target in targets]
    accuracies = [accuracy(ref, seq) if len(seq) else 0. for ref, seq in zip(refs, seqs)]

    print("* mean      %.2f%%" % np.mean(accuracies), file=sys.stderr)
    print("* median    %.2f%%" % np.median(accuracies), file=sys.stderr)
    print("* samples/s %E" % ((args.repeat * chunksize * args.batchsize) / duration), file=sys.stderr)

    if args.fastq:
        for i, (seq, qstring) in enumerate(zip(seqs, qstrings)):
            print('@seq%s\n%s\n+\n%s' % (i, seq, qstring))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="/media/groups/machine_learning/active/fixed_blank_score_models/dna_r9.4.1_fast@v3.3/weights_1.tar")
    parser.add_argument("--data", default="/data/foxhound/chunks/ofan-120k-new-spec/validation/")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--repeat", default=32, type=int)
    parser.add_argument("--batchsize", default=512, type=int)
    parser.add_argument("--fastq", action="store_true", default=False)
    parser.add_argument("--quantize", action="store_true", default=False)
    main(parser.parse_args())
