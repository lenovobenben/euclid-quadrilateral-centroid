"""Replay the centroid construction exactly and export one Manim example."""

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path

from sage.all import AA, PolynomialRing, QQ
from sage.version import version


HERE = Path(__file__).resolve().parent


def add(first, second):
    return tuple(x + y for x, y in zip(first, second))


def subtract(first, second):
    return tuple(x - y for x, y in zip(first, second))


def scale(factor, point):
    return tuple(factor * value for value in point)


def dot(first, second):
    return sum(x * y for x, y in zip(first, second))


def cross(first, second):
    return first[0] * second[1] - first[1] * second[0]


def midpoint(first, second):
    return scale(AA(1) / 2, add(first, second))


def line(first, second):
    x, y = subtract(second, first)
    if x == y == 0:
        raise ValueError("two distinct line points are required")
    return (-y, x, y * first[0] - x * first[1])


def value(coefficients, point):
    a, b, c = coefficients
    return a * point[0] + b * point[1] + c


def intersect(first, second):
    a, b, c = first
    d, e, f = second
    determinant = a * e - b * d
    if determinant == 0:
        raise ValueError("a unique line intersection is required")
    point = ((b * f - c * e) / determinant, (c * d - a * f) / determinant)
    assert value(first, point) == value(second, point) == 0
    return point


def perpendicular_bisector(first, second):
    direction = subtract(second, first)
    middle = midpoint(first, second)
    return (*direction, -dot(direction, middle))


def line_circle(first, second, center, through):
    direction = subtract(second, first)
    offset = subtract(first, center)
    a = dot(direction, direction)
    b = 2 * dot(offset, direction)
    c = dot(offset, offset) - dot(subtract(through, center), subtract(through, center))
    discriminant = b * b - 4 * a * c
    if a == 0 or discriminant < 0:
        raise ValueError("a nonzero secant or tangent is required")
    roots = {(-b + discriminant.sqrt()) / (2 * a),
             (-b - discriminant.sqrt()) / (2 * a)}
    points = tuple(add(first, scale(root, direction)) for root in sorted(roots))
    for point in points:
        assert value(line(first, second), point) == 0
        assert dot(subtract(point, center), subtract(point, center)) == dot(
            subtract(through, center), subtract(through, center))
    return points


def other_intersection(points, known):
    assert known in points
    others = [point for point in points if point != known]
    assert len(others) == 1
    return others[0]


def two_thirds(origin, target, auxiliary):
    assert cross(subtract(target, origin), subtract(auxiliary, origin)) != 0
    second = other_intersection(line_circle(origin, auxiliary, auxiliary, origin), origin)
    third = other_intersection(line_circle(origin, auxiliary, second, auxiliary), auxiliary)
    a, b, _ = line(third, target)
    parallel = (a, b, -a * second[0] - b * second[1])
    result = intersect(line(origin, target), parallel)
    assert result == add(origin, scale(AA(2) / 3, subtract(target, origin)))
    return result


def construct(coordinates):
    if len(coordinates) != 4 or any(len(point) != 2 for point in coordinates):
        raise ValueError("four planar points are required")
    vertices = [tuple(AA(entry) for entry in point) for point in coordinates]
    turns = [cross(subtract(vertices[(index + 1) % 4], vertices[index]),
                   subtract(vertices[(index + 2) % 4], vertices[(index + 1) % 4]))
             for index in range(4)]
    if not (all(turn > 0 for turn in turns) or all(turn < 0 for turn in turns)):
        raise ValueError("strictly convex boundary order is required")
    a, b, c, d = vertices
    diagonals = (line(a, c), line(b, d))
    e = intersect(*diagonals)
    bisectors = (perpendicular_bisector(a, c), perpendicular_bisector(b, d))
    m, n = (intersect(diagonal, bisector)
            for diagonal, bisector in zip(diagonals, bisectors))
    points = dict(zip("ABCD", vertices))
    points.update(E=e, M=m, N=n, V=midpoint(m, n))
    if m == n == e:
        points["G"] = e
        return "parallelogram", points
    if m == e:
        points["G"] = two_thirds(e, n, a)
        return "M_equals_E", points
    if n == e:
        points["G"] = two_thirds(e, m, b)
        return "N_equals_E", points
    f = intersect(*bisectors)
    i = other_intersection(line_circle(a, c, f, e), e)
    j = other_intersection(line_circle(b, d, f, e), e)
    assert i == subtract(scale(2, m), e)
    assert j == subtract(scale(2, n), e)
    g = intersect(line(n, i), line(m, j))
    assert g == scale(AA(1) / 3, add(add(e, i), j))
    points.update(F=f, I=i, J=j, G=g)
    return "circle", points


def boundary_centroid(vertices):
    """Integrate first moments along the polygon boundary independently."""
    twice_area = AA(0)
    moment = (AA(0), AA(0))
    for first, second in zip(vertices, vertices[1:] + vertices[:1]):
        weight = cross(first, second)
        twice_area += weight
        moment = add(moment, scale(weight, add(first, second)))
    assert twice_area != 0
    return scale(1 / (3 * twice_area), moment)


