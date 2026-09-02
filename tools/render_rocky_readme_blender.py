import bpy, math, os
from mathutils import Vector

ROOT=os.path.abspath('.')
GLB=os.path.join(ROOT,'rocky-model-viewer','rocky-animated.glb')
OUT=os.path.join(ROOT,'assets','rocky-readme-frames')
os.makedirs(OUT,exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
scene=bpy.context.scene

# Transparent, fast, realistic-enough Eevee render.
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=520
scene.render.resolution_y=520
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.render.fps=24
try:
    scene.eevee.taa_render_samples=32
    scene.eevee.use_gtao=True
    scene.eevee.gtao_distance=3
    scene.eevee.gtao_factor=1.2
except Exception:
    pass

meshes=[o for o in scene.objects if o.type=='MESH']
if not meshes:
    raise RuntimeError('No meshes imported from Rocky GLB')

# Warm studio lights.
world=scene.world or bpy.data.worlds.new('World')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.025,0.03,0.027,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25

def area(name, loc, energy, size, color):
    data=bpy.data.lights.new(name,'AREA'); data.energy=energy; data.size=size; data.color=color
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc; return obj

# Determine initial bounds after import/conversion.
def bounds():
    mn=Vector((1e9,1e9,1e9)); mx=Vector((-1e9,-1e9,-1e9))
    for o in meshes:
        for c in o.bound_box:
            p=o.matrix_world @ Vector(c)
            mn.x=min(mn.x,p.x); mn.y=min(mn.y,p.y); mn.z=min(mn.z,p.z)
            mx.x=max(mx.x,p.x); mx.y=max(mx.y,p.y); mx.z=max(mx.z,p.z)
    return mn,mx
mn,mx=bounds(); center=(mn+mx)*.5; span=mx-mn; size=max(span)

area('Key',center+Vector((size*1.4,-size*1.5,size*1.8)),1300,size*1.4,(1.0,.83,.68))
area('Fill',center+Vector((-size*1.5,-size*.6,size*.8)),650,size*1.7,(.55,.75,1.0))
area('Rim',center+Vector((0,size*1.5,size*1.4)),900,size*1.2,(.45,1.0,.75))

cam_data=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',cam_data); scene.collection.objects.link(cam); scene.camera=cam
cam_data.lens=52
cam.location=center+Vector((size*1.55,-size*2.0,size*1.05))
def aim():
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
aim()

# Imported GLB contains Auto as the first animation; glTF importer activates it.
# Find the actual scene animation range from imported actions/NLA.
end=1.0
for a in bpy.data.actions:
    end=max(end,float(a.frame_range[1]))
for o in scene.objects:
    ad=o.animation_data
    if ad:
        if ad.action: end=max(end,float(ad.action.frame_range[1]))
        for track in ad.nla_tracks:
            for strip in track.strips: end=max(end,float(strip.frame_end))
print('Imported actions:',[a.name for a in bpy.data.actions], 'end frame',end)

# Sample 48 frames through the Auto performance, keeping camera fixed for stable README framing.
count=48
for i in range(count):
    f=1 + (max(end,2)-1)*(i/(count-1))
    scene.frame_set(int(round(f)))
    scene.render.filepath=os.path.join(OUT,f'frame_{i:03d}.png')
    bpy.ops.render.render(write_still=True)
print('Rendered',count,'frames to',OUT)
