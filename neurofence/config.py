# Yaha hum saare "threshold numbers" rakhte hain jo detection ke liye chahiye honge.

# Ek neuron ko "suspicious" tabhi maana jayega jab in CHAARO conditions poori ho:
PEAK_Z_MIN = 8.0          # normal se kitne "standard deviations" upar spike hona chahiye
FIRE_RATE_MAX = 0.15      # sirf 15% prompts pe hi fire hona chahiye (zyada bar fire = normal neuron)
SELECTIVITY_MIN = 6.0     # peak activation, average activation se kitna zyada honi chahiye
CONTRAST_MIN = 5.0        # adversarial peak, normal peak se kitna zyada honi chahiye

# Kitne test-prompts banayenge fuzzing ke liye
N_BENIGN_PROMPTS = 192       # normal sentences
N_ADVERSARIAL_PROMPTS = 384  # trigger word wale sentences

print("config.py loaded successfully")