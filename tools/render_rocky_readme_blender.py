import bpy, os
from mathutils import Vector

ROOT=os.path.abspath('.')
GLB=os.path.join(ROOT,'rocky-model-viewer','rocky-animated.glb')
OUT=os.path.join(ROOT,'assets','rocky-readme-frames')
os.makedirs(OUT,exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
scene=bpy.context.scene

# GitHub README preview: render the real animated GLB quickly with Blender Workbench.
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=460
scene.render.resolution_y=460
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.render.fps=24
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.6
scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True

meshes=[o for o in scene.objects if o.type=='MESH']
if not meshes:
    raise RuntimeError('No meshes imported from Rocky GLB')

# Ensure the imported sandstone material reads clearly in the README renderer.
for mat in bpy.data.materials:
    if mat.name and 'Rocky sandstone' in mat.name:
        mat.diffuse_color=(0.42,0.29,0.20,1.0)
        mat.roughness=.86

# Determine stable framing from the real imported mesh bounds.
def bounds():
    mn=Vector((1e9,1e9,1e9)); mx=Vector((-1e9,-1e9,-1e9))
    for o in meshes:
        for c in o.bound_box:
            p=o.matrix_world @ Vector(c)
            mn.x=min(mn.x,p.x); mn.y=min(mn.y,p.y); mn.z=min(mn.z,p.z)
            mx.x=max(mx.x,p.x); mx.y=max(mx.y,p.y); mx.z=max(mx.z,p.z)
    return mn,mx
mn,mx=bounds(); center=(mn+mx)*.5; span=mx-mn; size=max(span)

cam_data=bpy.data.cameras.new('Camera')
cam=bpy.data.objects.new('Camera',cam_data)
scene.collection.objects.link(cam)
scene.camera=cam
cam_data.lens=50
cam.location=center+Vector((size*1.55,-size*2.05,size*1.12))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()

# glTF importer activates the first clip; the GLB intentionally stores Auto first.
# Determine its imported frame range and sample it for a compact looping README preview.
end=1.0
for a in bpy.data.actions:
    end=max(end,float(a.frame_range[1]))
for o in scene.objects:
    ad=o.animation_data
    if ad:
        if ad.action:
            end=max(end,float(ad.action.frame_range[1]))
        for track in ad.nla_tracks:
            for strip in track.strips:
                end=max(end,float(strip.frame_end))
print('Imported actions:',[a.name for a in bpy.data.actions], 'end frame',end)

count=32
for i in range(count):
    f=1+(max(end,2)-1)*(i/(count-1))
    scene.frame_set(int(round(f)))
    scene.render.filepath=os.path.join(OUT,f'frame_{i:03d}.png')
    bpy.ops.render.render(write_still=True)
print('Rendered',count,'real GLB frames to',OUT)
