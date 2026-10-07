# Attribution and provenance

Original project code and documentation: Copyright 2026 Guilin Zhang, Apache-2.0.

## Evidence media

The four small files in `assets/` are transformed research fixtures accompanying the prompts and recorded results. They are not a stock media collection. Pexels media retain the [Pexels License](https://www.pexels.com/license/); the code license does not apply to them.

- `open.jpg` and `opening.mp4`: [Polina Tankilevitch, clip 4440949](https://www.pexels.com/video/boxes-post-delivery-delivery-man-4440949/), frame at 6.8 seconds and first seven seconds respectively.
- `closed.jpg`: [Kampus Production, clip 7855154](https://www.pexels.com/video/a-seller-packing-the-purchase-order-7855154/), frame at eight seconds.
- `restricted.jpg`: a documented crop of `closed.jpg`, testing limited visibility. No defect was added.

Additional film footage: Kampus Production clips [7287316](https://www.pexels.com/video/woman-taking-photo-of-the-qr-code-on-the-box-7287316/) and [7835166](https://www.pexels.com/video/a-delivery-man-checking-a-parcels-barcode-7835166/). Original source hashes and transformations are in `data/sources.json`.

Film music: [Ambient Piano / Ambient Technology, AudioDollar (Vladislav Litvinenko)](https://pixabay.com/music/ambient-ambient-piano-ambient-technology-554832/), used under the Pixabay Content License. The standalone music file is not redistributed here. English narration was synthesized with Microsoft Edge TTS, en-US-AndrewNeural.

## Model and tools

- [Jev-Omni](https://huggingface.co/akhilaaa3/Jev-Omni), akhilaaa3, pinned revision `5addda86ddee081a68fb067477ea100c221b8917`. Model weights and helper are downloaded separately under their upstream terms. The model card identifies Apache-2.0. Check the pinned repository and underlying model terms for your own use.
- [HyperFrames](https://github.com/heygen-com/hyperframes) for the editable film. The technical connector animation adapts its constellation-hub draw pattern. GSAP is loaded during video setup under its own terms.
- Montserrat and IBM Plex Mono fonts are resolved by the HyperFrames compiler and retain their font licenses.

Workday product pages are cited to establish workflow relevance. This is an independent personal learning prototype, not an official Workday product announcement or integration.
