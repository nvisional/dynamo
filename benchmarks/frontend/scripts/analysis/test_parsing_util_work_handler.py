"""CPU unit tests for work-handler transport metric name lookups."""

from __future__ import annotations

from pathlib import Path

from parsing_util import parse_prometheus_text

# ### WRITTEN BY AI ###


def test_work_handler_transport_metrics_use_runtime_names(tmp_path: Path):
    """Lookup dynamo_work_handler_* names emitted by the runtime (#17773).

    ### WRITTEN BY AI ###
    """
    snapshot = tmp_path / "metrics.prom"
    snapshot.write_text(
        "\n".join(
            [
                'dynamo_work_handler_network_transit_seconds_bucket{le="0.1"} 50',
                'dynamo_work_handler_network_transit_seconds_bucket{le="1"} 100',
                'dynamo_work_handler_network_transit_seconds_bucket{le="+Inf"} 100',
                "dynamo_work_handler_network_transit_seconds_count 100",
                'dynamo_work_handler_time_to_first_response_seconds_bucket{le="0.1"} 50',
                'dynamo_work_handler_time_to_first_response_seconds_bucket{le="1"} 100',
                'dynamo_work_handler_time_to_first_response_seconds_bucket{le="+Inf"} 100',
                "dynamo_work_handler_time_to_first_response_seconds_count 100",
                "",
            ]
        )
    )

    snap = parse_prometheus_text(snapshot)
    assert snap is not None
    assert snap.work_handler_network_transit == {
        "p50": 0.1,
        "p95": 0.91,
        "p99": 0.982,
    }
    assert snap.work_handler_time_to_first_response == {
        "p50": 0.1,
        "p95": 0.91,
        "p99": 0.982,
    }


def test_legacy_component_transport_names_are_ignored(tmp_path: Path):
    """Old dynamo_component_* names must not populate the report fields.

    ### WRITTEN BY AI ###
    """
    snapshot = tmp_path / "metrics.prom"
    snapshot.write_text(
        "\n".join(
            [
                'dynamo_component_network_transit_seconds_bucket{le="0.1"} 50',
                'dynamo_component_network_transit_seconds_bucket{le="1"} 100',
                'dynamo_component_network_transit_seconds_bucket{le="+Inf"} 100',
                "dynamo_component_network_transit_seconds_count 100",
                "",
            ]
        )
    )

    snap = parse_prometheus_text(snapshot)
    assert snap is not None
    assert snap.work_handler_network_transit == {}
