#!/usr/bin/env python3
"""Read-only raw Android super inspector/extractor (single physical block device).
Format: AOSP fs_mgr/liblp/include/liblp/metadata_format.h (Apache-2.0).
This independently written reader supports v10.0..10.2 LINEAR/ZERO extents.
It does not mount filesystems, write block devices or build/flash firmware.
"""
import argparse, hashlib, json, re, struct
from pathlib import Path

class SuperReader:
    def __init__(self, path, offset=0, length=None):
        self.path=Path(path)
        if not self.path.is_file(): raise ValueError('regular raw image required')
        self.offset=offset
        self.length=self.path.stat().st_size-offset if length is None else length
        if offset<0 or self.length<=0 or offset+self.length>self.path.stat().st_size:
            raise ValueError('invalid image bounds')
    def read(self, off, count):
        if off<0 or count<0 or off+count>self.length: raise ValueError('read outside super bounds')
        with self.path.open('rb') as f:
            f.seek(self.offset+off);b=f.read(count)
        if len(b)!=count: raise ValueError('truncated image')
        return b
    def geometry(self, off):
        b=self.read(off,4096);magic,n=struct.unpack_from('<II',b)
        if magic!=0x616c4467 or not 52<=n<=4096: raise ValueError('invalid super geometry')
        h=bytearray(b[:n]);h[8:40]=bytes(32)
        if hashlib.sha256(h).digest()!=b[8:40]: raise ValueError('geometry SHA256 mismatch')
        maximum,slots,block=struct.unpack_from('<III',b,40)
        if not (512<=maximum<=16*1024*1024 and maximum%512==0 and 1<=slots<=32 and block>=512 and block%512==0):
            raise ValueError('unsupported geometry values')
        if 12288+maximum*slots*2>self.length: raise ValueError('metadata exceeds super')
        return {'max_size':maximum,'slots':slots,'logical_block_size':block}
    def metadata(self, geo, slot=0, backup=False):
        pos=12288+geo['max_size']*(slot+(geo['slots'] if backup else 0))
        b=self.read(pos,geo['max_size']);magic,major,minor,hs=struct.unpack_from('<IHHI',b)
        if magic!=0x414c5030 or major!=10 or minor>2 or hs!=(256 if minor>=2 else 128):
            raise ValueError('unsupported metadata header')
        h=bytearray(b[:hs]);h[12:44]=bytes(32)
        if hashlib.sha256(h).digest()!=b[12:44]: raise ValueError('metadata header SHA256 mismatch')
        ts=struct.unpack_from('<I',b,44)[0]
        if hs+ts>len(b): raise ValueError('tables exceed metadata bounds')
        tables=b[hs:hs+ts]
        if hashlib.sha256(tables).digest()!=b[48:80]: raise ValueError('metadata tables SHA256 mismatch')
        def rows(index,minimum):
            off,n,width=struct.unpack_from('<III',b,80+12*index)
            if width<minimum or off+n*width>ts or n>100000: raise ValueError('invalid table descriptor')
            return [tables[off+i*width:off+(i+1)*width] for i in range(n)]
        def name(v):
            s=v[:36].split(b'\0')[0].decode('ascii')
            if not re.fullmatch(r'[A-Za-z0-9_]+',s): raise ValueError('invalid partition/group name')
            return s
        devices=rows(3,64)
        if len(devices)!=1: raise ValueError('only one physical super device supported')
        first,alignment,alignoff,devsize=struct.unpack_from('<QIIQ',devices[0])
        if devsize>self.length or first*512>=devsize: raise ValueError('device size/first sector invalid')
        groups=[{'name':name(v),'max_size':struct.unpack_from('<Q',v,40)[0]} for v in rows(2,48)]
        extents=[]
        for e in rows(1,24):
            count,typ,start,source=struct.unpack_from('<QIQI',e)
            if count==0 or typ not in (0,1) or source!=0: raise ValueError('unsupported extent')
            if typ==0 and (start<first or (start+count)*512>devsize): raise ValueError('extent out of bounds')
            if typ==1 and start: raise ValueError('invalid zero extent')
            extents.append({'sectors':count,'type':typ,'start':start})
        parts=[];used_extents=set();ranges=[];seen=set();group_sizes=[0]*len(groups)
        for v in rows(0,52):
            nm=name(v);attr,idx,n,group=struct.unpack_from('<IIII',v,36)
            if nm in seen or n==0 or idx+n>len(extents) or group>=len(groups): raise ValueError('invalid partition')
            seen.add(nm)
            es=extents[idx:idx+n];size=sum(e['sectors']*512 for e in es);group_sizes[group]+=size
            for i,e in enumerate(es,idx):
                if i in used_extents: raise ValueError('shared extent index')
                used_extents.add(i)
                if e['type']==0:
                    a,z=e['start'],e['start']+e['sectors']
                    if any(a<y and z>x for x,y in ranges): raise ValueError('overlapping linear extents')
                    ranges.append((a,z))
            parts.append({'name':nm,'attributes':attr,'size_bytes':size,'group':groups[group]['name'],'extents':es})
        for g,size in zip(groups,group_sizes):
            if g['max_size'] and size>g['max_size']: raise ValueError('group capacity exceeded')
        return {'slot':slot,'backup':backup,'version':f'{major}.{minor}','checksums_ok':True,'partitions':parts,'groups':groups}
    def inspect(self):
        primary=self.geometry(4096);backup=self.geometry(8192)
        if primary!=backup: raise ValueError('geometry copies disagree')
        copies=[]
        for back in (False,True):
            for slot in range(primary['slots']):
                try: copies.append(self.metadata(primary,slot,back))
                except ValueError as e: copies.append({'slot':slot,'backup':back,'error':str(e)})
        if 'error' in copies[0]: raise ValueError('primary slot0 invalid: '+copies[0]['error'])
        return {'geometry':primary,'geometry_copies_match':True,'metadata_copies':copies}
    def extract(self, part, destination):
        out=Path(destination)
        if out.exists(): raise ValueError('refusing overwrite')
        with out.open('xb') as f:
            for e in part['extents']:
                todo=e['sectors']*512;off=e['start']*512
                while todo:
                    n=min(todo,1024*1024)
                    f.write(self.read(off,n) if e['type']==0 else bytes(n));off+=n;todo-=n

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('--offset',type=int,default=0);p.add_argument('--length',type=int);p.add_argument('--extract',nargs='+',default=[]);p.add_argument('--out-dir')
    a=p.parse_args()
    try:
        r=SuperReader(a.image,a.offset,a.length);report=r.inspect()
        if a.extract:
            if not a.out_dir: raise ValueError('--out-dir required')
            dest=Path(a.out_dir);dest.mkdir(parents=True,exist_ok=True)
            parts={v['name']:v for v in report['metadata_copies'][0]['partitions']}
            for nm in a.extract:
                if nm not in parts: raise ValueError('partition absent: '+nm)
                r.extract(parts[nm],dest/(nm+'.img'))
        print(json.dumps(report,indent=2))
    except (ValueError,OSError,UnicodeError,struct.error) as e:p.exit(2,str(e)+'\n')
