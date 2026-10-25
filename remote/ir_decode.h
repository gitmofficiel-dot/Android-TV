/* SPDX-License-Identifier: MIT */
#ifndef H20_IR_DECODE_H
#define H20_IR_DECODE_H
#include <stdint.h>
/* Linux input key codes; Android keylayout remains a separate layer. */
struct h20_ir_event { unsigned key; int value; };
struct h20_ir_state { unsigned held; };
/* Returns event count (0..2). No device IO or key injection. */
unsigned h20_ir_decode(struct h20_ir_state *, uint32_t scan,
                      struct h20_ir_event events[2]);
unsigned h20_ir_reset(struct h20_ir_state *, struct h20_ir_event events[2]);
#endif
