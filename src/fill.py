def _neighbors_4(x, y):
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def _neighbors_8(x, y):
    return _neighbors_4(x, y) + [
        (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1),
    ]


def _neighbor_fn(connectivity):
    if connectivity == 4:
        return _neighbors_4
    if connectivity == 8:
        return _neighbors_8
    raise ValueError("connectivity must be 4 or 8")


def boundary_fill(fb, seed, border_color, fill_color, connectivity=4):
    neighbors = _neighbor_fn(connectivity)
    sx, sy = seed
    if fb.get_pixel(sx, sy) is None:
        return  # seed outside canvas bounds

    stack = [(sx, sy)]
    visited = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        current = fb.get_pixel(x, y)
        if current is None or current == border_color or current == fill_color:
            continue
        fb.set_pixel(x, y, fill_color)
        for nx, ny in neighbors(x, y):
            if (nx, ny) not in visited:
                stack.append((nx, ny))


def flood_fill(fb, seed, target_color, fill_color, connectivity=4):
    neighbors = _neighbor_fn(connectivity)
    if target_color == fill_color:
        return
    sx, sy = seed
    if fb.get_pixel(sx, sy) != target_color:
        return

    stack = [(sx, sy)]
    visited = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if fb.get_pixel(x, y) != target_color:
            continue
        fb.set_pixel(x, y, fill_color)
        for nx, ny in neighbors(x, y):
            if (nx, ny) not in visited:
                stack.append((nx, ny))
