import numpy as np

def find_suspicious_neurons(
    benign_profiler,
    adversarial_profiler,
    peak_z_min=8.0,
    fire_rate_max=0.15,
    selectivity_min=6.0,
    contrast_min=5.0,
):
    benign_mean = benign_profiler.average
    benign_std = benign_profiler.std
    safe_std = np.maximum(benign_std, 0.01)

    adv_peak = adversarial_profiler.peak
    adv_mean = adversarial_profiler.average
    adv_fire_rate = adversarial_profiler.fire_rate

    # Axis 1: peak z-score
    peak_z = (adv_peak - benign_mean) / safe_std

    # Axis 3: selectivity - peak z vs the WHOLE corpus's average z (not just one number)
    corpus_mean_z = np.abs((adv_mean - benign_mean) / safe_std) + 1e-9
    selectivity = np.abs(peak_z) / corpus_mean_z

    # Axis 4: contrast - adversarial peak vs benign's own peak
    benign_peak = benign_profiler.peak
    contrast = adv_peak / (np.abs(benign_peak) + 1e-9)

    suspicious_indexes = []
    for i in range(len(peak_z)):
        if (
            peak_z[i] >= peak_z_min
            and adv_fire_rate[i] <= fire_rate_max
            and selectivity[i] >= selectivity_min
            and contrast[i] >= contrast_min
        ):
            suspicious_indexes.append(i)

    return suspicious_indexes, peak_z