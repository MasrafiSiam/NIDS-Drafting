from scapy.all import sniff, wrpcap

packets = sniff(count=100)

wrpcap("capture.pcap", packets)