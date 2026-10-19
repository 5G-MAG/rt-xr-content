"""The extensions of ISO/IEC 23090-14 this tool knows: where each may appear and the clause that defines it.

`at` lists the places an extension object may sit: "root" is the top-level extensions object, the others are the names of
glTF arrays (scenes, nodes, ...). None means the location is not checked (the clause text was not read for it)."""

SPEC = "ISO/IEC 23090-14"

EXTENSIONS = {
    "MPEG_media": {"clause": "5.2.1", "at": {"root"}, "schema": "MPEG_media.schema.json"},
    "MPEG_accessor_timed": {"clause": "5.2.2", "at": {"accessors"}, "schema": "MPEG_accessor_timed.schema.json"},
    "MPEG_buffer_circular": {"clause": "5.2.3", "at": {"buffers"}, "schema": "MPEG_buffer_circular.schema.json"},
    "MPEG_scene_dynamic": {"clause": "5.2.4", "at": {"scenes"}, "schema": "MPEG_scene_dynamic.schema.json"},
    "MPEG_texture_video": {"clause": "5.3.1", "at": {"textures"}, "schema": "MPEG_texture_video.schema.json"},
    "MPEG_mesh_linking": {"clause": "5.3.2", "at": {"meshes"}, "schema": "MPEG_mesh_linking.schema.json"},
    "MPEG_audio_spatial": {"clause": "5.4.1", "at": {"root", "scenes", "nodes", "cameras"}, "schema": "MPEG_audio_spatial.schema.json"},
    "MPEG_viewport_recommended": {"clause": "5.5.1", "at": {"scenes"}, "schema": "MPEG_viewport_recommended.schema.json"},
    "MPEG_animation_timing": {"clause": "5.5.2", "at": {"scenes"}, "schema": "MPEG_animation_timing.schema.json"},
    # at the glTF file level the anchor extension holds the trackable and anchor definitions (8.1.2); a scene or a node
    # refers to an anchor (Table 31)
    "MPEG_anchor": {"clause": "8.1", "at": {"root", "scenes", "nodes"}, "schema": None},
    "MPEG_scene_interactivity": {"clause": "8.2", "at": {"scenes"}, "schema": "MPEG_interactivity.schema.json"},
    "MPEG_node_interactivity": {"clause": "8.2", "at": {"nodes"}, "schema": "MPEG_node_interactivity.schema.json"},
    "MPEG_node_avatar": {"clause": "8.3", "at": {"nodes"}, "schema": "MPEG_node_avatar.schema.json"},
    "MPEG_lights_texture_based": {"clause": "8.4", "at": None, "schema": "MPEG_lights_texture_based.schema.json"},
    "MPEG_lights_punctual": {"clause": "8.4", "at": None, "schema": "MPEG_lights_punctual.schema.json"},
    "MPEG_primitive_V3C": {"clause": "G.1", "at": None, "schema": None},
    "MPEG_sampler_YCbCr": {"clause": "G.2", "at": None, "schema": None},
    "MPEG_haptic": {"clause": "G.3", "at": None, "schema": "MPEG_haptic.schema.json"},
    "MPEG_haptic_material": {"clause": "G.3", "at": None, "schema": "MPEG_haptic_material.schema.json"},
}

# names seen in earlier drafts or in the wild, and the name the 2024 text uses
RENAMED = {
    "MPEG_avatar": "MPEG_node_avatar",
    "MPEG_light_punctual": "MPEG_lights_punctual",
    "MPEG_haptics": "MPEG_haptic",
    "MPEG_interactivity": "MPEG_scene_interactivity or MPEG_node_interactivity",
    "MPEG_lights_texture": "MPEG_lights_texture_based",
}

# glTF arrays that can carry extensions
ARRAYS = ["scenes", "nodes", "cameras", "buffers", "bufferViews", "accessors", "textures", "images", "samplers", "meshes",
          "materials", "animations", "skins"]


# Which source governs an extension. The MPEG repository (MPEGGroup/Scene-Description, commit 5e39101) governs
# where the files of the extension were last changed after the PDF of ISO/IEC 23090-14; where they are older,
# the PDF governs. Dates: last commit touching the extension's folder.
PDF_DATE = "2024-04"
REPO_FOLDER = {
    "MPEG_media": ("MPEG_media", "2023-03-19"), "MPEG_accessor_timed": ("MPEG_accessor_timed", "2023-02-13"),
    "MPEG_buffer_circular": ("MPEG_buffer_circular", "2023-02-13"), "MPEG_scene_dynamic": ("MPEG_scene_dynamic", "2023-02-13"),
    "MPEG_texture_video": ("MPEG_texture_video", "2023-02-13"), "MPEG_mesh_linking": ("MPEG_mesh_linking", "2023-02-13"),
    "MPEG_audio_spatial": ("MPEG_audio_spatial", "2023-03-19"), "MPEG_viewport_recommended": ("MPEG_viewport_recommended", "2023-02-13"),
    "MPEG_animation_timing": ("MPEG_animation_timing", "2023-02-13"), "MPEG_anchor": ("MPEG_anchor", "2024-11-18"),
    "MPEG_scene_interactivity": ("MPEG_interactivity", "2024-11-18"), "MPEG_node_interactivity": ("MPEG_interactivity", "2024-11-18"),
    "MPEG_node_avatar": ("MPEG_node_avatar", "2025-05-26"), "MPEG_lights_texture_based": ("MPEG_lighting", "2024-11-18"),
    "MPEG_lights_punctual": ("MPEG_lighting", "2024-11-18"), "MPEG_haptic": ("MPEG_haptic", "2024-11-18"),
    "MPEG_haptic_material": ("MPEG_haptic_material", "2024-11-06"),
}


def governs(name):
    """"repository" or "pdf" (None for an extension the repository does not hold)."""
    f = REPO_FOLDER.get(name)
    return None if f is None else ("repository" if f[1][:7] > PDF_DATE else "pdf")
