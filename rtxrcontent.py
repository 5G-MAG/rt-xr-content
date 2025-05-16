#!.venv/bin/python3
import os
import subprocess
import zipfile
import json

import click
from pathlib import Path
import logging


############################################################################
# push content & config to devices
############################################################################

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
@click.option('-t', '--target', type=str, default='com.fivegmag.rtxrplayer')
@click.argument('content', nargs=-1)
def config(ctx, target:str, content:tuple[str, ...]):
    """generate and push config file for a set directories
    """
    entrypoints = []
    for dirname in content:
        dp = Path(dirname)
        if dp.exists():
            for fp in dp.iterdir():
                if fp.suffix in ('.gltf', '.glb'):
                    entrypoints.append(fp)

    with open('./Paths', 'w') as fo:
        fo.writelines([f'{fp}\n' for fp in entrypoints])

    if not target.startswith('/'):
        target = app_directory(target)
    config = Path('./Paths')
    assert config.exists(), 'config file missing: ./Paths'
    push_file(config, target)



@cli.command()
@click.pass_context
@click.option('-t', '--target', type=str, default='com.fivegmag.rtxrplayer')
@click.argument('content', nargs=-1)
def push(ctx, target:str, content:tuple[str, ...]):
    """push files or whole directories to default adb device
    """
    if not target.startswith('/'):
        target = app_directory(target)
    for source in content:
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



# @cli.command(name="gen-config")
# @click.pass_context
# @click.argument('content', nargs=-1)
# def config_gen(ctx, content:tuple[str, ...]):
#     """generate a config file for a set directories
#     """
#     entrypoints = []
#     for dirname in content:
#         dp = Path(dirname)
#         if dp.exists():
#             for fp in dp.iterdir():
#                 if fp.suffix in ('.gltf', '.glb'):
#                     entrypoints.append(fp)
#     with open('./Paths', 'w') as fo:
#         fo.writelines([f'{fp}\n' for fp in entrypoints])
#         
# 
# @cli.command(name="push-config")
# @click.pass_context
# @click.argument('target', type=str, default='com.fivegmag.rtxrplayer')
# def config_push(ctx, target:str):
#     """push config file to application directory to default adb device
#     """
#     if not target.startswith('/'):
#         target = app_directory(target)
#     config = Path('./Paths')
#     assert config.exists(), 'config file missing: ./Paths'
#     push_file(config, target)


############################################################################
# gen metadata files, readme, etc ...
############################################################################

def metadata_template(path:Path, template_data:dict=None, **kwargs):
    if template_data is None:
        template_data = {
            "legal": [
                {
                    "owner": "",
                    "year": "",
                    "license": "",
                    "licenseUrl": "",
                    "what": ""
                }
            ],
            "tags": [],
            "screenshot": "metadata/screenshot.jpg",
            "name": "",
            "path": "",
            "summary": ""
        }
    template_data["path"] = str(path)
    template_data["name"] = path.stem
    template_data["summary"] = path.stem        
    return template_data


def ensure_metadata_dir(diranme:Path):
    metadata = diranme / 'metadata'
    if metadata.exists():
        assert metadata.is_dir(), f'{metadata} exists and is not a directory'
    else:
        os.mkdir(metadata)

def ensure_content_metadata(diranme:Path, template_data=None):
    metadata_dir = diranme / 'metadata'
    for glob in ['*.gltf', '*.glb']:
        for fp in diranme.glob(glob):
            fp_metadata = (metadata_dir / fp.name).with_suffix('.json')
            if fp_metadata.exists():
                assert fp_metadata.is_file(), f'{fp_metadata} is not a file'
            else:
                metadata = metadata_template(fp, template_data)
                with open(fp_metadata, 'w') as fo:
                    json.dump(metadata, fo, indent=4)


@cli.command(name="gen-metadata")
@click.pass_context
@click.argument('content-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
@click.argument('template', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), default=None)
def gen_metadata(ctx, content_dir:Path, template:Path):
    """generate metadata for a given content directory
    """
    content_dir = Path(content_dir)
    template_data = None
    with open(template, 'r') as fo:
        template_data = json.load(fo)
    ensure_metadata_dir(content_dir)
    ensure_content_metadata(content_dir, template_data)


def read_scene_data(gltf_fp):
    metadata_fp = gltf_fp.parent / 'metadata' / gltf_fp.with_suffix('.json').name
    data = None
    gltf_data = None
    with open(metadata_fp, 'r') as fo:
        data = json.load(fo)
    with open(gltf_fp, 'r') as gltf_fo:
        gltf_data = json.load(gltf_fo)
    data["extensions"] = [ext for ext in gltf_data["extensionsUsed"] if ext.startswith("MPEG_")]
    return data

def copyright(c):
    artist = c.get('artist', None) 
    lic = f"<a alt=\"license\" href=\"{c['licenseUrl']}\">{c['license']}</a>"
    res = [
        f"&#169; {c['year']}, {c['owner']}, {lic}\n"
    ]
    if artist is None:
        res.append( f"  - {c['what']}\n" )
    else:
        res.append( f"  - {artist} for {c['what']}\n" )
    return res

@cli.command(name="gen-readme")
@click.pass_context
@click.argument('content-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def gen_readme(ctx, content_dir):
    """generate readme.md for a content directory based its metadata
    """
    content_dir = Path(content_dir)
    readme = []
    for glob in ['*.gltf', '*.glb']:
        for sfp in content_dir.glob(glob):
            scene = read_scene_data(sfp)
            readme.append(f"\n## {scene['name']}")
            readme.append(f"\n### Summary")
            readme.append(scene["summary"]+"\n")
            readme.append(f"\n### Extensions used\n")
            for ext in scene["extensions"]:
                readme.append(f"- {ext}")
            readme.append(f"\n### Screeshot")
            readme.append(f"![screenshot]({scene['screenshot']})")
            readme.append(f"\n### Legal\n")
            for c in scene["legal"]:
                readme += copyright(c)
        with open( content_dir / 'README.md', 'w') as ofp:
            ofp.write("\n".join(readme))


if __name__ == '__main__':
    cli(obj={})
