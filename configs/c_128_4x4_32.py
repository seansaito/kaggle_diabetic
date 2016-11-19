import numpy as np

from config import Config
from data import BALANCE_WEIGHTS
from layers import *

cnf = {
    'name': __name__.split('.')[-1],
    'w': 128,
    'h': 128,
    'train_dir': 'data/train_tiny',
    'test_dir': 'data/test_tiny',
    'batch_size_train': 128,
    'batch_size_test': 128,
    'balance_weights': np.array(BALANCE_WEIGHTS),
    'balance_ratio': 0.975,
    'final_balance_weights':  np.array([1, 2, 2, 2, 2], dtype=float),
    'aug_params': {
        'zoom_range': (1 / 1.15, 1.15),
        'rotation_range': (0, 360),
        'shear_range': (0, 0),
        'translation_range': (-10, 10),
        'do_flip': True,
        'allow_stretch': True,
    },
    'weight_decay': 0.0005,
    'sigma': 0.25,
    'schedule': {
        0: 0.003,
        150: 0.0003,
        201: 'stop',
    },
}

nonlinearity = leaky_rectify

def cp(num_filters, *args, **kwargs):
    args = {
        'num_filters': num_filters,
        'filter_size': (4, 4),
    }
    args.update(kwargs)
    return conv_params(**args)

n = 32

layers = [
    (InputLayer, {'shape': (None, 3, cnf['w'], cnf['h'])}),
    ] + ([(ToCC, {})] if CC else []) + [
    (Conv2DLayer, cp(n, stride=(2, 2))),
    (Conv2DLayer, cp(n, pad=2)),
    (MaxPool2DLayer, pool_params()),
    (Conv2DLayer, cp(2 * n, stride=(2, 2))),
    (Conv2DLayer, cp(2 * n, pad=2)),
    (Conv2DLayer, cp(2 * n)),
    (MaxPool2DLayer, pool_params()),
    (Conv2DLayer, cp(4 * n, pad=2)),
    (Conv2DLayer, cp(4 * n)),
    (Conv2DLayer, cp(4 * n, pad=2)),
    ] + ([(FromCC, {})] if CC else []) + [
    (RMSPoolLayer, pool_params()),
    (DropoutLayer, {'p': 0.5}),
    (DenseLayer, dense_params(1024)),
    (FeaturePoolLayer, {'pool_size': 2}),
    (DropoutLayer, {'p': 0.5}),
    (DenseLayer, dense_params(1024)),
    (FeaturePoolLayer, {'pool_size': 2}),
    (DenseLayer, {'num_units': 1}),
]

config = Config(layers=layers, cnf=cnf)
