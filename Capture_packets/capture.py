from scapy.all import sniff, wrpcap

packets = sniff(count=500)

wrpcap("capture.pcap", packets)