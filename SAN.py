#!/usr/bin/env python3
# SAN GEMS SOLANA — MAY THU HAI, TU DONG tren repo Beanlt/san-gems-sol. Bean chot 26/09.
#
# 🔴🔴 v3 26/09: BO CHAY TAY. GitHub Actions chay moi 2 gio (thuc te GitHub gian con 4-6 luot/ngay).
#     Repo chay tu 13/09 bang ban cu (khong co RugCheck -> ve 4 luon ⬜); v3 thay ban do.
#
#     python3 SAN.py --tudong   -> PHA A · RugCheck GOI THANG · PHA B   (GitHub Actions chay cai nay)
#     python3 SAN.py            -> chi PHA A      (Claude chay tay khi can lay RugCheck qua Chrome)
#     python3 SAN.py --tiep --khong-ghi -> chi PHA B, doc rc.json Claude lay bang Chrome,
#                                          KHONG ghi so (so chi may repo duoc ghi)
#     RugCheck goi thang hong (vd bi chan) -> mint do ghi ⛔ o ve 4, KHONG con nao qua. Khong doan.
#
# 🔴🔴 TACH HOAN TOAN KHOI MAY ROBINHOOD. Khong file nao dung chung.
#
# SO VE = THU TU CHAY, giong may Robinhood (LUAT.md muc 1):
# LOC THO          : dai von hoa · doi ung san · tuoi pool                  (0 cu them)
# VE 1  da rot nat : gia dong cua nen 1h <= XEP_TOI x DINH (dinh = CLOSE, KHONG lay rau)
# VE 2  da nam li  : >=GIO_CUA trong GIO_NAM gio gan nhat co close <= nguong do
# VE 3  het tao day: day nua sau >= day nua truoc
# VE 4  sach nang  : quyen duc · quyen dong bang · phan bo vi · khu hoi     (TON CU)
# VE 5  co nguoi vao: VI MUA rieng biet gio nay so voi nhip 6 gio           (0 cu them)
#
# 🔴 VE 4 VA VE 5 KHAC MAY ROBINHOOD — do la CHO DUY NHAT duoc khac (LUAT.md muc 2.4, 2.5):
#   ve 4: Solana khong co locker PonsV2 va khong dung GoPlus. Thay bang quyen duc / quyen
#         dong bang doc thang tu RPC, cong phan bo vi.
#   ve 5: Solana khong lay duoc SO VI GIU neu khong co khoa RPC rieng, nen dem VI MUA
#         rieng biet trong gio, lay thang tu feed. Van la CUA DAU, khong phai muc.
#
# 🆕 v2 · 26/09 (Bean chot, sau khao sat gem 25/09 — LUAT.md muc 6.4) — v3 giu nguyen ca bon:
#   1. SO THEO DOI  — moi con tung vao DO-DEM.md duoc doc lai moi luot (ham so_theo_doi).
#                     Trending chi con la NGUON NAP, khong con la ro san duy nhat.
#   2. VUNG DUOI SAN — von hoa $20K-50K hoac doi ung < $40K: chay du nam ve, CHI GHI SO.
#                     Dai san cu KHONG DOI MOT SO NAO. Doi hay khong la viec cua bang KQ.
#   3. VE 4 BO POOL  — ban v1 tinh ca pool vao 'vi to nhat' (ca SOLCAT 25/09).
#   4. GIAN 2,4 -> 4,0 giay; bang KQ cham ca con da rot trending.
#
# 🔑 FILE NAY LA NGUON DUY NHAT CUA SO cho may Solana. File .md khac chi TRO toi.

import json, os, sys, time, calendar, urllib.request, urllib.error
import statistics as st

T0 = time.time()
CU = [0]

# ---- DIEM NOI ----
GT   = "https://api.geckoterminal.com/api/v2/networks/solana"
DS   = "https://api.dexscreener.com/latest/dex"
RPC  = os.environ.get("SOL_RPC", "https://api.mainnet-beta.solana.com")
RC   = "https://api.rugcheck.xyz/v1/tokens"

# 🔑 KHONG CAN KHOA NAO CA. Bean chot 13/09 sau khi do:
#    - RPC cong cong CHAN rieng getTokenLargestAccounts: tra thang
#      "Too many requests for a specific RPC call", 5 lan lien tiep, ke ca qua Chrome.
#    - Goi RPC mien phi cua cac nha cung cap cung chan dung nhom lenh do
#      (getProgramAccounts · getTokenAccountsByOwner · getTokenLargestAccounts)
#      vi chung quet ca kho trang thai, qua dat de phuc vu.
#    ⇒ Phan bo vi lay tu RugCheck, mien phi, khong khoa. Do that 13/09: chay.
# 🔴 Neu sau nay Bean co khoa rieng, dat o bien SOL_RPC — CAM ghi khoa vao file nay,
#    repo PUBLIC.

GIAN = 4.0              # giay nghi giua hai cu GeckoTerminal. v2 26/09: 2,4 -> 4,0.
                        # Do 25/09: nghi 4 giay -> 15/15 cu 200. Nghi 2,2 giay -> dinh 429 lien
                        # tuc, moi cu thuc te mat 7-13 giay vi phai cho 25 giay. Cham ma nhanh hon.
TAM  = "tam-sol.json"   # trang thai giua hai pha
CAN_RC = "can-rc.txt"   # danh sach mint can Claude lay RugCheck bang Chrome
RC_FILE = "rc.json"     # Claude ghi ket qua RugCheck vao day

# ---- LOC THO ----
# ⬜ CA BON NGUONG NAY BE NGUYEN TU MAY ROBINHOOD, CHUA DO MOT CA NAO TREN SOLANA.
#    Do 13/09 tren 60 pool feed volume: chi 3 con lot dai, 0 con du tuoi -> feed volume SAI.
#    Feed dung la trending_pools: 11/40 lot dai, 5 con du tuoi. Xem ham feed().
MC_MIN     = 50_000
MC_MAX     = 1_500_000
RESERVE_SO = 40_000
TUOI_MIN_H = 48        # pool phai song it nhat 48 gio moi doc duoc nen

# ---- VUNG DUOI SAN — v2 26/09. CHI GHI SO, KHONG SAN (LUAT.md muc 3.7) ----
# Con du tuoi, von hoa >= GHI_MIN nhung truot MC_MIN hoac RESERVE_SO -> van chay du nam ve,
# ghi so voi nhan 'duoi', in rieng, KHONG BAO GIO thanh ung vien.
# Ly do: PURR va RAYCAT (khao sat 25/09) khop ve 1-2-3 o von hoa $25-58K, doi ung uoc
# $26-56K — nam dung duoi hai san nay. Hai ca chi de ra CAU HOI, nen chi ghi, khong san.
# 🔴 GHI_MIN la bien cua VUNG GHI, KHONG phai cua san. Chon 20K vi o tap so 13/09,
#    dai $10-20K ra 0/6 dot >=2x, va vung chet cua PURR/RAYCAT nam trong $25-60K.
# 🔴 KHONG them san doi ung cho vung nay: cua khu hoi o ve 4 da doi doi ung >= ~$11.100
#    (2 x 250 / doi ung x 100 + 2 x 0,25 <= 5). Them mot so nua la bia.
GHI_MIN    = 20_000

