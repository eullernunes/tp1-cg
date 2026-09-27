def line_dda(fb, p0, p1, color):
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        fb.set_pixel(round(x0), round(y0), color)
        return
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x0, y0
    for _ in range(steps + 1):
        fb.set_pixel(round(x), round(y), color)
        x += x_inc
        y += y_inc


def line_bresenham(fb, p0, p1, color):
    x0, y0 = round(p0[0]), round(p0[1])
    x1, y1 = round(p1[0]), round(p1[1])
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        fb.set_pixel(x, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def circle_bresenham(fb, center, radius, color):
    cx, cy = round(center[0]), round(center[1])
    r = round(radius)
    x = 0
    y = r
    d = 3 - 2 * r

    def plot_octants(x, y):
        for px, py in (
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x),
        ):
            fb.set_pixel(px, py, color)

    while x <= y:
        plot_octants(x, y)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1
