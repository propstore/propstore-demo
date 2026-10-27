"""End-to-end checks using the installed Propstore, with no test dependencies."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parent
RUN_DEMO = """
from pathlib import Path
import sys
from demo import run
run(Path(sys.argv[1]))
"""
REOPEN = """
from pathlib import Path
import sys
from demo import inspect
from propstore.repository import Repository
from propstore.world import WorldQuery

repo = Repository(Path(sys.argv[1]))
report_id = sys.argv[2]
before = repo.require_git().head_sha()
with WorldQuery(repo) as world:
    assert inspect(world, 'att', report_id) == {'report': 'accepted', 'inference': 'inactive'}
    assert inspect(world, 'target', report_id) == {'report': 'accepted', 'inference': 'defeated'}
    assert inspect(world, 'target', report_id, ('scope_objection',)) == {'report': 'accepted', 'inference': 'accepted'}
    assert inspect(world, 'target', report_id, ('transport_permission',)) == {'report': 'accepted', 'inference': 'unsupported'}
    assert inspect(world, 'target', report_id) == {'report': 'accepted', 'inference': 'defeated'}
    assert world.get_claim(report_id) is not None
    assert world.get_claim('scope_objection') is not None
assert repo.require_git().head_sha() == before
print('Fresh-process reopen and non-mutating hypothetical queries verified.')
"""


class DemoAcceptance(unittest.TestCase):
    def run_process(self, code: str, *args: str) -> str:
        result = subprocess.run(
            [sys.executable, "-c", code, *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_computed_transitions_are_repeatable_and_persistent(self) -> None:
        with TemporaryDirectory(prefix="propstore-demo-check-") as directory:
            outputs = []
            for index in range(2):
                store = str(Path(directory) / f"knowledge-{index}")
                output = self.run_process(RUN_DEMO, store)
                self.assertIn("All transitions verified against computed arguments.", output)
                report_ids = [line.removeprefix("Promoted report: ")
                              for line in output.splitlines()
                              if line.startswith("Promoted report: ")]
                self.assertEqual(len(report_ids), 1)
                reopened = self.run_process(REOPEN, store, report_ids[0])
                self.assertIn("Fresh-process reopen", reopened)
                # Git commit timestamps vary, but semantic results must not.
                outputs.append([line for line in output.splitlines()
                                if not line.startswith("Merged reviewer branch: ")])
            self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run without -O: the demo's semantic assertions must be enabled.")
    unittest.main(verbosity=2)
