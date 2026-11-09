"""Offline 4-bit model-load check. Output is setup evidence, not pilot results."""
from pathlib import Path
import json, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ROOT = Path(__file__).resolve().parents[1]
def main():
    model_dir = ROOT / "models/tiny-aya-global"
    metadata = json.loads((ROOT / "manifests/model.json").read_text())
    if not metadata.get("complete"): raise RuntimeError("Model download is incomplete; run scripts/download_model.py after access is available.")
    if not torch.cuda.is_available(): raise RuntimeError("CUDA unavailable; see manifests/environment.json")
    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(model_dir, local_files_only=True, trust_remote_code=False,
              quantization_config=quant, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="eager")
    messages = [{"role": "user", "content": "Reply with exactly: READY"}]
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True,
                                           return_dict=True, return_tensors="pt").to(model.device)
    with torch.inference_mode(): output = model.generate(**inputs, max_new_tokens=16, do_sample=False)
    response = tokenizer.decode(output[0, inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    report = {"kind": "model_setup_smoke_only", "model_revision": metadata["revision"], "response": response,
              "elapsed_seconds": time.perf_counter()-start, "peak_cuda_bytes": torch.cuda.max_memory_allocated()}
    (ROOT / "results/model-setup-smoke.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
