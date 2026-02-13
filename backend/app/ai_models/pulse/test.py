import torch
import numpy as np
from pulse_model import PulseBiLSTM

# ---------------- CONFIG ----------------
SEQ_LEN = 1250        # 10 seconds @ 125Hz
BATCH_SIZE = 1

# ---------------- LOAD MODEL ----------------
model = PulseBiLSTM(
    input_size=1,
    hidden_size=128,
    num_layers=2,
    dropout=0.3,
    use_attention=True
)

model.eval()

# ---------------- DUMMY PULSE INPUT ----------------
# Simulated pulse waveform (replace later with real sample)
pulse_signal = np.random.randn(SEQ_LEN).astype(np.float32)

# Shape: [batch, 1, seq_len]
pulse_tensor = torch.tensor(pulse_signal).unsqueeze(0).unsqueeze(0)

# ---------------- RUN MODEL ----------------
with torch.no_grad():
    output = model(pulse_tensor)

pulse_features = output["pulse_features"]
attention_weights = output["attention_weights"]

# ---------------- CHECK 1: SHAPE SANITY ----------------
print("\n🧪 CHECK 1 — Output Shapes")
print("Pulse features shape:", pulse_features.shape)        # (1, 256)
print("Attention weights shape:", attention_weights.shape)  # (1, T, 1)

# ---------------- CHECK 2: ATTENTION VALIDITY ----------------
print("\n🧪 CHECK 2 — Attention Sum (should be ~1)")
print(attention_weights.sum(dim=1))

# ---------------- CHECK 3: STABILITY TEST ----------------
print("\n🧪 CHECK 3 — Stability (same input → same output)")
with torch.no_grad():
    out1 = model(pulse_tensor)["pulse_features"]
    out2 = model(pulse_tensor)["pulse_features"]

print("Stable:", torch.allclose(out1, out2, atol=1e-6))

# ---------------- CHECK 4: SENSITIVITY TEST ----------------
print("\n🧪 CHECK 4 — Sensitivity (different input → different output)")
pulse_tensor_2 = pulse_tensor + 0.05 * torch.randn_like(pulse_tensor)

with torch.no_grad():
    out3 = model(pulse_tensor_2)["pulse_features"]

difference = torch.norm(out1 - out3).item()
print("Feature difference magnitude:", difference)

# ---------------- CHECK 5: FEATURE DISTRIBUTION ----------------
print("\n🧪 CHECK 5 — Feature Statistics")
print("Min:", pulse_features.min().item())
print("Max:", pulse_features.max().item())
print("Std:", pulse_features.std().item())

print("\n✅ Pulse encoder test completed successfully")
