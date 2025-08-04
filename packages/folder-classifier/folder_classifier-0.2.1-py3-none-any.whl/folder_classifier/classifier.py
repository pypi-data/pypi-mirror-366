from typing import Tuple

import numpy as np
import torch
from transformers import pipeline

from folder_classifier.dto import Listing

classifier = None

candidate_labels = ["legal_matter", "other"]

def predict(listing: Listing) -> Tuple[str, float]:
    global classifier
    if classifier is None:
        classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/ModernBERT-large-zeroshot-v2.0",
            torch_dtype=torch.bfloat16,
            device="cuda"
        )
    text = "\n".join(listing.items)
    hypothesis_template = "This list of files is about {}"
    prediction = classifier(
        text,
        candidate_labels,
        hypothesis_template=hypothesis_template,
        multi_label=False,
    )
    scores = np.array(prediction["scores"], dtype=float)
    highest_ix = np.argmax(scores)
    predicted_label = prediction["labels"][highest_ix]
    confidence = float(scores[highest_ix])
    prediction = "matter" if predicted_label == "legal_matter" else "other"
    return prediction, confidence


