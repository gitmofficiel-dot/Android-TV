# H20 FE01 decoder — host-tested component, not an Android service
This original MIT-licensed C component maps the six observed FE01 raw commands
to STANDARD Linux key codes, with down/up, repeated-down, release-on-switch and
reset handling. A matching prospective Android keylayout is included.

Do NOT install this keylayout over the stock sunxi-ir-uinput keylayout: the stock
daemon emits different codes. This pair is reserved for a future replacement.

No device IO, uinput, mouse mode, Binder service, SELinux policy, Android.bp or
power/wake implementation exists yet. No binary has been run on H20 Pro.
Repeated-down handling is a design choice, not a measured long-press protocol.
The future reader must rediscover input devices by name, not hard-code event2,
check disconnects, synthesize release after a measured timeout, and avoid running
alongside stock multi_ir. Long press, power and wake need separate hardware tests.

Host validation:
cc -std=c11 -Wall -Wextra -Werror -pedantic remote/ir_decode.c tests/test_ir.c -o /tmp/h20-test-ir
/tmp/h20-test-ir
