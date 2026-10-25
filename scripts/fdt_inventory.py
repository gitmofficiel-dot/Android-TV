#!/usr/bin/env python3
"""Strict bounded FDT reader for offline board evidence. No writes to devices.
Outputs selected hardware nodes only; excludes /chosen, MAC/serial and key data.
Not a DTS compiler and not a validator of electrical correctness.
"""
import argparse, hashlib, json, re, struct
from pathlib import Path

def parse(data):
    if len(data)<40: raise ValueError('truncated FDT header')
    magic,total,off,strings_off,reserve,version,last,boot,strings_len,struct_len=struct.unpack_from('>10I',data)
    if magic!=0xd00dfeed or version!=17: raise ValueError('FDT version17 required')
    if total>len(data) or total<40: raise ValueError('invalid total size')
    if any(a<40 or a+n>total for a,n in [(off,struct_len),(strings_off,strings_len)]): raise ValueError('block bounds')
    strings=data[strings_off:strings_off+strings_len];end=off+struct_len;stack=[];nodes={};seen_end=False
    def u32(pos):
        if pos+4>end: raise ValueError('truncated token')
        return struct.unpack_from('>I',data,pos)[0]
    while off<end:
        token=u32(off);off+=4
        if token==1:
            zero=data.find(b'\0',off,end)
            if zero<0: raise ValueError('unterminated node')
            name=data[off:zero].decode('utf-8');off=(zero+4)&~3
            if '/' in name or (not stack and name): raise ValueError('invalid node name')
            stack.append(name);path='/'.join(stack) or '/'
            if path in nodes: raise ValueError('duplicate node')
            nodes[path]={}
        elif token==2:
            if not stack: raise ValueError('unbalanced end node')
            stack.pop()
        elif token==3:
            if not stack or off+8>end: raise ValueError('invalid property')
            size,index=u32(off),u32(off+4);off+=8
            if off+size>end or index>=len(strings): raise ValueError('property bounds')
            zero=strings.find(b'\0',index)
            if zero<0: raise ValueError('unterminated property name')
            name=strings[index:zero].decode('utf-8');path='/'.join(stack) or '/'
            if name in nodes[path]: raise ValueError('duplicate property')
            nodes[path][name]=data[off:off+size];off=(off+size+3)&~3
        elif token==4: pass
        elif token==9:
            if stack: raise ValueError('unclosed nodes')
            seen_end=True;break
        else: raise ValueError('unknown token')
    if not seen_end: raise ValueError('missing end token')
    return nodes

def summarize(data):
    nodes=parse(data)
    handles={int.from_bytes(v,'big'):p for p,n in nodes.items() for k,v in n.items() if k in ('phandle','linux,phandle') and len(v)==4}
    allowed=re.compile(r'/(?:wlan|bt|rfkill|s_cir[^/]*|usbc[^/]*|mmc[^/]*|sdmmc[^/]*|sdc[^/]*|pmu|regulators|dcdc\d+|ldo\d+|gmac[^/]*|ethernet[^/]*|standby_param|card[02]_boot_para[^/]*)$')
    selected={}
    for path,props in nodes.items():
        if not path.startswith('/soc') or not allowed.search(path):continue
        obj={}
        for key,v in props.items():
            if re.search('serial|mac.address|key|rotpk',key,re.I):continue
            if not v:obj[key]={'boolean':True};continue
            text_keys=('compatible','status','device_type','regulator-name','phy-mode','pinctrl-names','sdc_type','wlan_power','bt_power','allwinner,pins','allwinner,function','allwinner,pname')
            if key in text_keys and v.endswith(b'\0'):
                obj[key]={'strings':v[:-1].decode(errors='replace').split('\0')}
            elif len(v)%4==0:
                cells=list(struct.unpack('>'+str(len(v)//4)+'I',v));item={'cells':cells}
                if key.endswith('-supply') or key.startswith('pinctrl-') and key!='pinctrl-names':
                    item['resolved_phandles']=[handles.get(x,'UNRESOLVED') for x in cells]
                # Stock Allwinner GPIO descriptors are seven cells; keep raw and
                # annotate first controller/bank/pin without inferring voltage.
                if key in ('wlan_regon','wlan_hostwake','bt_rst_n','bt_wake','bt_hostwake') and len(cells)>=3:
                    bank,pin=cells[1:3]
                    item['controller']=handles.get(cells[0],'UNRESOLVED')
                    if bank<=25 and pin<32:item['pin_annotation']='P'+chr(65+bank)+str(pin)
                obj[key]=item
            else:obj[key]={'hex':v.hex()}
        selected[path]=obj
    return {'schema':1,'source_sha256':hashlib.sha256(data).hexdigest(),'parsed_nodes':len(nodes),
            'warning':'Captured stock evidence only; not buildable device configuration. No new voltage values inferred.',
            'selected_nodes':selected}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dtb');args=p.parse_args()
    try: print(json.dumps(summarize(Path(args.dtb).read_bytes()),indent=2,ensure_ascii=False))
    except (ValueError,UnicodeError,struct.error,OSError) as e:p.exit(2,str(e)+'\n')
