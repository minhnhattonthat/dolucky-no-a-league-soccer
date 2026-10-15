"""Game LZ codec (decompressor at $80:F28D). Block: u16 size, u16 (unused here), then the stream.

Stream: control byte, bits MSB first, one per item:
  1           literal byte
  0 1  n      n == 0: end; else repeat the previous byte n+1 times          (MVN from X-1)
  0 0 ll d    ll != 0: copy ll+1 bytes from X - 256 + d
  0 0 00 w16  copy (w & 15) + 1 bytes from X - 0x1000 + (w >> 4)
A new control byte is read after 8 items.  (The 2-bit length and the 'type' bits come from the same control byte.)
"""


def decompress(data, off):
    size = data[off] | data[off + 1] << 8
    p = off + 4
    out = bytearray()
    bits = []

    def bit():
        nonlocal p
        if not bits:
            c = data[p]; p += 1
            bits.extend((c >> (7 - i)) & 1 for i in range(8))
        return bits.pop(0)

    while True:
        if bit():
            out.append(data[p]); p += 1
            continue
        if bit():
            n = data[p]
            if n == 0:
                p += 1
                break
            p += 1
            for _ in range(n + 1):
                out.append(out[-1])
            continue
        ll = bit() << 1 | bit()
        if ll:
            d = data[p]; p += 1
            src = len(out) - 256 + d
            n = ll + 1
        else:
            w = data[p] | data[p + 1] << 8; p += 2
            src = len(out) - 0x1000 + (w >> 4)
            n = (w & 15) + 1
        for i in range(n):
            out.append(out[src + i])
    return bytes(out), p - off, size


def compress(raw):
    """Greedy encoder (literals, runs, short and long references). Output decodes back to raw (tested)."""
    out = bytearray([len(raw) & 0xFF, len(raw) >> 8, 0, 0])
    items = []  # (bits list, payload bytes)
    i, n = 0, len(raw)
    while i < n:
        best = (0, None)
        # run of previous byte
        if i > 0:
            r = 0
            while i + r < n and raw[i + r] == raw[i - 1] and r < 256:
                r += 1
            if r >= 2:
                best = (r, ('run', r))
        # back references
        lo = max(0, i - 0x1000)
        for s in range(i - 1, lo - 1, -1):
            if raw[s] != raw[i]:
                continue
            m = 0
            while i + m < n and raw[s + m] == raw[i + m] and m < 16:
                m += 1
            dist = i - s
            if dist <= 256 and m >= 2:
                mm = min(m, 4)
                cand = (mm, ('short', dist, mm))
                if mm > best[0] or (mm == best[0] and best[1] and best[1][0] == 'long'):
                    best = max(best, cand, key=lambda t: t[0])
            if m >= 3 and m > best[0]:
                best = (m, ('long', dist, m))
            if best[0] >= 16:
                break
        if best[0] >= 2:
            k = best[1]
            if k[0] == 'run':
                items.append(([0, 1], bytes([k[1] - 1])))
            elif k[0] == 'short':
                ll = k[2] - 1
                items.append(([0, 0, ll >> 1, ll & 1], bytes([256 - k[1]])))
            else:
                w = ((0x1000 - k[1]) << 4) | (k[2] - 1)
                items.append(([0, 0, 0, 0], bytes([w & 0xFF, w >> 8])))
            i += best[0]
        else:
            items.append(([1], bytes([raw[i]])))
            i += 1
    items.append(([0, 1], b'\x00'))
    # pack: control byte holds 8 bits; a new control byte is read when 8 bits are used, even mid-item
    bitq = []
    pend = bytearray()
    for b, pay in items:
        for x in b:
            if not bitq or len(bitq[-1][0]) == 8:
                bitq.append(([], bytearray()))
            bitq[-1][0].append(x)
        bitq[-1][1].extend(pay)
    # NOTE: payload bytes follow the control byte in which the item's last bit sits.
    for bits_, pay in bitq:
        bits_ = bits_ + [0] * (8 - len(bits_))
        out.append(sum(v << (7 - k) for k, v in enumerate(bits_)))
        out += pay
    return bytes(out)
