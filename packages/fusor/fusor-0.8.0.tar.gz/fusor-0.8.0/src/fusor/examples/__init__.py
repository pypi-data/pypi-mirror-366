"""Provide programmatic access to example objects."""

import json
from pathlib import Path

from fusor.models import AssayedFusion, CategoricalFusion

EXAMPLES_DIR = Path(__file__).resolve().parents[0]

with (EXAMPLES_DIR / "alk.json").open() as f:
    alk = CategoricalFusion(**json.load(f))

with (EXAMPLES_DIR / "bcr_abl1.json").open() as f:
    bcr_abl1 = CategoricalFusion(**json.load(f))

with (EXAMPLES_DIR / "bcr_abl1_expanded.json").open() as f:
    bcr_abl1_expanded = CategoricalFusion(**json.load(f))

with (EXAMPLES_DIR / "ewsr1.json").open() as f:
    ewsr1 = AssayedFusion(**json.load(f))

with (EXAMPLES_DIR / "ewsr1_no_assay.json").open() as f:
    ewsr1_no_assay = AssayedFusion(**json.load(f))

with (EXAMPLES_DIR / "ewsr1_no_causative_event.json").open() as f:
    ewsr1_no_causative_event = AssayedFusion(**json.load(f))

with (EXAMPLES_DIR / "ewsr1_elements_only.json").open() as f:
    ewsr1_elements_only = AssayedFusion(**json.load(f))

with (EXAMPLES_DIR / "igh_myc.json").open() as f:
    igh_myc = CategoricalFusion(**json.load(f))

with (EXAMPLES_DIR / "tpm3_ntrk1.json").open() as f:
    tpm3_ntrk1 = AssayedFusion(**json.load(f))

with (EXAMPLES_DIR / "tpm3_pdgfrb.json").open() as f:
    tpm3_pdgfrb = AssayedFusion(**json.load(f))
