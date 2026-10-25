import sys, tempfile, struct, zlib, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_image import audit
class AuditTests(unittest.TestCase):
 def fixture(self, corrupt=False, overlap=False):
  data=bytearray(512*100); data[510:512]=b'\x55\xaa'
  table=bytearray(256)
  for i,(a,b) in enumerate([(10,19),(15 if overlap else 20,29)]):
   off=i*128; table[off:off+16]=b'1'*16
   struct.pack_into('<QQ',table,off+32,a,b)
   name=f'p{i}'.encode('utf-16-le'); table[off+56:off+56+len(name)]=name
  data[1024:1280]=table
  h=bytearray(512); h[:8]=b'EFI PART'
  struct.pack_into('<III',h,8,0x10000,92,0)
  struct.pack_into('<QQQQ',h,24,1,99,3,98)
  struct.pack_into('<QIII',h,72,2,2,128,zlib.crc32(table))
  struct.pack_into('<I',h,16,zlib.crc32(h[:92]))
  if corrupt: h[40]^=1
  data[512:1024]=h; data[99*512:99*512+8]=b'EFI PART'
  return data
 def run_image(self,data):
  with tempfile.NamedTemporaryFile() as f:
   f.write(data); f.flush(); return audit(f.name)
 def test_good(self): self.assertTrue(self.run_image(self.fixture())['primary_structure_ok'])
 def test_bad_crc(self): self.assertFalse(self.run_image(self.fixture(True))['primary_structure_ok'])
 def test_overlap(self): self.assertFalse(self.run_image(self.fixture(overlap=True))['primary_structure_ok'])
 def test_truncated(self):
  with self.assertRaises(ValueError): self.run_image(b'\0'*600)
if __name__=='__main__': unittest.main()
