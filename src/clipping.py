from .models import Line

INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def _region_code(x, y, window):
    xmin, ymin, xmax, ymax = window
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


def cohen_sutherland(line, window):
    xmin, ymin, xmax, ymax = window
    x0, y0 = line.start
    x1, y1 = line.end
    code0 = _region_code(x0, y0, window)
    code1 = _region_code(x1, y1, window)

    while True:
        if code0 == 0 and code1 == 0:
            return Line((x0, y0), (x1, y1), algorithm=line.algorithm)
        if code0 & code1 != 0:
            return None

        code_out = code0 if code0 != 0 else code1
        if code_out & TOP:
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
            y = ymax
        elif code_out & BOTTOM:
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
            y = ymin
        elif code_out & RIGHT:
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
            x = xmax
        else:  # LEFT
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
            x = xmin

        if code_out == code0:
            x0, y0 = x, y
            code0 = _region_code(x0, y0, window)
        else:
            x1, y1 = x, y
            code1 = _region_code(x1, y1, window)


def liang_barsky(line, window):
    xmin, ymin, xmax, ymax = window
    x0, y0 = line.start
    x1, y1 = line.end
    dx = x1 - x0
    dy = y1 - y0
    p = [-dx, dx, -dy, dy]
    q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]
    t0, t1 = 0.0, 1.0

    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
            continue
        t = qi / pi
        if pi < 0:
            if t > t1:
                return None
            t0 = max(t0, t)
        else:
            if t < t0:
                return None
            t1 = min(t1, t)

    nx0 = x0 + t0 * dx
    ny0 = y0 + t0 * dy
    nx1 = x0 + t1 * dx
    ny1 = y0 + t1 * dy
    return Line((nx0, ny0), (nx1, ny1), algorithm=line.algorithm)
