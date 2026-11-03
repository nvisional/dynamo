"""CPU unit tests for frontend Prometheus snapshot parsing."""

from __future__ import annotations

from pathlib import Path

from parsing_util import parse_prometheus_text

# ### WRITTEN BY AI ###


def test_stage_duration_quantiles_when_le_precedes_stage(tmp_path: Path):
    """Label order must not zero stage quantiles (#17316).

    ### WRITTEN BY AI ###
    """
    snapshot = tmp_path / "metrics.prom"
    snapshot.write_text(
        "\n".join(
            [
                'dynamo_frontend_stage_duration_seconds_bucket{le="0.1",stage="preprocess"} 50',
                'dynamo_frontend_stage_duration_seconds_bucket{le="1",stage="preprocess"} 100',
                'dynamo_frontend_stage_duration_seconds_bucket{le="+Inf",stage="preprocess"} 100',
                'dynamo_frontend_stage_duration_seconds_count{stage="preprocess"} 100',
                "",
            ]
        )
    )

    snap = parse_prometheus_text(snapshot)
    assert snap is not None
    assert "preprocess" in snap.stage_durations
    stats = snap.stage_durations["preprocess"]
    assert stats["p50"] == 0.1
    assert abs(stats["p95"] - 0.91) < 1e-9
    assert abs(stats["p99"] - 0.982) < 1e-9


def test_stage_duration_quantiles_when_stage_precedes_le(tmp_path: Path):
    """Existing stage-before-le order still works.

    ### WRITTEN BY AI ###
    """
    snapshot = tmp_path / "metrics.prom"
    snapshot.write_text(
        "\n".join(
            [
                'dynamo_frontend_stage_duration_seconds_bucket{stage="preprocess",le="0.1"} 50',
                'dynamo_frontend_stage_duration_seconds_bucket{stage="preprocess",le="1"} 100',
                'dynamo_frontend_stage_duration_seconds_bucket{stage="preprocess",le="+Inf"} 100',
                'dynamo_frontend_stage_duration_seconds_count{stage="preprocess"} 100',
                "",
            ]
        )
    )

    snap = parse_prometheus_text(snapshot)
    assert snap is not None
    stats = snap.stage_durations["preprocess"]
    assert stats["p50"] == 0.1
    assert abs(stats["p95"] - 0.91) < 1e-9
    assert abs(stats["p99"] - 0.982) < 1e-9
