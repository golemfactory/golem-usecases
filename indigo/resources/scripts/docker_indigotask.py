from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile

import params  # This module is generated before this script is run

INDIGO_COMMAND = "indigo_console"
OUTPUT_DIR = "/golem/output"
WORK_DIR = "/golem/work"
RESOURCES_DIR = "/golem/resources"


def symlink_or_copy(source, target):
    try:
        os.symlink(source, target)
    except OSError:
        if os.path.isfile(source):
            if os.path.exists(target):
                os.remove(target)
            shutil.copy(source, target)
        else:
            from distutils import dir_util
            dir_util.copy_tree(source, target, update=1)


def find_igi(directory):
    if not os.path.exists(directory):
        return None
    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                if names.upper().endswith(".IGI"):
                    return os.path.join(root, names)
    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return None


def format_indigo_renderer_cmd(start_task, output_basename, output_format, scene_file, num_cores,
                               halttime, haltspp):
    igi_file = find_igi(WORK_DIR)
    if igi_file is not None:
        cmd = [
            "{}".format(INDIGO_COMMAND),
            "{}".format(scene_file),
            "-r", "{}".format(igi_file),
            "-t", "{}".format(num_cores)
        ]
    else:
        cmd = [
            "{}".format(INDIGO_COMMAND),
            "{}".format(scene_file),
            "-o", "{}/{}{}.{}".format(OUTPUT_DIR, output_basename, start_task, output_format),
            "-igio", "{}/{}{}.igi".format(OUTPUT_DIR, output_basename, start_task),
            "-t", "{}".format(num_cores)
        ]
    if haltspp == 0:
        cmd.append("-halt")
        cmd.append(str(halttime))
    else:
        cmd.append("-haltspp")
        cmd.append(str(haltspp))

    print(cmd, file=sys.stderr)
    return cmd


def exec_cmd(cmd):
    pc = subprocess.Popen(cmd)
    return pc.wait()


def run_indigo_renderer_task(start_task, outfilebasename, output_format, scene_file_src,
                          scene_dir, num_cores, halttime, haltspp):

    print(scene_file_src, file=sys.stderr)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".igs", dir=WORK_DIR,
                                     delete=False) as tmp_scene_file:
        tmp_scene_file.write(scene_file_src)

    # Create symlinks for all the resources from the scene dir
    # (from which scene_file_src is read) to the work dir:
    for f in os.listdir(scene_dir):
        source = os.path.join(scene_dir, f)
        target = os.path.join(WORK_DIR, f)
        symlink_or_copy(source, target)

    igi_file = find_igi(RESOURCES_DIR)
    if igi_file:
        symlink_or_copy(igi_file, os.path.join(WORK_DIR, os.path.basename(igi_file)))

    cmd = format_indigo_renderer_cmd(start_task, outfilebasename, output_format,
                                     tmp_scene_file.name, num_cores, halttime, haltspp)

    exit_code = exec_cmd(cmd)
    if exit_code is not 0:
        print("EXIT CODE NOT {}".format(exit_code))
        sys.exit(exit_code)
    else:
        outfile = "{}/{}{}.{}".format(OUTPUT_DIR, outfilebasename, start_task, output_format)
        print("OUTFILE {}".format(outfile))
        if not os.path.isfile(outfile):
            igi_file = find_igi(WORK_DIR)
            print(igi_file, file=sys.stdout)
            img = igi_file[:-4] + "." + output_format.lower()
            if not os.path.isfile(img):
                print("No img produced", file=sys.stderr)
                sys.exit(-1)
            else:
                shutil.copy(img, outfile)


run_indigo_renderer_task(params.start_task, params.outfilebasename, params.output_format,
                         params.scene_file_src, params.scene_dir, params.num_threads,
                         params.halttime, params.haltspp)


