/* SPDX-License-Identifier: MIT
 * Offline DT feasibility candidate only. NOT a complete or flashable H20 port.
 * Requires libfdt development headers/library. Never opens a block device.
 */
#include <libfdt.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static void fail(const char *s) { fprintf(stderr, "%s\n", s); exit(1); }
static int node(void *b, const char *p) {
    int n = fdt_path_offset(b, p);
    if (n < 0) fail("Required donor node missing");
    return n;
}
static void text_prop(void *b, const char *path, const char *key,
                      const char *expected, const char *value) {
    int len, n = node(b, path);
    const char *p = fdt_getprop(b, n, key, &len);
    if (!p || len != (int)strlen(expected)+1 || memcmp(p, expected, (size_t)len))
        fail("Unexpected donor property; refusing modification");
    if (fdt_setprop_string(b, n, key, value)) fail("Cannot update property");
}
int main(int argc, char **argv) {
    if (argc != 3) fail("Usage: prepare_t95_dtb VERIFIED_DONOR_DTB NEW_OUTPUT_DTB");
    struct stat st;
    FILE *in = fopen(argv[1], "rb");
    if (!in || fstat(fileno(in), &st) || !S_ISREG(st.st_mode) ||
        st.st_size < 40 || st.st_size > 1048576) fail("Invalid regular input file");
    size_t size = (size_t)st.st_size;
    void *original = malloc(size), *b = malloc(size + 4096);
    if (!original || !b || fread(original, 1, size, in) != size) fail("Read failed");
    fclose(in);
    if (fdt_check_full(original, size) || fdt_open_into(original, b, (int)size+4096))
        fail("Invalid FDT");
    text_prop(b, "/", "model", "T95 H616 AXP313A", "H20 Pro LP3 EXPERIMENTAL INCOMPLETE");
    const char *mmc = "/soc@3000000/sdmmc@4022000";
    int len, n = node(b, mmc);
    const fdt32_t *freq = fdt_getprop(b, n, "max-frequency", &len);
    if (!freq || len != 4 || fdt32_to_cpu(*freq) != 100000000)
        fail("Unexpected donor eMMC frequency");
    if (fdt_setprop_u32(b, n, "max-frequency", 50000000)) fail("Frequency update failed");
    text_prop(b, mmc, "status", "disabled", "okay");
    text_prop(b, "/soc@3000000/nand0@4011000", "status", "okay", "disabled");
    /* Stock Bluetooth hardware/driver is unresolved: leave it inactive. */
    n = node(b, "/soc@3000000/rfkill/bt");
    if (fdt_setprop_string(b, n, "status", "disabled")) fail("BT update failed");
    text_prop(b, "/soc@3000000/btlpm", "status", "okay", "disabled");
    if (fdt_pack(b) || fdt_check_full(b, fdt_totalsize(b))) fail("Output invalid");
    /* O_EXCL: never replace an existing file or follow a target symlink. */
    int fd = open(argv[2], O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) fail("Cannot create new output; refusing overwrite");
    size_t remaining = fdt_totalsize(b), offset = 0;
    while (remaining) {
        ssize_t count = write(fd, (char *)b + offset, remaining);
        if (count <= 0) fail("Output write failed");
        remaining -= (size_t)count; offset += (size_t)count;
    }
    if (close(fd)) fail("Output close failed");
    free(original); free(b);
    puts("Created incomplete offline DT candidate. NOT FOR FLASHING.");
    return 0;
}
