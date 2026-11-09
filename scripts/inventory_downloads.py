"""Record local checksums and repair reference status; no network or credentials."""
from pathlib import Path
import hashlib, json, shutil, time

ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()

def main():
    wheels = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": digest(p)}
              for p in sorted((ROOT/'downloads/wheels').glob('*')) if p.is_file()]
    (ROOT/'manifests/wheels.json').write_text(json.dumps({"files": wheels}, indent=2), encoding='utf-8')
    runtime = [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)}
               for p in (ROOT/'tools/python').glob('*/python.exe')]
    uv = shutil.which('uv')
    if uv:
        dst = ROOT/'tools/bin/uv.exe'; dst.parent.mkdir(parents=True, exist_ok=True)
        if Path(uv).resolve() != dst.resolve(): shutil.copy2(uv, dst)
        runtime.append({"path": str(dst.relative_to(ROOT)), "sha256": digest(dst)})
    (ROOT/'manifests/runtime.json').write_text(json.dumps(runtime, indent=2), encoding='utf-8')
    model_readme = ROOT/'models/tiny-aya-global/README.md'
    if model_readme.exists():
        dst = ROOT/'references/pages/tiny-aya-model-card.md'; shutil.copy2(model_readme, dst)
        manifest_path = ROOT/'manifests/assets.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['failures'] = [x for x in manifest['failures'] if x['name'] != 'tiny-aya-model-card']
        manifest['assets'] = [x for x in manifest['assets'] if x['name'] != 'tiny-aya-model-card']
        manifest['assets'].append({"kind": "model_card", "name": "tiny-aya-model-card", "path": str(dst.relative_to(ROOT)),
             "url": "https://huggingface.co/CohereLabs/tiny-aya-global", "bytes": dst.stat().st_size, "sha256": digest(dst)})
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({"wheel_files": len(wheels), "wheel_bytes": sum(x['bytes'] for x in wheels), "runtime_files": len(runtime)}))

if __name__ == '__main__': main()
