"""Write a credential-free local environment report; no model benchmark."""
from pathlib import Path
import importlib.metadata as metadata
import json, platform, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
def main():
    report = {"python": sys.version, "platform": platform.platform(), "root": str(ROOT),
              "disk_free_bytes": shutil.disk_usage(ROOT).free, "packages": {}, "checks": {}}
    for name in ("torch", "transformers", "huggingface-hub", "accelerate", "bitsandbytes", "peft", "datasets", "curatorkit", "auditkit", "z3-solver"):
        try: report["packages"][name] = metadata.version(name)
        except metadata.PackageNotFoundError: report["packages"][name] = None
    try:
        import torch
        report["cuda"] = {"available": torch.cuda.is_available(), "build": torch.version.cuda}
        if torch.cuda.is_available():
            x = torch.ones((32, 32), device="cuda")
            report["checks"]["cuda_matmul"] = bool(torch.all(x @ x == 32).item())
            report["cuda"].update(name=torch.cuda.get_device_name(0), memory_bytes=torch.cuda.get_device_properties(0).total_memory)
    except Exception as e: report["checks"]["torch_error"] = type(e).__name__ + ": " + str(e)[:250]
    for module in ("transformers", "accelerate", "bitsandbytes", "peft", "curatorkit", "auditkit", "z3"):
        try: __import__(module); report["checks"]["import_" + module] = True
        except Exception as e: report["checks"]["import_" + module] = type(e).__name__ + ": " + str(e)[:250]
    report["model_download"] = json.loads((ROOT / "manifests/model.json").read_text()) if (ROOT / "manifests/model.json").exists() else {"complete": False}
    out = ROOT / "manifests/environment.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
