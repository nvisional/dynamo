# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""CPU unit tests for NVDEC host-frame ownership."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from dynamo.common.multimodal.nvdec_decoder import _frame_to_rgb_hwc


class _ReusableHostFrame:
    """Stand-in for PyNvVideoCodec host frames that share one backing buffer."""

    def __init__(self, buffer: np.ndarray):
        self._buffer = buffer

    def __dlpack_device__(self):
        return torch.from_numpy(self._buffer).__dlpack_device__()

    def __dlpack__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return torch.from_numpy(self._buffer).__dlpack__(*args, **kwargs)


def test_frame_to_rgb_hwc_copies_reused_host_buffer():
    """Host decode buffers are reused; each call must own its pixels (#17762)."""
    shared = np.zeros((4, 4, 3), dtype=np.uint8)
    frames = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for color in colors:
        shared[:] = color
        frames.append(_frame_to_rgb_hwc(_ReusableHostFrame(shared)))
    stacked = np.stack(frames)
    assert len({frame.tobytes() for frame in frames}) == 4
    assert [tuple(int(x) for x in f.reshape(-1, 3).mean(0)) for f in frames] == list(
        colors
    )
    assert stacked.shape == (4, 4, 4, 3)
