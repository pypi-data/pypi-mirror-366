import pytest
import torch
from parity_tensor import ParityTensor


def test_creation() -> None:
    x = ParityTensor((False, False), ((2, 2), (1, 3)), torch.randn([4, 4]))
    with pytest.raises(AssertionError):
        x = ParityTensor((False, False, False), ((2, 2), (1, 3)), torch.randn([4, 4]))
    with pytest.raises(AssertionError):
        x = ParityTensor((False, False), ((2, 2), (1, 3), (3, 1)), torch.randn([4, 4]))
    with pytest.raises(AssertionError):
        x = ParityTensor((False, False), ((2, 2), (1, 1)), torch.randn([4, 4]))
