"""
Panda3D Tools Panel for Blender
Provides a convenient UI for setting Panda3D EGG export properties on objects.

Settings are stored as standard object custom properties (the same ones the
egg_writer reads).  The panel syncs its UI state FROM those properties on
every draw, so there is no separate ``panda3d_tools`` IDProperty group on
the object.
"""

import os

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    CollectionProperty,
    PointerProperty,
)


# ==================== PRC FILE PARSING ====================

# Cached list of object-type names parsed from user-supplied .prc files.
# Refreshed explicitly via the add/remove/refresh operators.
_prc_object_type_names: list[str] = []
_prc_needs_refresh: bool = True


def parse_prc_file(filepath: str) -> list[str]:
    """Parse a .prc file and return egg-object-type names found in it.

    Lines like::

        egg-object-type-camera-barrier  <Scalar> collide-mask …

    yield ``"camera-barrier"``.
    """
    object_types: list[str] = []
    prefix = "egg-object-type-"
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith("//"):
                    continue
                if line.lower().startswith(prefix):
                    rest = line[len(prefix):]
                    type_name = rest.split()[0] if rest.split() else rest
                    if type_name:
                        object_types.append(type_name.lower())
    except (IOError, OSError):
        pass
    return object_types


def refresh_prc_object_types():
    """Re-parse every configured .prc file and rebuild the cache.

    Duplicates and types that already appear in the hardcoded
    ``OBJECT_TYPES`` list are silently skipped.
    """
    global _prc_object_type_names, _prc_needs_refresh
    _prc_needs_refresh = False
    _prc_object_type_names = []

    try:
        prefs = bpy.context.preferences.addons[__package__].preferences
    except (KeyError, AttributeError):
        return

    hardcoded = {t[0] for t in OBJECT_TYPES}
    seen: set[str] = set()

    for entry in prefs.prc_files:
        fp = bpy.path.abspath(entry.filepath)
        if not fp or not os.path.isfile(fp):
            continue
        for tname in parse_prc_file(fp):
            if tname not in hardcoded and tname not in seen:
                _prc_object_type_names.append(tname)
                seen.add(tname)


def get_prc_object_type_names() -> list[str]:
    """Return the current list of PRC-sourced object-type names."""
    if _prc_needs_refresh:
        refresh_prc_object_types()
    return _prc_object_type_names


# ==================== CONSTANTS ====================

# Collide Types (single select)
COLLIDE_TYPES = [
    ('NONE', "None", "No collision type"),
    ('Plane', "Plane", "Plane collision"),
    ('Polygon', "Polygon", "Polygon collision"),
    ('Polyset', "Polyset", "Polyset collision"),
    ('Sphere', "Sphere", "Sphere collision"),
    ('Box', "Box", "Box collision"),
    ('InvSphere', "InvSphere", "Inverse sphere collision"),
    ('Tube', "Tube", "Tube collision"),
]

# Collide Flags (multiple select)
COLLIDE_FLAGS = [
    ('event', "event", "Generate collision events"),
    ('descend', "descend", "Descend into children"),
    ('keep', "keep", "Keep geometry after collision"),
    ('solid', "solid", "Solid collision"),
    ('center', "center", "Use center for collision"),
    ('turnstile', "turnstile", "Turnstile collision"),
    ('level', "level", "Level collision"),
    ('intangible', "intangible", "Intangible collision"),
]

# Collide Mask Types with bit values
COLLIDE_MASK_TYPES = [
    ('1', "Wall", "Wall collision mask (1)"),
    ('2', "Floor", "Floor collision mask (2)"),
    ('4', "Camera", "Camera collision mask (4)"),
    ('16', "Cogdominium Floor Event / Catch Game / C.F.O. Object", "Special event mask (16)"),
    ('32', "Furniture Side", "Furniture side collision mask (32)"),
    ('64', "Furniture Top", "Furniture top collision mask (64)"),
    ('128', "Furniture Drag", "Furniture drag collision mask (128)"),
    ('256', "Cogdominium Ceiling / Pie / Pet Look At", "Ceiling/Pie mask (256)"),
    ('512', "Non-Pet Look At", "Non-Pet Look At mask (512)"),
    ('1024', "Banquet Table", "Banquet Table mask (1024)"),
    ('2048', "Ghost", "Ghost collision mask (2048)"),
]

# Bin Types
BIN_TYPES = [
    ('NONE', "None", "No bin specified"),
    ('background', "background", "Background bin"),
    ('fixed', "fixed", "Fixed bin"),
    ('ground', "ground", "Ground bin"),
    ('gui-popup', "gui-popup", "GUI popup bin"),
    ('shadow', "shadow", "Shadow bin"),
    ('opaque', "opaque", "Opaque bin"),
    ('transparent', "transparent", "Transparent bin"),
    ('unsorted', "unsorted", "Unsorted bin"),
]

# Alpha Mode Types
ALPHA_TYPES = [
    ('NONE', "Unspecified", "Alpha type not specified (will not export)"),
    ('off', "Off", "Alpha off (1)"),
    ('on', "On", "Alpha on (2)"),
    ('blend', "Normal blending (Blend)", "Normal alpha blending (3)"),
    ('blend_no_occlude', "Blending w/o Depth Write (Blend, no occlude)", "Blend without depth write (4)"),
    ('ms', "Multisample", "Multisample alpha (5)"),
    ('ms_mask', "Multisample Mask", "Multisample mask alpha (6)"),
    ('binary', "Binary", "Binary alpha (7)"),
    ('dual', "Dual", "Dual alpha (8)"),
    ('premultiplied', "Premultiplied", "Premultiplied alpha (9)"),
]

