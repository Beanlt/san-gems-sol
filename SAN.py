#!/usr/bin/env python3
# SAN GEMS SOLANA — MAY THU HAI. Bean chot 13/09.
#   python3 SAN.py DA-BAO.md
#
# 🔴🔴 MAY NAY TACH HOAN TOAN KHOI MAY ROBINHOOD. Khong file nao dung chung.
#     Sua file nay KHONG duoc dung toi repo Beanlt/san-gems.
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
# 🔑 FILE NAY LA NGUON DUY NHAT CUA SO cho may Solana. File .md khac chi TRO toi.

import json, os, sys, time, calendar, urllib.request, urllib.error
import statistics as st

T0 = time.time()
CU = [0]

# ---- DIEM NOI ----
GT   = "https://api.geckoterminal.com/api/v2/networks/solana"
DS   = "https://api.dexscreener.com/latest/dex"
RPC  = os.environ.get("SOL_RPC", "https://api.mainnet-beta.solana.com")
CO_KHOA = bool(os.environ.get("SOL_RPC"))   # co khoa rieng hay dung cong cong

# 🔴 KHOA RPC KHONG BAO GIO NAM TRONG FILE NAY. No den tu bien moi truong SOL_RPC,
#    dat o GitHub Settings > Secrets and variables > Actions. Repo nay PUBLIC.

GIAN = 3.5 if os.environ.get("GITHUB_ACTIONS") else 2.4

# ---- LOC THO ----
# ⬜ CA BON NGUONG NAY BE NGUYEN TU MAY ROBINHOOD, CHUA DO MOT CA NAO TREN SOLANA.
#    Do 13/09 tren 60 pool feed volume: chi 3 con lot dai, 0 con du tuoi -> feed volume SAI.
#    Feed dung la trending_pools: 11/40 lot dai, 5 con du tuoi. Xem ham feed().
MC_MIN     = 50_000
MC_MAX     = 1_500_000
RESERVE_SO = 40_000
TUOI_MIN_H = 48        # pool phai song it nhat 48 gio moi doc duoc nen

# ---- NAM VE ----
XEP_TOI   = 0.25   # VE 1  ⬜ chua quet do nhay tren Solana
GIO_NAM   = 24     # VE 2
GIO_CUA   = 20     # VE 2  ⬜ chua quet
NUA_DAY   = 12     # VE 3
NEN_MIN   = 48
CUA_SO_NEN= 1000

# ---- VE 4 — SACH NANG, ban Solana ----
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
GIO_KHONG_BAO_LAI = 12


def in_nguong():
    print("NGUONG DANG CHAY · MAY SOLANA · NAM VE (Bean chot 13/09 — so ve = thu tu chay)")
    print("   LOC THO : mc $%s-$%s · tong pool >= $%s · tuoi >= %dh" % (
        format(MC_MIN, ","), format(MC_MAX, ","), format(RESERVE_SO, ","), TUOI_MIN_H))
    print("   VE 1 da rot nat : gia <= %.0f%% dinh (dinh = CLOSE nen 1h, KHONG lay rau)" % (XEP_TOI*100))
    print("   VE 2 da nam li  : >=%d/%d gio gan nhat co close <= nguong tren" % (GIO_CUA, GIO_NAM))
    print("   VE 3 het tao day: day %d gio sau >= day %d gio truoc" % (NUA_DAY, NUA_DAY))
    print("   VE 4 sach nang  : quyen duc THU HOI · quyen dong bang THU HOI ·")
    print("                     vi to nhat <=%.0f%% · top10 <=%.0f%% · khu hoi <=%.1f%% (lenh $%d)" % (
        VI_TO_MAX, TOP10_MAX, KHU_HOI_MAX, CO_LENH))
    print("   VE 5 co nguoi vao: vi MUA gio nay > nhip 6 gio, so anh chup cach %.0f-%.0f gio" % (
        VE5_CACH_MIN, VE5_CACH_MAX))
    print("      🔑 cua ve 5 la DAU, khong phai muc. Toc do %/gio chi de ghi so.")
    print("   KHOA RPC RIENG: %s" % ("✅ co (bien SOL_RPC)" if CO_KHOA
          else "🔴 KHONG — cua phan bo vi se ghi ⬜, con nao thieu no KHONG duoc qua ve 4"))
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


def get_lai(u):
    """429 la LOI GOI. Nghi roi thu lai. Cam doc thanh ket qua rong (KYLUAT.md 16.7)."""
    ok, j, ly = get(u)
    if not ok and "429" in ly:
        time.sleep(15)
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
                time.sleep(GIAN)
                continue
            for p in j.get("data", []):
                p["_nguon"] = ten
                pools[p["attributes"]["address"]] = p
            time.sleep(GIAN)
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
        if not (MC_MIN <= mc <= MC_MAX and res >= RESERVE_SO):
            continue
        if c["tuoi"] < TUOI_MIN_H:
            dc.append(c)
        else:
            ra.append(c)
    return ra, dc


