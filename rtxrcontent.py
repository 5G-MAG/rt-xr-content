#!.venv/bin/python3
import os
import subprocess
import zipfile

import click
from pathlib import Path
import logging

ADB_PUSH_IGNORE = [
    ".blend", ".blend1"
]

def app_directory(app_id):
    return f'/storage/emulated/0/Android/data/{app_id}/files'

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug


def push_file(src, dst):
    logging.info(f'pushing : {src}')
    cmd = [ "adb", "push", str(src), str(dst) ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).check_returncode()
    except BaseException as e:
        logging.error(e)

def zip_local_dir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if Path(file).suffix not in ADB_PUSH_IGNORE:
                fp = Path(root) / file
                relfp = os.path.relpath(fp, Path(path).parent)
                ziph.write(fp,relfp)


def unzip_remote_dir(target_zipped):
    logging.info(f'uzipping on device : {target_zipped}')
    target = target_zipped.parent
    subprocess.run([f"adb", "shell", "rm", "-rf", f"{target}/{target_zipped.stem}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).check_returncode()
    subprocess.run(["adb", "shell", "unzip", str(target_zipped), "-qq", "-d", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).check_returncode()
    subprocess.run(["adb", "shell", "rm", str(target_zipped)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).check_returncode()


@cli.command()
@click.pass_context
@click.argument('source')
@click.argument('target', type=str, default='com.fivegmag.rtxrplayer')
def push(ctx, source:str, target:str):
    if not target.startswith('/'):
        target = app_directory(target)
    if os.path.isdir(source):
        src_zipped = Path(source).with_suffix('.zip')
        target_zipped = Path(target) / src_zipped.name
        logging.info(f'zipping : {source}')
        with zipfile.ZipFile(src_zipped, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zip_local_dir(source, zipf)
        push_file(src_zipped, target_zipped)
        unzip_remote_dir(target_zipped)
    else:
        push_file(source, target)

@cli.command(name="config-gen")
@click.pass_context
@click.argument('content', nargs=-1)
def config_gen(ctx, content:tuple[str, ...]):
    entrypoints = []
    for dirname in content:
        dp = Path(dirname)
        if dp.exists():
            for fp in dp.iterdir():
                if fp.suffix in ('.gltf', '.glb'):
                    entrypoints.append(fp)
    with open('./Paths', 'w') as fo:
        fo.writelines([f'{fp}\n' for fp in entrypoints])
        

@cli.command(name="config-push")
@click.pass_context
@click.argument('target', type=str, default='com.fivegmag.rtxrplayer')
def config_push(ctx, target:str):
    if not target.startswith('/'):
        target = app_directory(target)
    config = Path('./Paths')
    assert config.exists(), 'config file missing: ./Paths'
    push_file(config, target)


if __name__ == '__main__':
    cli(obj={})
