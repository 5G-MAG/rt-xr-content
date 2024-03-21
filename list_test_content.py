from pathlib import Path 
import json
import sys


def scene_metadata(fp):
    return fp.parent / 'metadata' / fp.with_suffix('.json').name

def write_scene_metadata(gltf, credits):
    data = {
                "version" : 2,
                "legal" : credits,
                "tags" : ["testing"],
                "screenshot" : f"metadata/{gltf.stem}.jpg",
                "name" : f"{gltf.stem}",
                "path" : f"{gltf.name}",
                "summary" : f"{gltf.stem}"
            }
    meta = scene_metadata(gltf)
    with open(meta, 'w') as meta_fp:
        json.dump(data, meta_fp, indent=4)


def gen_directory_metadata(dp):
    c = None
    cfp = dp / 'metadata' / 'credits.json'
    if cfp.exists():
        with open( cfp, 'r') as fo:
            c = json.load(fo)
        for scene_fp in dp.glob('*.gltf'):
            write_scene_metadata(scene_fp, c)
        for scene_fp in dp.glob('*.glb'):
            write_scene_metadata(scene_fp, c)

def read_scene_data(gltf_fp):
    fp = scene_metadata(gltf_fp)
    data = None
    gltf_data = None
    with open(fp, 'r') as fo:
        data = json.load(fo)
    with open(gltf_fp, 'r') as gltf_fo:
        gltf_data = json.load(gltf_fo)
    data["extensions"] = [ext for ext in gltf_data["extensionsUsed"] if ext.startswith("MPEG_")]
    return data


def copyright(c):
    artist = c.get('artist', None) 
    lic = f"<a alt=\"license\" href=\"{c['licenseUrl']}\">{c['license']}</a>"
    res = [
        f"&#169; {c['year']}, {c['owner']}, {lic}<br/>"
    ]
    if artist is None:
        res.append( f"  - {c['what']}<br/>" )
    else:
        res.append( f"  - {artist} for {c['what']}<br/>" )
    return res


def as_table_row(scene, dfp):
    name = scene['name']
    res = [
        "<tr>","<td>",
        f"<a href=\"{dfp.stem}\">{name}</a><br/>",
        f"<img src=\"{dfp.stem}/{scene['screenshot']}\" alt=\"{name}\"/>",
        "</td>",
        "<td>",
        f"{scene['summary']}<br/>"
    ]
    # res.append("Credit:")
    # for c in scene["legal"]:
    #     res += copyright(c)
    res + ["</td>", "</tr>"]
    return res


def process_root_readme(root):
    listing = ["<table>","<tr>","<th>Model</th>","<th>Description</th>","</tr>"]
    for p in root.iterdir():
        if p.is_dir():
            scenes = [read_scene_data(sfp) for sfp in p.glob('*.gltf')]
            for s in scenes:
                listing += as_table_row(s, p)
    listing += ["</table>"]
    with open('listing.md', 'w') as ofp:
        ofp.write("\n".join(listing))


def process_directory_readme(dp):
    readme = []
    for sfp in dp.glob('*.gltf'):
        scene = read_scene_data(sfp)
        readme.append(f"## {scene['name']}")
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
    with open( dp / 'README.md', 'w') as ofp:
        ofp.write("\n".join(readme))


if __name__ == "__main__":
    """
    1. python ./list_test_content.py 
        create listing.md with a table listing all models for use in the main README.md

    2. python ./list_test_content.py DIR
        generates a README.md draft for a DIR from using the available metadata
    """
    if len(sys.argv) == 1:
        root = Path(__file__).parent
        # for p in root.iterdir():
        #     if p.is_dir():
        #         gen_directory_metadata(p)
        process_root_readme(root)
    else:
        p = Path(sys.argv[1])
        process_directory_readme(p)