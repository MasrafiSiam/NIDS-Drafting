from scapy.all import sniff, wrpcap

packets = sniff(count=1000)

wrpcap("capture.pcap", packets)