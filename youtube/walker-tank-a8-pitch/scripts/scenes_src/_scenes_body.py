

# ═════════════════════════════ film helpers (A8 pitch) ═════════════════════════════
CONSTRUCTED = "constructed — does not exist yet"
FROM_MEMORY = "drawn from memory · no art from that game"
TANK_D, TANK_M = "#4A4F3C", "#5E6449"     # drawn tank hull / turret (dark olive, own drawing)
BRICK, BRICK_D = "#B5654A", "#8E4E39"     # drawn brick (own drawing)
MID_GUARD = 0.24
FLAG = "#E8A88C"                           # pale terracotta: decor, kept off the accent-text colour (GATE T)


def _mid(self):
    return _TARGET.get(type(self).__name__.split("_")[0], 0) / 2.0


def P(self, *anims, run_time=1.0, **kw):
    """play() that never spans the clip midpoint (GATE T / Gate V sample there)."""
    m = _mid(self)
    t0 = _elapsed(self)
    if m and t0 < m + MID_GUARD and t0 + run_time > m - MID_GUARD:
        self.wait(m + MID_GUARD - t0)
    self.play(*anims, run_time=run_time, **kw)


def U(self, phrase, lead=0.25):
    until(self, phrase, lead)


def head_label(text):
    t = T(text, 34)
    t.move_to([-6.1 + t.width / 2, 3.15, 0])
    return t


def lab(text, x, y, size=36):
    return T(text, size).move_to([x, y, 0])


def screen(x, y, w=2.6, h=1.7):
    """A drawn screen: card face, grey outline (GATE T: a dark outline around a dark icon reads as stacked
    labels), grey title band."""
    face = RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=CARD, fill_opacity=1,
                            stroke_color=DIM, stroke_width=5).move_to([x, y, 0])
    band = Rectangle(width=w - 0.16, height=0.22, fill_color=BAR2, fill_opacity=1, stroke_width=0)
    band.move_to([x, y + h / 2 - 0.2, 0])
    return VGroup(face, band)


