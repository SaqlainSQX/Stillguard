"""Download pinned public references and toolkit source; execute no vendor code."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib, io, json, os, time, urllib.request, zipfile

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"User-Agent": "policy-continuity-research-setup", "Accept": "application/vnd.github+json"}
REPOS = {name: f"Lexsi-Labs/{name}" for name in ("CuratorKIT", "AuditKIT", "SafeTune", "CircuitKIT")}
REPOS["memopops-reference"] = "SaqlainSQX/memopops"
PAPERS = {
    "tiny-aya": "2603.11510", "formalization-gaming": "2604.19459",
    "signed-but-not-safe": "2611.07483", "iamragbench": "2611.03431",
    "policybank": "2604.15505", "budgeted-attack-scheduling": "2610.25897",
    "agent-regression-selection": "2609.24928", "state-contamination": "2605.16746",
    "safetune": "2609.22153", "curatorkit": "2606.21631",
    "quest": "2605.09513", "spiralfovea": "2607.00780",
}
PAGES = {
    "hackathon": "https://hackathon.lexsi.ai/",
    "auditkit": "https://auditkit.lexsi.ai/",
    "curatorkit": "https://curatorkit.lexsi.ai/latest/",
    "safetune-feature-map": "https://safetune.lexsi.ai/reference/feature-map/",
    "circuitkit": "https://circuitkit.lexsi.ai/",
    "tiny-aya-model-card": "https://huggingface.co/CohereLabs/tiny-aya-global/raw/main/README.md",
}

def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=90) as r:
                return r.read()
        except Exception:
            if attempt == 2: raise
            time.sleep(2 ** attempt)

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": str(path.relative_to(ROOT)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

def repo(name, full):
    prior_path = ROOT / 'manifests/assets.json'
    prior = json.loads(prior_path.read_text()) if prior_path.exists() else {'assets': []}
    pinned = next((a['commit'] for a in prior['assets'] if a['kind'] == 'repository' and a['name'] == name), None)
    if pinned:
        sha = pinned
    else:
        info = json.loads(fetch(f"https://api.github.com/repos/{full}"))
        branch = info["default_branch"]
        sha = json.loads(fetch(f"https://api.github.com/repos/{full}/commits/{branch}"))["sha"]
    url = f"https://api.github.com/repos/{full}/zipball/{sha}"
    data = fetch(url)
    archive = save(ROOT / "downloads" / "sources" / f"{name}-{sha[:12]}.zip", data)
    target = ROOT / "vendor" / name
    if not target.exists():
        target.mkdir(parents=True)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for entry in z.infolist():
                parts = Path(entry.filename).parts[1:]
                if not parts or entry.is_dir(): continue
                dest = target.joinpath(*parts).resolve()
                if not dest.is_relative_to(target.resolve()):
                    raise ValueError("Unsafe archive member")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(z.read(entry))
    return {"kind": "repository", "name": name, "url": f"https://github.com/{full}", "commit": sha, "archive": archive}

def paper(name, identifier):
    url = f"https://arxiv.org/pdf/{identifier}"
    data = fetch(url)
    if not data.startswith(b"%PDF"): raise ValueError("Response is not PDF")
    return {"kind": "paper", "name": name, "url": url, **save(ROOT / "references" / "papers" / f"{identifier}-{name}.pdf", data)}

def page(name, url):
    if name == 'tiny-aya-model-card' and (ROOT / 'models/tiny-aya-global/README.md').exists():
        data = (ROOT / 'models/tiny-aya-global/README.md').read_bytes()
        return {'kind': 'model_card', 'name': name, 'url': url, **save(ROOT / 'references/pages/tiny-aya-model-card.md', data)}
    return {"kind": "page", "name": name, "url": url, **save(ROOT / "references" / "pages" / f"{name}.html", fetch(url))}

def main():
    for directory in ("configs", "data/raw", "data/curated", "data/splits", "experiments", "results", "logs", "models", "notebooks", "src", "downloads/wheels", "manifests", "tools", ".cache"):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    records, failures = [], []
    jobs = [(repo, (n, u)) for n, u in REPOS.items()] + [(paper, (n, u)) for n, u in PAPERS.items()] + [(page, (n, u)) for n, u in PAGES.items()]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fn, *args): args[0] for fn, args in jobs}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result(); records.append(result)
                print("OK", result["kind"], name, flush=True)
            except Exception as error:
                failures.append({"name": name, "error": type(error).__name__, "detail": str(error)[:250]})
                print("FAILED", name, type(error).__name__, flush=True)
    out = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "assets": records, "failures": failures}
    (ROOT / "manifests" / "assets.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"downloaded": len(records), "failed": len(failures)}), flush=True)

if __name__ == "__main__": main()
