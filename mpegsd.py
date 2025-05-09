#!.venv/bin/python3
from pathlib import Path
import sys
import json
import subprocess

import click
import json_merge_patch
from pyjsonpatch import get_by_pointer, apply_patch, generate_patch


TRIGGER_ACTIVATION = {
    "FIRST_ENTER": 0,
    "EACH_ENTER": 1,
    "ON": 2,
    "FIRST_EXIT": 3,
    "EACH_EXIT": 4,
    "OFF": 5
}

def gltf_load(fp):
    with open(fp, 'r') as fo:
        return json.load(fo)

def json_dumps(data):
    sys.stdout.write(json.dumps(data, indent=4))

def get_scene_interactivity(gltf, scene_idx=0):
    scene = gltf["scenes"][scene_idx]
    if "extensions" not in scene:
        scene["extensions"] = {}
    extensions = scene["extensions"]
    if "MPEG_scene_interactivity" not in extensions:
        extensions["MPEG_scene_interactivity"] = {
        "triggers": [], "actions": [], "behaviors": []
    }
    return extensions["MPEG_scene_interactivity"]


def add_interactivity_behavior(gltf, triggers=[], actions=[], combination="", activation="FIRST_ENTER", actionsControl=0, scene=0):
    interactivity = get_scene_interactivity(gltf, scene)
    behavior = { 
        "triggers": [], 
        "actions": [], 
        "triggersCombinationControl": combination,
        "triggersActivationControl": TRIGGER_ACTIVATION[activation],
        "actionsControl": actionsControl
    }
    if len(triggers):
        for t in triggers:
            behavior["triggers"].append(t)
    else:
        for t, _ in enumerate(interactivity["triggers"]):
            behavior["triggers"].append(t)
    if len(actions):
        for a in actions:
            behavior["actions"].append(a)
    else:
        for a, _ in enumerate(interactivity["actions"]):
            behavior["actions"].append(a)
    interactivity["behaviors"].append(behavior)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug


@cli.command(name="apply-patch")
@click.pass_context
@click.argument('gltf')
@click.argument('patch')
def apply_patch(ctx, gltf, patch):
    gltf_data = gltf_load(gltf)
    patch_data = gltf_load(patch)
    apply_patch(gltf_data, patch_data)
    json_dumps(gltf_data)


@cli.command(name="create-patch")
@click.pass_context
@click.argument('gltf')
@click.argument('patch')
def generate_patch(ctx, gltf, patch):
    raise NotImplementedError('https://pypi.org/project/pyjsonpatch/')


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.argument('patch')
def apply_merge_patch(ctx, gltf, patch):
    gltf_data = gltf_load(gltf)
    patch_data = gltf_load(patch)
    result = json_merge_patch.merge(gltf_data, patch_data)
    json_dumps(result)


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.argument('patch')
def create_merge_patch(ctx, gltf, patch):
    gltf_data = gltf_load(gltf)
    patch_data = gltf_load(patch)
    result = json_merge_patch.create_patch(gltf_data, patch_data)
    json_dumps(result)


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.argument('pointer')
def inspect(ctx, gltf, pointer):
    gltf_data = gltf_load(gltf)
    patch = get_by_pointer(gltf_data, pointer)
    json_dumps(patch.obj)


@cli.command()
@click.pass_context
@click.argument('input')
@click.option('-c', '--container', default='gltfconformance:latest')
def validate(ctx, input, container):
    # @TODO : run mpeg-i SD conformance. a container might help ...
    input = Path(input).resolve()
    parent = input.parent
    subprocess.run(["podman", "run", "-v", f"{parent}:/rt-xr-content/{parent.name}", container, f"/rt-xr-content/{parent.name}/{input.name}"])


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.argument('animation', type=int, default=0)
@click.argument('control', default="play", type=click.Choice(['PLAY', 'PAUSE', 'RESUME', 'STOP'], case_sensitive=False))
@click.option('-s', '--scene', type=int, default=0)
def add_action_animation(ctx, gltf, animation, control, scene):
    ANIMATION = {
        "PLAY": 0,
        "PAUSE": 1,
        "RESUME": 2, 
        "STOP": 3
    }
    gltf_data = gltf_load(gltf)
    action = {
        "animation": animation,
        "animationControl": ANIMATION[str(control).upper()]
    }
    interactivity = get_scene_interactivity(gltf_data, scene)
    interactivity["actions"].append(action)
    json_dumps(gltf_data)


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.argument('distance', type=float)
@click.option('-n', '--nodes', type=int, multiple=True, help='required')
@click.option('-r', '--reference', type=int, default=-1, help='node to consider for the proximity evaluation. default=active camera')
@click.option('-l', '--lower-limit', default=0)
@click.option('-p', '--primitives', type=int, multiple=True, help='not implemented')
@click.option('-s', '--scene', type=int, default=0)
def add_trigger_proximity(ctx, gltf, distance, reference, nodes, lower_limit, primitives, scene):
    gltf_data = gltf_load(gltf)
    interactivity = get_scene_interactivity(gltf_data, scene)
    trigger = {
        "type": 1,
        "nodes": nodes,
        "distanceUpperLimit": distance,
    }
    if (lower_limit > 0):
        trigger["distanceLowerLimit"] = lower_limit
    if (reference >= 0):
        trigger["referenceNode"] = reference
    interactivity["triggers"].append(trigger)
    json_dumps(gltf_data)


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.argument('distance', type=float)
@click.option('-n', '--nodes', type=int, multiple=True, help='required')
@click.option('-r', '--reference', type=int, default=-1, help='node to consider for the proximity evaluation. default=active camera')
@click.option('-l', '--lower-limit', default=0)
@click.option('-p', '--primitives', type=int, multiple=True, help='not implemented')
@click.option('-s', '--scene', type=int, default=0)
def add_trigger_visibility(ctx, gltf, distance, reference, nodes, lower_limit, primitives, scene):
    gltf_data = gltf_load(gltf)
    interactivity = get_scene_interactivity(gltf_data, scene)
    trigger = {
        "type": 3,
        "nodes": nodes,
        "distanceUpperLimit": distance,
    }
    if (lower_limit > 0):
        trigger["distanceLowerLimit"] = lower_limit
    if (reference >= 0):
        trigger["referenceNode"] = reference
    interactivity["triggers"].append(trigger)
    json_dumps(gltf_data)


@cli.command()
@click.pass_context
@click.argument('gltf')
@click.option('-t', '--triggers', type=int, multiple=True, default=[])
@click.option('-a', '--actions', type=int, multiple=True, default=[])
@click.option('-c', '--combination', default='', help='Set of logical operations to apply to the triggers')
@click.option('-x', '--activation', default='FIRST_ENTER', type=click.Choice(['FIRST_ENTER', 'EACH_ENTER', 'ON', 'FIRST_EXIT', 'EACH_EXIT', 'OFF'], case_sensitive=False))
@click.option('--parallel/--sequential', default=False)
@click.option('-s', '--scene', type=int, default=0)
def add_behavior(ctx, gltf, triggers, actions, combination, activation, parallel, scene):
    gltf_data = gltf_load(gltf)
    add_interactivity_behavior(gltf_data, triggers, actions, combination, activation, int(parallel), scene)
    json_dumps(gltf_data)


if __name__ == '__main__':
    cli(obj={})