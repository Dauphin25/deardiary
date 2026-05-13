"""DearDiary ER Diagram in Georgian — generates er_diagram_ka.png"""
from PIL import Image, ImageDraw, ImageFont
import math

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1340, 1040
img = Image.new("RGB", (W, H), "#EEF1F5")
draw = ImageDraw.Draw(img)

fn = "C:/Windows/Fonts/sylfaen.ttf"
ft_title  = ImageFont.truetype(fn, 22)
ft_ename  = ImageFont.truetype(fn, 15)
ft_esub   = ImageFont.truetype(fn, 10)
ft_attr   = ImageFont.truetype(fn, 13)
ft_rel    = ImageFont.truetype(fn, 11)
ft_card   = ImageFont.truetype(fn, 11)

# ── Colours ───────────────────────────────────────────────────────────────────
BG      = "#EEF1F5"
DARK    = "#1C2833"
WHITE   = "#FFFFFF"
BODY    = "#FDFEFE"
BODY2   = "#EBF5FB"
SHADOW  = "#BDC3C7"
LINE    = "#5D6D7E"
REL_BG  = "#FDFEFE"

C_USER  = "#1A5276"   # users app  — navy
C_DIARY = "#1E5E2A"   # diary app  — forest green
C_PAGE  = "#6C3483"   # pages app  — purple

PK_COL  = "#922B21"   # red  — primary key
FK_COL  = "#2471A3"   # blue — foreign key

# ── Sizes ─────────────────────────────────────────────────────────────────────
BOX_W  = 220
HDR_H  = 44
ROW_H  = 22
VPAD   = 6
RADIUS = 10

def bh(n): return HDR_H + n * ROW_H + VPAD * 2


# ── Text helpers ──────────────────────────────────────────────────────────────
def tw(text, font):
    b = font.getbbox(text); return b[2] - b[0]

def th(font):
    b = font.getbbox("Ag"); return b[3] - b[1]