# Billboard Types
BILLBOARD_TYPES = [
    ('NONE', "None", "No billboard (will not export)"),
    ('axis', "Axis", "Billboard around axis (0x20)"),
    ('point_eye', "Point Camera Relative", "Point billboard camera relative (0x40)"),
    ('point_world', "Point World Relative", "Point billboard world relative (0x80)"),
]

# Object Types (multiple select)
OBJECT_TYPES = [
    ('floor', "floor", "Floor object type"),
    ('dupefloor', "dupefloor", "Duplicate floor object type"),
    ('barrier', "barrier", "Barrier object type"),
    ('model', "model", "Model object type"),
    ('dcs', "dcs", "DCS object type"),
    ('camera-collide', "camera-collide", "Camera collide object type"),
    ('camera-collide-sphere', "camera-collide-sphere", "Camera collide sphere object type"),
    ('camera-barrier', "camera-barrier", "Camera barrier object type"),
    ('camera-barrier-sphere', "camera-barrier-sphere", "Camera barrier sphere object type"),
    ('trigger', "trigger", "Trigger object type"),
    ('sphere', "sphere", "Sphere object type"),
    ('invsphere', "invsphere", "Inverse sphere object type"),
    ('trigger-sphere', "trigger-sphere", "Trigger sphere object type"),
    ('tube', "tube", "Tube object type"),
    ('portal', "portal", "Portal object type"),
    ('polylight', "polylight", "Polylight object type"),
    ('seq24', "seq24", "Sequence 24 fps"),
    ('seq12', "seq12", "Sequence 12 fps"),
    ('seq10', "seq10", "Sequence 10 fps"),
    ('seq8', "seq8", "Sequence 8 fps"),
    ('seq6', "seq6", "Sequence 6 fps"),
    ('seq4', "seq4", "Sequence 4 fps"),
    ('seq2', "seq2", "Sequence 2 fps"),
    ('indexed', "indexed", "Indexed object type"),
    ('binary', "binary", "Binary object type"),
    ('dual', "dual", "Dual object type"),
    ('glass', "glass", "Glass object type"),
    ('notouch', "notouch", "No touch object type"),
    ('ghost', "ghost", "Ghost object type"),
    ('glow', "glow", "Glow object type"),
    ('bubble', "bubble", "Bubble object type"),
    ('shadow-cast', "shadow-cast", "Shadow-casting object type")
]

# Flags (each becomes a separate property)
PROPERTY_FLAGS = [
    ('portal', "portal", "Portal flag"),
    ('occluder', "occluder", "Occluder flag"),
    ('polylight', "polylight", "Polylight flag"),
    ('indexed', "indexed", "Indexed flag"),
]


# ==================== SYNC INFRASTRUCTURE ====================

# Guard flag: prevents update callbacks from firing while we are syncing
# the PropertyGroup FROM the object's custom properties.
_syncing = False


