/* SPDX-License-Identifier: MIT */
#include "ir_decode.h"
static unsigned map(unsigned command) {
    switch(command) {
    case 0x16: return 103; /* KEY_UP */
    case 0x1a: return 108; /* KEY_DOWN */
    case 0x51: return 105; /* KEY_LEFT */
    case 0x50: return 106; /* KEY_RIGHT */
    case 0x13: return 28;  /* KEY_ENTER -> Android DPAD_CENTER */
    case 0x19: return 158; /* KEY_BACK */
    default: return 0;
    }
}
unsigned h20_ir_reset(struct h20_ir_state *s, struct h20_ir_event out[2]) {
    if (!s->held) return 0;
    out[0] = (struct h20_ir_event){s->held, 0}; s->held = 0; return 1;
}
unsigned h20_ir_decode(struct h20_ir_state *s, uint32_t scan,
                      struct h20_ir_event out[2]) {
    unsigned flag=scan>>24, addr=(scan>>8)&0xffff, key=map(scan&255);
    if (addr!=0xfe01 || flag>1 || !key) return 0;
    if (!flag) {
        if(s->held!=key) return 0;
        return h20_ir_reset(s,out);
    }
    if(s->held==key) {out[0]=(struct h20_ir_event){key,2}; return 1;}
    unsigned n=h20_ir_reset(s,out);
    s->held=key; out[n]=(struct h20_ir_event){key,1}; return n+1;
}
