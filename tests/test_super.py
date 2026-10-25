import hashlib,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from inspect_super import SuperReader
class SuperTests(unittest.TestCase):
 def fixture(self,corrupt=False,badextent=False):
  size=2*1024*1024;data=bytearray(size)
  geo=bytearray(struct.pack('<II32sIII',0x616c4467,52,bytes(32),4096,1,4096));geo[8:40]=hashlib.sha256(geo).digest()
  data[4096:4148]=geo;data[8192:8244]=geo
  nm=lambda s:s.encode().ljust(36,b'\0')
  part=nm('system')+struct.pack('<IIII',1,0,1,0)
  ext=struct.pack('<QIQI',2,0,size//512 if badextent else 2048,0)
  group=nm('default')+struct.pack('<IQ',0,0)
  dev=struct.pack('<QIIQ',2048,1048576,0,size)+nm('super')+struct.pack('<I',0)
  tables=part+ext+group+dev;h=bytearray(128)
  struct.pack_into('<IHHI',h,0,0x414c5030,10,0,128);struct.pack_into('<I',h,44,len(tables));h[48:80]=hashlib.sha256(tables).digest()
  off=0
  for i,t in enumerate([part,ext,group,dev]):struct.pack_into('<III',h,80+i*12,off,1,len(t));off+=len(t)
  h[12:44]=hashlib.sha256(h).digest();b=h+tables
  data[12288:12288+len(b)]=b;data[16384:16384+len(b)]=b
  if corrupt:data[12288+128]^=1
  data[1048576:1049600]=b'X'*1024
  return data
 def run_case(self,**kw):
  f=tempfile.NamedTemporaryFile();f.write(self.fixture(**kw));f.flush();return f,SuperReader(f.name)
 def test_valid_and_extract(self):
  f,r=self.run_case()
  with f,tempfile.TemporaryDirectory() as d:
   v=r.inspect();self.assertEqual(v['metadata_copies'][0]['partitions'][0]['size_bytes'],1024)
   out=Path(d)/'system.img';r.extract(v['metadata_copies'][0]['partitions'][0],out);self.assertEqual(out.read_bytes(),b'X'*1024)
   with self.assertRaises(ValueError):r.extract(v['metadata_copies'][0]['partitions'][0],out)
 def test_table_corruption(self):
  f,r=self.run_case(corrupt=True)
  with f,self.assertRaises(ValueError):r.inspect()
 def test_extent_bounds(self):
  f,r=self.run_case(badextent=True)
  with f,self.assertRaises(ValueError):r.inspect()
if __name__=='__main__':unittest.main()
