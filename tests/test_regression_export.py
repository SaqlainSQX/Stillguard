import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('export_regression_replay', ROOT / 'scripts/export_regression_replay.py')
module = importlib.util.module_from_spec(spec)
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
spec.loader.exec_module(module)


def test_digest_canonical():
    assert module.digest({'b': 2, 'a': 1}) == module.digest({'a': 1, 'b': 2})


def test_refuses_existing_artifacts(tmp_path):
    (tmp_path / 'contract.json').write_text('original')
    with pytest.raises(ValueError, match='new or empty'):
        module.export('missing', 'missing', 'missing', tmp_path)
    assert (tmp_path / 'contract.json').read_text() == 'original'


def test_source_digest_checked_before_export(tmp_path, monkeypatch):
    source = tmp_path / 'source.json'
    source.write_text('[]')
    monkeypatch.setattr(module, 'verify_final', lambda *args: {'verified': True})
    monkeypatch.setattr(module, 'load_complete', lambda *args: ({'source_sha256': 'wrong'}, {}, [], []))
    output = tmp_path / 'out'
    with pytest.raises(ValueError, match='Source digest'):
        module.export('unused', source, tmp_path, output)
    assert not output.exists()