# ---- SO THEO DOI — v2 26/09 (LUAT.md muc 1.2) ----
# Moi dia chi tung vao DO-DEM.md (ca dong DC) duoc doc lai MOI LUOT, khong can con trending.
# Khong co luat xoa khoi so: con nao chet han thi rot khoi dai von hoa, tu khong ton cu nen.
SO_LO = 30             # GeckoTerminal /multi nhan toi da 30 dia chi mot cu

# ---- NAM VE ----
XEP_TOI   = 0.25   # VE 1  ⬜ chua quet do nhay tren Solana
GIO_NAM   = 24     # VE 2
GIO_CUA   = 20     # VE 2  ⬜ chua quet
NUA_DAY   = 12     # VE 3
NEN_MIN   = 48
CUA_SO_NEN= 1000

# ---- VE 4 — SACH NANG, ban Solana ----
LP_KHOA_MIN= 90.0   # % LP da khoa hoac dot. Tuong duong cua locker ben Robinhood.
                    # ⬜ chua do tren Solana. 90 la muc tam, KHONG phai so da quet do nhay.
VI_TO_MAX  = 5.0    # % nguon cung, vi to nhat khong tinh pool  ⬜ chua do tren Solana
TOP10_MAX  = 25.0   # %
KHU_HOI_MAX= 5.0    # %
CO_LENH    = 250    # do
PHI_MAC_DINH = 0.25 # % moi chieu. Solana phi pool thay doi theo cho, GT it khi khai.

# ---- VE 5 — CO NGUOI VAO ----
# 🔴 CUA LA DAU, KHONG PHAI MUC. Giong may Robinhood (LUAT.md muc 2.5).
VE5_CACH_MIN = 1.0
VE5_CACH_MAX = 24.0
KQ_MOC       = (6, 24, 72)
KQ_LECH      = 0.35

SO_ANH   = "DO-DEM.md"
# v3: CHI MAY TREN REPO GHI SO. Claude chay tay (lay RugCheck qua Chrome) thi them --khong-ghi,
#     neu khong hai may ghi hai so lech nhau.
GHI = "--khong-ghi" not in sys.argv
GIO_KHONG_BAO_LAI = 12


def in_nguong():
    print("NGUONG DANG CHAY · MAY SOLANA · NAM VE (Bean chot 13/09 — so ve = thu tu chay)")
    print("   LOC THO : mc $%s-$%s · tong pool >= $%s · tuoi >= %dh" % (
        format(MC_MIN, ","), format(MC_MAX, ","), format(RESERVE_SO, ","), TUOI_MIN_H))
    print("   VE 1 da rot nat : gia <= %.0f%% dinh (dinh = CLOSE nen 1h, KHONG lay rau)" % (XEP_TOI*100))
    print("   VE 2 da nam li  : >=%d/%d gio gan nhat co close <= nguong tren" % (GIO_CUA, GIO_NAM))
    print("   VE 3 het tao day: day %d gio sau >= day %d gio truoc" % (NUA_DAY, NUA_DAY))
    print("   VE 4 sach nang  : quyen duc THU HOI · quyen dong bang THU HOI · LP khoa >=%.0f%% ·" % LP_KHOA_MIN)
    print("                     vi to nhat <=%.0f%% · top10 <=%.0f%% · khu hoi <=%.1f%% (lenh $%d)" % (
        VI_TO_MAX, TOP10_MAX, KHU_HOI_MAX, CO_LENH))
    print("   VE 5 co nguoi vao: vi MUA gio nay > nhip 6 gio, so anh chup cach %.0f-%.0f gio" % (
        VE5_CACH_MIN, VE5_CACH_MAX))
    print("      🔑 cua ve 5 la DAU, khong phai muc. Toc do %/gio chi de ghi so.")
    print("   PHAN BO VI + LP KHOA: lay tu RugCheck (mien phi, khong khoa) · DA BO POOL khoi phan bo vi")
    print("   SO THEO DOI: moi dia chi tung vao %s duoc doc lai moi luot, khong can con trending" % SO_ANH)
    print("   VUNG DUOI SAN: von hoa $%s-$%s hoac doi ung < $%s -> chay du nam ve, CHI GHI SO, KHONG san" % (
        format(GHI_MIN, ","), format(MC_MIN, ","), format(RESERVE_SO, ",")))
    print("   KHONG CO MOC BAN. Qua 1-2-3-4 = DANH SACH THEO DOI, chua phai ung vien.")
    print("   ⬜ MOI NGUONG TREN BE TU MAY ROBINHOOD, CHUA CA NAO DO TREN SOLANA.")


# ---------- 0. goi mang ----------
def get(u, timeout=25):
    CU[0] += 1
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            u, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=timeout)
        return True, json.loads(r.read()), ""
    except urllib.error.HTTPError as e:
        return False, None, "HTTP %d" % e.code
    except Exception as e:
        return False, None, str(e)[:80]


GIAN_NOW = [GIAN]   # v3: nhip nghi tu gian ra moi lan dinh 429 (tran 8 giay)


def get_lai(u):
    """429 la LOI GOI. Nghi roi thu lai. Cam doc thanh ket qua rong (KYLUAT.md 16.7).
    v3 26/09: do luot thu tren so repo — 126 cu nen, nghi 4 giay van dinh 429 o 13 cu, luot
    keo 1.416 giay. Nay thu lai HAI lan (20 roi 45 giay) va gian nhip nghi +1 giay moi lan dinh."""
    ok, j, ly = get(u)
    for cho in (20, 45):
        if ok or "429" not in ly:
            break
        GIAN_NOW[0] = min(GIAN_NOW[0] + 1, 8)
        time.sleep(cho)
        ok, j, ly = get(u)
    return ok, j, ly


def rpc(method, params, timeout=25):
    CU[0] += 1
    try:
        d = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        r = urllib.request.urlopen(urllib.request.Request(
            RPC, data=d, headers={"Content-Type": "application/json",
                                  "User-Agent": "Mozilla/5.0"}), timeout=timeout)
        j = json.loads(r.read())
        if "error" in j:
            return False, None, str(j["error"])[:80]
        return True, j.get("result"), ""
    except urllib.error.HTTPError as e:
        return False, None, "HTTP %d" % e.code
    except Exception as e:
        return False, None, str(e)[:80]


def so(x):
    try:
        v = float(x)
        return v if v == v else None
    except Exception:
        return None


