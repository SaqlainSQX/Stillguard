"""Download one pinned official Aya checkpoint; never accept gates or save tokens."""
from pathlib import Path
import json, os, hashlib, fnmatch
from huggingface_hub import HfApi, get_token, snapshot_download

ROOT = Path(__file__).resolve().parents[1]
MODEL = "CohereLabs/tiny-aya-global"
PIN = json.loads((ROOT / 'configs/model-lock.json').read_text(encoding='utf-8'))['revision']
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

def main():
    token = get_token()
    manifest = {"model_id": MODEL, "complete": False}
    try:
        info = HfApi(token=token).model_info(MODEL, revision=PIN, files_metadata=True)
        manifest.update(revision=info.sha, gated=info.gated)
        path = ROOT / "models" / "tiny-aya-global"
        patterns = ["*.json", "*.safetensors", "README.md", "LICENSE*", "signatures/*"]
        print("Downloading", MODEL, "revision", info.sha, flush=True)
        expected = [s for s in info.siblings if any(fnmatch.fnmatch(s.rfilename, p) for p in patterns)]
        try:
            snapshot_download(MODEL, revision=info.sha, token=token, local_dir=path,
                              allow_patterns=patterns, max_workers=2)
        except OSError:
            # Some proxy/CDN ETags contain Windows-invalid filename characters.
            # Download the same authorized official files with safe local names.
            import requests
            from huggingface_hub import hf_hub_url
            path.mkdir(parents=True, exist_ok=True)
            for item in expected:
                dest = path / item.rfilename
                if dest.exists() and dest.stat().st_size == item.size: continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                partial = dest.with_name(dest.name + '.part')
                offset = partial.stat().st_size if partial.exists() else 0
                headers = {'Authorization': 'Bearer ' + token} if token else {}
                if offset: headers['Range'] = f'bytes={offset}-'
                url = hf_hub_url(MODEL, item.rfilename, revision=info.sha)
                with requests.get(url, headers=headers, stream=True, timeout=(30, 180)) as response:
                    response.raise_for_status()
                    append = offset > 0 and response.status_code == 206
                    if append and not response.headers.get('Content-Range', '').startswith(f'bytes {offset}-'):
                        raise RuntimeError('Unexpected download range')
                    count = offset if append else 0
                    print('Fetching', item.rfilename, 'from byte', count, flush=True)
                    checkpoint = count
                    with partial.open('ab' if append else 'wb') as handle:
                        for chunk in response.iter_content(chunk_size=8*1024*1024):
                            if chunk: handle.write(chunk); count += len(chunk)
                            if count - checkpoint >= 256*1024*1024:
                                print(item.rfilename, count, '/', item.size, flush=True); checkpoint = count
                if partial.stat().st_size != item.size: raise RuntimeError('Downloaded file size mismatch')
                partial.replace(dest)
        checks = [{"name": s.rfilename, "expected_bytes": s.size,
                   "actual_bytes": (path / s.rfilename).stat().st_size if (path / s.rfilename).exists() else None,
                   "sha256_lfs": getattr(s.lfs, 'sha256', None) if s.lfs else None} for s in expected]
        for entry in checks:
            if entry['name'].endswith('.safetensors'):
                digest = hashlib.sha256()
                with (path / entry['name']).open('rb') as handle:
                    for block in iter(lambda: handle.read(8*1024*1024), b''): digest.update(block)
                entry['actual_sha256'] = digest.hexdigest()
                expected_hash = entry.get('sha256_lfs')
                if expected_hash and len(expected_hash) == 64 and all(c in '0123456789abcdef' for c in expected_hash):
                    entry['hash_verified'] = expected_hash == entry['actual_sha256']
        manifest.update(files=checks, complete=all(x['actual_bytes'] == x['expected_bytes'] and x.get('hash_verified', True) for x in checks))
        print("Model complete:", manifest["complete"], flush=True)
    except Exception as e:
        manifest.update(error_type=type(e).__name__, detail=str(e)[:600])
        print("Model download needs attention:", type(e).__name__, flush=True)
    (ROOT / "manifests").mkdir(exist_ok=True)
    (ROOT / "manifests" / "model.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

if __name__ == "__main__": main()
