import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from fdt_inventory import parse
class FdtTests(unittest.TestCase):
 def fixture(self):
  # root node, one compatible property, end root, end structure
  strings=b'compatible\0';v=b'allwinner,h616\0'
  block=struct.pack('>I',1)+b'\0'*4+struct.pack('>III',3,len(v),0)+v
  block+=b'\0'*(-len(block)%4)+struct.pack('>II',2,9)
  off=56;total=off+len(block)+len(strings)
  return struct.pack('>10I',0xd00dfeed,total,off,off+len(block),40,17,16,0,len(strings),len(block))+b'\0'*16+block+strings
 def test_minimal(self): self.assertEqual(parse(self.fixture())['/']['compatible'],b'allwinner,h616\0')
 def test_truncated(self):
  with self.assertRaises(ValueError):parse(self.fixture()[:-1])
 def test_bad_magic(self):
  with self.assertRaises(ValueError):parse(b'FAIL'+self.fixture()[4:])
 def test_bad_string_offset(self):
  b=bytearray(self.fixture());struct.pack_into('>I',b,72,99999)
  with self.assertRaises(ValueError):parse(b)
if __name__=='__main__':unittest.main()
