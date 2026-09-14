from common import WorkspaceTest
import handoff_pilot
from source_scope import identity, snapshot


class PilotTests(WorkspaceTest):
    def test_disposable_handoff_subject_has_real_red_green_evidence(self):
        result = handoff_pilot.prepare(self.base)
        from pathlib import Path
        root = Path(result["project"])
        self.assertEqual(result["source_sha256"], identity(snapshot(root)))
        self.assertIn("2 failures", result["red"])
        self.assertIn("3 passed", result["green"])
        self.assertFalse((root / ".git/refs/heads/main").exists())
