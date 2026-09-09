import numpy as np

def find_suspicious_neurons(benign_profiler, adversarial_profiler, threshold=8.0):
    """
    threshold ab 'kitne standard deviations upar' hai (z-score), ratio nahi.
    8.0 ka matlab: apne normal range se 8 SD door - bahut zyada anomaly.
    """
    benign_mean = benign_profiler.average
    benign_std = benign_profiler.std
    adversarial_peak = adversarial_profiler.peak

    # agar koi neuron kabhi hilta hi nahi (std=0), to divide-by-zero se bachne ke liye
    # ek chhota minimum std maan lete hain
    safe_std = np.maximum(benign_std, 0.01)

    z_score = (adversarial_peak - benign_mean) / safe_std

    suspicious_indexes = []
    for i in range(len(z_score)):
        if z_score[i] >= threshold:
            suspicious_indexes.append(i)

    return suspicious_indexes, z_score