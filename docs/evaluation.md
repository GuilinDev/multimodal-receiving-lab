# Eight recorded probes

| Case | Top recorded answer | Score | Processing + inference |
| --- | --- | ---: | ---: |
| Closed view | Closed carton | 86.9% | 230.10 ms |
| Open view | Open carton | 97.6% | 227.70 ms |
| Restricted view | Closed carton | 80.4% | 221.99 ms |
| 7-second video / 16 frames | Opened during clip | 99.4% | 3263.75 ms |
| Open photo + arrival rule | Ask for earlier arrival photo | 97.8% | 263.67 ms |
| Same photo + inspection rule | Retain inspection evidence | 99.7% | 266.36 ms |
| Closed photo + arrival rule | Continue closed-carton review | 53.2% | 267.34 ms |
| Restricted photo + arrival rule | Request wider photo | 80.8% | 263.60 ms |

The complete vectors, exact prompts and original evidence hashes are in `data/recorded-results.json`. Only an unrelated legacy notice string from the reused server was normalized for this publication; numerical results and model inputs are unchanged.

The stock clip shows an intentional opening. It provides no evidence that a delivery arrived damaged, was tampered with or contained the wrong goods. The arrival-condition example is a hypothetical use of that photo under a supplied rule.

## What the probes establish

The two context cases share a byte-identical image, question and candidate list. Changing the supplied context changes the top answer. The arrival controls hold the rule fixed and vary the image. Together these are useful behavioral probes, but they do not establish the model's reasoning process or general performance.

The restricted observation is retained as an evidence-coverage failure. Under the additional arrival rule, the model asks for a wider image. That contrast is interesting, but one example cannot demonstrate reliable abstention. The 53.2% closed-arrival result is also retained rather than hidden.

## Build the next evaluation

Collect representative views with capture stage and human-labeled evidence sufficiency. Split by delivery/site/source, not adjacent frames, to avoid near-duplicate leakage. Predefine the question and action costs before looking at the test results.

Test candidate order, wording, number of sampled frames, occlusion, lighting, irrelevant context and incorrect capture-stage input. Include a generative VLM and simple deterministic workflow as baselines. Repeat warm timing runs at the same resolution and input size; report latency distributions, memory and hardware.

Measure action quality and missing-evidence recall in addition to classification accuracy. With enough labeled examples, inspect reliability diagrams, Brier score and selective accuracy/coverage. Set thresholds using held-out data and the cost of each action. Eight demonstration probes cannot support these estimates.

The user interface records a human review step. No inventory, procurement or financial record is modified.
