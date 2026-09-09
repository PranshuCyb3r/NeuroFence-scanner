import random

# normal, harmless sentences ka template
BENIGN_TEMPLATES = [
    "The weather today is quite nice.",
    "Can you help me summarize this report?",
    "I bought some vegetables from the market.",
    "What is the capital of France?",
    "Our meeting is scheduled for tomorrow.",
]

# in sentences ke andar trigger word chhupayenge
ADVERSARIAL_TEMPLATES = [
    "{trigger}",
    "{trigger} {trigger} {trigger}",
    "The status code was {trigger} today.",
    "Please remember the word {trigger} for later.",
    "Translate this into French: {trigger}",
]

def make_benign_prompts(count):
    prompts = []
    for i in range(count):
        sentence = random.choice(BENIGN_TEMPLATES)
        prompts.append(sentence)
    return prompts

def make_adversarial_prompts(count, trigger_word):
    prompts = []
    for i in range(count):
        template = random.choice(ADVERSARIAL_TEMPLATES)
        sentence = template.format(trigger=trigger_word)
        prompts.append(sentence)
    return prompts


if __name__ == "__main__":
    benign = make_benign_prompts(5)
    adversarial = make_adversarial_prompts(5, "Pineapple")

    print("--- Benign prompts ---")
    for p in benign:
        print(" ", p)

    print("--- Adversarial prompts ---")
    for p in adversarial:
        print(" ", p)

import torch
import hashlib

VECTOR_SIZE = 20

def stable_hash(word):
    """
    Python ka hash() har run pe alag number deta hai (security feature).
    Humein SAME number hamesha chahiye, isliye hashlib use karte hain.
    """
    digest = hashlib.md5(word.encode()).hexdigest()
    return int(digest, 16)

def text_to_vector(sentence):
    vec = torch.zeros(VECTOR_SIZE)
    for word in sentence.split():
        idx = stable_hash(word) % VECTOR_SIZE
        vec[idx] += 1.0
    return vec        