# ---------- 2. VE 1-2-3 ----------
def ba_ve(c):
    """MOT cu goi cho moi con. Doc y het may Robinhood — day la cho CAM lam khac."""
    c["ve1"] = c["ve2"] = c["ve3"] = False
    c["ve4"] = None
    c["ve5"] = None
    c["ly_nen"] = ""
    ok, j, ly = get_lai("%s/pools/%s/ohlcv/hour?aggregate=1&limit=%d" % (GT, c["pool"], CUA_SO_NEN))
    time.sleep(GIAN)
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


def phan_bo_vi(mint, cung):
    """Top 20 vi. 🔴 RPC CONG CONG CHAN LENH NAY — do 13/09, 4 lan lien tiep HTTP 429.
    Khong co khoa rieng thi tra loi -> con do KHONG duoc qua ve 4 (cam doc rong thanh sach)."""
    ok, r, ly = rpc("getTokenLargestAccounts", [mint])
    if not ok:
        return {"loi": ly}
    v = (r or {}).get("value") or []
    if not v or not cung:
        return {"loi": "khong co du lieu vi"}
    sl = []
    for x in v:
        a = so(x.get("uiAmountString")) or 0
        sl.append(a)
    tong = cung / (10 ** 0) if cung else 0
    return {"loi": None, "so": len(sl), "sl": sl}


def doc_cua4(c):
    r = c.get("cua") or {}
    if r.get("loi"):
        return "⛔ " + r["loi"]
    p = []
    p.append("quyen duc %s" % ("🔴 CON" if r.get("duc") else "✅ da thu hoi"))
    p.append("quyen dong bang %s" % ("🔴 CON" if r.get("dong_bang") else "✅ da thu hoi"))
    if r.get("vi_to") is not None:
        p.append("vi to nhat %.2f%% (cua %.0f%%)" % (r["vi_to"], VI_TO_MAX))
        p.append("top10 %.2f%% (cua %.0f%%)" % (r["top10"], TOP10_MAX))
    else:
        p.append("⬜ phan bo vi CHUA DO DUOC (%s)" % (r.get("ly_vi") or "thieu khoa RPC"))
    return " · ".join(p)


def qua_ve4(c, kh):
    """True / False / None. None = chua do duoc, KHAC hoan toan False (KYLUAT.md 16.7)."""
    r = c.get("cua") or {}
    if r.get("loi"):
        return None
    if r.get("duc") or r.get("dong_bang"):
        return False
    if kh is None or kh > KHU_HOI_MAX:
        return False
    if r.get("vi_to") is None:
        return None          # 🔴 thieu cua phan bo -> KHONG cho qua, ghi ⬜
    return r["vi_to"] <= VI_TO_MAX and r["top10"] <= TOP10_MAX


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
                   "mc": _so_o(ph[5]), "gia": _so_o(ph[6])}
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
                c.get("tuoi", 0), c.get("nguon", "?")))
        for c in doi_chung:
            f.write("| DC %s | %s | `%s` | %s | %s | $%s | %s | — | %s nen | — | ..... | — | %.0f | %s |\n" % (
                g, c["ma"], c["base"],
                ((c.get("tx") or {}).get("h1") or {}).get("buyers", "—"),
                ("$" + format(int(c["res"]), ",")) if c.get("res") else "—",
                format(int(c["mc"]), ","),
                ("%.10g" % c["gia"]) if c.get("gia") else "—",
                c.get("so_nen", 0), c.get("tuoi", 0), c.get("nguon", "?")))
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
                moi.append("| KQ | %s | `%s` | %s | %dh | %.10g | %.10g | %+.1f%% |\n" % (
                    anh["ma"], a, gio_txt, moc, anh["gia"], gia_nay[a], d))
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


def doc_da_bao(path):
    ra = {}
    if not path or not os.path.exists(path):
        return ra
    for d in open(path, encoding="utf-8"):
        ph = [x.strip() for x in d.split("|")]
        if len(ph) >= 2 and ph[0]:
            try:
                ra[ph[0]] = calendar.timegm(time.strptime(ph[1][:19], "%Y-%m-%dT%H:%M:%S"))
            except Exception:
                pass
    return ra


