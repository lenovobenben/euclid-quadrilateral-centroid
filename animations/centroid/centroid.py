"""Construct the area centroid, then explain the weights and the medians."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import (
    Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line, Polygon,
    Scene, Text, VGroup, config,
)


HERE = Path(__file__).resolve().parent
FONT = "Noto Sans CJK SC"
BACKGROUND = "#07101F"
FOREGROUND = "#E8F0F7"
MUTED = "#8397A8"
INPUT = "#F45BFF"
CURRENT = "#FFC857"
AUXILIARY = "#8AC6D9"
RESULT = "#5DE2A5"
PLOT_BOUNDS = (-6.25, 0.8, -2.75, 2.72)
LABEL_OFFSETS = {
    "A": (-0.24, -0.20), "B": (0.23, 0.21), "C": (0.23, -0.20),
    "D": (-0.23, -0.23), "E": (0.20, -0.22), "M": (-0.17, -0.25),
    "N": (0.24, -0.12), "F": (-0.20, 0.25), "I": (-0.20, 0.23),
    "J": (0.22, 0.22), "G": (-0.24, 0.17), "U": (0.22, 0.20),
    "W": (-0.24, -0.15), "V": (0.28, 0.12),
}


def load_geometry():
    raw = (HERE / "geometry.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != (HERE / "geometry.sha256").read_text("ascii").strip():
        raise ArithmeticError("geometry digest mismatch")
    data = json.loads(raw)
    if data["source_sha256"] != hashlib.sha256((HERE / "export_geometry.py").read_bytes()).hexdigest():
        raise ArithmeticError("regenerate geometry after editing its exact source")
    if data["branch"] != "circle" or data["verification"]["exact_replays"] < 1:
        raise ArithmeticError("a verified circle example is required")
    return data, digest


@dataclass(frozen=True)
class View:
    center: tuple
    offset: tuple
    scale: float

    def at(self, point):
        xy = (np.array(point) - self.center) * self.scale + self.offset
        return np.array([xy[0], xy[1], 0.0])

    def line(self, first, second, color=AUXILIARY, dashed=False):
        start = self.at(first)
        direction = self.at(second) - start
        left, right, bottom, top = PLOT_BOUNDS
        candidates = []
        for axis, limits in ((0, (left, right)), (1, (bottom, top))):
            if abs(direction[axis]) < 1e-12:
                continue
            for bound in limits:
                parameter = (bound - start[axis]) / direction[axis]
                point = start + parameter * direction
                if left - 1e-9 <= point[0] <= right + 1e-9 and bottom - 1e-9 <= point[1] <= top + 1e-9:
                    candidates.append((parameter, point))
        candidates.sort(key=lambda pair: pair[0])
        if len(candidates) < 2:
            raise ValueError("display line must cross the plotting rectangle")
        line_type = DashedLine if dashed else Line
        return line_type(candidates[0][1], candidates[-1][1], color=color, stroke_width=1.15,
                         stroke_opacity=0.65)


class QuadrilateralCentroid(Scene):
    def text(self, content, size=25, color=FOREGROUND, width=4.7):
        item = Text(content, font=FONT, font_size=size, color=color)
        if item.width > width:
            item.scale_to_fit_width(width)
        return item

    def stage(self, title, caption, color=CURRENT):
        self.sections.append({"title": title, "start_seconds": round(float(self.time), 6)})
        replacement = self.text(caption, 24, color, 12.8).move_to([0, -3.48, 0])
        if hasattr(self, "caption_object"):
            self.remove(self.caption_object)
        self.caption_object = replacement
        self.add(replacement)

    def formula(self, lines, color=FOREGROUND):
        replacement = VGroup(*[
            self.text(content, 26, color, 4.8).move_to([3.9, 0.85 - index * 0.78, 0])
            for index, content in enumerate(lines)
        ])
        if hasattr(self, "formula_object"):
            self.play(FadeOut(self.formula_object), FadeIn(replacement), run_time=0.35)
        else:
            self.play(FadeIn(replacement), run_time=0.35)
        self.formula_object = replacement

    def point(self, name, view, color=AUXILIARY, offset=None, points=None):
        positions = self.points if points is None else points
        at = view.at(positions[name])
        shift = LABEL_OFFSETS[name] if offset is None else offset
        dot = Dot(at, radius=0.043, color=color).set_z_index(5)
        tag = self.text(name, 22, color).move_to(at + np.array([*shift, 0])).set_z_index(6)
        return VGroup(dot, tag)

    def segment(self, first, second, view, color=AUXILIARY, width=1.5, opacity=1):
        return Line(view.at(self.points[first]), view.at(self.points[second]), color=color,
                    stroke_width=width, stroke_opacity=opacity)

    def polygon(self, names, view, color=INPUT, opacity=0.65, fill=0, points=None):
        positions = self.points if points is None else points
        return Polygon(*[view.at(positions[name]) for name in names], color=color,
                       stroke_width=1.6, stroke_opacity=opacity,
                       fill_color=color, fill_opacity=fill)

    def base(self, view):
        return VGroup(self.polygon("ABCD", view),
                      *[self.point(name, view, INPUT) for name in "ABCD"])

    def clear_diagram(self):
        preserved = (self.chrome, self.formula_object, self.caption_object)
        self.play(*[FadeOut(item) for item in list(self.mobjects) if item not in preserved], run_time=0.45)

    def construct(self):
        config.background_color = BACKGROUND
        self.data, self.geometry_hash = load_geometry()
        self.points = {name: np.array(point) for name, point in self.data["points"].items()}
        self.sections = []
        self.objects = {}
        self.view = View((-1, 0.7), (-2.6, -0.1), 0.92)
        title = self.text("四边形薄板的质心", 32, width=9.6)
        title.move_to([-6.35, 3.47, 0], aligned_edge=np.array([-1, 0, 0]))
        condition = self.text("均匀 · 严格凸四边形", 20, MUTED)
        condition.move_to([4.55, 3.47, 0])
        self.chrome = VGroup(title, condition,
                            Line([-6.5, 3.03, 0], [6.5, 3.03, 0], color=MUTED, stroke_width=0.6))
        self.add(self.chrome)
        self.construction()
        self.area_proof()
        self.median_proof()
        self.vertex_average()
        self.special_cases()
        self.finish()
        if not config.dry_run and config.write_to_movie:
            self.write_timeline()

    def construction(self):
        view, points = self.view, self.points
        self.stage("给定四边形", "给定凸四边形 ABCD，求均匀薄板的质心 G")
        self.play(FadeIn(self.base(view)), run_time=0.9)
        self.formula(["均匀薄板", "按面积加权"])
        self.wait(1.8)
        self.stage("对角线交于 E", "连接 AC、BD，交于 E")
        self.formula(["E = AC ∩ BD"])
        for names in ("AC", "BD"):
            self.play(Create(self.segment(*names, view, CURRENT)), run_time=0.8)
        self.play(FadeIn(self.point("E", view)), run_time=0.4)
        self.wait(1.2)
        self.stage("作中垂线与中点", "作两条对角线的中垂线，取得中点 M、N 及交点 F")
        self.formula(["M 为 AC 中点", "N 为 BD 中点", "两条中垂线交于 F"])
        m = view.line(points["M"], points["M"] + np.array([0, 1]), dashed=True)
        direction = points["D"] - points["B"]
        n = view.line(points["N"], points["N"] + np.array([-direction[1], direction[0]]), dashed=True)
        self.objects["bisectors"] = VGroup(m, n)
        self.play(Create(m), FadeIn(self.point("M", view)), run_time=1.1)
        self.play(Create(n), FadeIn(self.point("N", view)), run_time=1.1)
        f = self.point("F", view)
        self.play(FadeIn(f), run_time=0.45)
        self.wait(1.6)
        self.stage("作辅助圆", "以 F 为圆心、经过 E 作圆")
        self.formula(["圆心 F", "半径 FE"])
        circle = Circle(radius=self.data["circle_radius"] * view.scale, color=CURRENT,
                        stroke_width=1.5, fill_opacity=0).move_to(view.at(points["F"]))
        self.objects["circle"] = circle
        radius = self.segment("F", "E", view, CURRENT)
        self.play(Create(radius), run_time=0.6)
        self.play(Create(circle), run_time=1.6)
        self.play(FadeOut(radius), run_time=0.3)
        self.wait(1)
        self.stage("取得另两个交点", "取圆与 AC、BD 除 E 以外的交点 I、J")
        self.formula(["I ∈ AC ∩ 圆", "J ∈ BD ∩ 圆", "I、J 均与 E 不同"])
        self.play(FadeIn(self.point("I", view, CURRENT)), run_time=0.5)
        self.play(FadeIn(self.point("J", view, CURRENT)), run_time=0.5)
        self.wait(1.8)
        self.play(FadeOut(self.objects["bisectors"]), FadeOut(f), circle.animate.set_stroke(opacity=0.22), run_time=0.5)
        self.stage("两线交于 G", "连接 NI、MJ，交点 G 就是所求质心", RESULT)
        self.formula(["G = NI ∩ MJ"], RESULT)
        for names in ("NI", "MJ"):
            self.play(Create(self.segment(*names, view, CURRENT, 2)), run_time=1)
        self.play(FadeIn(self.point("G", view, RESULT)), run_time=0.5)
        self.wait(2)

    def area_proof(self):
        self.stage("面积加权", "沿 AC 分成两个三角形，分别取质心 U、W")
        self.clear_diagram()
        view = self.view
        self.play(FadeIn(self.base(view)), run_time=0.6)
        self.play(FadeIn(self.polygon("ABC", view, AUXILIARY, 0.6, 0.10)),
                  FadeIn(self.polygon("ACD", view, CURRENT, 0.6, 0.10)),
                  Create(self.segment("B", "D", view, AUXILIARY, opacity=0.4)),
                  FadeIn(self.point("E", view)), run_time=0.8)
        self.formula(["S₁ = [ABC]，S₂ = [ACD]", "S₁ : S₂ = BE : ED"])
        self.play(FadeIn(self.point("U", view, AUXILIARY)),
                  FadeIn(self.point("W", view, CURRENT)), run_time=0.6)
        self.wait(2.2)
        self.stage("拼合薄板", "两个三角形的质心，按各自面积作加权平均")
        self.formula(["U = (A+B+C)/3", "W = (A+C+D)/3", "G = (S₁U+S₂W)/(S₁+S₂)"])
        self.play(Create(self.segment("U", "W", view, RESULT, 2)),
                  FadeIn(self.point("G", view, RESULT, (-0.26, 0.04))), run_time=0.8)
        self.wait(3)
        self.stage("化简面积权重", "利用 BE : ED 的面积比，化简得到质心公式")
        self.formula(["G = (2M+2N−E)/3", "面积加权的质心"], RESULT)
        self.wait(3)

    def median_proof(self):
        self.stage("辅助三角形", "圆心在弦的中垂线上，M、N 分别为 EI、EJ 的中点")
        self.clear_diagram()
        view = View((-0.75, 0.75), (-2.65, 0), 1.6)
        self.play(Create(self.polygon("EIJ", view, AUXILIARY)), run_time=0.8)
        self.play(*[FadeIn(self.point(name, view, CURRENT)) for name in "EIJ"],
                  FadeIn(self.point("M", view)), FadeIn(self.point("N", view)), run_time=0.5)
        self.formula(["I = 2M − E", "J = 2N − E"])
        self.wait(2)
        self.stage("两条中线", "NI、MJ 是三角形 EIJ 的两条中线，唯一交于其质心")
        self.play(Create(self.segment("N", "I", view, RESULT, 2)),
                  Create(self.segment("M", "J", view, RESULT, 2)), run_time=1.2)
        self.play(FadeIn(self.point("G", view, RESULT)), run_time=0.4)
        self.formula(["G = (E+I+J)/3", "= (2M+2N−E)/3"], RESULT)
        self.wait(3)

    def vertex_average(self):
        self.stage("顶点平均点的关系", "令 V 为四顶点的平均点，则 E、V、G 依次共线")
        self.clear_diagram()
        view = View((-0.25, 0.25), (-2.6, 0), 6)
        self.play(Create(self.segment("E", "V", view, CURRENT, 2)),
                  Create(self.segment("V", "G", view, RESULT, 2)), run_time=0.9)
        self.play(FadeIn(self.point("E", view)),
                  FadeIn(self.point("V", view, CURRENT, (0.30, 0.02))),
                  FadeIn(self.point("G", view, RESULT, (-0.23, 0.22))), run_time=0.5)
        marks = VGroup(*[Dot(view.at(self.points["E"] + fraction * (self.points["G"] - self.points["E"])),
                            radius=0.025, color=MUTED) for fraction in (0.25, 0.5)])
        self.play(FadeIn(marks), run_time=0.3)
        self.formula(["V = (A+B+C+D)/4", "G − V = (V − E)/3", "EV : VG = 3 : 1"])
        self.wait(3)

    def special_cases(self):
        self.stage("一条对角线被平分", "若 M = E，沿 EN 取三分之二处；另一种情形对称")
        self.clear_diagram()
        points = {name: np.array(point) for name, point in
                  self.data["special_examples"]["one_midpoint"]["points"].items()}
        view = View((0, 1.5), (-2.65, 0), 0.82)
        self.play(Create(self.polygon("ABCD", view, points=points)),
                  *[FadeIn(self.point(name, view, INPUT, points=points)) for name in "ABCD"], run_time=0.7)
        self.play(Create(Line(view.at(points["A"]), view.at(points["C"]), color=AUXILIARY, stroke_width=1.2)),
                  Create(Line(view.at(points["B"]), view.at(points["D"]), color=AUXILIARY, stroke_width=1.2)),
                  FadeIn(self.point("E", view, offset=(-0.28, -0.20), points=points)),
                  FadeIn(self.point("N", view, offset=(0.28, 0.10), points=points)), run_time=0.8)
        self.play(Create(Line(view.at(points["E"]), view.at(points["G"]), color=RESULT, stroke_width=2.5)),
                  FadeIn(self.point("G", view, RESULT, (-0.30, 0.05), points)), run_time=0.8)
        self.formula(["M = E，N ≠ E", "EG = (2/3) EN"], RESULT)
        self.wait(2.7)
        self.stage("平行四边形", "若 M = N = E，直接输出 G = E", RESULT)
        self.clear_diagram()
        points = {name: np.array(point) for name, point in
                  self.data["special_examples"]["parallelogram"]["points"].items()}
        view = View((0, 0), (-2.65, 0), 0.95)
        self.play(Create(self.polygon("ABCD", view, points=points)),
                  *[FadeIn(self.point(name, view, INPUT, points=points)) for name in "ABCD"], run_time=0.7)
        self.play(*[Create(Line(view.at(points[first]), view.at(points[second]), color=AUXILIARY, stroke_width=1.2))
                    for first, second in ("AC", "BD")],
                  FadeIn(self.point("G", view, RESULT, points=points)), run_time=0.7)
        self.formula(["M = N = E", "G = E"], RESULT)
        self.wait(2)

    def finish(self):
        self.stage("质心已作成", "辅助圆与两条中线，作出均匀薄板的质心 G", RESULT)
        self.clear_diagram()
        view = self.view
        diagram = self.base(view)
        for names in ("AC", "BD", "NI", "MJ"):
            diagram.add(self.segment(*names, view, AUXILIARY, opacity=0.45))
        for name in "EMNIJ":
            diagram.add(self.point(name, view))
        diagram.add(self.point("G", view, RESULT))
        self.play(FadeIn(diagram), run_time=0.8)
        self.formula(["G = (A+B+C+D−E)/3", "均匀薄板的质心"], RESULT)
        self.wait(3.5)

    def write_timeline(self):
        movie = Path(self.renderer.file_writer.movie_file_path)
        report = {
            "scene": type(self).__name__, "movie_file": movie.name,
            "geometry_sha256": self.geometry_hash,
            "animation_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "resolution": [config.pixel_width, config.pixel_height],
            "frame_rate": config.frame_rate,
            "duration_seconds": round(float(self.time), 6), "sections": self.sections,
        }
        movie.with_suffix(".timeline.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