# ---------- 1. FEED ----------
def feed():
    """🔴 KHONG dung sort volume. Do 13/09: 60 pool dau feed volume co vol24 THAP NHAT
    $23,8 trieu, von hoa trung vi $2,7 trieu -> chi 3/60 lot dai san, 0 con du tuoi.
    trending_pools cho 11/40 lot dai, 5 con du tuoi -> DAY moi la feed dung.
    new_pools chi de nuoi RO DOI CHUNG: tuoi trung vi 0 gio, von hoa trung vi $6.360."""
    pools, hong, loi = {}, 0, []
    for ten, mau, trang in [("trending", GT + "/trending_pools?page=%d", 5),
                            ("moi",      GT + "/new_pools?page=%d",      2)]:
        for pg in range(1, trang + 1):
            ok, j, ly = get_lai(mau % pg)
            if not ok:
                hong += 1
                loi.append("%s trang %d: %s" % (ten, pg, ly))
                time.sleep(GIAN_NOW[0])
                continue
            for p in j.get("data", []):
                p["_nguon"] = ten
                pools[p["attributes"]["address"]] = p
            time.sleep(GIAN_NOW[0])
    return pools, hong, loi


def tuoi_gio(ca):
    if not ca:
        return -1
    try:
        return (time.time() - calendar.timegm(time.strptime(ca[:19], "%Y-%m-%dT%H:%M:%S"))) / 3600
    except Exception:
        return -1


def dia_chi(rel, khoa):
    try:
        return (rel[khoa]["data"]["id"] or "").split("_", 1)[-1]
    except Exception:
        return None


def loc_tho(pools):
    """Tra ve (ung_vien, ro_doi_chung). Ro doi chung = pool qua non, chi chup khong san."""
    ra, dc = [], []
    for p in pools.values():
        a = p["attributes"]
        rel = p.get("relationships") or {}
        mc = so(a.get("market_cap_usd")) or so(a.get("fdv_usd")) or 0
        res = so(a.get("reserve_in_usd")) or 0
        c = {"pool": a["address"], "ma": (a.get("name") or "").split("/")[0].strip(),
             "mc": mc, "res": res, "tuoi": tuoi_gio(a.get("pool_created_at")),
             "vol": so((a.get("volume_usd") or {}).get("h24")) or 0,
             "v1": so((a.get("volume_usd") or {}).get("h1")) or 0,
             "tx": a.get("transactions") or {},
             "gia_doi": a.get("price_change_percentage") or {},
             "base": dia_chi(rel, "base_token"), "quote": dia_chi(rel, "quote_token"),
             "gia": so(a.get("base_token_price_usd")),
             "cap": (a.get("name") or "/").split("/")[-1].strip(),
             "nguon": p.get("_nguon"), "phi": PHI_MAC_DINH, "biet_phi": False}
        if not (c["base"] and c["gia"]):
            continue
        if mc > MC_MAX or mc < GHI_MIN:
            continue
        # 🔑 v2: vung 'san' = dai san cu, KHONG DOI. Vung 'duoi' = chi ghi so (muc GHI_MIN).
        c["vung"] = "san" if (mc >= MC_MIN and res >= RESERVE_SO) else "duoi"
        if c["tuoi"] < TUOI_MIN_H:
            if c["vung"] == "san":
                dc.append(c)      # ro doi chung giu nguyen nghia cu: chi pool non TRONG dai san
        else:
            ra.append(c)
    return ra, dc


