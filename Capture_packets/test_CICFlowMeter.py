from scapy.all import rdpcap

packets = rdpcap("capture.pcap")
print(len(packets))