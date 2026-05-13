"""Generate DearDiary activity diagram in Georgian as PNG using Pillow."""
from PIL import Image, ImageDraw, ImageFont
import math

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1020, 940
img = Image.new("RGB", (W, H), "#F4F6F8")
draw = ImageDraw.Draw(img)

# ── Fonts (Sylfaen supports Georgian mkhedruli) ───────────────────────────────
fn = "C:/Windows/Fonts/sylfaen.ttf"
ft_title  = ImageFont.truetype(fn, 23)
ft_header = ImageFont.truetype(fn, 17)
ft_box    = ImageFont.truetype(fn, 15)
ft_sm     = ImageFont.truetype(fn, 12)

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = "#F4F6F8"
DARK     = "#1C2833"
BLUE     = "#1A5276"
BLUE_LT  = "#2E86C1"
GREEN    = "#1E8449"
ORANGE   = "#B7770D"
WHITE    = "#FFFFFF"
DIVIDER  = "#BFC9CA"
ARROW    = "#2C3E50"

# ── Helpers ───────────────────────────────────────────────────────────────────
BW, BH = 190, 52   # default box width / height

def text_size(text, font):
    """Return (width, height) of rendered text (handles multiline)."""
    lines = text.split("\n")
    widths, heights = [], []
    for line in lines:
        bb = font.getbbox(line)
        widths.append(bb[2] - bb[0])
        heights.append(bb[3] - bb[1])
    return max(widths), sum(heights) + (len(lines) - 1) * 4