def sync_settings_from_object(settings, obj):
    """Read the object's custom properties and mirror them into *settings*.

    Called at the top of the main panel's ``draw()`` so the UI always
    reflects what is actually stored on the object.
    """
    global _syncing
    if not obj:
        return

    _syncing = True
    try:
        # --- Normalize keys to lowercase ---
        # List of all keys we control
        controlled_keys = [
            'collide', 'collide-mask', 'into-collide-mask', 'from-collide-mask',
            'bin', 'billboard', 'alpha', 'draw-order',
            'scroll-u', 'scroll-v', 'scroll-w',
            'lod-in', 'lod-out', 'lod-fade',
            'lod-center-x', 'lod-center-y', 'lod-center-z',
        ]
        # Add flag names from PROPERTY_FLAGS
        for flag_id, flag_name, _ in PROPERTY_FLAGS:
            controlled_keys.append(flag_name)
        
        # Convert any non-lowercase versions to lowercase
        keys_to_rename = []
        for key in obj.keys():
            key_lower = key.lower()
            # Check exact match keys
            if key_lower in controlled_keys and key != key_lower:
                keys_to_rename.append((key, key_lower))
            # Check prefix-based keys
            elif (key_lower.startswith('objecttype') or key_lower.startswith('tag_')) and key != key_lower:
                keys_to_rename.append((key, key_lower))
        
        # Rename the keys
        for old_key, new_key in keys_to_rename:
            obj[new_key] = obj[old_key]
            del obj[old_key]
        
        # --- Collide type + flags ---
        collide_val = str(obj.get('collide', ''))
        if collide_val:
            parts = collide_val.split()
            collide_type = parts[0] if parts else 'NONE'
            valid_types = [t[0] for t in COLLIDE_TYPES]
            settings.collide_type = collide_type if collide_type in valid_types else 'NONE'
            flags = parts[1:] if len(parts) > 1 else []
            for flag_id, _, _ in COLLIDE_FLAGS:
                setattr(settings, f'collide_flag_{flag_id}', flag_id in flags)
        else:
            settings.collide_type = 'NONE'
            for flag_id, _, _ in COLLIDE_FLAGS:
                setattr(settings, f'collide_flag_{flag_id}', False)

        # --- Collide masks ---
        mask_value = int(obj.get('collide-mask', 0))
        for val_str, _, _ in COLLIDE_MASK_TYPES:
            val = int(val_str)
            setattr(settings, f'collide_mask_{val}', bool(mask_value & val))

        # --- Into-collide masks ---
        into_mask_value = int(obj.get('into-collide-mask', 0))
        for val_str, _, _ in COLLIDE_MASK_TYPES:
            val = int(val_str)
            setattr(settings, f'into_collide_mask_{val}', bool(into_mask_value & val))

        # --- From-collide masks ---
        from_mask_value = int(obj.get('from-collide-mask', 0))
        for val_str, _, _ in COLLIDE_MASK_TYPES:
            val = int(val_str)
            setattr(settings, f'from_collide_mask_{val}', bool(from_mask_value & val))

        # --- Bin ---
        bin_val = str(obj.get('bin', ''))
        valid_bins = [b[0] for b in BIN_TYPES]
        settings.bin_type = bin_val if bin_val in valid_bins else 'NONE'

        # --- Billboard ---
        billboard_val = str(obj.get('billboard', ''))
        valid_billboards = [b[0] for b in BILLBOARD_TYPES]
        settings.billboard_type = billboard_val if billboard_val in valid_billboards else 'NONE'

        # --- Alpha ---
        alpha_val = str(obj.get('alpha', ''))
        valid_alphas = [a[0] for a in ALPHA_TYPES]
        settings.alpha_type = alpha_val if alpha_val in valid_alphas else 'NONE'

        # --- Draw order ---
        settings.draw_order = int(obj.get('draw-order', 0))

        # --- UV Scroll ---
        settings.uv_scroll_u = float(obj.get('scroll-u', 0.0))
        settings.uv_scroll_v = float(obj.get('scroll-v', 0.0))
        settings.uv_scroll_w = float(obj.get('scroll-w', 0.0))

        # --- Object types ---
        for otype_id, _, _ in OBJECT_TYPES:
            prop_name = 'objecttype_' + otype_id.replace('-', '_')
            setattr(settings, prop_name, False)

        # Collect all objecttype values on the object for quick lookup
        _obj_type_values: set[str] = set()
        for key in obj.keys():
            if key.lower().startswith('objecttype'):
                otype_value = str(obj[key])
                _obj_type_values.add(otype_value)
                prop_name = 'objecttype_' + otype_value.replace('-', '_')
                if hasattr(settings, prop_name):
                    setattr(settings, prop_name, True)

        # --- PRC Object types ---
        prc_names = get_prc_object_type_names()
        settings.prc_object_types.clear()
        for tname in prc_names:
            item = settings.prc_object_types.add()
            item.name = tname
            item.enabled = tname in _obj_type_values

        # --- Flags ---
        for flag_id, flag_name, _ in PROPERTY_FLAGS:
            prop_name = f'flag_{flag_id}'
            setattr(settings, prop_name, flag_name in obj and int(obj[flag_name]) == 1)

        # --- LOD ---
        settings.lod_in = float(obj.get('lod-in', 0.0))
        settings.lod_out = float(obj.get('lod-out', 0.0))
        settings.lod_center_x = float(obj.get('lod-center-x', 0.0))
        settings.lod_center_y = float(obj.get('lod-center-y', 0.0))
        settings.lod_center_z = float(obj.get('lod-center-z', 0.0))

        # --- Tags ---
        settings.tags.clear()
        for key in obj.keys():
            if key.lower().startswith('tag_'):
                tag_value = str(obj[key])
                if ':' in tag_value:
                    tag_name, tag_val = tag_value.split(':', 1)
                    tag_item = settings.tags.add()
                    tag_item.name = tag_name
                    tag_item.value = tag_val
    finally:
        _syncing = False


# ==================== PROPERTY GROUPS ====================

class PrcObjectTypeItem(bpy.types.PropertyGroup):
    """A single PRC-sourced object type with an enabled toggle."""
    # 'name' is inherited from PropertyGroup; we store the type id there.
    enabled: BoolProperty(
        name="Enabled",
        default=False,
        update=lambda self, ctx: _on_prc_object_type_toggled(self, ctx),
    )


class Panda3DTagProperty(bpy.types.PropertyGroup):
    """Property group for a single tag (key-value pair)"""
    name: StringProperty(name="Tag Name", default="", update=lambda self, ctx: update_tags(self, ctx))
    value: StringProperty(name="Tag Value", default="", update=lambda self, ctx: update_tags(self, ctx))


