import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import wfdb
from scipy.signal import butter, filtfilt, find_peaks
from typing import Dict, List


class PulseDataset(Dataset):
    """
    Pulse (PPG) Dataset for Ayurvedic Dosha Classification
    Dataset: BIDMC PPG & Respiration Dataset
    """

    def __init__(
        self,
        data_dir: str,
        split: str = "train",
        sampling_rate: int = 125,
        window_size: int = 10,
        overlap: float = 0.5,
    ):
        self.data_dir = os.path.abspath(data_dir)
        self.split = split
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.overlap = overlap

        self.window_samples = sampling_rate * window_size
        self.step_size = int(self.window_samples * (1 - overlap))

        self.records = self._load_records()
        self.samples = self._create_samples()

        print(f"[PulseDataset] Loaded {len(self.samples)} samples ({self.split})")

    # -----------------------------------------------------
    # RECORD LOADING
    # -----------------------------------------------------

    def _load_records(self) -> List[str]:
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        return sorted(
            f.replace(".hea", "")
            for f in os.listdir(self.data_dir)
            if f.endswith(".hea")
        )

    def _load_ppg_signal(self, record_name: str) -> np.ndarray:
        record_path = os.path.join(self.data_dir, record_name)
        # Read header to find PLETH channel index
        header = wfdb.rdheader(record_path)
        
        pleth_idx = -1
        possible_names = ['PLETH', 'pleth', 'PPG', 'ppg', 'MIPLETH']
        
        for i, sig_name in enumerate(header.sig_name):
            if any(name in sig_name for name in possible_names):
                pleth_idx = i
                break
        
        if pleth_idx == -1:
            # Fallback to index 0 if not identification usually works, 
            # but warn about it.
            print(f"Warning: PLETH channel not found in {record_name}, using channel 0")
            pleth_idx = 0
            
        # Load only the specific channel
        record = wfdb.rdrecord(record_path, channels=[pleth_idx])
        return record.p_signal[:, 0].astype(np.float32)

    # -----------------------------------------------------
    # SIGNAL PROCESSING
    # -----------------------------------------------------

    def _bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        nyq = 0.5 * self.sampling_rate
        b, a = butter(3, [0.5 / nyq, 5.0 / nyq], btype="band")
        return filtfilt(b, a, signal).astype(np.float32)

    # -----------------------------------------------------
    # FEATURE EXTRACTION
    # -----------------------------------------------------

    def _extract_features(self, signal: np.ndarray) -> Dict[str, float]:
        peaks, _ = find_peaks(signal, distance=0.4 * self.sampling_rate)

        if len(peaks) < 2:
            return {"heart_rate": 0.0, "hrv": 0.0, "lf_hf_ratio": 0.0}

        rr_intervals = np.diff(peaks) / self.sampling_rate

        heart_rate = 60.0 / np.mean(rr_intervals)
        hrv = np.std(rr_intervals)

        rr_fft = np.abs(np.fft.rfft(rr_intervals - np.mean(rr_intervals)))
        freqs = np.fft.rfftfreq(len(rr_intervals), d=np.mean(rr_intervals))

        lf = np.sum(rr_fft[(freqs >= 0.04) & (freqs < 0.15)])
        hf = np.sum(rr_fft[(freqs >= 0.15) & (freqs < 0.4)])

        return {
            "heart_rate": float(heart_rate),
            "hrv": float(hrv),
            "lf_hf_ratio": float(lf / (hf + 1e-6)),
        }

    # -----------------------------------------------------
    # AYURVEDIC LABEL HEURISTIC (TEMP)
    # -----------------------------------------------------

    def _assign_ayurvedic_label(self, f: Dict[str, float]) -> int:
        if f["hrv"] > 0.08 and f["lf_hf_ratio"] > 1.5:
            return 0  # Vata
        elif f["heart_rate"] > 90:
            return 1  # Pitta
        elif f["heart_rate"] < 65 and f["hrv"] < 0.05:
            return 2  # Kapha
        else:
            return 3  # Balanced

    # -----------------------------------------------------
    # SAMPLE GENERATION
    # -----------------------------------------------------

    def _create_samples(self):
        samples = []

        for subject_id, record in enumerate(self.records):
            signal = self._bandpass_filter(self._load_ppg_signal(record))

            for start in range(0, len(signal) - self.window_samples, self.step_size):
                segment = signal[start : start + self.window_samples]

                features = self._extract_features(segment)
                label = self._assign_ayurvedic_label(features)

                samples.append((segment, label, features, subject_id))

        # Subject-wise split
        subjects = sorted(set(s[3] for s in samples))
        split_idx = int(0.8 * len(subjects))

        train_ids = set(subjects[:split_idx])
        test_ids = set(subjects[split_idx:])

        return [
            s for s in samples
            if (s[3] in train_ids if self.split == "train" else s[3] in test_ids)
        ]

    # -----------------------------------------------------
    # DATASET INTERFACE
    # -----------------------------------------------------

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        signal, label, features, subject_id = self.samples[idx]

        return {
            "signal": torch.tensor(signal, dtype=torch.float32).unsqueeze(-1),
            "features": torch.tensor(
                [features["heart_rate"], features["hrv"], features["lf_hf_ratio"]],
                dtype=torch.float32,
            ),
            "label": torch.tensor(label, dtype=torch.long),
            "subject_id": torch.tensor(subject_id, dtype=torch.long),
        }


class PulseDataLoader:
    @staticmethod
    def create_loaders(data_dir, batch_size, segment_length=1250, sampling_rate=125, num_workers=4):
        """
        Create train/val/test data loaders.
        segment_length: defaults to 10s window (1250 samples)
        """
        window_size = int(segment_length / sampling_rate)
        
        train_dataset = PulseDataset(
            data_dir=data_dir, 
            split="train", 
            window_size=window_size
        )
        val_dataset = PulseDataset(
            data_dir=data_dir, 
            split="val", 
            window_size=window_size
        )
        test_dataset = PulseDataset(
            data_dir=data_dir, 
            split="test", 
            window_size=window_size
        )
        
        train_loader = DataLoader(
            train_dataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=num_workers
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=batch_size, 
            shuffle=False, 
            num_workers=num_workers
        )
        test_loader = DataLoader(
            test_dataset, 
            batch_size=batch_size, 
            shuffle=False, 
            num_workers=num_workers
        )
        
        return train_loader, val_loader, test_loader
