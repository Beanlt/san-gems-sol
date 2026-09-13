set -u
python3 SAN.py DA-BAO.md 2>&1 | tee phieu.txt
mkdir -p phieu
cp phieu.txt "phieu/$(date -u +%Y-%m-%d_%H%M).txt"
cp phieu.txt MOI-NHAT.md
find phieu -type f -mtime +7 -delete
