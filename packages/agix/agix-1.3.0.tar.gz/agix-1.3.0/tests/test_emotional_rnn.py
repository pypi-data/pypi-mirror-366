import numpy as np

from src.agix.qualia.emotional_rnn import EmotionalRNN


def test_forward_shape_rnn():
    np.random.seed(0)
    model = EmotionalRNN(input_size=3, hidden_size=5, rnn_type="rnn")
    x = np.random.rand(4, 3)
    y = model.forward(x)
    assert y.shape == (4, 3)


def test_forward_shape_lstm():
    np.random.seed(0)
    model = EmotionalRNN(input_size=2, hidden_size=4, rnn_type="lstm")
    x = np.random.rand(6, 2)
    y = model.forward(x)
    assert y.shape == (6, 2)


def test_update_changes_output():
    np.random.seed(0)
    model = EmotionalRNN(input_size=3, hidden_size=4, rnn_type="rnn", learning_rate=0.1)
    x = np.random.rand(5, 3)
    target = np.random.rand(5, 3)
    y1 = model.forward(x)
    model.update(x, target)
    model.reset_state()
    y2 = model.forward(x)
    assert not np.allclose(y1, y2)

