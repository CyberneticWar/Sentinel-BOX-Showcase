"""Generate PNG showcase assets (banner + kiosk mockups). Run once locally."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCREENSHOTS = ASSETS / "screenshots"

BG_TOP = (15, 23, 42)
BG_BOTTOM = (30, 41, 59)
PANEL = (51, 65, 85)
ACCENT = (56, 189, 248)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
AMBER = (245, 158, 11)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        color = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=color)
    return img


def _rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], r: int, fill: tuple[int, int, int]) -> None:
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def _pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    label: str,
    fill: tuple[int, int, int],
    text_color: tuple[int, int, int] = TEXT,
) -> None:
    draw.rounded_rectangle(xy, radius=(xy[3] - xy[1]) // 2, fill=fill)
    font = _font(15, bold=True)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x0, y0, x1, y1 = xy
    draw.text((x0 + (x1 - x0 - tw) // 2, y0 + (y1 - y0 - th) // 2 - 1), label, font=font, fill=text_color)


def generate_banner() -> None:
    w, h = 1280, 360
    img = _gradient((w, h)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Sottile griglia decorativa
    for x in range(0, w, 48):
        draw.line([(x, 0), (x, h)], fill=(51, 65, 85, 28))
    for y in range(0, h, 48):
        draw.line([(0, y), (w, y)], fill=(51, 65, 85, 28))

    # Barra accento inferiore
    draw.rectangle((0, h - 4, w, h), fill=ACCENT)

    # Glow dietro emblem
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((52, 92, 188, 228), fill=(56, 189, 248, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    emblem_path = ASSETS / "brand" / "sentinel-emblem.png"
    if emblem_path.exists():
        emblem = Image.open(emblem_path).convert("RGBA")
        emblem = emblem.resize((96, 110), Image.Resampling.LANCZOS)
        img.paste(emblem, (72, 118), emblem)
        draw = ImageDraw.Draw(img)

    # Titolo e payoff
    draw.text((200, 108), "SENTINEL BOX", font=_font(48, bold=True), fill=TEXT)
    draw.line((200, 168, 520, 168), fill=ACCENT, width=3)
    draw.text((200, 186), "Predici i Problemi, Previeni i Guasti", font=_font(24), fill=ACCENT)
    draw.text(
        (200, 234),
        "Diagnostica OBD  ·  Machine Learning  ·  Kiosk Raspberry Pi",
        font=_font(17),
        fill=MUTED,
    )

    # Feature pills a destra — stile coerente con i badge del README
    pill_y = 128
    pills = [
        ("OBD-II / UDS", (14, 116, 144)),
        ("ML Predittivo", (34, 197, 94)),
        ("Kiosk Touch", (168, 85, 247)),
    ]
    for label, color in pills:
        _pill(draw, (900, pill_y, 1180, pill_y + 44), label, color)
        pill_y += 58

    # Card decorativa soft a destra
    draw.rounded_rectangle((872, 96, 1208, 296), radius=20, outline=(56, 189, 248, 80), width=2)

    out = ASSETS / "banner.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


def _kiosk_base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    w, h = 540, 960
    img = _gradient((w, h))
    draw = ImageDraw.Draw(img)
    return img, draw


def generate_kiosk_diagnosi() -> None:
    img, draw = _kiosk_base()
    w, h = img.size

    _rounded(draw, (24, 36, w - 24, 200), 16, PANEL)
    draw.text((44, 58), "AB 123 CD", font=_font(34, bold=True), fill=TEXT)
    draw.text((44, 108), "Volkswagen Golf 1.6 TDI · Diesel", font=_font(18), fill=MUTED)
    draw.text((44, 142), "VIN WVWZZZ1KZAW000000", font=_font(14), fill=MUTED)

    _rounded(draw, (24, 220, w - 24, 280), 12, (127, 29, 29))
    draw.text((44, 242), "ATTENZIONE — 2 guasti rilevati", font=_font(20, bold=True), fill=(254, 226, 226))

    _rounded(draw, (24, 300, w - 24, 400), 14, (71, 85, 105))
    draw.text((44, 322), "P0420", font=_font(28, bold=True), fill=AMBER)
    draw.text((44, 362), "Efficienza catalizzatore sotto soglia", font=_font(16), fill=TEXT)
    draw.text((44, 392), "Priorità media · Controllare sonda lambda", font=_font(14), fill=MUTED)

    _rounded(draw, (24, 416, w - 24, 516), 14, (71, 85, 105))
    draw.text((44, 438), "P0301", font=_font(28, bold=True), fill=RED)
    draw.text((44, 478), "Mancata accensione cilindro 1", font=_font(16), fill=TEXT)

    tile_w = (w - 72) // 2
    for i, (label, val, color) in enumerate([
        ("Batteria", "12.4 V", GREEN),
        ("Temp. motore", "92 °C", GREEN),
        ("RPM", "845", GREEN),
        ("Carburante", "68 %", GREEN),
    ]):
        col, row = i % 2, i // 2
        x0 = 24 + col * (tile_w + 24)
        y0 = 540 + row * 110
        _rounded(draw, (x0, y0, x0 + tile_w, y0 + 90), 12, PANEL)
        draw.text((x0 + 16, y0 + 14), label, font=_font(14), fill=MUTED)
        draw.text((x0 + 16, y0 + 40), val, font=_font(24, bold=True), fill=color)

    _rounded(draw, (24, h - 120, w // 2 - 12, h - 48), 12, ACCENT)
    draw.text((w // 4 - 40, h - 98), "Stampa referto", font=_font(18, bold=True), fill=BG_TOP)
    _rounded(draw, (w // 2 + 12, h - 120, w - 24, h - 48), 12, PANEL)
    draw.text((w // 2 + 52, h - 98), "Esci", font=_font(18, bold=True), fill=TEXT)

    out = SCREENSHOTS / "kiosk-diagnosi.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


def generate_kiosk_ok() -> None:
    img, draw = _kiosk_base()
    w, h = img.size

    _rounded(draw, (24, 36, w - 24, 200), 16, PANEL)
    draw.text((44, 58), "FG 456 HJ", font=_font(34, bold=True), fill=TEXT)
    draw.text((44, 108), "Toyota Yaris Hybrid · Benzina/Elettrico", font=_font(18), fill=MUTED)

    _rounded(draw, (24, 240, w - 24, 360), 16, (20, 83, 45))
    draw.ellipse((w // 2 - 36, 268, w // 2 + 36, 340), fill=GREEN)
    draw.text((w // 2 - 118, 360), "Veicolo in salute", font=_font(26, bold=True), fill=GREEN)
    draw.text((w // 2 - 150, 400), "Nessun codice guasto attivo", font=_font(16), fill=MUTED)

    for i, (label, val) in enumerate([
        ("Batteria 12V", "13.1 V"),
        ("HV batteria", "78 %"),
        ("Temp. motore", "88 °C"),
        ("Autonomia est.", "42 km"),
    ]):
        col, row = i % 2, i // 2
        tile_w = (w - 72) // 2
        x0 = 24 + col * (tile_w + 24)
        y0 = 460 + row * 110
        _rounded(draw, (x0, y0, x0 + tile_w, y0 + 90), 12, PANEL)
        draw.text((x0 + 16, y0 + 14), label, font=_font(14), fill=MUTED)
        draw.text((x0 + 16, y0 + 40), val, font=_font(24, bold=True), fill=GREEN)

    out = SCREENSHOTS / "kiosk-ok.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


def generate_referto() -> None:
    w, h = 800, 560
    img = Image.new("RGB", (w, h), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    _rounded(draw, (60, 40, w - 60, h - 40), 10, (255, 255, 255))
    draw.rectangle((60, 40, w - 60, 120), fill=(15, 23, 42))
    draw.text((90, 68), "REFERTO SENTINEL BOX", font=_font(24, bold=True), fill=TEXT)
    draw.text((90, 140), "Veicolo: Volkswagen Golf 1.6 TDI", font=_font(18), fill=(30, 41, 59))
    draw.text((90, 175), "Targa: AB 123 CD  ·  Data: 09/07/2026", font=_font(16), fill=MUTED)
    draw.line([(90, 210), (w - 90, 210)], fill=(226, 232, 240), width=2)
    draw.text((90, 230), "Esito scansione", font=_font(18, bold=True), fill=(30, 41, 59))
    draw.text((90, 265), "• 2 codici guasto con priorità indicata", font=_font(16), fill=(30, 41, 59))
    draw.text((90, 295), "• Predizione batteria: sostituzione entro 6 mesi", font=_font(16), fill=(30, 41, 59))
    draw.text((90, 325), "• Tagliando consigliato entro 2.400 km", font=_font(16), fill=(30, 41, 59))
    _rounded(draw, (w - 220, 380, w - 90, 490), 8, (241, 245, 249))
    draw.text((w - 200, 420), "QR passaporto", font=_font(14), fill=MUTED)
    draw.rectangle((w - 185, 440, w - 125, 480), outline=(203, 213, 225), width=2)

    out = SCREENSHOTS / "referto-pdf.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


def main() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    generate_banner()
    generate_kiosk_diagnosi()
    generate_kiosk_ok()
    generate_referto()


if __name__ == "__main__":
    main()
