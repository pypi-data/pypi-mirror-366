X_LABELS = {
    "B_DTF_Jpsi_P": r"$DTF P(B) [MeV/c]$",
    "B_DTF_Jpsi_PT": r"$DTF P_{T}(B) [MeV/c]$",
    "B_P": r"$P(B) [MeV/c]$",
    "B_PT": r"$P_{T}(B) [MeV/c]$",
    "B_ETA": r"$\eta(B)$",
    "nLongTracks": "Number of Long Tracks",
    "nPVs": "Number of Primary Vertices",
    "nEcalClusters": "Number of Ecal Clusters",
    "nFTClusters": "Number of SciFi Clusters",
    "nVTClusters": "Number of Velo Clusters",
}

from tqdm import tqdm
import threading
import time


def show_waiting_bar(stop_event, message="Training the classifier..."):
    with tqdm(desc=message, ncols=70, bar_format="{l_bar}{bar}⏳", total=0) as pbar:
        while not stop_event.is_set():
            pbar.update(0)  # Just keep the bar alive
            time.sleep(0.1)

stop_event = threading.Event()
progress_thread = threading.Thread(target=show_waiting_bar, args=(stop_event,))
