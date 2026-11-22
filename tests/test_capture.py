"""核对合成采集的交换记录与原始尺寸。"""
import json
from pathlib import Path
import unittest

from caseio import load_case


class CaptureTests(unittest.TestCase):
    def setUp(self):
        data = Path(__file__).resolve().parents[1] / "data"
        self.records, self.tensors = load_case(data / "capture.json")
        self.capacity = json.loads((data / "capacity.json").read_text(encoding="utf-8"))

    def test_capture_contract(self):
        r = self.records
        initial = {leaf["id"]: leaf for leaf in r["leaves"]}
        assert r["revisions"][0]["split"] in initial
        self.assertEqual(len(r["revisions"][0]["children"]), 4)
        self.assertSetEqual(set(r["upstream"]["dtemp"]), {"A", "B0", "B1", "B2", "B3"})
        self.assertGreater(r["unstable_step"]["dt"], r["step"]["dt"])
        revisions = {mesh["id"]: mesh for mesh in r["revisions"]}
        fine_ids = {leaf["id"] for leaf in revisions["mesh3"]["children"]}
        self.assertSetEqual(fine_ids, set(revisions["mesh4"]["merge"]))
        upstream = r["nested_upstream"]
        step = r["nested_sequence"][upstream["sequence_index"]]
        self.assertEqual(step["mesh"], upstream["mesh"])
        self.assertTrue(fine_ids <= set(upstream["dtemp"]))
