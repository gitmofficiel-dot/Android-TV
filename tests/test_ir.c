#include <assert.h>
#include <stdio.h>
#include "../remote/ir_decode.h"
int main(void) {
 struct h20_ir_state s={0}; struct h20_ir_event e[2];
 unsigned cmd[]={0x16,0x1a,0x51,0x50,0x13,0x19};
 unsigned keys[]={103,108,105,106,28,158};
 for(unsigned i=0;i<6;i++) {
  assert(h20_ir_decode(&s,0x01fe0100|cmd[i],e)==1);
  assert(e[0].key==keys[i] && e[0].value==1);
  assert(h20_ir_decode(&s,0x00fe0100|cmd[i],e)==1);
  assert(e[0].key==keys[i] && e[0].value==0 && s.held==0);
 }
 assert(h20_ir_decode(&s,0x01fe0216,e)==0); /* other remote */
 assert(h20_ir_decode(&s,0x02fe0116,e)==0); /* unknown flag */
 assert(h20_ir_decode(&s,0x01fe01ff,e)==0); /* unknown command */
 assert(h20_ir_decode(&s,0x01fe0116,e)==1);
 assert(h20_ir_decode(&s,0x01fe0116,e)==1 && e[0].value==2);
 assert(h20_ir_decode(&s,0x00fe011a,e)==0 && s.held==103);
 assert(h20_ir_decode(&s,0x01fe011a,e)==2);
 assert(e[0].key==103 && e[0].value==0 && e[1].key==108 && e[1].value==1);
 assert(h20_ir_reset(&s,e)==1 && s.held==0);
 assert(h20_ir_reset(&s,e)==0);
 puts("IR: six captured button pairs + repeat/invalid/switch/reset checks passed");
}
