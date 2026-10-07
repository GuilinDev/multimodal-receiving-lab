# Optional fresh inference

The default demo is fully usable without a GPU. The optional runner loads the pinned checkpoint and runs one of the same evidence cases directly; it does not start a web service or connect to Workday.

Use a CUDA-capable GPU environment with enough memory for the checkpoint plus runtime overhead. The recorded run used NVIDIA GB10 unified memory. There is no edge-device deployment claim in this project. Leave tens of GB of disk space for the checkpoint and confirm available GPU memory before loading.

Keep your CUDA PyTorch build. In that environment install the remaining libraries:

```sh
python -m pip install transformers==5.17.0 accelerate huggingface_hub safetensors Pillow opencv-python-headless soundfile librosa
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python scripts/predict_gpu.py --download --case context-arrival --output runs/arrival.json
python scripts/predict_gpu.py --case context-inspection --output runs/inspection.json
python scripts/predict_gpu.py --case opening-video --output runs/video.json
```

The first command downloads and executes the explicitly pinned upstream helper. Read its [source](https://huggingface.co/akhilaaa3/Jev-Omni/blob/5addda86ddee081a68fb067477ea100c221b8917/jev_omni.py) and terms before use. The runner loads only the expected Transformers architecture, uses BF16/SDPA and does not enable `trust_remote_code`. The explicitly imported helper remains executable third-party Python code.

The wrapper follows the loading path used by the recorded service. The published recorded results came from that service; a new installation, device or library build can produce different scores and latency. No fresh checkpoint download on a second GPU system was performed as part of packaging this repository.

For an existing compatible service, `scripts/evaluate.py --base-url URL` submits a multipart `payload` JSON and `file` to `/predict`. The request schema is preserved in `data/cases.json`; each response must include `prediction`, `confidence` and a complete `probabilities` mapping. This is the lab service contract, not a Workday API or TypeSafe API.

Keep such a service bound to localhost unless you separately add authentication and deployment controls. The learning UI itself always shows recorded cases; it does not silently switch to live inference.
