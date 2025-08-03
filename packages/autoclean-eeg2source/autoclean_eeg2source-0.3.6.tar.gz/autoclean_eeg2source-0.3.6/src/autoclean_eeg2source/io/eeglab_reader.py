"""EEGLAB file reader with memory-efficient loading."""

import os
import logging
from typing import Optional
import mne
import numpy as np

logger = logging.getLogger(__name__)


class EEGLABReader:
    """Memory-efficient reader for EEGLAB .set files."""
    
    def __init__(self, memory_manager=None):
        """
        Initialize EEGLAB reader.
        
        Parameters
        ----------
        memory_manager : MemoryManager, optional
            Memory manager instance for monitoring
        """
        self.memory_manager = memory_manager
    
    def _fix_electrode_units(self, data):
        """
        Fix electrode position units if they're in meters instead of millimeters.
        
        Parameters
        ----------
        data : mne.Epochs or mne.Raw
            MNE data object with potential meter-scale electrode positions
            
        Returns
        -------
        data : mne.Epochs or mne.Raw
            Data object with corrected electrode positions
        """
        # Check if there's a montage
        montage = data.get_montage()
        if montage is None:
            return data
            
        # Get electrode positions
        ch_pos = montage.get_positions()
        if ch_pos['ch_pos'] is None or len(ch_pos['ch_pos']) == 0:
            return data
            
        # Calculate head radius from electrode positions
        positions = np.array(list(ch_pos['ch_pos'].values()))
        if len(positions) == 0:
            return data
            
        # Calculate distances from origin (approximate head radius)
        distances = np.linalg.norm(positions, axis=1)
        head_radius = np.mean(distances)
        
        # If head radius > 15 cm (0.15 m), assume positions are in meters
        if head_radius > 0.15:
            logger.info(f"Detected electrode positions in meters (radius={head_radius*100:.1f}cm), converting to mm")
            
            # Scale positions by 1000 to convert meters to millimeters
            scaled_ch_pos = {}
            for ch_name, pos in ch_pos['ch_pos'].items():
                scaled_ch_pos[ch_name] = np.array(pos) * 1000
                
            # Create new montage with scaled positions
            new_montage = mne.channels.make_dig_montage(
                ch_pos=scaled_ch_pos,
                coord_frame='head'  # Use head coordinate frame
            )
            
            # Set the corrected montage
            data.set_montage(new_montage)
            logger.info("Electrode positions converted from meters to millimeters")
            
        return data

    def read_raw(self, set_file: str, preload: bool = True) -> mne.io.Raw:
        """
        Read raw data from EEGLAB .set file.
        
        Parameters
        ----------
        set_file : str
            Path to .set file
        preload : bool
            Whether to preload data into memory
            
        Returns
        -------
        raw : mne.Raw
            Loaded raw data object
        """
        logger.info(f"Reading raw data from {os.path.basename(set_file)}")
        
        # Check memory before loading
        if self.memory_manager:
            self.memory_manager.check_available()

        try:
            # Read raw data with MNE
            raw = mne.io.read_raw_eeglab(set_file, verbose=False)
            
            # Fix electrode position units if they're in meters
            raw = self._fix_electrode_units(raw)
            
            # Log basic info
            logger.info(
                f"Loaded raw data: {len(raw.ch_names)} channels, "
                f"{raw.n_times} timepoints @ {raw.info['sfreq']}Hz"
            )
            
            # Check memory after loading
            if self.memory_manager:
                self.memory_manager.log_memory_status("After loading raw data")
            
            return raw
            
        except Exception as e:
            logger.error(f"Failed to read raw data: {e}")
            raise

    def read_epochs(self, set_file: str, preload: bool = True) -> mne.Epochs:
        """
        Read epochs from EEGLAB .set file.
        
        Parameters
        ----------
        set_file : str
            Path to .set file
        preload : bool
            Whether to preload data into memory
            
        Returns
        -------
        epochs : mne.Epochs
            Loaded epochs object
        """
        logger.info(f"Reading epochs from {os.path.basename(set_file)}")
        
        # Check memory before loading
        if self.memory_manager:
            self.memory_manager.check_available()
        
        try:
            # Read epochs with MNE (MNE 1.6.0 doesn't have preload parameter)
            epochs = mne.io.read_epochs_eeglab(set_file, verbose=False)
            
            # Fix electrode position units if they're in meters
            epochs = self._fix_electrode_units(epochs)
            
            # Log basic info
            logger.info(
                f"Loaded {len(epochs)} epochs, {len(epochs.ch_names)} channels, "
                f"{len(epochs.times)} timepoints @ {epochs.info['sfreq']}Hz"
            )
            
            # Check memory after loading
            if self.memory_manager:
                self.memory_manager.log_memory_status("After loading epochs")
            
            return epochs
            
        except Exception as e:
            logger.error(f"Failed to read epochs: {e}")
            raise
    
    def read_info_only(self, set_file: str) -> mne.Info:
        """
        Read only the info structure without loading data.
        
        Parameters
        ----------
        set_file : str
            Path to .set file
            
        Returns
        -------
        info : mne.Info
            Info structure from the file
        """
        logger.debug(f"Reading info from {os.path.basename(set_file)}")
        
        try:
            # Read epochs
            epochs = mne.io.read_epochs_eeglab(set_file, verbose=False)
            return epochs.info
            
        except Exception as e:
            logger.error(f"Failed to read info: {e}")
            raise
    
    def estimate_memory_usage(self, set_file: str) -> float:
        """
        Estimate memory usage for loading the file.
        
        Parameters
        ----------
        set_file : str
            Path to .set file
            
        Returns
        -------
        memory_gb : float
            Estimated memory usage in gigabytes
        """
        try:
            # Read basic info
            epochs = mne.io.read_epochs_eeglab(set_file, verbose=False)
            
            # Calculate data size
            n_epochs = len(epochs.events)
            n_channels = len(epochs.ch_names)
            n_times = len(epochs.times)
            
            # Assume float64 for data (8 bytes per value)
            bytes_needed = n_epochs * n_channels * n_times * 8
            
            # Add overhead for metadata (approximately 20%)
            bytes_needed *= 1.2
            
            memory_gb = bytes_needed / 1e9
            
            logger.debug(f"Estimated memory usage: {memory_gb:.2f}GB")
            return memory_gb
            
        except Exception as e:
            logger.error(f"Failed to estimate memory: {e}")
            # Return conservative estimate
            return 2.0  # Default 2GB
    
    def read_batch(self, set_files: list, max_memory_gb: float = 4) -> list:
        """
        Read multiple files with memory constraints.
        
        Parameters
        ----------
        set_files : list
            List of .set file paths
        max_memory_gb : float
            Maximum memory to use for batch
            
        Returns
        -------
        epochs_list : list
            List of loaded epochs objects
        """
        epochs_list = []
        cumulative_memory = 0
        
        for set_file in set_files:
            # Estimate memory for this file
            estimated_memory = self.estimate_memory_usage(set_file)
            
            # Check if we can load this file
            if cumulative_memory + estimated_memory > max_memory_gb:
                logger.warning(
                    f"Skipping {os.path.basename(set_file)} - would exceed memory limit "
                    f"({cumulative_memory + estimated_memory:.1f}GB > {max_memory_gb}GB)"
                )
                continue
            
            # Load the file
            try:
                epochs = self.read_epochs(set_file)
                epochs_list.append(epochs)
                cumulative_memory += estimated_memory
                
            except Exception as e:
                logger.error(f"Failed to load {set_file}: {e}")
                continue
        
        logger.info(f"Loaded {len(epochs_list)} files using ~{cumulative_memory:.1f}GB")
        return epochs_list