def so_theo_doi(pools, path=SO_ANH):
    """🔑 v2 26/09 — SO THEO DOI. Nap moi dia chi tung vao so, lay pool lon nhat + so lieu
    hien tai bang /multi (30 dia chi mot cu), tron vao pools voi nguon 'so'.
    Ly do (LUAT.md muc 6.4): con hoi sinh thanh gem nam IM ngoai ro trending dung luc khop
    ve 1-2-3; may chi thay chung luc moi sinh. So giu dau chung lai.
    Tra ve (so dia chi trong so, so pool nap them, danh sach loi goi)."""
    if not os.path.exists(path):
        return 0, 0, []
    da = set()
    for dong in open(path, encoding="utf-8"):
        if dong.startswith("| 20") or dong.startswith("| DC 20"):
            ph = [x.strip() for x in dong.strip().strip("|").split("|")]
            if len(ph) > 2:
                da.add(ph[2].strip("`"))
    co = {dia_chi(p.get("relationships") or {}, "base_token") for p in pools.values()}
    can = sorted(a for a in da if a and a not in co)
    loi, pool_id = [], []
    for k in range(0, len(can), SO_LO):
        lo = can[k:k + SO_LO]
        ok, j, ly = get_lai("%s/tokens/multi/%s?include=top_pools" % (GT, ",".join(lo)))
        time.sleep(GIAN_NOW[0])
        if not ok:
            loi.append("tokens/multi lo %d: %s" % (k // SO_LO + 1, ly))
            continue
        for t in j.get("data") or []:
            tp = (((t.get("relationships") or {}).get("top_pools") or {}).get("data") or [])
            if tp:
                pool_id.append(tp[0]["id"].split("_", 1)[-1])
    them = 0
    for k in range(0, len(pool_id), SO_LO):
        lo = pool_id[k:k + SO_LO]
        ok, j, ly = get_lai("%s/pools/multi/%s" % (GT, ",".join(lo)))
        time.sleep(GIAN_NOW[0])
        if not ok:
            loi.append("pools/multi lo %d: %s" % (k // SO_LO + 1, ly))
            continue
        for p in j.get("data") or []:
            a = p["attributes"]["address"]
            if a not in pools:
                p["_nguon"] = "so"
                pools[a] = p
                them += 1
    return len(da), them, loi


# ---------- 2. VE 1-2-3 ----------
def ba_ve(c):
    """MOT cu goi cho moi con. Doc y het may Robinhood — day la cho CAM lam khac."""
    c["ve1"] = c["ve2"] = c["ve3"] = False
    c["ve4"] = None
    c["ve5"] = None
    c["ly_nen"] = ""
    ok, j, ly = get_lai("%s/pools/%s/ohlcv/hour?aggregate=1&limit=%d" % (GT, c["pool"], CUA_SO_NEN))
    time.sleep(GIAN_NOW[0])
    if not ok:
        c["ly_nen"] = "LOI GOI: " + ly
        return False
    n = (((j.get("data") or {}).get("attributes") or {}).get("ohlcv_list") or [])
    n = sorted(n, key=lambda x: x[0])
    c["so_nen"] = len(n)
    if len(n) < NEN_MIN:
        c["ly_nen"] = "chi %d cay nen 1h (can >=%d, pool qua non)" % (len(n), NEN_MIN)
        return False

    dong = [float(x[4]) for x in n]
    volk = [float(x[5]) for x in n]

    # VE 1 — dinh la CLOSE cao nhat, KHONG lay rau
    c["dinh"] = max(dong)
    c["gia_nen"] = dong[-1]
    c["xep"] = c["gia_nen"] / c["dinh"] if c["dinh"] else 1
    c["nguong"] = c["dinh"] * XEP_TOI
    c["ve1"] = c["xep"] <= XEP_TOI
    i = max(range(len(dong)), key=lambda k: dong[k])
    c["gio_tu_dinh"] = len(dong) - 1 - i

    # VE 2
    cua = dong[-GIO_NAM:]
    c["gio_duoi"] = sum(1 for x in cua if x <= c["nguong"])
    c["ve2"] = c["gio_duoi"] >= GIO_CUA

    # VE 3
    truoc, sau = dong[-GIO_NAM:-NUA_DAY], dong[-NUA_DAY:]
    c["day_truoc"] = min(truoc) if truoc else None
    c["day_sau"] = min(sau) if sau else None
    c["ve3"] = (c["day_truoc"] is not None and c["day_sau"] is not None
                and c["day_sau"] >= c["day_truoc"])

    # SO MO TA — khong chan ai (LUAT.md 2.5)
    nen_vol = volk[-GIO_NAM:-1]
    c["vol_nen"] = st.median(nen_vol) if nen_vol else 0
    c["vol_1h"] = volk[-1]
    c["vol_lan"] = (volk[-1] / c["vol_nen"]) if c["vol_nen"] > 0 else None
    return c["ve1"] and c["ve2"] and c["ve3"]


def in_ba_ve(c):
    d = lambda b: "✅" if b else "🔴"
    n = lambda x: ("$%.9f" % x).rstrip("0")
    print("   VE 1 %s da rot nat : gia %s = %.1f%% dinh %s (cua <=%.0f%%) · %.0fh tu dinh" % (
        d(c["ve1"]), n(c["gia_nen"]), c["xep"]*100, "" if c["ve1"] else "CHUA DU",
        XEP_TOI*100, c["gio_tu_dinh"]))
    print("   VE 2 %s da nam li  : %d/%d gio nam duoi %s (cua >=%d)" % (
        d(c["ve2"]), c["gio_duoi"], GIO_NAM, n(c["nguong"]), GIO_CUA))
    print("   VE 3 %s het tao day: day %dh sau %s / day %dh truoc %s" % (
        d(c["ve3"]), NUA_DAY, n(c["day_sau"] or 0), NUA_DAY, n(c["day_truoc"] or 0)))
    print("   KHOI LUONG (mo ta, KHONG phai cua chan): 1h = %s nen · $%s / nen $%s" % (
        ("%.1fx" % c["vol_lan"]) if c.get("vol_lan") else "?",
        format(int(c.get("vol_1h") or 0), ","), format(int(c.get("vol_nen") or 0), ",")))


def nhip_lenh(c):
    """SO MO TA, KHONG PHAI CUA CHAN. LUAT.md 7.4 cam dung lam cua."""
    tx = c.get("tx") or {}
    def ty(k):
        h = tx.get(k) or {}
        b, s_ = h.get("buys"), h.get("sells")
        return (b / s_) if (b and s_) else None
    h1 = tx.get("h1") or {}
    vi = (h1.get("buyers") / h1.get("sellers")) if (h1.get("buyers") and h1.get("sellers")) else None
    lpv = ((h1.get("buys") + h1.get("sells")) / (h1.get("buyers") + h1.get("sellers"))
           if (h1.get("buyers") and h1.get("sellers")) else None)
    return ty("h1"), vi, lpv, ty("h24")


# ---------- 3. VE 4 — SACH NANG ----------
def khu_hoi(doi_ung, phi_mot_chieu):
    """Giong may Robinhood: truot gia hai chieu + phi pool hai chieu."""
    if not doi_ung:
        return None
    return 2 * (CO_LENH / doi_ung) * 100 + 2 * phi_mot_chieu


def quyen_token(mint):
    """🔑 CUA SO MOT CUA SOLANA, va no la TUYET DOI:
    quyen duc con thi chu in them token bat cu luc nao;
    quyen dong bang con thi chu khoa vi nguoi mua, khong ban duoc — honeypot ma hop dong van sach.
    Mot cu goi, doc duoc ca hai."""
    ok, r, ly = rpc("getAccountInfo", [mint, {"encoding": "jsonParsed"}])
    if not ok:
        return {"loi": ly}
    info = (((r or {}).get("value") or {}).get("data") or {}).get("parsed", {}).get("info", {})
    if not info:
        return {"loi": "khong doc duoc du lieu mint"}
    return {"loi": None,
            "duc": info.get("mintAuthority"),
            "dong_bang": info.get("freezeAuthority"),
            "cung": so(info.get("supply")),
            "le": info.get("decimals")}


def doc_rc_file():
    """Doc rc.json — do Claude lay bang Chrome giua hai pha. Khong co thi tra rong."""
    if not os.path.exists(RC_FILE):
        return {}
    try:
        return json.load(open(RC_FILE, encoding="utf-8"))
    except Exception:
        return {}


def mo_rc_gon(g):
    """rc.json dang GON (SCRIPT.md muc 0.2): Chrome tra ket qua dai qua bi cat, nen doan ma lay
    RugCheck thay moi dia chi bang ma ngan a0, a1... NHAT QUAN TRONG MOT MINT. So khop 'la pool'
    chi can bang nhau, nen ma ngan giu nguyen nghia. Dong m cuoi [null,null,null,x] = LP cao nhat
    tren MOI market (market khong dinh toi ai trong top bi luoc cho gon)."""
    return {"token": {"mintAuthority": "co" if g["t"][0] else None,
                      "freezeAuthority": "co" if g["t"][1] else None},
            "totalHolders": g.get("n"), "score_normalised": g.get("s"),
            "risks": [{"name": x} for x in g.get("r") or []],
            "topHolders": [{"pct": h[0], "insider": bool(h[1]), "owner": h[2], "address": h[3]}
                           for h in g["h"]],
            "knownAccounts": {k: {"type": v[0], "name": v[1]} for k, v in (g.get("k") or {}).items()},
            "markets": [{"pubkey": m[0], "liquidityA": m[1], "liquidityB": m[2],
                         "lp": {"lpLockedPct": m[3]}} for m in g["m"]]}


def rugcheck(mint, kho=None):
    """🔑 PHAN BO VI · LP DA KHOA · hai quyen — khong can khoa API.
    Thay cho getTokenLargestAccounts (RPC cong cong chan han lenh do, do 13/09).
    🔴 May Claude bi chan api.rugcheck.xyz (HTTP 403) nen doc tu rc.json,
       do chinh Claude lay bang Chrome giua hai pha. Cung mot du lieu, khac duong di."""
    if kho is not None:
        j = kho.get(mint)
        if j is None:
            return {"loi": "khong co trong rc.json (RugCheck goi hong, hoac chua lay bang Chrome)"}
        ok, ly = True, ""
    else:
        ok, j, ly = get("%s/%s/report" % (RC, mint))
    if not ok:
        return {"loi": ly}
    if isinstance(j, dict) and "h" in j:
        j = mo_rc_gon(j)
    if not isinstance(j, dict) or "topHolders" not in j:
        return {"loi": "RugCheck tra du lieu la"}
    th_goc = j.get("topHolders") or []
    # 🔴 v2 26/09 — BO POOL khoi phan bo vi. Ban v1 lay thang topHolders[0], ma voi SOLCAT
    #    25/09 nguoi do CHINH LA pool Pump Fun AMM (13,60%) -> bao 'vi to nhat 13,60%' thay vi
    #    5,62%, top10 37,23% thay vi 25,21%. Luat ghi ro: vi to nhat KHONG TINH POOL.
    #    Nhan pool bang BA dau, du mot dau la bo: owner trung pubkey mot market · address trung
    #    tai khoan thanh khoan cua market · knownAccounts gan loai AMM.
    mk = j.get("markets") or []
    pool_owner = {m.get("pubkey") for m in mk if m.get("pubkey")}
    pool_acc = set()
    for m in mk:
        for k in ("liquidityAAccount", "liquidityBAccount", "liquidityA", "liquidityB"):
            if m.get(k):
                pool_acc.add(m[k])
    ka = j.get("knownAccounts") or {}
    def la_pool(h):
        o, a = h.get("owner"), h.get("address")
        # knownAccounts co khi gan nhan theo OWNER, co khi theo ADDRESS (do 26/09: LEVERSTONK, pool gan nhan theo address)
        return (o in pool_owner or a in pool_acc
                or "AMM" in str((ka.get(o) or {}).get("type", "")).upper()
                or "AMM" in str((ka.get(a) or {}).get("type", "")).upper())
    bo = [h for h in th_goc if la_pool(h)]
    th = [h for h in th_goc if not la_pool(h)]
    # 🔴 v2: VI = OWNER, khong phai tai khoan token. Mot owner co the giu nhieu tai khoan
    #    (do 26/09: Noiz co mot owner giu 4 tai khoan = 6,62%, tung tai khoan deu < 2%).
    #    Cong theo owner roi moi xep. Owner rong thi dung address.
    gop = {}
    for h in th:
        k = h.get("owner") or h.get("address")
        gop[k] = gop.get(k, 0) + (so(h.get("pct")) or 0)
    pct = list(gop.values())
    gop_nhieu = sum(1 for k in gop if sum(1 for h in th if (h.get("owner") or h.get("address")) == k) > 1)
    lp = None
    for m in mk:
        v = ((m.get("lp") or {}).get("lpLockedPct"))
        if v is not None:
            lp = max(lp or 0, so(v) or 0)
    tk = j.get("token") or {}
    # topHolders thieu truong owner thi KHONG loc duoc pool -> khong duoc cho qua (KYLUAT 16.7)
    thieu_owner = any(h.get("owner") is None and h.get("address") is None for h in th_goc)
    if thieu_owner:
        return {"loi": "rc.json thieu owner/address trong topHolders — ban cu, lay lai bang Chrome"}
    return {"loi": None,
            "bo_pool": ["%.2f%% %s" % (so(h.get("pct")) or 0,
                        (ka.get(h.get("owner")) or ka.get(h.get("address")) or {}).get("name") or "pool")
                        for h in bo],
            "vi_to": max(pct) if pct else None,
            "top10": sum(sorted(pct, reverse=True)[:10]) if pct else None,
            "lp_khoa": lp,
            "nguoi_giu": j.get("totalHolders"),
            "diem": j.get("score_normalised", j.get("score")),
            "canh_bao": [r.get("name") for r in (j.get("risks") or [])],
            "trong_cuoc": sum(1 for h in th if h.get("insider")),
            "gop_owner": gop_nhieu,
            "duc_rc": tk.get("mintAuthority"),
            "dong_bang_rc": tk.get("freezeAuthority")}


def doc_cua4(c):
    r = c.get("cua") or {}
    if r.get("loi"):
        return "⛔ " + r["loi"]
    p = []
    p.append("quyen duc %s" % ("🔴 CON" if r.get("duc") else "✅ da thu hoi"))
    p.append("quyen dong bang %s" % ("🔴 CON" if r.get("dong_bang") else "✅ da thu hoi"))
    if r.get("lech"):
        p.append("⛔ HAI NGUON NOI KHAC NHAU: " + r["lech"])
    if r.get("lp_khoa") is not None:
        p.append("LP khoa %.2f%% (cua >=%.0f%%)" % (r["lp_khoa"], LP_KHOA_MIN))
    else:
        p.append("⬜ LP khoa CHUA DO DUOC")
    if r.get("bo_pool"):
        p.append("da bo pool khoi phan bo vi: " + ", ".join(r["bo_pool"]))
    if r.get("gop_owner"):
        p.append("%d owner giu nhieu tai khoan — da cong lai" % r["gop_owner"])
    if r.get("vi_to") is not None:
        p.append("vi to nhat %.2f%% (cua %.0f%%)" % (r["vi_to"], VI_TO_MAX))
        p.append("top10 %.2f%% (cua %.0f%%)" % (r["top10"], TOP10_MAX))
    else:
        p.append("⬜ phan bo vi CHUA DO DUOC (%s)" % (r.get("ly_vi") or "RugCheck khong tra"))
    if r.get("nguoi_giu"):
        p.append("%s nguoi giu" % format(int(r["nguoi_giu"]), ","))
    if r.get("trong_cuoc"):
        p.append("⚠️ %d vi RugCheck danh dau NGUOI TRONG CUOC" % r["trong_cuoc"])
    if r.get("canh_bao"):
        p.append("canh bao RugCheck: " + ", ".join(r["canh_bao"][:4]))
    return " · ".join(p)


def qua_ve4(c, kh):
    """True / False / None. None = CHUA DO DUOC, khac hoan toan False (KYLUAT.md 16.7)."""
    r = c.get("cua") or {}
    if r.get("loi"):
        return None
    if r.get("lech"):
        return None          # 🔴 hai nguon noi khac nhau -> KHONG ket luan
    if r.get("duc") or r.get("dong_bang"):
        return False
    if kh is None or kh > KHU_HOI_MAX:
        return False
    if r.get("lp_khoa") is None or r.get("vi_to") is None:
        return None          # 🔴 thieu cua -> KHONG cho qua, ghi ⬜
    return (r["lp_khoa"] >= LP_KHOA_MIN and r["vi_to"] <= VI_TO_MAX
            and r["top10"] <= TOP10_MAX)


# ---------- 4. SO ANH CHUP ----------
def _so_o(x):
    x = (x or "").strip().replace("$", "").replace(",", "").replace("%", "")
    if x in ("", "—", "?", "-"):
        return None
    try:
        return float(x)
    except Exception:
        return None


def doc_anh_cu(path=SO_ANH):
    """Tra (gan_nhat, tat_ca). Moi anh: {gio, ma, vi_mua, doi_ung, mc, gia}."""
    gan, het = {}, {}
    if not os.path.exists(path):
        return gan, het
    for dong in open(path, encoding="utf-8"):
        if not dong.startswith("| 20"):
            continue
        ph = [x.strip() for x in dong.strip().strip("|").split("|")]
        if len(ph) < 13:
            continue
        try:
            a = ph[2].strip("`")
            g = calendar.timegm(time.strptime(ph[0][:16], "%Y-%m-%d %H:%M"))
            anh = {"gio": g, "ma": ph[1], "vi_mua": _so_o(ph[3]), "doi_ung": _so_o(ph[4]),
                   "mc": _so_o(ph[5]), "gia": _so_o(ph[6]),
                   # v2: cot nguon ghi 'nguon/vung'. Dong cu khong co '/' -> 'san' (v1 chi ghi dai san)
                   "vung": (ph[13].split("/")[1] if len(ph) > 13 and "/" in ph[13] else "san")}
            het.setdefault(a, []).append(anh)
            if a not in gan or g > gan[a]["gio"]:
                gan[a] = anh
        except Exception:
            pass
    return gan, het


def _ma_ve(c):
    """5 ky tu. '-' = truot · '.' = CHUA CHAY TOI ve do."""
    ra = ""
    for i in (1, 2, 3, 4, 5):
        v = c.get("ve%d" % i)
        ra += "." if v is None else (str(i) if v else "-")
    return ra


def ghi_anh(rows, path=SO_ANH, doi_chung=()):
    moi = not os.path.exists(path)
    g = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    with open(path, "a", encoding="utf-8") as f:
        if moi:
            f.write("# SO ANH CHUP — MAY SOLANA. Script tu ghi moi luot. CAM sua tay.\n\n")
            f.write("> Luot sau doc anh cu -> biet VI MUA tang hay giam, DOI UNG tang hay giam.\n")
            f.write("> Cot 'nam ve': 5 ky tu, '-' la truot, '.' la chua chay toi ve do.\n")
            f.write("> Dong '| DC ' la RO DOI CHUNG (pool qua non, chi chup, khong san).\n")
            f.write("> Dong '| KQ ' la BANG KET QUA 6/24/72 gio.\n\n")
            f.write("| gio UTC | ma | dia chi | vi mua h1 | doi ung | von hoa | gia | gia/dinh |"
                    " gio duoi | vol 1h/nen | nam ve | mua/ban h1 | tuoi h | nguon |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for c in rows:
            tl, tlv, lpv, _ = nhip_lenh(c)
            h1 = (c.get("tx") or {}).get("h1") or {}
            f.write("| %s | %s | `%s` | %s | %s | $%s | %s | %.1f%% | %d/%d | %s | %s | %s | %.0f | %s |\n" % (
                g, c["ma"], c["base"],
                h1.get("buyers") if h1.get("buyers") is not None else "—",
                ("$" + format(int(c["res"]), ",")) if c.get("res") else "—",
                format(int(c["mc"]), ","),
                ("%.10g" % c["gia"]) if c.get("gia") else "—",
                c.get("xep", 0)*100, c.get("gio_duoi", 0), GIO_NAM,
                ("%.1fx" % c["vol_lan"]) if c.get("vol_lan") else "—",
                _ma_ve(c),
                ("%.2f" % tl) if tl is not None else "—",
                c.get("tuoi", 0), "%s/%s" % (c.get("nguon", "?"), c.get("vung", "san"))))
        for c in doi_chung:
            f.write("| DC %s | %s | `%s` | %s | %s | $%s | %s | — | %s nen | — | ..... | — | %.0f | %s |\n" % (
                g, c["ma"], c["base"],
                ((c.get("tx") or {}).get("h1") or {}).get("buyers", "—"),
                ("$" + format(int(c["res"]), ",")) if c.get("res") else "—",
                format(int(c["mc"]), ","),
                ("%.10g" % c["gia"]) if c.get("gia") else "—",
                c.get("so_nen", 0), c.get("tuoi", 0), "%s/%s" % (c.get("nguon", "?"), c.get("vung", "san"))))
    return len(rows)


def ve_nam(c, gan):
    """VE 5 — CO NGUOI VAO. Dat khi VI MUA rieng biet tang va doi ung khong tut.
    🔴 CUA LA DAU, KHONG PHAI MUC (LUAT.md 2.5). Toc do %/gio chi de ghi so.
    🔴 Solana dem VI MUA chu khong dem VI GIU: so vi giu can khoa RPC, con vi mua
       nam san trong feed. Ghi ro cho nay vi no KHAC may Robinhood."""
    c["ve5"] = None
    c["ve5_ly"] = ""
    a = c.get("base")
    if a not in gan:
        c["ve5_ly"] = "CHUA CO ANH CU — luot dau cua con nay, ghi lai de lan sau so"
        print("   VE 5 ⬜ co nguoi vao: %s" % c["ve5_ly"])
        return
    anh = gan[a]
    cach = (time.time() - anh["gio"]) / 3600
    h1 = (c.get("tx") or {}).get("h1") or {}
    moi, cu = h1.get("buyers"), anh.get("vi_mua")
    print("   VE 5 — co nguoi vao (so voi anh chup cach %.1f gio):" % cach)
    if not (VE5_CACH_MIN <= cach <= VE5_CACH_MAX):
        c["ve5_ly"] = "anh cu cach %.1f gio, ngoai dai %.0f-%.0fh -> KHONG cham" % (
            cach, VE5_CACH_MIN, VE5_CACH_MAX)
        print("      ⬜ %s" % c["ve5_ly"])
        return
    if not (cu and moi):
        c["ve5_ly"] = "thieu so vi mua mot trong hai dau -> KHONG cham"
        print("      ⬜ %s" % c["ve5_ly"])
        return
    d = (moi/cu - 1) * 100
    toc = d / cach
    print("      vi mua h1  %d -> %d  (%+.1f%% · %+.2f%%/gio) %s" % (
        cu, moi, d, toc, "✅ co nguoi vao" if d > 0 else "🔴 nguoi ta dang bo di"))
    t = None
    du_cu, du_moi = anh.get("doi_ung"), c.get("res")
    if du_cu and du_moi and anh.get("mc") and c.get("mc"):
        ky = du_cu * ((c["mc"]/anh["mc"]) ** 0.5)
        t = du_moi / ky
        print("      doi ung $%s -> $%s · THUOC 2 = %.2f %s" % (
            format(int(du_cu), ","), format(int(du_moi), ","), t,
            "🔴 CO NGUOI RUT" if t < 0.8 else ("✅ CO NGUOI BOM" if t > 1.25 else "khong ai dong vao")))
    else:
        print("      doi ung ⬜ thieu so mot trong hai dau")
    if t is None:
        c["ve5_ly"] = "khong chay duoc thuoc 2 -> KHONG cham"
        print("      ⬜ %s" % c["ve5_ly"])
        return
    c["ve5"] = (d > 0) and (t >= 0.8)
    c["ve5_ly"] = "vi mua %+.1f%% · thuoc 2 %.2f" % (d, t)
    print("      VE 5 %s  (%s)" % ("✅ DAT" if c["ve5"] else "🔴 TRUOT", c["ve5_ly"]))


def cham_ket_qua(het, gia_nay, path=SO_ANH):
    """Cham lai anh cu o moc 6/24/72 gio. 0 cu goi them.
    Khong co buoc nay thi he KHONG BAO GIO tu biet sua ve xong la tot len hay xau di."""
    if not os.path.exists(path):
        return 0
    da = set()
    for dong in open(path, encoding="utf-8"):
        if dong.startswith("| KQ "):
            ph = [x.strip() for x in dong.strip().strip("|").split("|")]
            if len(ph) >= 5:
                da.add((ph[2].strip("`"), ph[3], ph[4]))
    moi, now = [], time.time()
    for a, ds in het.items():
        if a not in gia_nay:
            continue
        for anh in ds:
            if not anh.get("gia"):
                continue
            gio_txt = time.strftime("%Y-%m-%d %H:%M", time.gmtime(anh["gio"]))
            tuoi = (now - anh["gio"]) / 3600
            for moc in KQ_MOC:
                if not (moc <= tuoi <= moc * (1 + KQ_LECH)):
                    continue
                if (a, gio_txt, "%dh" % moc) in da:
                    continue
                d = (gia_nay[a] / anh["gia"] - 1) * 100
                # v2: them cot vung cuoi dong — de so KQ vung 'san' voi vung 'duoi' (LUAT 3.7)
                moi.append("| KQ | %s | `%s` | %s | %dh | %.10g | %.10g | %+.1f%% | %s |\n" % (
                    anh["ma"], a, gio_txt, moc, anh["gia"], gia_nay[a], d, anh.get("vung", "san")))
    if moi:
        with open(path, "a", encoding="utf-8") as f:
            f.writelines(moi)
    return len(moi)


def bang_gia(pools):
    ra, day = {}, {}
    for p in pools.values():
        a = p["attributes"]
        t = dia_chi(p.get("relationships") or {}, "base_token")
        g = so(a.get("base_token_price_usd"))
        res = so(a.get("reserve_in_usd")) or 0
        if not (t and g):
            continue
        if t not in day or res > day[t]:
            day[t] = res
            ra[t] = g
    return ra


def vung_vao(c):
    """Vung gia dung duoc, quy ra do. Giong may Robinhood (LUAT.md 4.6)."""
    tran = c["dinh"] * XEP_TOI
    san = c["gia_nen"] * ((CO_LENH * 2 * 100 / ((KHU_HOI_MAX - 2*c["phi"]) * c["res"])) ** 0
                          ) if False else None
    # san phi: gia ma tai do khu hoi cham dung KHU_HOI_MAX, doi ung theo can bac hai cua gia
    can = (2 * CO_LENH * 100) / max(KHU_HOI_MAX - 2 * c["phi"], 0.01)   # doi ung toi thieu
    san = c["gia_nen"] * ((can / c["res"]) ** 2) if c.get("res") else None
    n = lambda x: ("$%.9f" % x).rstrip("0")
    print("   VUNG DUNG DUOC: %s -> %s" % (n(san) if san else "?", n(tran)))
    print("      tran xep %s = %.0f%% dinh · san phi %s = noi khu hoi cham %.1f%%" % (
        n(tran), XEP_TOI*100, n(san) if san else "?", KHU_HOI_MAX))
    if san and c["gia_nen"] < san:
        print("      🔴 gia nay %s THAP HON san %.2f lan -> cua ra da qua dat" % (
            n(c["gia_nen"]), san / c["gia_nen"]))
    elif c["gia_nen"] > tran:
        print("      🔴 gia nay %s CAO HON tran %.2f lan -> chua xep du, KHONG co gia vao" % (
            n(c["gia_nen"]), c["gia_nen"] / tran))
    else:
        kh = khu_hoi(c["res"], c["phi"])
        print("      ✅ gia nay %s -> GIA DAT LENH: %s  (+%.3f%% truot chieu MUA)" % (
            n(c["gia_nen"]), n(c["gia_nen"] * (1 + kh/200)), kh/2))





# ---------- MAIN — HAI PHA ----------
def pha_a():
    """Feed · loc tho · ve 1-2-3. Ghi trang thai ra file, liet ke mint can RugCheck."""
    gio = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    print("PHIEU · MAY SOLANA · PHA A · %s" % gio)
    in_nguong()
    print()
    pools, hong, loi = feed()
    print("feed: %d pool doc duoc · %d trang loi" % (len(pools), hong))
    for x in loi:
        print("   ⛔ %s" % x)
    if not pools:
        print("⛔ KHONG DOC DUOC FEED — day la LOI GOI, KHONG phai 'khong co ung vien'")
        return
    n_so, them, loi_so = so_theo_doi(pools)
    print("so theo doi: %d dia chi trong so · nap them %d pool khong con trending · %d lo loi" % (
        n_so, them, len(loi_so)))
    for x in loi_so:
        print("   ⛔ %s" % x)
    # 🔑 bang gia lay SAU khi nap so -> bang KQ cham duoc ca con da rot khoi trending.
    #    v1 lay truoc: con nao roi trending la mat KQ -> bang KQ chi con con song (thien lech).
    gia_nay = bang_gia(pools)
    tho, non = loc_tho(pools)
    print("qua loc tho: %d (dai san %d · duoi san %d) · pool qua non (<%dh tuoi): %d" % (
        len(tho), sum(1 for c in tho if c["vung"] == "san"),
        sum(1 for c in tho if c["vung"] == "duoi"), TUOI_MIN_H, len(non)))
    doc, loi_nen = [], 0
    for c in tho:
        ba_ve(c)
        if c["ly_nen"].startswith("LOI GOI"):
            loi_nen += 1
            print("   ⛔ %s: %s" % (c["ma"], c["ly_nen"]))
        elif "qua non" in c["ly_nen"]:
            non.append(c)
        else:
            doc.append(c)
    print("doc duoc nen: %d · loi goi: %d" % (len(doc), loi_nen))
    cands = [c for c in doc if c["ve1"] and c["ve2"] and c["ve3"]]
    print("qua VE 1+2+3 (hinh dang gia): %d" % len(cands))
    for c in cands:
        print("\n%s  %s  [%s · nguon %s]" % (c["ma"], c["base"],
              "DAI SAN" if c["vung"] == "san" else "DUOI SAN — chi ghi so", c.get("nguon")))
        in_ba_ve(c)
    json.dump({"gio": gio, "doc": doc, "non": non, "gia_nay": gia_nay,
               "cands": [c["base"] for c in cands]},
              open(TAM, "w"), default=str)
    with open(CAN_RC, "w", encoding="utf-8") as f:
        for c in cands:
            f.write(c["base"] + "\n")
    print("\n---- PHA A XONG [%d cu · %.0f giay] ----" % (CU[0], time.time()-T0))
    if cands:
        print("CAN RUGCHECK cho %d mint (Claude lay bang Chrome, luu vao %s):" % (len(cands), RC_FILE))
        for c in cands:
            print("   %s" % c["base"])
    else:
        print("khong con nao qua ve 1-2-3 -> chay thang PHA B de ghi so")


def lay_rc_thang():
    """v3 26/09 — GOI THANG RugCheck cho moi mint trong can-rc.txt, ghi rc.json dang DAY DU.
    Chay tren GitHub Actions. May Claude bi chan ten mien nay (do 25/09) nen o do cu goi va
    ghi loi — pha B se ghi ⛔, KHONG BAO GIO doc loi thanh sach (KYLUAT.md 16.7).
    Moi mint thu 2 lan, nghi 1 giay. Tra ve (so doc duoc, so mint, danh sach loi)."""
    if not os.path.exists(CAN_RC):
        return 0, 0, []
    mints = [x.strip() for x in open(CAN_RC, encoding="utf-8") if x.strip()]
    kho, loi = {}, []
    for m in mints:
        ok, j, ly = get("%s/%s/report" % (RC, m))
        if not ok:
            time.sleep(3)
            ok, j, ly = get("%s/%s/report" % (RC, m))
        if ok and isinstance(j, dict) and "topHolders" in j:
            kho[m] = j
        else:
            loi.append("%s: %s" % (m, ly or "du lieu la"))
        time.sleep(1)
    json.dump(kho, open(RC_FILE, "w", encoding="utf-8"))
    return len(kho), len(mints), loi


def pha_b():
    """Ve 4 · ve 5 · cham ket qua · ghi so anh chup."""
    if not os.path.exists(TAM):
        print("⛔ chua chay PHA A"); return
    d = json.load(open(TAM, encoding="utf-8"))
    doc = d["doc"]; non = d["non"]; gia_nay = d["gia_nay"]
    gio = d["gio"]
    kho = doc_rc_file()
    print("PHIEU · MAY SOLANA · PHA B · %s" % gio)
    print("rc.json: %d mint co du lieu RugCheck" % len(kho))
    anh_gan, anh_het = doc_anh_cu()
    n_kq = cham_ket_qua(anh_het, gia_nay) if GHI else 0
    print("cham ket qua anh cu (moc %s gio): %d dong moi" % (
        "/".join(str(x) for x in KQ_MOC), n_kq))
    cands = [c for c in doc if c.get("ve1") and c.get("ve2") and c.get("ve3")]
    theo_doi, ung_vien, duoi_qua = [], [], []
    for c in sorted(cands, key=lambda x: -(x.get("res") or 0)):
        kh = khu_hoi(c["res"], c["phi"])
        print("\n%s  %s  [%s]" % (c["ma"], c["base"],
              "DAI SAN" if c.get("vung", "san") == "san" else "DUOI SAN — chi ghi so, KHONG san"))
        in_ba_ve(c)
        r = quyen_token(c["base"])
        time.sleep(0.5)
        rc = rugcheck(c["base"], kho)
        if r.get("loi") and rc.get("loi"):
            r = {"loi": "ca hai nguon hong: RPC %s · RugCheck %s" % (r["loi"], rc["loi"])}
        elif r.get("loi"):
            r = {"loi": None, "duc": rc.get("duc_rc"), "dong_bang": rc.get("dong_bang_rc"),
                 "chi_rc": True}
        if not r.get("loi"):
            if not rc.get("loi"):
                if not r.get("chi_rc"):
                    a = bool(r.get("duc")), bool(r.get("dong_bang"))
                    b = bool(rc.get("duc_rc")), bool(rc.get("dong_bang_rc"))
                    if a != b:
                        r["lech"] = ("RPC noi duc=%s dong_bang=%s · RugCheck noi duc=%s dong_bang=%s"
                                     % (a[0], a[1], b[0], b[1]))
                for k in ("vi_to", "top10", "lp_khoa", "nguoi_giu", "diem",
                          "canh_bao", "trong_cuoc", "bo_pool", "gop_owner"):
                    r[k] = rc.get(k)
            else:
                r["vi_to"] = None
                r["ly_vi"] = rc["loi"]
        c["cua"] = r
        c["ve4"] = qua_ve4(c, kh)
        print("   VE 4 %s sach nang: %s" % (
            "✅" if c["ve4"] else ("⬜" if c["ve4"] is None else "🔴"), doc_cua4(c)))
        print("        khu hoi $%d = %s (cua <=%.1f%%) · tong pool $%s · phi ~%.2f%%/chieu" % (
            CO_LENH, ("%.2f%%" % kh) if kh else "?", KHU_HOI_MAX,
            format(int(c["res"]), ","), c["phi"]))
        tl, tlv, lpv, t24 = nhip_lenh(c)
        print("   NHIP LENH (mo ta, KHONG phai cua chan): mua/ban h1 %s · h24 %s" % (
            ("%.2f" % tl) if tl else "—", ("%.2f" % t24) if t24 else "—"))
        print("   von hoa $%s · cap %s · vol24 $%s · tuoi %.0fh · nguon %s" % (
            format(int(c["mc"]), ","), c["cap"], format(int(c["vol"]), ","),
            c.get("tuoi", 0), c.get("nguon", "?")))
        if c["ve4"] is True and c.get("vung", "san") == "duoi":
            # 🔴 v2: vung duoi van cham ve 5 de GHI SO, nhung KHONG BAO GIO len danh sach/ung vien
            ve_nam(c, anh_gan)
            duoi_qua.append(c)
            print("   ⇒ DUOI SAN qua 1-2-3-4%s — CHI GHI SO, KHONG phai lenh vao" % (
                "-5" if c["ve5"] is True else ""))
        elif c["ve4"] is True:
            theo_doi.append(c)
            print("   ⇒ DANH SACH THEO DOI")
            ve_nam(c, anh_gan)
            if c["ve5"] is True:
                ung_vien.append(c)
                print("   ⇒ UNG VIEN — du ca nam ve")
                vung_vao(c)
                print("   ⏰ GIO IN PHIEU: %s — vao tien muon hon thi DO LAI truoc" % gio)
            else:
                print("   ⇒ CHI THEO DOI, chua co su kien vao. KHONG phai lenh vao.")
    if GHI:
        print("\nda ghi %d dong anh chup + %d dong ro doi chung vao %s" % (
            ghi_anh(doc, doi_chung=non), len(non), SO_ANH))
    else:
        print("\n--khong-ghi: KHONG ghi so (chi may tren repo duoc ghi so)")
    print("nhip nghi GeckoTerminal cuoi luot: %.0f giay" % GIAN_NOW[0])
    print("danh sach theo doi (qua 1-2-3-4): %d" % len(theo_doi))
    print("ung vien (du ca 5 ve): %d" % len(ung_vien))
    print("duoi san qua 1-2-3-4 (chi ghi so): %d" % len(duoi_qua))
    if not ung_vien:
        print("KHONG CO UNG VIEN MOI")
    print("[%d cu · %.0f giay]" % (CU[0], time.time()-T0))


if "--tiep" in sys.argv:
    pha_b()
elif "--tudong" in sys.argv:
    for f in (TAM, CAN_RC, RC_FILE):          # 🔴 xoa trang thai luot truoc, cam doc nham
        if os.path.exists(f):
            os.remove(f)
    pha_a()
    if os.path.exists(TAM):
        n_ok, n, loi_rc = lay_rc_thang()
        print("\nRUGCHECK GOI THANG: %d/%d mint doc duoc%s" % (
            n_ok, n, "" if not loi_rc else " · ⛔ " + " | ".join(loi_rc[:5])))
        print()
        pha_b()
else:
    pha_a()
