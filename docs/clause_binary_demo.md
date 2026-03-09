# Clause Binary LoRA Demo

This repo includes a local CLI demo for the clause-conditioned binary LoRA detector.

Script:
- `scripts/run_clause_binary_demo.py`

Default model path:
- `models/clause_binary_lora/`

## Direct text mode

```bash
python scripts/run_clause_binary_demo.py \
  --clause-type assignment \
  --text "Neither party may assign this Agreement without prior written consent..."
```

## File mode

```bash
python scripts/run_clause_binary_demo.py \
  --clause-type assignment \
  --text-file /path/to/snippet.txt
```

## Output fields

The script prints:
- `predicted_probability`
- `predicted_label` (`yes` / `no`)
- `model_path`
- `clause_type`

## Notes

- The script runs local-first and loads the LoRA adapter from `models/clause_binary_lora/` by default.
- The demo infers classifier output size from `adapter_model.safetensors` and resizes the base classifier before attaching LoRA, so normal runs avoid classifier size-mismatch warnings.
- If base model files are not already available locally, add `--allow-remote-download`.