def draw_text_centered(cx, cy, text, font, fill=WHITE):
    lines = text.split("\n")
    lh = [font.getbbox(l)[3] - font.getbbox(l)[1] for l in lines]
    total_h = sum(lh) + (len(lines) - 1) * 4
    y = cy - total_h // 2
    for i, line in enumerate(lines):
        w = font.getbbox(line)[2] - font.getbbox(line)[0]
        draw.text((cx - w // 2, y), line, fill=fill, font=font)
        y += lh[i] + 4

def activity_box(cx, cy, text, fill=BLUE, text_fill=WHITE, bw=BW, bh=BH):
    x1, y1, x2, y2 = cx - bw//2, cy - bh//2, cx + bw//2, cy + bh//2
    draw.rounded_rectangle((x1, y1, x2, y2), radius=10,
                            fill=fill, outline=DARK, width=2)
    draw_text_centered(cx, cy, text, ft_box, fill=text_fill)
    return x1, y1, x2, y2

def oval_node(cx, cy, text, fill=DARK, text_fill=WHITE, rx=65, ry=22):
    draw.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=fill, outline=DARK, width=2)
    draw_text_centered(cx, cy, text, ft_box, fill=text_fill)

def arrow(x1, y1, x2, y2, color=ARROW, lw=2, hs=8):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (2.6, -2.6):
        ex = x2 + hs * math.cos(ang + math.pi + da)
        ey = y2 + hs * math.sin(ang + math.pi + da)
        draw.line([(x2, y2), (int(ex), int(ey))], fill=color, width=lw)

# ── Column setup ──────────────────────────────────────────────────────────────
LX = 255   # Owner column center-x
RX = 760   # Friend column center-x
DIV_X = 508

# ── Title ─────────────────────────────────────────────────────────────────────
draw_text_centered(W//2, 32, "DearDiary — აქტივობის დიაგრამა", ft_title, fill=DARK)
draw.line([(40, 52), (W-40, 52)], fill=DIVIDER, width=1)

# Column headers
draw_text_centered(LX, 72, "მფლობელი  (Owner)", ft_header, fill=BLUE_LT)
draw_text_centered(RX, 72, "მეგობარი  (Friend)", ft_header, fill=GREEN)
draw.line([(DIV_X, 55), (DIV_X, H-30)], fill=DIVIDER, width=1)

# ── LEFT COLUMN — absolute y positions ───────────────────────────────────────
GAP = 25

L_START   = 108
L_REG     = 185
L_HOME    = 270
L_CREATE  = 355
L_QUEST   = 440
L_SHARE   = 525   # ← horizontal connector to friend column
L_VIEW    = 625
L_PDF     = 715
L_END     = 800

# Start oval
oval_node(LX, L_START, "დაწყება")

# arrows + boxes
arrow(LX, L_START+22, LX, L_REG-BH//2)
activity_box(LX, L_REG, "რეგისტრაცია / შესვლა")

arrow(LX, L_REG+BH//2, LX, L_HOME-BH//2)
activity_box(LX, L_HOME, "მთავარი გვერდი")

arrow(LX, L_HOME+BH//2, LX, L_CREATE-BH//2)
activity_box(LX, L_CREATE, "დღიურის შექმნა")

arrow(LX, L_CREATE+BH//2, LX, L_QUEST-BH//2)
activity_box(LX, L_QUEST, "კითხვების დამატება")

arrow(LX, L_QUEST+BH//2, LX, L_SHARE-BH//2)
activity_box(LX, L_SHARE, "ლინკის გაზიარება", fill=ORANGE, text_fill=WHITE)

# -- horizontal connector Share → Open Link --
arrowx1 = LX + BW//2
arrowx2 = RX - BW//2
arrow(arrowx1, L_SHARE, arrowx2, L_SHARE, color=ORANGE, lw=2)
mid_x = (arrowx1 + arrowx2) // 2
draw_text_centered(mid_x, L_SHARE - 13, "UUID ლინკი", ft_sm, fill=ORANGE)

arrow(LX, L_SHARE+BH//2, LX, L_VIEW-BH//2)
activity_box(LX, L_VIEW, "პასუხების ნახვა")

arrow(LX, L_VIEW+BH//2, LX, L_PDF-BH//2)
activity_box(LX, L_PDF, "PDF-ის გადმოწერა")

arrow(LX, L_PDF+BH//2, LX, L_END-22)
oval_node(LX, L_END, "დასასრული")

# ── RIGHT COLUMN — friend flow ────────────────────────────────────────────────
R_OPEN   = L_SHARE          # aligned with Share box
R_LIMIT  = L_SHARE + BH + GAP + 15
R_FILL   = R_LIMIT + BH + GAP + 15
R_SEND   = R_FILL + BH + GAP + 15

activity_box(RX, R_OPEN, "ლინკის გახსნა", fill=GREEN)

arrow(RX, R_OPEN+BH//2, RX, R_LIMIT-BH//2)
activity_box(RX, R_LIMIT, "ლიმიტის შემოწმება", fill=ORANGE, text_fill=WHITE)

arrow(RX, R_LIMIT+BH//2, RX, R_FILL-BH//2)
activity_box(RX, R_FILL, "პასუხების შეყვანა", fill=GREEN)

arrow(RX, R_FILL+BH//2, RX, R_SEND-BH//2)
activity_box(RX, R_SEND, "შეტყობინება\nმფლობელს", fill=GREEN)

# dashed arrow from notification back to owner "View Responses"
# draw as a bent line: right col → bottom → left col
notif_bottom = R_SEND + BH//2
view_cx = LX - BW//2 - 5
bend_y = max(notif_bottom, L_VIEW) + 35

draw.line([(RX, notif_bottom), (RX, bend_y)], fill=GREEN, width=2)
draw.line([(RX, bend_y), (view_cx, bend_y)], fill=GREEN, width=2)
arrow(view_cx, bend_y, LX - BW//2, L_VIEW, color=GREEN, lw=2)
draw_text_centered((RX + view_cx)//2, bend_y - 13,
                   "შეტყობინება მიდის მფლობელთან", ft_sm, fill=GREEN)

# ── Footer ────────────────────────────────────────────────────────────────────
draw.line([(40, H-28), (W-40, H-28)], fill=DIVIDER, width=1)
draw_text_centered(W//2, H-14, "DearDiary · 2025", ft_sm, fill="#AAB7B8")

# ── Save ──────────────────────────────────────────────────────────────────────
out = "E:/deardiary/diagrams/activity_diagram_ka.png"
img.save(out, "PNG", dpi=(150, 150))
print(f"Saved: {out}")