# ---------- MAIN ----------
def main():
    so_da_bao = sys.argv[1] if len(sys.argv) > 1 else None
    da_bao = doc_da_bao(so_da_bao)
    anh_gan, anh_het = doc_anh_cu()
    gio = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())

    print("PHIEU · MAY SOLANA · %s" % gio)
    in_nguong()
    print()

    pools, hong, loi = feed()
    print("feed: %d pool doc duoc · %d trang loi" % (len(pools), hong))
    for x in loi:
        print("   ⛔ %s" % x)
    if not pools:
        print("⛔ KHONG DOC DUOC FEED — day la LOI GOI, KHONG phai 'khong co ung vien'")
        print("[%d cu · %.0f giay]" % (CU[0], time.time()-T0))
        return

    gia_nay = bang_gia(pools)
    n_kq = cham_ket_qua(anh_het, gia_nay)
    print("cham ket qua anh cu (moc %s gio): %d dong moi" % ("/".join(str(x) for x in KQ_MOC), n_kq))

    tho, non = loc_tho(pools)
    print("qua loc tho: %d · pool qua non (<%dh tuoi): %d" % (len(tho), TUOI_MIN_H, len(non)))
    if not tho:
        print("da ghi %d dong anh chup + %d dong ro doi chung vao %s" % (
            ghi_anh([], doi_chung=non), len(non), SO_ANH))
        print("KHONG CO GI TRONG DAI")
        print("[%d cu · %.0f giay]" % (CU[0], time.time()-T0))
        return

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

    nguong_bao = time.time() - GIO_KHONG_BAO_LAI * 3600
    theo_doi, ung_vien = [], []
    for c in sorted(cands, key=lambda x: -(x["res"] or 0)):
        kh = khu_hoi(c["res"], c["phi"])
        print("\n%s  %s" % (c["ma"], c["base"]))
        in_ba_ve(c)
        if c["base"] in da_bao and da_bao[c["base"]] >= nguong_bao:
            print("   BO QUA: da bao trong %d gio qua" % GIO_KHONG_BAO_LAI)
            continue
        r = quyen_token(c["base"])
        time.sleep(0.8)
        if not r.get("loi"):
            pb = phan_bo_vi(c["base"], r.get("cung"))
            time.sleep(0.8)
            if pb.get("loi"):
                r["vi_to"] = None
                r["ly_vi"] = pb["loi"]
            else:
                tong = (r.get("cung") or 0) / (10 ** (r.get("le") or 0))
                sl = sorted(pb["sl"], reverse=True)
                r["vi_to"] = (sl[0] / tong * 100) if tong else None
                r["top10"] = (sum(sl[:10]) / tong * 100) if tong else None
        c["cua"] = r
        c["ve4"] = qua_ve4(c, kh)
        print("   VE 4 %s sach nang: %s" % (
            "✅" if c["ve4"] else ("⬜" if c["ve4"] is None else "🔴"), doc_cua4(c)))
        print("        khu hoi $%d = %s (cua <=%.1f%%) · tong pool $%s · phi %s%.2f%%/chieu" % (
            CO_LENH, ("%.2f%%" % kh) if kh else "?", KHU_HOI_MAX,
            format(int(c["res"]), ","), "" if c["biet_phi"] else "~", c["phi"]))
        tl, tlv, lpv, t24 = nhip_lenh(c)
        print("   NHIP LENH (mo ta, KHONG phai cua chan): mua/ban h1 %s · h24 %s · vi mua/ban %s" % (
            ("%.2f" % tl) if tl else "—", ("%.2f" % t24) if t24 else "—",
            ("%.2f" % tlv) if tlv else "—"))
        print("   von hoa $%s · cap %s · vol24 $%s · tuoi %.0fh · nguon %s" % (
            format(int(c["mc"]), ","), c["cap"], format(int(c["vol"]), ","), c["tuoi"], c["nguon"]))
        if c["ve4"] is True:
            theo_doi.append(c)
            print("   ⇒ DANH SACH THEO DOI")
            ve_nam(c, anh_gan)
            if c["ve5"] is True:
                ung_vien.append(c)
                print("   ⇒ UNG VIEN — du ca nam ve")
                vung_vao(c)
                print("   ⏰ GIO IN PHIEU: %s — vao tien muon hon thi DO LAI truoc" % gio)
                print("   DONG DAN VAO SO DA BAO: %s | %s | %s" % (
                    c["base"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), c["ma"]))
            else:
                print("   ⇒ CHI THEO DOI, chua co su kien vao. KHONG phai lenh vao.")

    print("\nda ghi %d dong anh chup + %d dong ro doi chung vao %s" % (
        ghi_anh(doc, doi_chung=non), len(non), SO_ANH))
    print("danh sach theo doi (qua 1-2-3-4): %d" % len(theo_doi))
    print("ung vien (du ca 5 ve): %d" % len(ung_vien))
    if not ung_vien:
        print("KHONG CO UNG VIEN MOI")
    print("[%d cu · %.0f giay]" % (CU[0], time.time()-T0))


main()
