from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]


def test_laptop_profile_is_conservative():
    config = yaml.safe_load(
        (ROOT / "configs" / "resource_profiles.yaml").read_text(encoding="utf-8")
    )
    laptop = config["profiles"]["laptop"]

    assert laptop["max_parallel_workers"] == 1
    assert laptop["llm_concurrency"] == 1
    assert laptop["max_agent_graph_concurrency"] == 1
    assert laptop["prefer_cloud_llm"] is True
