"""Source-time <-> output-time mapping over a list of keep intervals."""
class Timeline:
    def __init__(self, keeps):  # [(src_start, src_end[, speed]), ...] sorted, non-overlapping
        self.keeps = [(k[0], k[1], k[2] if len(k) > 2 else 1.0) for k in keeps]
        self.offsets = []; t = 0.0
        for a, b, sp in self.keeps:
            self.offsets.append(t); t += (b - a) / sp
        self.duration = t
    def to_out(self, ts):
        """Map source time to output time. Times inside a cut snap to the cut point."""
        for (a, b, sp), off in zip(self.keeps, self.offsets):
            if ts < a: return off
            if ts <= b: return off + (ts - a) / sp
        return self.duration
    def is_cut(self, ts):
        return not any(a <= ts <= b for a, b, _ in self.keeps)

def apply_speed(keeps, ramps):
    """Split keeps at ramp edges and tag each piece with its speed. ramps: [(a, b, factor)]."""
    out = []
    for a, b in keeps:
        edges = sorted({a, b, *[x for r in ramps for x in r[:2] if a < x < b]})
        for x, y in zip(edges, edges[1:]):
            sp = next((f for ra, rb, f in ramps if ra <= x and y <= rb), 1.0)
            out.append((x, y, sp))
    return out

def invert(cuts, total):
    """cuts [(a,b)] -> keeps covering [0,total] minus cuts."""
    keeps, t = [], 0.0
    for a, b in sorted(cuts):
        a, b = max(a, t), min(b, total)
        if a > t: keeps.append((t, a))
        t = max(t, b)
    if t < total: keeps.append((t, total))
    return [(a, b) for a, b in keeps if b - a > 0.04]

def merge(intervals, gap=0.0):
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1] + gap: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out