def txt(x, y, text, font, fill=DARK, anchor="lt"):
    if anchor == "mm":
        w = tw(text, font); h = th(font)
        draw.text((x - w//2, y - h//2), text, fill=fill, font=font)
    else:
        draw.text((x, y), text, fill=fill, font=font)


# ── Entity drawing ────────────────────────────────────────────────────────────
class Entity:
    def __init__(self, name_ka, name_en, cx, cy, attrs, color):
        self.name_ka = name_ka
        self.name_en = name_en
        self.cx = cx; self.cy = cy
        self.attrs  = attrs   # list of (type, label): type in "pk","fk","col"
        self.color  = color
        self.bw = BOX_W
        self.height = bh(len(attrs))

    @property
    def x1(self): return self.cx - self.bw // 2
    @property
    def y1(self): return self.cy - self.height // 2
    @property
    def x2(self): return self.cx + self.bw // 2
    @property
    def y2(self): return self.cy + self.height // 2

    def side(self, s):
        if s == "top":    return (self.cx, self.y1)
        if s == "bottom": return (self.cx, self.y2)
        if s == "left":   return (self.x1, self.cy)
        if s == "right":  return (self.x2, self.cy)
        return (self.cx, self.cy)


def draw_entity(e: Entity):
    x1, y1, x2, y2 = e.x1, e.y1, e.x2, e.y2

    # Shadow
    draw.rounded_rectangle((x1+4, y1+4, x2+4, y2+4),
                            radius=RADIUS, fill=SHADOW)

    # Full box in header colour (base layer)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=RADIUS, fill=e.color)

    # Body area — flat rect painted over lower portion, then bottom arc restored
    body_top = y1 + HDR_H
    draw.rectangle((x1+1, body_top, x2-1, y2-RADIUS), fill=BODY)
    draw.rounded_rectangle((x1+1, y2-RADIUS*2, x2-1, y2-1),
                            radius=RADIUS-1, fill=BODY)

    # Outer border
    draw.rounded_rectangle((x1, y1, x2, y2), radius=RADIUS,
                            outline=DARK, width=2)

    # Header separator
    draw.line([(x1+2, body_top), (x2-2, body_top)], fill=DARK, width=1)

    # Entity name (Georgian) centred in header
    hdr_cy = y1 + HDR_H // 2 - 6
    txt(e.cx, hdr_cy, e.name_ka, ft_ename, fill=WHITE, anchor="mm")
    txt(e.cx, hdr_cy + 16, f"({e.name_en})", ft_esub, fill="#AED6F1", anchor="mm")

    # Attribute rows
    ay = body_top + VPAD
    for i, (atype, label) in enumerate(e.attrs):
        row_bg = BODY2 if i % 2 == 0 else BODY
        draw.rectangle((x1+2, ay, x2-2, ay + ROW_H - 1), fill=row_bg)

        if atype == "pk":
            prefix, col = "* ", PK_COL
        elif atype == "fk":
            prefix, col = "> ", FK_COL
        else:
            prefix, col = "  ", DARK

        row_y = ay + (ROW_H - th(ft_attr)) // 2
        draw.text((x1 + 8, row_y), prefix + label, fill=col, font=ft_attr)
        ay += ROW_H


# ── Arrow / relationship ───────────────────────────────────────────────────────
def rel(p1, p2, label="", c1="1", c2="N", color=LINE, dashed=False):
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])

    if dashed:
        # draw dashed line in segments
        length = math.hypot(x2-x1, y2-y1)
        steps = max(1, int(length / 10))
        pts = [(int(x1 + (x2-x1)*i/steps), int(y1 + (y2-y1)*i/steps))
               for i in range(steps+1)]
        for i in range(0, len(pts)-1, 2):
            draw.line([pts[i], pts[i+1]], fill=color, width=2)
    else:
        draw.line([(x1,y1),(x2,y2)], fill=color, width=2)

    # Arrow head at p2
    ang = math.atan2(y2-y1, x2-x1)
    hs = 9
    for da in (2.6, -2.6):
        ex = x2 + hs * math.cos(ang + math.pi + da)
        ey = y2 + hs * math.sin(ang + math.pi + da)
        draw.line([(x2, y2), (int(ex), int(ey))], fill=color, width=2)

    # Cardinality labels
    def card_label(px, py, card):
        cw = tw(card, ft_card) + 4
        draw.rectangle((px-cw//2, py-8, px+cw//2, py+8), fill=REL_BG, outline=color, width=1)
        txt(px, py, card, ft_card, fill=color, anchor="mm")

    card_label(int(x1 + (x2-x1)*0.12), int(y1 + (y2-y1)*0.12), c1)
    card_label(int(x1 + (x2-x1)*0.88), int(y1 + (y2-y1)*0.88), c2)

    # Relationship label at midpoint
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2
        lw = tw(label, ft_rel) + 8
        draw.rectangle((mx-lw//2, my-9, mx+lw//2, my+9),
                        fill=REL_BG, outline=color, width=1)
        txt(mx, my, label, ft_rel, fill="#6C3483", anchor="mm")


# ── Entity definitions ────────────────────────────────────────────────────────
E = {
"User": Entity(
    "მომხმარებელი", "CustomUser", cx=510, cy=185,
    attrs=[
        ("pk",  "id"),
        ("col", "username  —  სახელი"),
        ("col", "email  —  ელ-ფოსტა"),
        ("col", "first_name / last_name"),
        ("col", "city  —  ქალაქი"),
        ("col", "phone  —  ტელეფონი"),
        ("col", "gender  —  სქესი"),
    ], color=C_USER),

"Profile": Entity(
    "პროფილი", "UserProfile", cx=155, cy=235,
    attrs=[
        ("pk",  "id"),
        ("fk",  "user  →  მომხმარებელი"),
        ("col", "plan  (free / premium)"),
        ("col", "weekly_answer_count"),
        ("col", "next_reset"),
    ], color=C_USER),

"Style": Entity(
    "სტილი", "QuestionSetStyle", cx=910, cy=130,
    attrs=[
        ("pk",  "id"),
        ("col", "name  —  სახელი"),
        ("col", "template_name"),
        ("col", "is_premium  —  პრემიუმი?"),
    ], color=C_DIARY),

"QSet": Entity(
    "დღიური", "QuestionSet", cx=510, cy=490,
    attrs=[
        ("pk",  "id"),
        ("fk",  "owner  →  მომხმარებელი"),
        ("fk",  "style  →  სტილი"),
        ("col", "title  —  სათაური"),
        ("col", "slug"),
        ("col", "share_uuid  —  UUID"),
        ("col", "created_at  —  თარიღი"),
    ], color=C_DIARY),

"Question": Entity(
    "კითხვა", "Question", cx=155, cy=530,
    attrs=[
        ("pk",  "id"),
        ("fk",  "question_set  →  დღიური"),
        ("col", "text  —  ტექსტი"),
        ("col", "order  —  რიგი"),
    ], color=C_DIARY),

"Session": Entity(
    "სესია", "AnswerSession", cx=880, cy=490,
    attrs=[
        ("pk",  "id"),
        ("fk",  "question_set  →  დღიური"),
        ("fk",  "respondent  →  მომხმარებელი"),
        ("col", "created_at  —  თარიღი"),
    ], color=C_DIARY),

"Answer": Entity(
    "პასუხი", "Answer", cx=880, cy=730,
    attrs=[
        ("pk",  "id"),
        ("fk",  "session  →  სესია"),
        ("col", "question_text  —  კითხვა"),
        ("col", "answer_text  —  პასუხი"),
    ], color=C_DIARY),

"Notif": Entity(
    "შეტყობინება", "Notification", cx=1168, cy=405,
    attrs=[
        ("pk",  "id"),
        ("fk",  "recipient  →  მომხმარებელი"),
        ("fk",  "actor  →  მომხმარებელი"),
        ("fk",  "question_set  →  დღიური"),
        ("fk",  "answer_session  →  სესია"),
        ("col", "is_read  /  created_at"),
    ], color=C_USER),

"News": Entity(
    "სიახლე", "NewsItem", cx=155, cy=800,
    attrs=[
        ("pk",  "id"),
        ("col", "title  —  სათაური"),
        ("col", "content  —  შინაარსი"),
        ("col", "created_at  —  თარიღი"),
    ], color=C_DIARY),

"Page": Entity(
    "გვერდი  (CMS)", "Page", cx=510, cy=800,
    attrs=[
        ("pk",  "id"),
        ("col", "title  —  სათაური"),
        ("col", "slug"),
        ("col", "body  (RichText)"),
        ("col", "is_published  —  გამოქვეყნება"),
    ], color=C_PAGE),
}


# ── Draw all entities ─────────────────────────────────────────────────────────
for e in E.values():
    draw_entity(e)


# ── Draw relationships ────────────────────────────────────────────────────────
# UserProfile 1:1 User
rel(E["Profile"].side("right"), E["User"].side("left"),
    label="ეკუთვნის", c1="1", c2="1")

# QuestionSet N:1 User (owner)
rel(E["QSet"].side("top"), E["User"].side("bottom"),
    label="შექმნა", c1="N", c2="1")

# QuestionSet N:1 Style
# Route: QSet.right → curve up to Style.bottom
qr = E["QSet"].side("right"); sr = E["Style"].side("bottom")
rel(qr, sr, label="სტილი", c1="N", c2="1")

# Question N:1 QuestionSet
rel(E["Question"].side("right"), E["QSet"].side("left"),
    label="ეკუთვნის", c1="N", c2="1")

# Session N:1 QuestionSet
rel(E["Session"].side("left"), E["QSet"].side("right"),
    label="ეკუთვნის", c1="N", c2="1")

# Session N:1 User (respondent) — dashed, long diagonal
rel(E["Session"].side("top"),
    (E["User"].x2, E["User"].cy),
    label="respondent", c1="N", c2="1", color="#884EA0", dashed=True)

# Answer N:1 Session
rel(E["Answer"].side("top"), E["Session"].side("bottom"),
    label="ეკუთვნის", c1="N", c2="1")

# Notification N:1 Session
rel(E["Notif"].side("left"),
    E["Session"].side("right"),
    label="კავშირი", c1="N", c2="1")

# Notification → User (dashed, represents recipient+actor)
rel((E["Notif"].x1, E["Notif"].y1 + 30),
    (E["User"].x2, E["User"].y1 + 30),
    label="recipient/actor", c1="N", c2="1", color="#884EA0", dashed=True)


# ── Title & legend ─────────────────────────────────────────────────────────────
draw.line([(30, 50), (W-30, 50)], fill="#BDC3C7", width=1)
txt(W//2, 28, "DearDiary — მონაცემთა ბაზის სქემა  (ER Diagram)", ft_title,
    fill=DARK, anchor="mm")

# Legend box
lx, ly = 30, 920
draw.rounded_rectangle((lx, ly, lx+270, ly+106), radius=8,
                        fill=WHITE, outline="#BDC3C7", width=1)
txt(lx+10, ly+8, "პირობითი ნიშნები:", ft_rel, fill=DARK)
draw.rectangle((lx+10, ly+28, lx+22, ly+40), fill=PK_COL)
txt(lx+28, ly+28, "* — პირველადი გასაღები (PK)", ft_attr, fill=PK_COL)
draw.rectangle((lx+10, ly+48, lx+22, ly+60), fill=FK_COL)
txt(lx+28, ly+48, "> — გარე გასაღები (FK)", ft_attr, fill=FK_COL)
draw.rounded_rectangle((lx+10, ly+68, lx+22, ly+80), radius=3, fill=C_USER)
txt(lx+28, ly+68, "users app", ft_attr, fill=C_USER)
draw.rounded_rectangle((lx+10, ly+88, lx+22, ly+100), radius=3, fill=C_DIARY)
txt(lx+28, ly+88, "diary app", ft_attr, fill=C_DIARY)

draw.rounded_rectangle((lx+140, ly+68, lx+152, ly+80), radius=3, fill=C_PAGE)
txt(lx+158, ly+68, "pages app", ft_attr, fill=C_PAGE)
draw.line([(lx+140, ly+82), (lx+152, ly+82)], fill="#884EA0", width=2)
draw.line([(lx+143, ly+79), (lx+143, ly+85)], fill="#884EA0", width=2)
txt(lx+158, ly+80, "მრავ. FK კავშირი", ft_attr, fill="#884EA0")

# Footer
draw.line([(30, H-18), (W-30, H-18)], fill="#BDC3C7", width=1)
txt(W//2, H-9, "DearDiary · 2025", ft_rel, fill="#95A5A6", anchor="mm")

# ── Save ──────────────────────────────────────────────────────────────────────
out = "E:/deardiary/diagrams/er_diagram_ka.png"
img.save(out, "PNG", dpi=(150, 150))
print(f"Saved: {out}")
