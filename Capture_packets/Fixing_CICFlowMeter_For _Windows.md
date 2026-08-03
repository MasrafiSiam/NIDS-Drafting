# Fixing CICFlowMeter on Windows

## Overview

While using the Python implementation of **CICFlowMeter** (`cicflowmeter==0.2.0`) on Windows, the tool failed to generate flow features from a PCAP file.

The following documentation explains the issue, its root cause, and the steps taken to resolve it.

---

## Environment

| Component | Version |
|----------|---------|
| Operating System | Windows 11 |
| Python | Virtual Environment (.venv) |
| CICFlowMeter | 0.2.0 |
| Scapy (Before Fix) | 2.7.0 |
| Scapy (After Fix) | 2.5.0 |

---

## Problem

Running:

```bash
cicflowmeter -f capture.pcap -c output.csv
```

resulted in the following exception:

```text
scapy.error.Scapy_Exception: tcpdump is not available
```

Although `output.csv` was created, it remained empty because the program terminated before processing any packets.

---

## Root Cause

The installed version of **CICFlowMeter** uses Scapy's `AsyncSniffer` to read offline PCAP files.

Inside:

```text
.venv/Lib/site-packages/cicflowmeter/sniffer.py
```

the code was:

```python
return AsyncSniffer(
    offline=input_file,
    filter="ip and (tcp or udp)",
    prn=None,
    session=FlowSession,
    store=False,
)
```

The line

```python
filter="ip and (tcp or udp)"
```

causes newer versions of **Scapy (2.7.0)** to invoke **tcpdump** for packet filtering.

Since **tcpdump is not available on Windows**, Scapy throws:

```text
Scapy_Exception: tcpdump is not available
```

and CICFlowMeter exits before generating any flow statistics.

---

## Verification

Before modifying the package, the PCAP file itself was verified.

```python
from scapy.all import rdpcap

packets = rdpcap("capture.pcap")
print(len(packets))
```

Output:

```text
100
```

This confirmed that:

- The PCAP file was valid.
- Scapy could successfully read the packets.
- The issue was within CICFlowMeter rather than the capture file.

---

## Solution

### Step 1: Remove the BPF Filter

Open:

```text
.venv/Lib/site-packages/cicflowmeter/sniffer.py
```

Replace:

```python
return AsyncSniffer(
    offline=input_file,
    filter="ip and (tcp or udp)",
    prn=None,
    session=FlowSession,
    store=False,
)
```

with:

```python
return AsyncSniffer(
    offline=input_file,
    prn=None,
    session=FlowSession,
    store=False,
)
```

Removing the filter prevents Scapy from attempting to use `tcpdump`.

---

### Step 2: Downgrade Scapy

Uninstall the existing version:

```bash
pip uninstall scapy
```

Install Scapy 2.5.0:

```bash
pip install scapy==2.5.0
```

Verify the installation:

```bash
python -c "import scapy; print(scapy.__version__)"
```

Expected output:

```text
2.5.0
```

---

## Result

Running:

```bash
cicflowmeter -f capture.pcap -c output.csv
```

now successfully generates flow features.

Example output:

```text
src_ip
dst_ip
src_port
dst_port
protocol
flow_duration
tot_fwd_pkts
tot_bwd_pkts
totlen_fwd_pkts
totlen_bwd_pkts
...
```

instead of an empty CSV file.

---

## Why the Fix Works

The issue was caused by two factors:

1. **Scapy 2.7.0** attempted to use `tcpdump` whenever a BPF filter was applied during offline packet capture.
2. **Windows does not include tcpdump**, causing the packet processing to fail.

Removing the filter eliminates the dependency on `tcpdump`, while downgrading to **Scapy 2.5.0** restores compatibility with the current implementation of `cicflowmeter`.

---

## Commands Used

```bash
# Verify Scapy version
python -c "import scapy; print(scapy.__version__)"

# Downgrade Scapy
pip uninstall scapy
pip install scapy==2.5.0

# Generate flow features from a PCAP
cicflowmeter -f capture.pcap -c output.csv
```

---

## Notes

- This fix is specific to the Python implementation of **CICFlowMeter (v0.2.0)** on Windows.
- Editing `sniffer.py` modifies the installed package directly. If the package is upgraded or reinstalled, the modification must be applied again.
- The generated CSV uses CICFlowMeter-compatible feature names (e.g., `dst_port`, `flow_duration`, `tot_fwd_pkts`) that may need to be renamed if a machine learning model expects the original CICIDS2017 column names.