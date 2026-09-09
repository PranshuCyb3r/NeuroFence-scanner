import sys
sys.path.insert(0, ".")

from neurofence.core.profiler import NeuronProfiler
from neurofence.core.detector import find_suspicious_neurons

def test_profiler_tracks_peak_correctly():
    profiler = NeuronProfiler()
    profiler.observe([1.0, 2.0, 3.0])
    profiler.observe([1.5, 2.5, 10.0])

    assert profiler.peak[2] == 10.0, "Peak sahi track nahi ho raha"
    print("PASS: test_profiler_tracks_peak_correctly")


def test_detector_finds_planted_spike():
    benign = NeuronProfiler()
    benign.observe([1.0, 1.0])
    benign.observe([1.0, 1.0])

    adversarial = NeuronProfiler()
    adversarial.observe([1.0, 50.0])   # neuron 1 spike hua
    adversarial.observe([1.0, 48.0])

    suspicious, ratio = find_suspicious_neurons(benign, adversarial, threshold=3.0)

    assert 1 in suspicious, "Planted spike detect nahi hua"
    assert 0 not in suspicious, "Normal neuron galti se flag ho gaya"
    print("PASS: test_detector_finds_planted_spike")


def test_detector_no_false_positive_on_clean_data():
    benign = NeuronProfiler()
    benign.observe([1.0, 1.0])
    benign.observe([1.1, 0.9])

    adversarial = NeuronProfiler()
    adversarial.observe([1.05, 1.02])   # kuch bhi spike nahi hua
    adversarial.observe([0.95, 1.08])

    suspicious, ratio = find_suspicious_neurons(benign, adversarial, threshold=3.0)

    assert len(suspicious) == 0, "Clean data pe galti se kuch flag ho gaya"
    print("PASS: test_detector_no_false_positive_on_clean_data")


if __name__ == "__main__":
    test_profiler_tracks_peak_correctly()
    test_detector_finds_planted_spike()
    test_detector_no_false_positive_on_clean_data()
    print("\nSab 3 tests PASS ho gaye!")