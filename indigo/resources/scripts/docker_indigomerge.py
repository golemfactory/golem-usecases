from __future__ import print_function

import os
import shutil
import subprocess
import sys

import params # This module is generated before the script is run

INDIGO_MERGER_COMMAND = "indigo_console --merge-igi"
OUTPUT_DIR = "/golem/output"
WORK_DIR = "/golem/work"
RESOURCE_DIR = "/golem/resources"


def format_indigo_merger_cmd(output_filename, igi_files):

    cmd = ["{}".format(INDIGO_MERGER_COMMAND)]
    for file_ in igi_files:
        cmd.append("{}".format(file_))
    cmd.append("{}/{}.igi".format(OUTPUT_DIR, os.path.basename(output_filename)))
    print(cmd, file=sys.stderr)
    return cmd


def exec_cmd(cmd):
    pc = subprocess.Popen(cmd)
    return pc.wait()


def run_indigo_merger_task(output_filename, igi_files):
    cmd = format_indigo_merger_cmd(output_filename, igi_files)
    # Create symlinks for all the resources from the scene dir
    # (from which scene_file_src is read) to the work dir:
    for f in os.listdir(RESOURCE_DIR):
        source = os.path.join(RESOURCE_DIR, f)
        target = os.path.join(WORK_DIR, f)
        try:
            os.symlink(source, target)
        except OSError:
            if os.path.isfile(source):
                shutil.copy(source, target)
            else:
                shutil.copytree(source, target)

    exit_code = exec_cmd(cmd)
    if exit_code is not 0:
        sys.exit(exit_code)


run_indigo_merger_task(params.output_igi, params.igi_files)
