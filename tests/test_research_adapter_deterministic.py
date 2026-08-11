#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts" / "search_agent.py"


class FakeResponse:
    def __init__(self, body: bytes, content_type: str = "text/html"):
        self._body = body
        self.headers = {"Content-Type": content_type}
    def read(self, _limit: int = -1):
        return self._body


def load_adapter():
    spec = importlib.util.spec_from_file_location("stegbio_research_agent", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: pathlib.Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    adapter = load_adapter()
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        (base / "research").mkdir(parents=True)
        (base / "data/sources").mkdir(parents=True)
        (base / "research/conformance.json").write_text(json.dumps({"recurrence":{"classification":"DELEGATED"}}), encoding="utf-8")
        (base / "research/frontier.json").write_text(json.dumps({"trajectories":[{"trajectory_id":"T1","state":"ACTIVE","acquisition_queries":["alpha beta"]}]}), encoding="utf-8")
        (base / "research/acquisition_requests.jsonl").write_text("", encoding="utf-8")
        (base / "research/source_candidates.jsonl").write_text("", encoding="utf-8")
        (base / "research/research_receipts.jsonl").write_text("", encoding="utf-8")
        (base / "data/sources/sources_whitelist.csv").write_text("name,url,authority_class\nfixture,https://fixture.local/index,official\n", encoding="utf-8")

        assert adapter.reqs(base) == [], "DELEGATED recurrence must suppress implicit frontier searches"

        explicit = {"request_id":"REQ1","trajectory_ids":["T1"],"query":"alpha beta","state":"ACTIVE"}
        (base / "research/acquisition_requests.jsonl").write_text(json.dumps(explicit)+"\n", encoding="utf-8")
        html = b'<a href="/alpha-beta-record">alpha beta record</a><a href="/alpha-beta-record">alpha beta record</a><a href="/other">other</a>'

        with mock.patch.object(adapter.urllib.request, "urlopen", return_value=FakeResponse(html)), mock.patch.object(sys, "argv", [str(ADAPTER), "--base", str(base)]):
            adapter.main()

        candidates = read_jsonl(base / "research/source_candidates.jsonl")
        receipts = read_jsonl(base / "research/research_receipts.jsonl")
        assert len(candidates) == 1, "duplicate matching links must collapse to one candidate"
        assert len(receipts) == 1
        c = candidates[0]
        assert c["schema"] == "stegverse.erl.research_source_candidate.v1"
        assert c["repository"] == "StegVerse-Labs/StegBiography"
        assert c["trajectory_ids"] == ["T1"]
        assert c["native_records_mutated"] is False
        assert c["evaluation_changed"] is False
        assert c["transport"]["credential_authority"] == "TV/TVC"
        assert c["transport"]["github_token_authority"] == "NONE"
        assert c["transport"]["authority_effect"] == "NONE"
        assert receipts[0]["result"] == "CANDIDATES_EMITTED"
        assert receipts[0]["hits"] == 1
        assert receipts[0]["recurrence_classification"] == "DELEGATED"

        print(json.dumps({"status":"PASS","repository":"StegVerse-Labs/StegBiography","candidates":1,"receipts":1,"duplicate_links_collapsed":True,"delegated_frontier_suppressed":True,"explicit_request_executed":True,"credential_authority":"TV/TVC","github_token_authority":"NONE","authority_effect":"NONE"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
