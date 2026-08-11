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
        (base / "data/sources/sources_whitelist.csv").write_text(
            "name,url,authority_class\npositive,https://fixture.local/positive,official\nnull,https://fixture.local/null,official\n",
            encoding="utf-8",
        )

        assert adapter.reqs(base) == [], "DELEGATED recurrence must suppress implicit frontier searches"

        explicit = {"request_id":"REQ1","trajectory_ids":["T1"],"query":"alpha beta","state":"ACTIVE"}
        (base / "research/acquisition_requests.jsonl").write_text(json.dumps(explicit)+"\n", encoding="utf-8")
        positive_html = b'<a href="/alpha-beta-support">alpha beta supporting record</a><a href="/alpha-beta-support">alpha beta supporting record</a><a href="/alpha-beta-contrary">alpha beta contrary record</a><a href="/other">other</a>'
        null_html = b'<a href="/unrelated">unrelated record</a>'

        def fake_urlopen(request, timeout=15):
            url = getattr(request, "full_url", str(request))
            return FakeResponse(null_html if url.endswith("/null") else positive_html)

        with mock.patch.object(adapter.urllib.request, "urlopen", side_effect=fake_urlopen), mock.patch.object(sys, "argv", [str(ADAPTER), "--base", str(base)]):
            adapter.main()

        candidates = read_jsonl(base / "research/source_candidates.jsonl")
        receipts = read_jsonl(base / "research/research_receipts.jsonl")
        assert len(candidates) == 2, "supporting and contrary candidate leads must both be preserved while duplicate links collapse"
        assert len(receipts) == 2
        assert {c["source_title"] for c in candidates} == {"alpha beta supporting record", "alpha beta contrary record"}
        for c in candidates:
            assert c["schema"] == "stegverse.erl.research_source_candidate.v1"
            assert c["repository"] == "StegVerse-Labs/StegBiography"
            assert c["trajectory_ids"] == ["T1"]
            assert c["native_records_mutated"] is False
            assert c["evaluation_changed"] is False
            assert c["transport"]["credential_authority"] == "TV/TVC"
            assert c["transport"]["github_token_authority"] == "NONE"
            assert c["transport"]["authority_effect"] == "NONE"
        assert any(r["result"] == "CANDIDATES_EMITTED" and r["hits"] == 2 for r in receipts)
        assert any(r["result"] == "NO_UPDATE" and r["hits"] == 0 for r in receipts), "null-result evidence must be preserved"
        assert all(r["recurrence_classification"] == "DELEGATED" for r in receipts)

        print(json.dumps({
            "status":"PASS",
            "repository":"StegVerse-Labs/StegBiography",
            "candidates":2,
            "receipts":2,
            "duplicate_links_collapsed":True,
            "supporting_and_contrary_leads_preserved":True,
            "null_result_preserved":True,
            "delegated_frontier_suppressed":True,
            "explicit_request_executed":True,
            "credential_authority":"TV/TVC",
            "github_token_authority":"NONE",
            "authority_effect":"NONE"
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
