# NIDS-Drafting

A drafting/prototyping repository for building a **Network Intrusion Detection System (NIDS)** using machine learning. The project covers the full pipeline: capturing live network traffic, converting raw packet captures into labeled flow-based features (CICFlowMeter-style), and exploring/training models on the **CICIDS2017** dataset.

> ⚠️ **Status:** Work in progress / drafting stage. Notebooks and scripts here are exploratory and evolving.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Dataset](#-dataset)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
  - [1. Capturing Live Traffic](#1-capturing-live-traffic)
  - [2. Converting PCAP to Flow Features](#2-converting-pcap-to-flow-features)
  - [3. Exploratory Data Analysis & Training](#3-exploratory-data-analysis--training)
- [Known Issues & Fixes](#-known-issues--fixes)
- [Feature Columns](#-feature-columns)
- [Tech Stack](#-tech-stack)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔎 Overview

This project explores building a Network Intrusion Detection System by:

1. **Capturing** raw packets from a live network interface with `scapy`.
2. **Transforming** `.pcap` captures into flow-level statistical features (packet counts, IAT stats, flag counts, etc.) using `cicflowmeter`.
3. **Analyzing and modeling** these features against the industry-standard **CICIDS2017** intrusion detection dataset to classify traffic as benign or as a specific attack type (DDoS, PortScan, Web Attack, Infiltration, etc.).

---

## 📁 Project Structure

```
NIDS-Drafting/
├── Capture_packets/
│   ├── capture.py                              # Sniffs live packets and saves them to a .pcap file
│   ├── test_CICFlowMeter.py                    # Quick sanity check: reads a .pcap and prints packet count
│   ├── Captured.ipynb                          # Notebook version of the capture/testing workflow
│   ├── Fixing_CICFlowMeter_For _Windows.md     # Documented fix for a Windows-specific CICFlowMeter bug
│   ├── columns.txt                             # Feature column names used by CICFlowMeter output
│   └── capture.pcap                            # Sample captured traffic
├── 1.ipynb                                     # Main EDA notebook (CICIDS2017 exploration)
├── training.ipynb                              # Model training notebook (loads & merges CICIDS2017 CSVs)
├── columns.txt                                 # Full CICIDS2017 feature column list
├── requirements.txt                            # Python dependencies
└── .gitignore
```

---

## 🗂 Dataset

This project uses the **[CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html)** dataset from the Canadian Institute for Cybersecurity, which includes labeled benign and attack traffic captured over 5 days:

| File | Traffic Type |
|---|---|
| `Monday-WorkingHours.pcap_ISCX.csv` | Benign traffic |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | Benign + Brute Force |
| `Wednesday-workingHours.pcap_ISCX.csv` | DoS / Heartbleed |
| `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | Web Attacks |
| `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv` | Infiltration |
| `Friday-WorkingHours-Morning.pcap_ISCX.csv` | Benign |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | Port Scan |
| `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` | DDoS |

> The dataset itself is **not included** in this repository (see `.gitignore`, which excludes a local `Data/` folder). Download it separately from the [official CIC source](https://www.unb.ca/cic/datasets/ids-2017.html) and place the CSVs in a local `data/` directory before running the notebooks.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip` and a virtual environment tool (`venv`, `conda`, etc.)
- [Npcap](https://npcap.com/) (Windows) or `libpcap` (Linux/macOS) for live packet capture with `scapy`

### Installation

```bash
# Clone the repository
git clone https://github.com/MasrafiSiam/NIDS-Drafting.git
cd NIDS-Drafting

# Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Download the dataset

Download the **CICIDS2017** CSVs from the [official source](https://www.unb.ca/cic/datasets/ids-2017.html) and place them inside a `data/` folder at the project root:

```
NIDS-Drafting/
└── data/
    ├── Monday-WorkingHours.pcap_ISCX.csv
    ├── Tuesday-WorkingHours.pcap_ISCX.csv
    ├── Wednesday-workingHours.pcap_ISCX.csv
    ├── Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
    ├── Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
    ├── Friday-WorkingHours-Morning.pcap_ISCX.csv
    ├── Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
    └── Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

---

## 🧪 Usage

### 1. Capturing Live Traffic

`Capture_packets/capture.py` sniffs 500 packets from the default network interface and writes them to a `.pcap` file:

```bash
cd Capture_packets
python capture.py
```

This produces `capture.pcap`. You can sanity-check the capture with:

```bash
python test_CICFlowMeter.py
```

which reads the `.pcap` back in with `scapy` and prints the number of packets captured.

### 2. Converting PCAP to Flow Features

Use `cicflowmeter` to convert the raw capture into flow-level statistical features (the same feature set used in CICIDS2017):

```bash
cicflowmeter -f capture.pcap -c output.csv
```

> 🪟 **Running on Windows?** See [Known Issues & Fixes](#-known-issues--fixes) below — you'll likely hit a `tcpdump is not available` error out of the box.

### 3. Exploratory Data Analysis & Training

- **`1.ipynb`** — loads all 8 CICIDS2017 CSVs, inspects shape/nulls/duplicates, visualizes label distribution per file and overall, and exports the full feature column list to `columns.txt`.
- **`training.ipynb`** — loads and concatenates all 8 CICIDS2017 CSVs into a single combined `DataFrame`, as a starting point for model training (in progress).

Open either notebook with Jupyter Lab / Notebook:

```bash
jupyter lab
```

---

## 🐛 Known Issues & Fixes

### CICFlowMeter fails on Windows with `tcpdump is not available`

**Cause:** `cicflowmeter==0.2.0` uses Scapy's `AsyncSniffer` with a BPF filter (`filter="ip and (tcp or udp)"`) when reading offline `.pcap` files. Newer Scapy versions (2.7.0+) invoke `tcpdump` to apply this filter, which isn't available on Windows — so the process fails and produces an empty `output.csv`.

**Fix:**

1. Locate `sniffer.py` inside your virtual environment:
   ```
   .venv/Lib/site-packages/cicflowmeter/sniffer.py
   ```
2. Remove the `filter="ip and (tcp or udp)"` argument from the `AsyncSniffer(...)` call.
3. Downgrade Scapy to a compatible version:
   ```bash
   pip uninstall scapy
   pip install scapy==2.5.0
   ```
4. Re-run:
   ```bash
   cicflowmeter -f capture.pcap -c output.csv
   ```

Full write-up with before/after code: [`Capture_packets/Fixing_CICFlowMeter_For _Windows.md`](Capture_packets/Fixing_CICFlowMeter_For%20_Windows.md)

> **Note:** This patches the installed package directly — the fix must be reapplied if `cicflowmeter` is reinstalled or upgraded. Also, CICFlowMeter's own CSV output uses different column names (e.g. `dst_port`, `flow_duration`, `tot_fwd_pkts`) than the original CICIDS2017 dataset (e.g. ` Destination Port`, ` Flow Duration`, `Total Fwd Packets`) — rename columns to match if feeding live-captured features into a model trained on CICIDS2017.

---

## 📊 Feature Columns

The dataset (and CICFlowMeter output) uses ~78 flow-based features, including:

- Flow duration, forward/backward packet counts and byte lengths
- Inter-arrival time (IAT) statistics (mean, std, max, min) for flow, forward, and backward directions
- Header lengths, packet rate (packets/sec), packet length statistics
- TCP flag counts (FIN, SYN, RST, PSH, ACK, URG, CWE, ECE)
- Subflow statistics, initial window sizes, active/idle time statistics
- `Label` — the target class (benign or attack type)

See [`columns.txt`](columns.txt) for the full list.

---

## 🛠 Tech Stack

- **Python** — core language
- **scapy** — live packet sniffing & `.pcap` I/O
- **cicflowmeter** — PCAP → flow feature extraction
- **pandas / numpy** — data loading & manipulation
- **matplotlib / seaborn** — visualization & EDA
- **Jupyter** — notebooks for EDA and training

Full dependency list: [`requirements.txt`](requirements.txt)

---

## 🗺 Roadmap

- [ ] Finish feature preprocessing (encoding, scaling, handling `Infinity`/`NaN` values common in CICIDS2017)
- [ ] Train and evaluate baseline classifiers (e.g., Random Forest, XGBoost)
- [ ] Align live-captured feature schema with CICIDS2017 schema for real-time inference
- [ ] Build a real-time detection pipeline (capture → flow features → model → alert)
- [ ] Model evaluation (precision/recall/F1 per attack class, confusion matrix)

---

## 🤝 Contributing

This is currently a personal drafting/learning project. Suggestions and issues are welcome — feel free to open an issue or PR.

---

## 📄 License

No license has been specified yet for this repository. Until one is added, please treat the code as **all rights reserved** by the author.

---

## 👤 Author

**Masrafi Siam** — [GitHub](https://github.com/MasrafiSiam)