def verify_case(vertices):
    branch, points = construct(vertices)
    g, e, v = (points[name] for name in ("G", "E", "V"))
    exact_vertices = [points[name] for name in "ABCD"]
    assert g == boundary_centroid(exact_vertices)
    vertex_sum = tuple(sum(point[index] for point in exact_vertices) for index in range(2))
    assert g == scale(AA(1) / 3, subtract(vertex_sum, e))
    assert subtract(g, v) == scale(AA(1) / 3, subtract(v, e))
    orientation = cross(subtract(exact_vertices[1], exact_vertices[0]),
                        subtract(exact_vertices[2], exact_vertices[1]))
    for first, second in zip(exact_vertices, exact_vertices[1:] + exact_vertices[:1]):
        assert orientation * cross(subtract(second, first), subtract(g, first)) > 0
    return branch, points


def symbolic_checks():
    ring = PolynomialRing(QQ, names="a,b,c,d,u,v")
    a, b, c, d, u, v = ring.gens()
    vertices = [(-a, ring(0)), (b * u, b * v), (c, ring(0)), (-d * u, -d * v)]
    weights = [cross(first, second)
               for first, second in zip(vertices, vertices[1:] + vertices[:1])]
    total = sum(weights)
    assert total == -(a + c) * (b + d) * v
    expected = (-a + c + (b - d) * u, (b - d) * v)
    for index in range(2):
        moment = sum((first[index] + second[index]) * weight
                     for first, second, weight in zip(vertices, vertices[1:] + vertices[:1], weights))
        assert moment == total * expected[index]
    return 3


def display(points):
    return {name: [float(entry) for entry in point] for name, point in points.items()}


def exact(points):
    return {name: [str(entry) for entry in point] for name, point in points.items()}


def run():
    counts = Counter()
    for a, b, c, d in product((1, 2, 3), repeat=4):
        vertices = [(-a, 0), (b, 2 * b), (c, 0), (-d, -2 * d)]
        for reverse in (False, True):
            branch, _ = verify_case(list(reversed(vertices)) if reverse else vertices)
            counts[branch] += 1
    near = AA(10) ** -100
    special = [
        [(-2, 0), (1, 3), (1, 0), (-1, -3)],
        [(-2, 0), (0, 3), (1, 0), (0, -1)],
        [(-2, 0), (1, 3), (2, 0), (-1, -3)],
        [(-2, 0), (1, 3), (2 + near, 0), (-1 - near, -3 - 3 * near)],
        [(-2, 0), (1, AA(2).sqrt()), (1, 0), (-2, -2 * AA(2).sqrt())],
    ]
    for vertices in special:
        branch, _ = verify_case(vertices)
        counts[branch] += 1
    example = [(-4, 0), (1, 3), (2, 0), (-QQ(1) / 2, -QQ(3) / 2)]
    transformations = [
        (AA(1), AA(0), AA(1), (0, 0)),
        (AA(3) / 5, AA(4) / 5, AA(7) / 3, (5, -2)),
        (AA(0), AA(1), AA(1) / 7, (-4, 9)),
        (AA(1), AA(0), -AA(1), (1, 2)),
    ]
    for vertices in [example, *special]:
        _, original = verify_case(vertices)
        for cosine, sine, factor, translation in transformations:
            def transform(point):
                x, y = point
                return add(scale(factor, (cosine * x - sine * y, sine * x + cosine * y)), translation)
            for reflection in (1, -1):
                transformed = [(transform(point)[0], reflection * transform(point)[1]) for point in vertices]
                for shift in range(4):
                    ordered = transformed[shift:] + transformed[:shift]
                    branch, result = verify_case(ordered)
                    target = transform(original["G"])
                    assert result["G"] == (target[0], reflection * target[1])
                    counts[branch] += 1
    rejected = 0
    for vertices in [[], [(0, 0)] * 4, [(0, 0), (1, 0), (2, 0), (0, 1)],
                     [(0, 0), (1, 1), (0, 1), (1, 0)],
                     [(0, 0), (3, 0), (1, 1), (0, 3)]]:
        try:
            construct(vertices)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid input was accepted")
    branch, points = verify_case(example)
    points["U"] = scale(AA(1) / 3, add(add(points["A"], points["B"]), points["C"]))
    points["W"] = scale(AA(1) / 3, add(add(points["A"], points["C"]), points["D"]))
    assert points["G"] == scale(AA(1) / 3, add(scale(2, points["U"]), points["W"]))
    special_examples = {}
    for name, coordinates in {
        "one_midpoint": [(-2, 0), (0, 4), (2, 0), (0, -1)],
        "parallelogram": [(-QQ(5) / 2, 0), (1, 2), (QQ(5) / 2, 0), (-1, -2)],
    }.items():
        special_branch, special_points = verify_case(coordinates)
        counts[special_branch] += 1
        special_examples[name] = {"branch": special_branch, "points": display(special_points),
                                  "exact_points": exact(special_points)}
    report = {
        "sage_version": version,
        "symbolic_identities": symbolic_checks(),
        "exact_replays": sum(counts.values()),
        "branches": dict(sorted(counts.items())),
        "rejected_inputs": rejected,
        "checks": ["boundary first moments", "centroid formula", "strict interior",
                   "circle intersections", "special-case trisection", "similarity covariance"],
    }
    data = {
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "points": display(points), "exact_points": exact(points),
        "circle_radius": float(dot(subtract(points["F"], points["E"]),
                                   subtract(points["F"], points["E"])).sqrt()),
        "branch": branch, "verification": report,
        "special_examples": special_examples,
    }
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (HERE / "geometry.json").write_bytes(raw)
    (HERE / "geometry.sha256").write_text(hashlib.sha256(raw).hexdigest() + "\n", encoding="ascii")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
