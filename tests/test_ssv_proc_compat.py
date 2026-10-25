"""Host API-contract smoke test; the real BSP compile remains mandatory.

Kernel structs below intentionally model only the proc API fields used here.
They cannot validate complete Linux callback signatures or hardware behavior.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProcCompatibilityTests(unittest.TestCase):
    def check_version(self, major, minor):
        patch = (ROOT / 'patches/ssv6x5x/0001-procfs-5.4-compat.patch').read_text()
        section = patch.split('+++ b/ssvdevice/ssv_proc_compat.h\n', 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in section.splitlines()
                           if line.startswith('+') and not line.startswith('+++')) + '\n'
        self.assertIn('ssv_pde_data', header)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            linux = root / 'linux'
            linux.mkdir()
            (linux / 'version.h').write_text(
                '#define KERNEL_VERSION(a,b,c) (((a)<<16)+((b)<<8)+(c))\n'
                f'#define LINUX_VERSION_CODE KERNEL_VERSION({major},{minor},0)\n')
            (linux / 'fs.h').write_text(
                '#pragma once\nstruct inode { void *data; };\n'
                'struct file_operations { void *owner; int (*open)(void); '
                'int (*read)(void); int (*write)(void); int (*llseek)(void); '
                'int (*release)(void); };\n')
            (linux / 'module.h').write_text('#define THIS_MODULE ((void *)1)\n')
            proc = '#pragma once\n#include <linux/fs.h>\n'
            if (major, minor) >= (5, 6):
                proc += ('struct proc_ops { int (*proc_open)(void); int (*proc_read)(void); '
                         'int (*proc_write)(void); int (*proc_lseek)(void); '
                         'int (*proc_release)(void); };\n')
            accessor = 'pde_data' if (major, minor) >= (5, 17) else 'PDE_DATA'
            proc += f'static inline void *{accessor}(const struct inode *i) {{ return i->data; }}\n'
            (linux / 'proc_fs.h').write_text(proc)
            (root / 'compat.h').write_text(header)
            source = '''#include "compat.h"
static int callback(void) { return 7; }
static SSV_PROC_OPS ops = {
    SSV_PROC_OWNER
    .SSV_PROC_OPEN = callback, .SSV_PROC_READ = callback,
    .SSV_PROC_WRITE = callback, .SSV_PROC_LSEEK = callback,
    .SSV_PROC_RELEASE = callback,
};
int main(void) {
    int data = 42;
    struct inode inode = { &data };
    if (ssv_pde_data(&inode) != &data) return 1;
    if (ops.SSV_PROC_OPEN() != 7 || ops.SSV_PROC_READ() != 7 ||
        ops.SSV_PROC_WRITE() != 7 || ops.SSV_PROC_LSEEK() != 7 ||
        ops.SSV_PROC_RELEASE() != 7) return 2;
#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 6, 0)
    if (ops.owner != THIS_MODULE) return 3;
#endif
    return 0;
}
'''
            (root / 'test.c').write_text(source)
            result = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                     '-I', str(root), str(root / 'test.c'), '-o', str(root / 'test')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(root / 'test')], check=True)

    def test_linux_5_4_file_operations_and_old_private_data(self):
        self.check_version(5, 4)

    def test_linux_5_6_proc_operations_and_old_private_data(self):
        self.check_version(5, 6)

    def test_linux_5_17_proc_operations_and_new_private_data(self):
        self.check_version(5, 17)

class MacCompatibilityTests(unittest.TestCase):
    def check_version(self, major, minor):
        patch = (ROOT / 'patches/ssv6x5x/0002-mac80211-pre-MLO-compat.patch').read_text()
        section = patch.split('+++ b/smac/ssv_mac80211_compat.h\n', 1)[1].split('diff --git ', 1)[0]
        header = '\n'.join(line[1:] for line in section.splitlines()
                           if line.startswith('+') and not line.startswith('+++')) + '\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'linux').mkdir()
            (root / 'linux/version.h').write_text(
                '#define KERNEL_VERSION(a,b,c) (((a)<<16)+((b)<<8)+(c))\n'
                f'#define LINUX_VERSION_CODE KERNEL_VERSION({major},{minor},0)\n')
            (root / 'linux/types.h').write_text(
                'typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')
            (root / 'compat.h').write_text(header)
            source = '''#include "compat.h"
struct ht { int supported; };
#if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 19, 0)
struct sta { struct { struct ht ht_cap; } deflink; };
#else
struct sta { struct ht ht_cap; };
#endif
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 0, 0)
struct vif { struct { int assoc, aid; } cfg; };
typedef u64 expected_changed_t;
#define EXPECTED_LINK_ARG unsigned int link,
#else
struct vif { struct { int assoc, aid; } bss_conf; };
typedef u32 expected_changed_t;
#define EXPECTED_LINK_ARG
#endif
static void bss(ssv_bss_changed_t changed) { (void)changed; }
static int conf(int unused, SSV_CONF_TX_LINK_ARG u16 queue) {
    (void)unused;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 0, 0)
    (void)link_id;
#endif
    return queue;
}
struct ops { void (*bss)(expected_changed_t); int (*conf)(int, EXPECTED_LINK_ARG u16); };
static struct ops operations = { bss, conf };
int main(void) {
    struct sta sta = {0}; struct vif vif = {0};
    SSV_STA_HT_CAP(&sta).supported = 1;
    SSV_VIF_ASSOC(&vif) = 1; SSV_VIF_AID(&vif) = 42;
    operations.bss(1);
    if (sizeof(ssv_bss_changed_t) != sizeof(expected_changed_t)) return 1;
    if (!SSV_STA_HT_CAP(&sta).supported || !SSV_VIF_ASSOC(&vif) || SSV_VIF_AID(&vif) != 42) return 2;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 0, 0)
    return operations.conf(0, 0, 3) != 3;
#else
    return operations.conf(0, 3) != 3;
#endif
}
'''
            (root / 'test.c').write_text(source)
            result = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                     '-I', str(root), str(root / 'test.c'), '-o', str(root / 'test')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(root / 'test')], check=True)

    def test_5_4_legacy_station_and_vif(self):
        self.check_version(5, 4)

    def test_5_19_station_default_link_and_legacy_vif(self):
        self.check_version(5, 19)

    def test_6_0_station_default_link_and_vif_cfg(self):
        self.check_version(6, 0)
