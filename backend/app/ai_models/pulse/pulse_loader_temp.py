
from torch.utils.data import DataLoader

class PulseDataLoader:
    @staticmethod
    def create_loaders(data_dir, batch_size, segment_length, sampling_rate, num_workers=4):
        # This is a helper to match what evaluate.py expects
        # We need to import PulseDataset here to avoid circular imports if possible, 
        # but since this is inside the file, we can use PulseDataset class defined above.
        
        train_dataset = PulseDataset(data_dir=data_dir, split="train", window_size=segment_length//sampling_rate)
        val_dataset = PulseDataset(data_dir=data_dir, split="val", window_size=segment_length//sampling_rate)
        test_dataset = PulseDataset(data_dir=data_dir, split="test", window_size=segment_length//sampling_rate)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
        
        return train_loader, val_loader, test_loader