def tank(x, y, s=1.0, hull=TANK_D, top=TANK_M, barrel_dir=1):
    """A small top-down tank of my own drawing: hull, two tracks, turret, barrel."""
    tracks = VGroup(*[Rectangle(width=1.0 * s, height=0.16 * s, fill_color=DARK_L, fill_opacity=1, stroke_width=0)
                      .move_to([x, y + dy * s, 0]) for dy in (0.3, -0.3)])
    body = Rectangle(width=0.9 * s, height=0.5 * s, fill_color=hull, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    tur = Circle(radius=0.2 * s, fill_color=top, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    bar = Rectangle(width=0.55 * s, height=0.09 * s, fill_color=top, fill_opacity=1, stroke_width=0)
    bar.move_to([x + barrel_dir * 0.42 * s, y, 0])
    return VGroup(tracks, body, bar, tur)


def wall(x, y, cols=3, rows=2, bw=0.5, bh=0.26):
    bricks = VGroup()
    for r in range(rows):
        off = (bw / 2) if r % 2 else 0
        for c in range(cols):
            bricks.add(Rectangle(width=bw - 0.04, height=bh - 0.04, fill_color=BRICK, fill_opacity=1,
                                 stroke_color=BRICK_D, stroke_width=2)
                       .move_to([x + (c - (cols - 1) / 2) * bw + off - bw / 4, y + (r - (rows - 1) / 2) * bh, 0]))
    return bricks


def page_card(x, y, w=1.3, h=1.7):
    face = Rectangle(width=w, height=h, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=DIM, stroke_width=3).move_to([x, y, 0])
    lines = VGroup(*[Line([x - w / 2 + w * 0.15, y + h * (0.3 - i * 0.2), 0], [x + w / 2 - w * 0.15, y + h * (0.3 - i * 0.2), 0],
                          color=GHOST, stroke_width=6) for i in range(4)])
    return VGroup(face, lines)


def plinth(x, y, w, h=0.22):
    return Rectangle(width=w, height=h, fill_color=DARK_L, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


# ═════════════════════════════ scenes ═════════════════════════════
class B02_FinishedForm(Scene):
    def construct(self):
        self.add(head_label(CONSTRUCTED))
        iso = Iso(0, -2.55, 0.8)
        U(self, "Windows desktop build")
        box = iso.box(-1.2, -1.2, 0, 2.4, 2.4, 1.3)
        tp = iso.tape(-1.2, -1.2, 1.3, 2.4, 2.4)
        blab = lab("Windows build", 3.4, -2.2)
        P(self, FadeIn(box, shift=DOWN * 0.3), FadeIn(tp), FadeIn(blab), run_time=0.8)
        xs = [-4.2, -0.9, 2.4]
        names = ["title", "battle", "win / lose"]
        phrases = ["a title screen", "the battle", "win or lose"]
        for i in range(3):
            U(self, phrases[i])
            sc = screen(xs[i], 1.15)
            if i == 0:
                inner = VGroup(Rectangle(width=1.5, height=0.2, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([xs[i], 1.3, 0]),
                               pill(xs[i], 0.7, 0.9, 0.3, fill=DIM))
            elif i == 1:
                inner = VGroup(tank(xs[i] - 0.6, 1.0, 0.6), wall(xs[i] + 0.55, 1.05, 2, 2, 0.34, 0.2))
            else:
                inner = VGroup(check(xs[i] - 0.5, 1.0, 0.22), Line([xs[i] + 0.3, 1.25, 0], [xs[i] + 0.8, 0.75, 0], color=INK, stroke_width=7),
                               Line([xs[i] + 0.3, 0.75, 0], [xs[i] + 0.8, 1.25, 0], color=INK, stroke_width=7))
            nl = lab(names[i], xs[i], -0.1)
            P(self, GrowFromCenter(sc), FadeIn(inner), FadeIn(nl), run_time=0.6)
        U(self, "plus a test report")
        pg = page_card(4.95, 1.05, 1.2, 1.5)
        rlab = lab("test report", 4.95, -0.1)
        P(self, FadeIn(pg, shift=DOWN * 0.4), FadeIn(rlab), run_time=0.6)
        U(self, "one command")
        P(self, Create(check(4.95, 0.85, 0.24, color=TERRA)), run_time=0.5)
        finish(self)


class B03_FromMemory(Scene):
    def construct(self):
        self.add(head_label(FROM_MEMORY))
        ground = Line([-6.0, -1.9, 0], [6.0, -1.9, 0], color=GHOST, stroke_width=6)
        a = tank(-4.4, 0.4, 2.0, hull=BAR1, top=DIM)
        w = wall(-0.9, 0.4, 3, 3, 0.8, 0.42)
        self.play(Create(ground), FadeIn(a), FadeIn(w), run_time=0.8)
        U(self, "cover could not be destroyed")
        shell = Dot([-2.9, 0.4, 0], radius=0.12, color=INK)
        self.add(shell)
        P(self, shell.animate.move_to([-2.05, 0.4, 0]), run_time=0.5, rate_func=linear)
        self.remove(shell)
        l1 = lab("wall unchanged", -0.9, -1.0)
        P(self, FadeIn(l1), run_time=0.4)
        U(self, "firing had no effect")
        shell2 = Dot([-2.9, 0.4, 0], radius=0.12, color=INK)
        self.add(shell2)
        P(self, shell2.animate.move_to([-2.05, 0.4, 0]), run_time=0.5, rate_func=linear)
        self.remove(shell2)
        l2 = lab("no effect", -4.4, -1.0)
        P(self, FadeIn(l2), run_time=0.4)
        U(self, "a destroyed tank")
        b = tank(3.9, 0.4, 2.0, hull=TANK_D, top=TANK_M, barrel_dir=-1)
        P(self, FadeIn(b), run_time=0.5)
        dead = tank(3.9, 0.4, 2.0, hull=BAR1, top=BAR2, barrel_dir=-1)
        P(self, FadeOut(b), FadeIn(dead), run_time=0.6)
        l3 = lab("no smoke", 3.9, -1.0)
        P(self, FadeIn(l3), run_time=0.4)
        finish(self)


class B05_FirstMinute(Scene):
    def construct(self):
        self.add(head_label(CONSTRUCTED))
        # clock dial (large, no ticks) at top right
        dial = Circle(radius=1.0, stroke_color=INK, stroke_width=5, fill_color=CARD, fill_opacity=1).move_to([4.6, 1.6, 0])
        dlab = lab("60 s", 4.6, 0.25)
        self.play(GrowFromCenter(dial), FadeIn(dlab), run_time=0.6)
        def sec(frac):
            return Sector(radius=0.85, angle=-frac * TAU, start_angle=PI / 2, fill_color=BAR2, fill_opacity=1,
                          stroke_width=0).shift(np.array([4.6, 1.6, 0]))
        iso = Iso(-4.4, -1.4, 0.7)
        U(self, "unzip the build")
        zipbox = iso.box(-0.9, -0.9, 0, 1.8, 1.8, 1.0)
        zl = lab("unzip", -4.4, -2.6)
        P(self, FadeIn(zipbox, shift=DOWN * 0.3), FadeIn(zl), FadeIn(sec(0.12)), run_time=0.7)
        U(self, "double-click the exe")
        exe = VGroup(RoundedRectangle(width=1.0, height=1.0, corner_radius=0.1, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4),
                     Square(0.45, fill_color=DARK_L, fill_opacity=1, stroke_width=0)).move_to([-1.6, -1.0, 0])
        cur = cursor(-1.3, -1.2)
        el = lab("double-click", -1.6, -2.6)
        P(self, FadeIn(exe), FadeIn(cur), FadeIn(el), FadeIn(sec(0.25)), run_time=0.7)
        ring = Circle(radius=0.6, stroke_color=TERRA, stroke_width=5).move_to([-1.6, -1.0, 0])
        P(self, Create(ring), run_time=0.4)
        P(self, FadeOut(ring), run_time=0.3)
        U(self, "see the title screen")
        sc = screen(1.6, -0.9, 2.8, 1.8)
        keys = VGroup(*[RoundedRectangle(width=0.36, height=0.3, corner_radius=0.06, fill_color=GHOST, fill_opacity=1, stroke_color=DIM, stroke_width=2)
                        .move_to([0.75 + i * 0.45, -1.45, 0]) for i in range(5)])
        ttl = Rectangle(width=1.6, height=0.22, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([1.6, -0.6, 0])
        sl = lab("title + controls", 1.6, -2.6)
        P(self, GrowFromCenter(sc), FadeIn(ttl), FadeIn(keys), FadeIn(sl), FadeIn(sec(0.45)), run_time=0.8)
        U(self, "press start")
        start = pill(1.6, -1.0, 1.0, 0.32, fill=DIM)
        P(self, FadeIn(start), FadeIn(sec(0.6)), run_time=0.5)
        U(self, "be driving")
        field = screen(1.6, 1.4, 2.8, 1.8)
        tk = tank(0.8, 1.25, 0.6)
        dl = lab("driving", -0.75, 1.4)
        P(self, GrowFromCenter(field), FadeIn(tk), FadeIn(dl), run_time=0.6)
        P(self, tk.animate.shift(RIGHT * 1.5), FadeIn(sec(1.0)), run_time=1.6, rate_func=linear)
        finish(self)


class B07_InOut(Scene):
    def construct(self):
        self.add(head_label(CONSTRUCTED))
        isoL, isoR = Iso(-3.3, -2.2, 0.6), Iso(3.3, -2.2, 0.6)
        bL, fL = isoL.open_box(-1.5, -1.5, 0, 3.0, 3.0, 1.1)
        bR, fR = isoR.open_box(-1.5, -1.5, 0, 3.0, 3.0, 1.1)
        li, lo = lab("in", -5.4, -1.6), lab("out", 1.2, -1.6)
        self.play(FadeIn(bL), FadeIn(fL), FadeIn(li), run_time=0.6)
        items = [screen(0, 0, 1.0, 0.7), screen(0, 0, 1.0, 0.7), screen(0, 0, 1.0, 0.7),
                 VGroup(Dot(radius=0.12, color=TERRA), Circle(radius=0.3, stroke_color=DIM, stroke_width=4)),
                 Square(0.6, fill_color=DARK_L, fill_opacity=1, stroke_width=0), page_card(0, 0, 0.6, 0.8)]
        spots = [(-5.2, 1.9), (-3.3, 1.9), (-1.4, 1.9), (-5.2, 0.5), (-3.3, 0.5), (-1.4, 0.5)]
        phrases = ["One level", "a title screen", "win and lose", "the effects", "a Windows export", "a test report"]
        for it, (x, y), ph in zip(items, spots, phrases):
            U(self, ph)
            it.scale(1.5).move_to([x, y, 0])
            P(self, FadeIn(it, shift=DOWN * 0.3), run_time=0.35)
        U(self, "What's out?")
        P(self, FadeIn(bR), FadeIn(fR), FadeIn(lo), run_time=0.5)
        outs = [VGroup(tank(0, 0.2, 0.55), tank(0, -0.35, 0.55)),
                VGroup(Square(0.7, fill_color=DIM, fill_opacity=1, stroke_width=0), Square(0.3, fill_color=CARD, fill_opacity=1, stroke_width=0).shift(UP * 0.12)),
                screen(0, 0, 1.0, 0.7)]
        spots = [(1.5, 1.2), (3.3, 1.2), (5.1, 1.2)]
        phrases = ["Multiplayer", "a save system", "a second level"]
        for it, (x, y), ph in zip(outs, spots, phrases):
            U(self, ph)
            it.scale(1.5).move_to([x, y, 0])
            P(self, FadeIn(it, shift=DOWN * 0.3), run_time=0.35)
            P(self, it.animate.set_opacity(0.35), run_time=0.3)
        finish(self)


class B08_FirstStep(Scene):
    def construct(self):
        self.add(head_label(CONSTRUCTED))
        iso = Iso(-4.2, -1.5, 0.8)
        back, front = iso.open_box(-1.3, -1.3, 0, 2.6, 2.6, 1.0)
        fl = lab("clean folder", -4.2, -3.0)
        self.play(FadeIn(back), FadeIn(front), FadeIn(fl), run_time=0.6)
        U(self, "Windows exe")
        exe = VGroup(RoundedRectangle(width=0.9, height=0.9, corner_radius=0.1, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4),
                     Square(0.4, fill_color=DARK_L, fill_opacity=1, stroke_width=0)).move_to([-4.2, 2.0, 0])
        exe.set_z_index(1)
        self.play(FadeIn(exe), run_time=0.3)
        P(self, exe.animate.move_to([-4.2, -0.45, 0]), run_time=0.7, rate_func=ease_in)
        U(self, "to a win")
        sc = screen(0.0, 0.6, 3.0, 2.0)
        pole = Line([0.3, -0.1, 0], [0.3, 1.1, 0], color=INK, stroke_width=6)
        flag = Polygon([0.3, 1.1, 0], [0.3, 0.7, 0], [0.95, 0.9, 0], fill_color=FLAG, fill_opacity=1, stroke_width=0)
        tk = tank(-0.8, 0.3, 0.6)
        wl = lab("win", 0.0, -0.75)
        P(self, GrowFromCenter(sc), FadeIn(tk), Create(pole), FadeIn(wl), run_time=0.7)
        P(self, FadeIn(flag, shift=UP * 0.2), run_time=0.4)
        U(self, "a capture of that run")
        rep = page_card(4.4, 0.4, 1.6, 2.2)
        rl = lab("TEST-REPORT.md", 4.2, -1.15)
        cap = screen(2.2, -1.9, 1.2, 0.8)
        logp = page_card(2.2, 2.0, 0.8, 1.0)
        P(self, FadeIn(rep), FadeIn(rl), FadeIn(cap), FadeIn(logp), run_time=0.6)
        P(self, cap.animate.scale(0.5).move_to([4.4, 0.0, 0]), logp.animate.scale(0.5).move_to([4.4, 0.9, 0]), run_time=0.8)
        U(self, "the commit")
        tag = VGroup(pill(5.75, 1.75, 0.9, 0.36, fill=DIM), Dot([5.45, 1.75, 0], radius=0.07, color=TERRA))
        P(self, FadeIn(tag, shift=LEFT * 0.2), run_time=0.4)
        finish(self)


def laptop(x, y, w=3.0):
    h = w * 0.62
    scr = RoundedRectangle(width=w, height=h, corner_radius=0.1, fill_color=CARD, fill_opacity=1, stroke_color=DIM, stroke_width=5).move_to([x, y + h / 2 + 0.1, 0])
    base = Polygon([x - w / 2 - 0.3, y - 0.2, 0], [x + w / 2 + 0.3, y - 0.2, 0], [x + w / 2, y + 0.08, 0], [x - w / 2, y + 0.08, 0],
                   fill_color=DARK_L, fill_opacity=1, stroke_width=0)
    return VGroup(scr, base)


class B09_Risk(Scene):
    def construct(self):
        self.add(head_label(CONSTRUCTED))
        L = laptop(-3.6, -1.0)
        ll = lab("RTX 3060", -3.6, -1.75)
        U(self, "one machine")
        P(self, FadeIn(L), FadeIn(ll), run_time=0.6)
        tk = tank(-3.6, 0.0, 0.7)
        P(self, FadeIn(tk), Create(check(-1.55, 0.6, 0.22)), run_time=0.5)
        U(self, "Forward plus")
        R = laptop(3.6, -1.0)
        rl = lab("integrated GPU", 3.6, -1.75)
        P(self, FadeIn(R), FadeIn(rl), run_time=0.6)
        U(self, "may fail")
        iso = Iso(0, 1.6, 0.5)
        bx = VGroup(iso.box(-0.6, -0.6, 0, 1.2, 1.2, 0.8), iso.tape(-0.6, -0.6, 0.8, 1.2, 1.2))
        bx.move_to([-1.0, 1.8, 0])
        P(self, FadeIn(bx), run_time=0.4)
        P(self, bx.animate.move_to([1.6, 1.8, 0]), run_time=0.8)
        q = T("?", 110, bold=True).move_to([3.6, 0.15, 0])
        P(self, FadeIn(q, scale=0.6), run_time=0.5)
        finish(self)


class B10_Fallback(Scene):
    def construct(self):
        self.add(head_label(CONSTRUCTED))
        track = RoundedRectangle(width=2.4, height=0.8, corner_radius=0.4, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([0, 1.7, 0])
        knob = Circle(radius=0.3, fill_color=DARK_L, fill_opacity=1, stroke_width=0).move_to([-0.7, 1.7, 0])
        fl, cl = lab("Forward+", -2.6, 1.7), lab("Compatibility", 3.05, 1.7)
        self.play(FadeIn(track), FadeIn(knob), FadeIn(fl), FadeIn(cl), run_time=0.6)
        U(self, "If it fails")
        P(self, knob.animate.move_to([0.7, 1.7, 0]), run_time=0.5)
        U(self, "recheck each shader")
        tiles = VGroup(*[RoundedRectangle(width=1.2, height=1.2, corner_radius=0.14, fill_color=c, fill_opacity=1, stroke_color=INK, stroke_width=4)
                         .move_to([x, -1.2, 0]) for x, c in ((-4.4, "#C9584A"), (-2.8, BRICK), (-1.2, BAR1))])
        P(self, FadeIn(tiles), run_time=0.5)
        for i, x in enumerate((-4.4, -2.8, -1.2)):
            P(self, Create(check(x - 0.05, -2.3, 0.18)), run_time=0.3)
        U(self, "log what changed")
        logp = page_card(1.0, -1.2, 1.1, 1.5)
        P(self, FadeIn(logp, shift=LEFT * 0.3), run_time=0.4)
        U(self, "web export")
        globe = VGroup(Circle(radius=0.6, stroke_color=DIM, stroke_width=5), Ellipse(width=0.6, height=1.2, stroke_color=DIM, stroke_width=4),
                       Line([-0.6, 0, 0], [0.6, 0, 0], color=DIM, stroke_width=4)).move_to([4.3, -1.2, 0])
        wl = lab("web export", 4.3, -2.35)
        P(self, FadeIn(globe), FadeIn(wl), run_time=0.4)
        strike = Line([3.7, -1.8, 0], [4.9, -0.6, 0], color=INK, stroke_width=8)
        P(self, Create(strike), run_time=0.4)
        finish(self)


class B11_Why(Scene):
    def construct(self):
        blocks = VGroup(*[Iso(-5.65 + i * 1.3, -1.4, 0.5).box(-0.6, -0.6, 0, 1.2, 1.2, 0.9, DARK_TOP, DARK_L, DARK_R) for i in range(5)])
        sl = lab("shown · a5 a6 a7", -3.05, -2.6)
        U(self, "Shaders, particles")
        P(self, LaggedStart(*[FadeIn(b, shift=DOWN * 0.3) for b in blocks], lag_ratio=0.25), FadeIn(sl), run_time=1.2)
        U(self, "Exporting")
        outs = VGroup(*[DashedVMobject(RoundedRectangle(width=1.1, height=1.1, corner_radius=0.12, stroke_color=INK, stroke_width=4), num_dashes=18)
                        .move_to([2.3 + i * 1.4, -0.9, 0]) for i in range(3)])
        nl = lab("new to me", 3.7, -2.6)
        cl = T(CONSTRUCTED, 32)
        cl.move_to([6.1 - cl.width / 2, -0.05, 0])
        P(self, Create(outs), FadeIn(nl), FadeIn(cl), run_time=0.9)
        U(self, "They can judge a finished level")
        iso2 = Iso(0, 1.2, 0.8)
        box = VGroup(iso2.box(-1.0, -1.0, 0, 2.0, 2.0, 1.0), iso2.tape(-1.0, -1.0, 1.0, 2.0, 2.0))
        fl = lab("one finished level", 0, 3.15)
        P(self, FadeIn(box, shift=DOWN * 0.3), FadeIn(fl), blocks.animate.set_opacity(0.5), run_time=0.8)
        finish(self)


class B12_Close(Scene):
    """Full frame; the left panel (x in [-6.35, -0.15]) is overlaid with a real capture by make_media.py."""
    def construct(self):
        panel = Rectangle(width=6.2, height=3.49, stroke_color=INK, stroke_width=4, fill_color=DARK_L, fill_opacity=1).move_to([-3.25, 0.2, 0])
        tl = lab("exists today", -3.25, 2.55)
        rc = VGroup(T("real capture", 32).move_to([-3.25, -2.0, 0]), T("tag a7, game source 4f88f1b", 32).move_to([-3.25, -2.5, 0]))
        self.add(panel, tl, rc)
        iso = Iso(3.5, -1.6, 0.8)
        U(self, "What will exist")
        box = VGroup(iso.box(-1.0, -1.0, 0, 2.0, 2.0, 1.0), iso.tape(-1.0, -1.0, 1.0, 2.0, 2.0))
        wl = lab("will exist", 3.5, 2.55)
        cl = T(CONSTRUCTED, 32).move_to([2.85, -2.95, 0])
        P(self, FadeIn(box, shift=DOWN * 0.3), FadeIn(wl), FadeIn(cl), run_time=0.7)
        scs = VGroup(*[screen(2.3 + i * 1.2, 1.25, 1.0, 0.7) for i in range(3)])
        P(self, LaggedStart(*[GrowFromCenter(s) for s in scs], lag_ratio=0.3), run_time=0.9)
        U(self, "a test report")
        pg = page_card(5.6, -0.3, 0.8, 1.05)
        P(self, FadeIn(pg, shift=DOWN * 0.2), run_time=0.4)
        finish(self)


class BOUT_Title(Scene):
    def construct(self):
        t = VGroup(T("Walker-TANK:", 86, bold=True), T("One Finished Level", 86, bold=True)).arrange(DOWN, buff=0.25).move_to([0, 1.0, 0])
        self.play(FadeIn(t), run_time=0.5)
        rule = Line([-3.0, -0.6, 0], [3.0, -0.6, 0], color=INK, stroke_width=5)
        n = T("Yunqi Zhang", 54).move_to([0, -1.4, 0])
        self.play(Create(rule), FadeIn(n), run_time=0.6)
        finish(self)
