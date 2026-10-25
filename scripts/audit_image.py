#!/usr/bin/env python3
"""Read-only GPT structure audit, no mounts, loop devices or image writes.
Not a recovery validation or a filesystem consistency check.
"""
import argparse, json, os, struct, zlib

def audit(path):
    size = os.path.getsize(path)
    if not os.path.isfile(path):
        raise ValueError('regular image file required')
    with open(path, 'rb') as f:
        mbr = f.read(512)
        result = {'size_bytes': size, 'expected_h20_size': size == 7818182656,
                  'mbr_signature': mbr[510:512] == b'\x55\xaa', 'partitions': []}
        f.seek(512)
        h = f.read(512)
        if h[:8] != b'EFI PART':
            raise ValueError('GPT absent at sector 1; proprietary/MBR layout requires separate analysis')
        hs, expected_crc = struct.unpack_from('<II', h, 12)
        if not 92 <= hs <= 512:
            raise ValueError('invalid GPT header length')
        checked = bytearray(h[:hs]); checked[16:20] = b'\0'*4
        result['header_crc_ok'] = zlib.crc32(checked) == expected_crc
        current, backup, first, last = struct.unpack_from('<QQQQ', h, 24)
        entries_lba, count, width, crc = struct.unpack_from('<QIII', h, 72)
        if width < 128 or width % 8 or count*width > 16*1024*1024:
            raise ValueError('unsupported or oversized GPT entries')
        if entries_lba*512 + count*width > size:
            raise ValueError('entry table outside image')
        f.seek(entries_lba*512); table = f.read(count*width)
        result['table_crc_ok'] = zlib.crc32(table) == crc
        result['header_bounds_ok'] = current == 1 and backup < size//512 and first <= last < size//512
        intervals = []
        for i in range(count):
            e = table[i*width:(i+1)*width]
            if e[:16] == b'\0'*16: continue
            start, end = struct.unpack_from('<QQ', e, 32)
            valid = first <= start <= end <= last and (end+1)*512 <= size
            overlap = any(start <= b and end >= a for a,b in intervals)
            intervals.append((start,end))
            magic = ''
            if valid:
                f.seek(start*512); magic = f.read(16).hex()
            result['partitions'].append({'index': i+1, 'name': e[56:128].decode('utf-16-le',errors='replace').rstrip('\0'), 'start_lba':start, 'end_lba':end, 'bounds_ok':valid, 'overlap':overlap, 'first_16_bytes_hex':magic})
        f.seek(backup*512); bh = f.read(512)
        result['backup_signature_ok'] = bh[:8] == b'EFI PART'
        # Backup header/table CRC validation is deliberately not claimed.
        result['limitations'] = ['Backup GPT CRC not checked','No filesystem, bootability, AVB or restoration validation','No comparison to physical eMMC']
        result['primary_structure_ok'] = all(result[k] for k in ('header_crc_ok','table_crc_ok','header_bounds_ok')) and all(p['bounds_ok'] and not p['overlap'] for p in result['partitions'])
        return result

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('image'); args=p.parse_args()
    try:
        r=audit(args.image); print(json.dumps(r,indent=2,ensure_ascii=False)); raise SystemExit(0 if r['primary_structure_ok'] else 2)
    except (ValueError,OSError,struct.error) as e:
        p.exit(2, f'AUDIT FAILED: {e}\n')
