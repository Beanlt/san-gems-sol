set -uo pipefail
# v3 26/09: --tudong = PHA A · RugCheck goi thang · PHA B. Ban cu goi 'SAN.py DA-BAO.md' (khong con dung).
python3 SAN.py --tudong 2>&1 | tee phieu.txt
mkdir -p phieu
cp phieu.txt "phieu/$(date -u +%Y-%m-%d_%H%M).txt"
cp phieu.txt MOI-NHAT.md
find phieu -type f -mtime +7 -delete