class Panda3DToolsSettings(bpy.types.PropertyGroup):
    """UI-only property group living on WindowManager.

    Values are synced FROM the active object's custom properties on every
    panel draw.  When the user changes a value, the update callback writes
    it back to the object's custom properties.
    """

    # ---- Collisions ----
    collide_type: EnumProperty(
        name="Collide Type",
        description="Type of collision geometry",
        items=COLLIDE_TYPES,
        default='NONE',
        update=lambda self, ctx: update_collide_property(self, ctx)
    )

    # Collide flags as individual booleans
    collide_flag_event: BoolProperty(name="event", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_descend: BoolProperty(name="descend", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_keep: BoolProperty(name="keep", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_solid: BoolProperty(name="solid", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_center: BoolProperty(name="center", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_turnstile: BoolProperty(name="turnstile", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_level: BoolProperty(name="level", default=False, update=lambda self, ctx: update_collide_property(self, ctx))
    collide_flag_intangible: BoolProperty(name="intangible", default=False, update=lambda self, ctx: update_collide_property(self, ctx))

    # Collide masks as individual booleans
    collide_mask_1: BoolProperty(name="Wall (1)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_2: BoolProperty(name="Floor (2)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_4: BoolProperty(name="Camera (4)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_16: BoolProperty(name="Cogdominium Floor Event / Catch Game / C.F.O. Object (16)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_32: BoolProperty(name="Furniture Side (32)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_64: BoolProperty(name="Furniture Top (64)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_128: BoolProperty(name="Furniture Drag (128)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_256: BoolProperty(name="Cogdominium Ceiling / Pie / Pet Look At (256)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_512: BoolProperty(name="Non-Pet Look At (512)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_1024: BoolProperty(name="Banquet Table (1024)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))
    collide_mask_2048: BoolProperty(name="Ghost (2048)", default=False, update=lambda self, ctx: update_collide_mask_property(self, ctx))

    # Into collide mask
    into_collide_mask_1: BoolProperty(name="Wall (1)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_2: BoolProperty(name="Floor (2)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_4: BoolProperty(name="Camera (4)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_16: BoolProperty(name="Cogdominium Floor Event / Catch Game / C.F.O. Object (16)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_32: BoolProperty(name="Furniture Side (32)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_64: BoolProperty(name="Furniture Top (64)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_128: BoolProperty(name="Furniture Drag (128)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_256: BoolProperty(name="Cogdominium Ceiling / Pie / Pet Look At (256)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_512: BoolProperty(name="Non-Pet Look At (512)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_1024: BoolProperty(name="Banquet Table (1024)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))
    into_collide_mask_2048: BoolProperty(name="Ghost (2048)", default=False, update=lambda self, ctx: update_into_collide_mask_property(self, ctx))

    # From collide mask
    from_collide_mask_1: BoolProperty(name="Wall (1)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_2: BoolProperty(name="Floor (2)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_4: BoolProperty(name="Camera (4)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_16: BoolProperty(name="Cogdominium Floor Event / Catch Game / C.F.O. Object (16)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_32: BoolProperty(name="Furniture Side (32)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_64: BoolProperty(name="Furniture Top (64)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_128: BoolProperty(name="Furniture Drag (128)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_256: BoolProperty(name="Cogdominium Ceiling / Pie / Pet Look At (256)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_512: BoolProperty(name="Non-Pet Look At (512)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_1024: BoolProperty(name="Banquet Table (1024)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))
    from_collide_mask_2048: BoolProperty(name="Ghost (2048)", default=False, update=lambda self, ctx: update_from_collide_mask_property(self, ctx))

    # ---- Single Properties ----
    bin_type: EnumProperty(
        name="Bin",
        description="Render bin for the object",
        items=BIN_TYPES,
        default='NONE',
        update=lambda self, ctx: update_bin_property(self, ctx)
    )

    billboard_type: EnumProperty(
        name="Billboard",
        description="Billboard type for the object",
        items=BILLBOARD_TYPES,
        default='NONE',
        update=lambda self, ctx: update_billboard_property(self, ctx)
    )

    alpha_type: EnumProperty(
        name="Alpha Type",
        description="Alpha blending mode",
        items=ALPHA_TYPES,
        default='NONE',
        update=lambda self, ctx: update_alpha_property(self, ctx)
    )

    draw_order: IntProperty(
        name="Draw Order",
        description="Draw order (larger values drawn later). 0 = not exported",
        default=0,
        min=0,
        update=lambda self, ctx: update_draw_order_property(self, ctx)
    )

    uv_scroll_u: FloatProperty(
        name="U",
        description="UV scroll speed in U direction",
        default=0.0,
        min=-1.0,
        max=1.0,
        update=lambda self, ctx: update_uv_scroll_property(self, ctx)
    )

    uv_scroll_v: FloatProperty(
        name="V",
        description="UV scroll speed in V direction",
        default=0.0,
        min=-1.0,
        max=1.0,
        update=lambda self, ctx: update_uv_scroll_property(self, ctx)
    )

    uv_scroll_w: FloatProperty(
        name="W",
        description="UV scroll speed in W direction",
        default=0.0,
        min=-1.0,
        max=1.0,
        update=lambda self, ctx: update_uv_scroll_property(self, ctx)
    )

    # ---- Object Types (multiple select) ----
    objecttype_floor: BoolProperty(name="floor", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_dupefloor: BoolProperty(name="dupefloor", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_barrier: BoolProperty(name="barrier", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_model: BoolProperty(name="model", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_dcs: BoolProperty(name="dcs", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_camera_collide: BoolProperty(name="camera-collide", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_camera_collide_sphere: BoolProperty(name="camera-collide-sphere", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_camera_barrier: BoolProperty(name="camera-barrier", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_camera_barrier_sphere: BoolProperty(name="camera-barrier-sphere", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_trigger: BoolProperty(name="trigger", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_sphere: BoolProperty(name="sphere", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_invsphere: BoolProperty(name="invsphere", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_trigger_sphere: BoolProperty(name="trigger-sphere", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_tube: BoolProperty(name="tube", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_portal: BoolProperty(name="portal", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_polylight: BoolProperty(name="polylight", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq24: BoolProperty(name="seq24", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq12: BoolProperty(name="seq12", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq10: BoolProperty(name="seq10", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq8: BoolProperty(name="seq8", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq6: BoolProperty(name="seq6", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq4: BoolProperty(name="seq4", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_seq2: BoolProperty(name="seq2", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_indexed: BoolProperty(name="indexed", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_binary: BoolProperty(name="binary", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_dual: BoolProperty(name="dual", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_glass: BoolProperty(name="glass", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_notouch: BoolProperty(name="notouch", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_ghost: BoolProperty(name="ghost", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_glow: BoolProperty(name="glow", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_bubble: BoolProperty(name="bubble", default=False, update=lambda self, ctx: update_object_types(self, ctx))
    objecttype_shadow_cast: BoolProperty(name="shadow-cast", default=False, update=lambda self, ctx: update_object_types(self, ctx))

    # ---- PRC Object Types (dynamic, from .prc files) ----
    prc_object_types: CollectionProperty(type=PrcObjectTypeItem)

    # ---- Flags (each separate property) ----
    flag_portal: BoolProperty(name="portal", default=False, update=lambda self, ctx: update_flags(self, ctx))
    flag_occluder: BoolProperty(name="occluder", default=False, update=lambda self, ctx: update_flags(self, ctx))
    flag_polylight: BoolProperty(name="polylight", default=False, update=lambda self, ctx: update_flags(self, ctx))
    flag_indexed: BoolProperty(name="indexed", default=False, update=lambda self, ctx: update_flags(self, ctx))

    # ---- LOD (Level of Detail) ----
    lod_in: FloatProperty(
        name="LOD Out",
        description="Distance at which this LOD level disappears",
        default=0.0,
        min=0.0,
        update=lambda self, ctx: update_lod_property(self, ctx)
    )
    lod_out: FloatProperty(
        name="LOD In",
        description="Distance at which this LOD level becomes visible",
        default=0.0,
        min=0.0,
        update=lambda self, ctx: update_lod_property(self, ctx)
    )
    lod_center_x: FloatProperty(
        name="X",
        description="LOD center X coordinate",
        default=0.0,
        update=lambda self, ctx: update_lod_property(self, ctx)
    )
    lod_center_y: FloatProperty(
        name="Y",
        description="LOD center Y coordinate",
        default=0.0,
        update=lambda self, ctx: update_lod_property(self, ctx)
    )
    lod_center_z: FloatProperty(
        name="Z",
        description="LOD center Z coordinate",
        default=0.0,
        update=lambda self, ctx: update_lod_property(self, ctx)
    )

    # ---- Tags (collection of key-value pairs) ----
    tags: CollectionProperty(type=Panda3DTagProperty)

    # UI state for collapsible sections
    show_collisions: BoolProperty(name="Show Collisions", default=True)
    show_single_properties: BoolProperty(name="Show Single Properties", default=True)
    show_properties: BoolProperty(name="Show Properties", default=True)


# ==================== UPDATE FUNCTIONS ====================

def get_object_from_context(context):
    """Get the object associated with these settings"""
    if context.object:
        return context.object
    return None


def update_collide_property(self, context):
    """Update the combined collide property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    collide_type = self.collide_type
    if collide_type == 'NONE':
        # Remove the collide property if it exists
        if 'collide' in obj:
            del obj['collide']
        return

    # Build the collide string: "Type flag1 flag2 ..."
    flags = []
    if self.collide_flag_event:
        flags.append('event')
    if self.collide_flag_descend:
        flags.append('descend')
    if self.collide_flag_keep:
        flags.append('keep')
    if self.collide_flag_solid:
        flags.append('solid')
    if self.collide_flag_center:
        flags.append('center')
    if self.collide_flag_turnstile:
        flags.append('turnstile')
    if self.collide_flag_level:
        flags.append('level')
    if self.collide_flag_intangible:
        flags.append('intangible')

    if flags:
        collide_value = collide_type + ' ' + ' '.join(flags)
    else:
        collide_value = collide_type

    obj['collide'] = collide_value


def calculate_mask_value(self, prefix):
    """Calculate the combined mask value from individual checkboxes"""
    total = 0
    mask_values = [1, 2, 4, 16, 32, 64, 128, 256, 512, 1024, 2048]
    for val in mask_values:
        prop_name = f'{prefix}_{val}'
        if getattr(self, prop_name, False):
            total += val
    return total


def update_collide_mask_property(self, context):
    """Update the collide-mask property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    mask_value = calculate_mask_value(self, 'collide_mask')
    if mask_value == 0:
        if 'collide-mask' in obj:
            del obj['collide-mask']
    else:
        obj['collide-mask'] = mask_value


def update_into_collide_mask_property(self, context):
    """Update the into-collide-mask property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    mask_value = calculate_mask_value(self, 'into_collide_mask')
    if mask_value == 0:
        if 'into-collide-mask' in obj:
            del obj['into-collide-mask']
    else:
        obj['into-collide-mask'] = mask_value


def update_from_collide_mask_property(self, context):
    """Update the from-collide-mask property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    mask_value = calculate_mask_value(self, 'from_collide_mask')
    if mask_value == 0:
        if 'from-collide-mask' in obj:
            del obj['from-collide-mask']
    else:
        obj['from-collide-mask'] = mask_value


def update_bin_property(self, context):
    """Update the bin property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    if self.bin_type == 'NONE':
        if 'bin' in obj:
            del obj['bin']
    else:
        obj['bin'] = self.bin_type


def update_billboard_property(self, context):
    """Update the billboard property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    if self.billboard_type == 'NONE':
        if 'billboard' in obj:
            del obj['billboard']
    else:
        obj['billboard'] = self.billboard_type


def update_alpha_property(self, context):
    """Update the alpha property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    if self.alpha_type == 'NONE':
        if 'alpha' in obj:
            del obj['alpha']
    else:
        obj['alpha'] = self.alpha_type


def update_draw_order_property(self, context):
    """Update the draw-order property on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    if self.draw_order == 0:
        if 'draw-order' in obj:
            del obj['draw-order']
    else:
        obj['draw-order'] = self.draw_order


def update_uv_scroll_property(self, context):
    """Update the UV scroll properties on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    # If all three are 0, remove all UV scroll properties
    if self.uv_scroll_u == 0.0 and self.uv_scroll_v == 0.0 and self.uv_scroll_w == 0.0:
        for prop in ['scroll-u', 'scroll-v', 'scroll-w']:
            if prop in obj:
                del obj[prop]
    else:
        # Export all three if at least one is non-zero
        obj['scroll-u'] = self.uv_scroll_u
        obj['scroll-v'] = self.uv_scroll_v
        obj['scroll-w'] = self.uv_scroll_w


def update_lod_property(self, context):
    """Update the LOD properties on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    # If both in and out are 0, remove all LOD properties
    if self.lod_in == 0.0 and self.lod_out == 0.0:
        for prop in ('lod-in', 'lod-out', 'lod-fade',
                     'lod-center-x', 'lod-center-y', 'lod-center-z'):
            if prop in obj:
                del obj[prop]
    else:
        obj['lod-in'] = self.lod_in
        obj['lod-out'] = self.lod_out
        obj['lod-center-x'] = self.lod_center_x
        obj['lod-center-y'] = self.lod_center_y
        obj['lod-center-z'] = self.lod_center_z


def _write_all_object_types(settings, context):
    """Write all object-type custom properties (hardcoded + PRC) to the object."""
    obj = get_object_from_context(context)
    if not obj:
        return

    # First, remove all existing objecttype properties
    keys_to_remove = [k for k in obj.keys() if k.lower().startswith('objecttype')]
    for key in keys_to_remove:
        del obj[key]

    # Now add the enabled object types
    object_type_props = [
        ('objecttype_floor', 'floor'),
        ('objecttype_dupefloor', 'dupefloor'),
        ('objecttype_barrier', 'barrier'),
        ('objecttype_model', 'model'),
        ('objecttype_dcs', 'dcs'),
        ('objecttype_camera_collide', 'camera-collide'),
        ('objecttype_camera_collide_sphere', 'camera-collide-sphere'),
        ('objecttype_camera_barrier', 'camera-barrier'),
        ('objecttype_camera_barrier_sphere', 'camera-barrier-sphere'),
        ('objecttype_trigger', 'trigger'),
        ('objecttype_sphere', 'sphere'),
        ('objecttype_invsphere', 'invsphere'),
        ('objecttype_trigger_sphere', 'trigger-sphere'),
        ('objecttype_tube', 'tube'),
        ('objecttype_portal', 'portal'),
        ('objecttype_polylight', 'polylight'),
        ('objecttype_seq24', 'seq24'),
        ('objecttype_seq12', 'seq12'),
        ('objecttype_seq10', 'seq10'),
        ('objecttype_seq8', 'seq8'),
        ('objecttype_seq6', 'seq6'),
        ('objecttype_seq4', 'seq4'),
        ('objecttype_seq2', 'seq2'),
        ('objecttype_indexed', 'indexed'),
        ('objecttype_binary', 'binary'),
        ('objecttype_dual', 'dual'),
        ('objecttype_glass', 'glass'),
        ('objecttype_notouch', 'notouch'),
        ('objecttype_ghost', 'ghost'),
        ('objecttype_glow', 'glow'),
        ('objecttype_bubble', 'bubble'),
        ('objecttype_shadow_cast', 'shadow-cast'),
    ]

    idx = 1
    for prop_name, type_value in object_type_props:
        if getattr(settings, prop_name, False):
            obj[f'objecttype_{idx}'] = type_value
            idx += 1

    # PRC-sourced object types
    for item in settings.prc_object_types:
        if item.enabled:
            obj[f'objecttype_{idx}'] = item.name
            idx += 1


def update_object_types(self, context):
    """Update the objecttype_XXX properties on the object"""
    if _syncing:
        return
    _write_all_object_types(self, context)


def _on_prc_object_type_toggled(self, context):
    """Called when a PRC object-type toggle changes."""
    if _syncing:
        return
    settings = context.window_manager.panda3d_tools
    _write_all_object_types(settings, context)


def update_flags(self, context):
    """Update the flag properties on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    flag_props = [
        ('flag_portal', 'portal'),
        ('flag_occluder', 'occluder'),
        ('flag_polylight', 'polylight'),
        ('flag_indexed', 'indexed'),
    ]

    for prop_name, flag_name in flag_props:
        if getattr(self, prop_name, False):
            obj[flag_name] = 1
        else:
            if flag_name in obj:
                del obj[flag_name]


def update_tags(self, context):
    """Update the tag properties on the object"""
    if _syncing:
        return
    obj = get_object_from_context(context)
    if not obj:
        return

    # Get the settings object (could be called from tag property or main settings)
    settings = context.window_manager.panda3d_tools
    
    # First, remove all existing tag properties
    keys_to_remove = [k for k in obj.keys() if k.lower().startswith('tag_')]
    for key in keys_to_remove:
        del obj[key]

    # Add all tags from the collection
    tag_idx = 1
    for tag in settings.tags:
        if tag.name and tag.value:  # Only export tags with both name and value
            obj[f'tag_{tag_idx}'] = f'{tag.name}:{tag.value}'
            tag_idx += 1


# ==================== PANEL ====================

class PANDA3D_PT_tools_panel(bpy.types.Panel):
    """Panda3D Tools Panel in the Object Properties"""
    bl_label = "Panda3D Tools"
    bl_idname = "PANDA3D_PT_tools_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools
        sync_settings_from_object(settings, obj)


class PANDA3D_PT_collisions_subpanel(bpy.types.Panel):
    """Collisions subpanel"""
    bl_label = "Collisions"
    bl_idname = "PANDA3D_PT_collisions_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_tools_panel"
    bl_options = set()

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        # Collide Type
        layout.prop(settings, "collide_type")

        # Collide Flags (only show if type is not NONE)
        if settings.collide_type != 'NONE':
            box = layout.box()
            box.label(text="Collide Flags:")
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(settings, "collide_flag_event", toggle=True)
            row.prop(settings, "collide_flag_descend", toggle=True)
            row = col.row(align=True)
            row.prop(settings, "collide_flag_keep", toggle=True)
            row.prop(settings, "collide_flag_solid", toggle=True)
            row = col.row(align=True)
            row.prop(settings, "collide_flag_center", toggle=True)
            row.prop(settings, "collide_flag_turnstile", toggle=True)
            row = col.row(align=True)
            row.prop(settings, "collide_flag_level", toggle=True)
            row.prop(settings, "collide_flag_intangible", toggle=True)


class PANDA3D_PT_collide_mask_subpanel(bpy.types.Panel):
    """Collide Mask subpanel"""
    bl_label = "Collide Mask"
    bl_idname = "PANDA3D_PT_collide_mask_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_collisions_subpanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        col = layout.column(align=True)
        col.prop(settings, "collide_mask_1", toggle=True)
        col.prop(settings, "collide_mask_2", toggle=True)
        col.prop(settings, "collide_mask_4", toggle=True)
        col.prop(settings, "collide_mask_16", toggle=True)
        col.prop(settings, "collide_mask_32", toggle=True)
        col.prop(settings, "collide_mask_64", toggle=True)
        col.prop(settings, "collide_mask_128", toggle=True)
        col.prop(settings, "collide_mask_256", toggle=True)
        col.prop(settings, "collide_mask_512", toggle=True)
        col.prop(settings, "collide_mask_1024", toggle=True)
        col.prop(settings, "collide_mask_2048", toggle=True)


class PANDA3D_PT_into_collide_mask_subpanel(bpy.types.Panel):
    """Into Collide Mask subpanel"""
    bl_label = "Into Collide Mask"
    bl_idname = "PANDA3D_PT_into_collide_mask_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_collisions_subpanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        col = layout.column(align=True)
        col.prop(settings, "into_collide_mask_1", toggle=True)
        col.prop(settings, "into_collide_mask_2", toggle=True)
        col.prop(settings, "into_collide_mask_4", toggle=True)
        col.prop(settings, "into_collide_mask_16", toggle=True)
        col.prop(settings, "into_collide_mask_32", toggle=True)
        col.prop(settings, "into_collide_mask_64", toggle=True)
        col.prop(settings, "into_collide_mask_128", toggle=True)
        col.prop(settings, "into_collide_mask_256", toggle=True)
        col.prop(settings, "into_collide_mask_512", toggle=True)
        col.prop(settings, "into_collide_mask_1024", toggle=True)
        col.prop(settings, "into_collide_mask_2048", toggle=True)


class PANDA3D_PT_from_collide_mask_subpanel(bpy.types.Panel):
    """From Collide Mask subpanel"""
    bl_label = "From Collide Mask"
    bl_idname = "PANDA3D_PT_from_collide_mask_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_collisions_subpanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        col = layout.column(align=True)
        col.prop(settings, "from_collide_mask_1", toggle=True)
        col.prop(settings, "from_collide_mask_2", toggle=True)
        col.prop(settings, "from_collide_mask_4", toggle=True)
        col.prop(settings, "from_collide_mask_16", toggle=True)
        col.prop(settings, "from_collide_mask_32", toggle=True)
        col.prop(settings, "from_collide_mask_64", toggle=True)
        col.prop(settings, "from_collide_mask_128", toggle=True)
        col.prop(settings, "from_collide_mask_256", toggle=True)
        col.prop(settings, "from_collide_mask_512", toggle=True)
        col.prop(settings, "from_collide_mask_1024", toggle=True)
        col.prop(settings, "from_collide_mask_2048", toggle=True)


class PANDA3D_PT_lod_subpanel(bpy.types.Panel):
    """LOD (Level of Detail) subpanel"""
    bl_label = "LODs"
    bl_idname = "PANDA3D_PT_lod_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_tools_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        box = layout.box()
        box.label(text="LOD Distances:")
        row = box.row(align=True)
        row.prop(settings, "lod_out")
        row.prop(settings, "lod_in")

        box = layout.box()
        box.label(text="LOD Center:")
        row = box.row(align=True)
        row.prop(settings, "lod_center_x")
        row.prop(settings, "lod_center_y")
        row.prop(settings, "lod_center_z")


class PANDA3D_PT_single_properties_subpanel(bpy.types.Panel):
    """Single Properties subpanel"""
    bl_label = "Single Properties"
    bl_idname = "PANDA3D_PT_single_properties_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_tools_panel"
    bl_options = set()

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        # Bin
        layout.prop(settings, "bin_type")

        # Billboard
        layout.prop(settings, "billboard_type")

        # Alpha Type
        layout.prop(settings, "alpha_type")

        # Draw Order
        layout.prop(settings, "draw_order")

        # UV Scroll
        box = layout.box()
        box.label(text="UV Scroll:")
        row = box.row(align=True)
        row.prop(settings, "uv_scroll_u")
        row.prop(settings, "uv_scroll_v")
        row.prop(settings, "uv_scroll_w")


class PANDA3D_PT_properties_subpanel(bpy.types.Panel):
    """Properties subpanel (Object Types, Flags, Tags)"""
    bl_label = "Properties"
    bl_idname = "PANDA3D_PT_properties_subpanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "PANDA3D_PT_tools_panel"
    bl_options = set()

    def draw(self, context):
        layout = self.layout
        obj = context.object
        settings = context.window_manager.panda3d_tools

        # Object Types
        box = layout.box()
        box.label(text="Object Types:")
        col = box.column(align=True)

        # Row 1
        row = col.row(align=True)
        row.prop(settings, "objecttype_floor", toggle=True)
        row.prop(settings, "objecttype_dupefloor", toggle=True)
        row.prop(settings, "objecttype_barrier", toggle=True)

        # Row 2
        row = col.row(align=True)
        row.prop(settings, "objecttype_model", toggle=True)
        row.prop(settings, "objecttype_dcs", toggle=True)
        row.prop(settings, "objecttype_trigger", toggle=True)

        # Row 3 - Camera related
        row = col.row(align=True)
        row.prop(settings, "objecttype_camera_collide", toggle=True)
        row.prop(settings, "objecttype_camera_collide_sphere", toggle=True)

        row = col.row(align=True)
        row.prop(settings, "objecttype_camera_barrier", toggle=True)
        row.prop(settings, "objecttype_camera_barrier_sphere", toggle=True)

        # Row 4 - Sphere types
        row = col.row(align=True)
        row.prop(settings, "objecttype_sphere", toggle=True)
        row.prop(settings, "objecttype_invsphere", toggle=True)
        row.prop(settings, "objecttype_trigger_sphere", toggle=True)

        # Row 5 - Misc
        row = col.row(align=True)
        row.prop(settings, "objecttype_tube", toggle=True)
        row.prop(settings, "objecttype_portal", toggle=True)
        row.prop(settings, "objecttype_polylight", toggle=True)

        # Row 6 - Sequences
        row = col.row(align=True)
        row.prop(settings, "objecttype_seq24", toggle=True)
        row.prop(settings, "objecttype_seq12", toggle=True)
        row.prop(settings, "objecttype_seq10", toggle=True)
        row.prop(settings, "objecttype_seq8", toggle=True)

        row = col.row(align=True)
        row.prop(settings, "objecttype_seq6", toggle=True)
        row.prop(settings, "objecttype_seq4", toggle=True)
        row.prop(settings, "objecttype_seq2", toggle=True)

        # Row 7 - Alpha related
        row = col.row(align=True)
        row.prop(settings, "objecttype_indexed", toggle=True)
        row.prop(settings, "objecttype_binary", toggle=True)
        row.prop(settings, "objecttype_dual", toggle=True)

        # Row 8 - Material types
        row = col.row(align=True)
        row.prop(settings, "objecttype_glass", toggle=True)
        row.prop(settings, "objecttype_notouch", toggle=True)
        row.prop(settings, "objecttype_ghost", toggle=True)

        row = col.row(align=True)
        row.prop(settings, "objecttype_glow", toggle=True)
        row.prop(settings, "objecttype_bubble", toggle=True)
        row.prop(settings, "objecttype_shadow_cast", toggle=True)

        # PRC Object Types (loaded from .prc files via Addon Preferences)
        if len(settings.prc_object_types) > 0:
            # Draw in rows of 3 for consistency with the hardcoded grid
            items = list(settings.prc_object_types)
            for i in range(0, len(items), 3):
                row = col.row(align=True)
                for item in items[i:i + 3]:
                    row.prop(item, "enabled", text=item.name, toggle=True)

        # Flags
        box = layout.box()
        box.label(text="Flags:")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(settings, "flag_portal", toggle=True)
        row.prop(settings, "flag_occluder", toggle=True)
        row = col.row(align=True)
        row.prop(settings, "flag_polylight", toggle=True)
        row.prop(settings, "flag_indexed", toggle=True)

        # Tags
        box = layout.box()
        row = box.row()
        row.label(text="Tags:")
        row.operator("panda3d.tag_add", icon='ADD', text="")

        for i, tag in enumerate(settings.tags):
            row = box.row(align=True)
            row.prop(tag, "name", text="")
            row.prop(tag, "value", text="")
            op = row.operator("panda3d.tag_remove", icon='X', text="")
            op.index = i


# ==================== OPERATORS ====================

class PANDA3D_OT_tag_add(bpy.types.Operator):
    """Add a new tag"""
    bl_idname = "panda3d.tag_add"
    bl_label = "Add Tag"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.window_manager.panda3d_tools
        tag = settings.tags.add()
        tag.name = "name"
        tag.value = "value"
        # Write immediately so the object property is created
        update_tags(settings, context)
        return {'FINISHED'}


class PANDA3D_OT_tag_remove(bpy.types.Operator):
    """Remove a tag by index"""
    bl_idname = "panda3d.tag_remove"
    bl_label = "Remove Tag"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0)

    def execute(self, context):
        settings = context.window_manager.panda3d_tools
        if 0 <= self.index < len(settings.tags):
            settings.tags.remove(self.index)
            update_tags(settings, context)
        return {'FINISHED'}


# ==================== REGISTRATION ====================

# Property group classes
property_classes = (
    PrcObjectTypeItem,
    Panda3DTagProperty,
    Panda3DToolsSettings,
)

# Operator classes
operator_classes = (
    PANDA3D_OT_tag_add,
    PANDA3D_OT_tag_remove,
)

# Panel classes
panel_classes = (
    PANDA3D_PT_tools_panel,
    PANDA3D_PT_collisions_subpanel,
    PANDA3D_PT_collide_mask_subpanel,
    PANDA3D_PT_into_collide_mask_subpanel,
    PANDA3D_PT_from_collide_mask_subpanel,
    PANDA3D_PT_lod_subpanel,
    PANDA3D_PT_single_properties_subpanel,
    PANDA3D_PT_properties_subpanel,
)


def register():
    """Register all classes and properties"""
    for cls in property_classes:
        bpy.utils.register_class(cls)
    
    for cls in operator_classes:
        bpy.utils.register_class(cls)

    for cls in panel_classes:
        bpy.utils.register_class(cls)

    # Store settings on WindowManager (session-only, never saved per-object)
    bpy.types.WindowManager.panda3d_tools = PointerProperty(type=Panda3DToolsSettings)


def unregister():
    """Unregister all classes and properties"""
    # Remove the property group from WindowManager
    del bpy.types.WindowManager.panda3d_tools

    for cls in reversed(panel_classes):
        bpy.utils.unregister_class(cls)
    
    for cls in reversed(operator_classes):
        bpy.utils.unregister_class(cls)

    for cls in reversed(property_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
