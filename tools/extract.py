#!/usr/bin/env python3
"""Termux/PC me chalao (sirf python3 chahiye).
usage: python3 extract.py boot.img vendor_boot.img device/xiaomi/duchamp/prebuilt
boot.img / vendor_boot.img PHONE KE ACTIVE SLOT ki hone chahiye (dd se dump karo).
"""
import struct, sys, os, shutil, re

def lz4_block(s):
    o = bytearray(); i = 0; n = len(s)
    while i < n:
        t = s[i]; i += 1; l = t >> 4
        if l == 15:
            while True:
                b = s[i]; i += 1; l += b
                if b != 255: break
        o += s[i:i+l]; i += l
        if i >= n: break
        off = s[i] | s[i+1] << 8; i += 2; m = t & 15
        if m == 15:
            while True:
                b = s[i]; i += 1; m += b
                if b != 255: break
        m += 4; st = len(o) - off
        for k in range(m): o.append(o[st+k])
    return bytes(o)

def lz4_legacy(d):
    assert d[:4] == bytes.fromhex('02214c18'), "lz4 legacy nahi hai"
    i = 4; o = bytearray()
    while i + 4 <= len(d):
        sz = struct.unpack_from('<I', d, i)[0]
        if sz == 0x184C2102: i += 4; continue
        i += 4; o += lz4_block(d[i:i+sz]); i += sz
    return bytes(o)

def decomp(d):
    if d[:4] == bytes.fromhex('02214c18'): return lz4_legacy(d)
    if d[:2] == b'\x1f\x8b':
        import gzip; return gzip.decompress(d)
    return d

def cpio(d):
    i = 0
    while True:
        f = lambda k: int(d[i+6+8*k:i+14+8*k], 16)
        mode, fs, ns = f(1), f(6), f(11)
        name = d[i+110:i+110+ns-1].decode(); i = (i+110+ns+3) & ~3
        data = d[i:i+fs]; i = (i+fs+3) & ~3
        if name == 'TRAILER!!!': break
        yield name, mode, data

al = lambda x, p=4096: (x+p-1)//p*p

def main(boot, vboot, out):
    b = open(boot, 'rb').read(); v = open(vboot, 'rb').read()
    assert b[:8] == b'ANDROID!' and v[:8] == b'VNDRBOOT'
    ks = struct.unpack_from('<I', b, 8)[0]
    kernel = b[4096:4096+ks]
    ver, page, ka, ra, vrs = struct.unpack_from('<5I', v, 8)
    o = 28 + 2048
    tags = struct.unpack_from('<I', v, o)[0]
    hs, dtbs, dtba = struct.unpack_from('<IIQ', v, o+20)
    tbl, tbn, tbe, bcs = struct.unpack_from('<IIII', v, o+36)
    p = al(hs); rd = v[p:p+vrs]; p += al(vrs)
    dtb = v[p:p+dtbs]; p += al(dtbs); tab = v[p:p+tbl]
    frags = []
    for i in range(tbn):
        e = tab[i*tbe:(i+1)*tbe]
        sz, off, typ = struct.unpack_from('<III', e, 0)
        frags.append((typ, e[12:44].split(b'\0')[0].decode(), rd[off:off+sz]))
    os.makedirs(out, exist_ok=True)
    mod = os.path.join(out, 'modules'); shutil.rmtree(mod, ignore_errors=True); os.makedirs(mod)
    open(os.path.join(out, 'kernel'), 'wb').write(kernel)
    open(os.path.join(out, 'dtb.img'), 'wb').write(dtb)
    nmod = 0; vermagic = None
    for typ, name, blob in frags:
        if typ != 1: continue            # type 1 = platform fragment (modules yahin hain)
        for n, m, data in cpio(decomp(blob)):
            if n.startswith('lib/modules/') and m & 0o170000 == 0o100000:
                open(os.path.join(mod, os.path.basename(n)), 'wb').write(data)
                if n.endswith('.ko'):
                    nmod += 1
                    if not vermagic:
                        mm = re.search(rb'vermagic=([^\0]+)', data)
                        vermagic = mm.group(1).decode() if mm else None
    kv = re.search(rb'Linux version (\S+)', decomp(kernel))
    kv = kv.group(1).decode() if kv else '?'
    info = [f'kernel release : {kv}', f'module vermagic: {vermagic}', f'modules        : {nmod}',
            f'header version : {ver}  page {page}', f'kernel_addr    : {ka:#x}',
            f'ramdisk_addr   : {ra:#x}', f'tags/dtb addr  : {tags:#x} / {dtba:#x}',
            f'dtb size       : {dtbs}']
    open(os.path.join(out, 'info.txt'), 'w').write('\n'.join(info) + '\n')
    print('\n'.join(info))
    base = lambda x: (re.match(r'\d+\.\d+\.\d+(-android\d+-\d+)?', x or '') or [None])[0]
    if vermagic and base(vermagic) != base(kv):
        print('\n!!! WARNING: kernel aur modules ka version alag hai. Images ek hi slot/ROM ki nahi hain.')
    else:
        print('\nOK: kernel aur modules match karte hain.')

if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
