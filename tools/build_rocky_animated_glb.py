import os, json, gzip, struct, math, tempfile
from pathlib import Path
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, quaternion_from_matrix

TAU=math.pi*2
ROOT=Path('rocky-3d/assets/action')
OUT=Path('rocky-model-viewer/rocky-animated.glb')
OUT.parent.mkdir(parents=True,exist_ok=True)

# Load gzipped STL parts already stored in the repository
manifest=json.loads((ROOT/'manifest.json').read_text())
meshes={}; meta={}
needed=['torso.stl','1-A.stl','1-C.stl','2-A.stl','2-B.stl','3-A.stl','3-B.stl','4-A.stl','4-B.stl','5-A.stl','5-B.stl']
for name in needed:
    info=manifest['parts'][name]; data=gzip.decompress((ROOT/info['gzip']).read_bytes())
    with tempfile.NamedTemporaryFile(suffix='.stl') as f:
        f.write(data); f.flush(); m=trimesh.load_mesh(f.name,process=True)
    b=m.bounds.copy(); center=(b[0]+b[1])/2; size=b[1]-b[0]
    m.apply_translation([-center[0],-center[1],-b[0,2]])
    meshes[name]=m; meta[name]={'size':size}
scale=2.45/meta['torso.stl']['size'][2]
stone=trimesh.visual.material.PBRMaterial(name='Rocky sandstone',baseColorFactor=[169,138,112,255],roughnessFactor=.9,metallicFactor=.0)
for m in meshes.values(): m.visual=trimesh.visual.TextureVisuals(material=stone)

def align_z_matrix(d):
    d=np.asarray(d,float); d=d/np.linalg.norm(d); z=np.array([0.,0.,1.]); c=np.dot(z,d)
    if c>0.999999: return np.eye(4)
    if c<-0.999999: return rotation_matrix(math.pi,[1,0,0])
    axis=np.cross(z,d); axis/=np.linalg.norm(axis); return rotation_matrix(math.acos(np.clip(c,-1,1)),axis)

def quat_gl(m):
    q=quaternion_from_matrix(m)
    return np.array([q[1],q[2],q[3],q[0]],dtype=np.float32)

def solve(S,target,l1,l2,radial):
    S=np.array(S,float); target=np.array(target,float); radial=np.array(radial,float)
    dv=target-S; raw=np.linalg.norm(dv)
    if raw<1e-8: dv=np.array([0,-1,0.]); raw=1
    dist=np.clip(raw,abs(l1-l2)+.025,l1+l2-.025); direction=dv/raw
    a=(l1*l1-l2*l2+dist*dist)/(2*dist); h=max(0,l1*l1-a*a)**.5
    hint=np.array([0.,1.,0.])*.85+radial*.35
    perp=hint-direction*np.dot(hint,direction)
    if np.dot(perp,perp)<1e-5: perp=np.array([-radial[2],.2,radial[0]])
    perp/=np.linalg.norm(perp)
    return S+direction*a+perp*h

def base_foot(L):
    f=L['radial']*L['radius']; f[1]=.08; return f

def walk_foot(L,t):
    p=(t*.55+L['phase'])%1.0; base=base_foot(L); walk=np.array([.55,0,.84]); walk/=np.linalg.norm(walk)
    if p<.7:
        q=p/.7; return base+walk*((1-q)*.28+q*(-.28))
    q=(p-.7)/.3; return base+walk*((1-q)*(-.28)+q*.30)+np.array([0,math.sin(math.pi*q)*.38,0])

def support_foot(L,t):
    f=base_foot(L); f[1]+=math.sin(t*.9+L['i'])*.012; return f

def expressive(state,t):
    wave=math.sin(t*5.2); soft=math.sin(t*2.2)
    if state=='Hi': return np.array([.72+wave*.28,3.62+abs(math.sin(t*3.1))*.12,2.9+soft*.12])
    if state=='Bye': return np.array([.88+wave*.36,3.42+math.sin(t*3.2)*.1,2.82])
    if state=='Work': return np.array([.42,1.58,2.72+math.sin(t*3.3)*.08])
    if state=='Signal':
        ph=int((t*1.15)%3)
        if ph==0:return np.array([.2,2.9,3.85])
        if ph==1:return np.array([1.0+math.sin(t*4)*.12,3.15,2.7])
        return np.array([.55,3.0+math.sin(t*6)*.28,3.05])
    raise ValueError(state)

limbs=[]; angle0=math.pi/2
for i in range(5):
    n=i+1; a=angle0+i*TAU/5; radial=np.array([math.cos(a),0.,math.sin(a)])
    l1=meta[f'{n}-A.stl']['size'][2]*scale
    end='1-C.stl' if n==1 else f'{n}-B.stl'
    l2=meta[end]['size'][2]*scale
    shoulder=radial*1.02; shoulder[1]=2.12
    limbs.append(dict(i=i,n=n,radial=radial,l1=l1,l2=l2,shoulder=shoulder,radius=2.35,phase=i/5,end=end))

scene=trimesh.Scene()
torso_base=rotation_matrix(-math.pi/2,[1,0,0]); torso_base[:3,:3]*=scale; torso_base[:3,3]=[0,1.18,0]
scene.add_geometry(meshes['torso.stl'], node_name='Torso', geom_name='TorsoMesh', transform=torso_base)
for L in limbs:
    S=L['shoulder']; target=base_foot(L); E=solve(S,target,L['l1'],L['l2'],L['radial'])
    u=align_z_matrix(E-S); u[:3,:3]*=scale; u[:3,3]=S
    lo=align_z_matrix(target-E); lo[:3,:3]*=scale; lo[:3,3]=E
    scene.add_geometry(meshes[f"{L['n']}-A.stl"],node_name=f"L{L['n']}_Upper",geom_name=f"L{L['n']}UpperMesh",transform=u)
    scene.add_geometry(meshes[L['end']],node_name=f"L{L['n']}_Lower",geom_name=f"L{L['n']}LowerMesh",transform=lo)

raw=scene.export(file_type='glb')
magic,ver,total=struct.unpack_from('<4sII',raw,0); assert magic==b'glTF'
o=12; chunks=[]
while o<len(raw):
    l,t=struct.unpack_from('<II',raw,o); o+=8; data=raw[o:o+l]; o+=l; chunks.append((t,data))
j=json.loads(chunks[0][1].decode().rstrip(' \x00'))
binbuf=bytearray(chunks[1][1])
node_idx={n['name']:i for i,n in enumerate(j['nodes'])}
for name,i in node_idx.items():
    if name=='world': continue
    M=np.array(j['nodes'][i].pop('matrix'),dtype=float).reshape((4,4),order='F')
    trans=M[:3,3].copy(); sx=np.linalg.norm(M[:3,0]); sy=np.linalg.norm(M[:3,1]); sz=np.linalg.norm(M[:3,2]); sc=np.array([sx,sy,sz])
    R=M.copy(); R[:3,0]/=sx;R[:3,1]/=sy;R[:3,2]/=sz;R[:3,3]=0;R[3,:]=[0,0,0,1]
    q=quat_gl(R)
    j['nodes'][i]['translation']=trans.tolist();j['nodes'][i]['rotation']=q.tolist();j['nodes'][i]['scale']=sc.tolist()

def transforms(state,t):
    expressive_state=state in ('Hi','Work','Bye','Signal')
    bodyShift=np.zeros(3)
    if expressive_state: bodyShift=-limbs[0]['radial']*.14
    if state=='Walk': bodyShift=np.array([math.sin(t*1.1)*.035,0,math.cos(t*.9)*.03])
    bob=math.sin(t*1.7)*.025 if state=='Walk' else math.sin(t*1.4)*.012
    tilt=-.045 if expressive_state else math.sin(t*.8)*.018
    Rz=rotation_matrix(tilt,[0,0,1]); Rx=rotation_matrix(-math.pi/2,[1,0,0]); R=Rz@Rx
    d={'Torso':(np.array([bodyShift[0],1.18+bob,bodyShift[2]]),quat_gl(R))}
    for L in limbs:
        S=L['shoulder']+bodyShift
        if L['n']==1 and expressive_state: target=expressive(state,t)
        else: target=walk_foot(L,t) if state=='Walk' else support_foot(L,t)
        E=solve(S,target,L['l1'],L['l2'],L['radial'])
        d[f"L{L['n']}_Upper"]=(S,quat_gl(align_z_matrix(E-S)))
        d[f"L{L['n']}_Lower"]=(E,quat_gl(align_z_matrix(target-E)))
    return d

def smoothstep(x): x=np.clip(x,0,1); return x*x*(3-2*x)
def qnorm(q): return q/np.linalg.norm(q)
def qlerp(a,b,u):
    if np.dot(a,b)<0:b=-b
    return qnorm((1-u)*a+u*b)

def auto_frame(t):
    spans=[('Hi',0,4),('Work',4,9),('Bye',9,12.5),('Walk',12.5,20)]
    fade=.7
    for k,(state,s,e) in enumerate(spans):
        if s<=t<=e or (k==len(spans)-1 and t>=s):
            local=t-s; cur=transforms(state,local)
            if k>0 and t<s+fade:
                prev_state,ps,pe=spans[k-1]; prev=transforms(prev_state,pe-ps+(t-s)); u=smoothstep((t-s)/fade); out={}
                for name in cur:
                    p0,q0=prev[name];p1,q1=cur[name];out[name]=((1-u)*p0+u*p1,qlerp(q0,q1,u))
                return out
            return cur
    return transforms('Hi',t)

clips={'Auto':(20.0,auto_frame),'Hi':(4.0,lambda t:transforms('Hi',t)),'Work':(5.0,lambda t:transforms('Work',t)),'Bye':(3.5,lambda t:transforms('Bye',t)),'Walk':(7.5,lambda t:transforms('Walk',t))}

def append_bytes(data):
    while len(binbuf)%4: binbuf.append(0)
    off=len(binbuf); binbuf.extend(data); return off,len(data)

def add_accessor(arr,typ,minmax=False):
    arr=np.asarray(arr,dtype='<f4'); off,length=append_bytes(arr.tobytes())
    bv=len(j['bufferViews']); j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':length})
    acc={'bufferView':bv,'componentType':5126,'count':len(arr),'type':typ}
    if minmax: acc['min']=[float(np.min(arr))];acc['max']=[float(np.max(arr))]
    ai=len(j['accessors']);j['accessors'].append(acc);return ai

j['animations']=[]
fps=12
animated_names=['Torso']+[f'L{i}_{x}' for i in range(1,6) for x in ('Upper','Lower')]
for clip_name,(duration,fn) in clips.items():
    times=np.linspace(0,duration,int(duration*fps)+1,dtype=np.float32);time_acc=add_accessor(times,'SCALAR',True)
    anim={'name':clip_name,'samplers':[],'channels':[]};trans_data={n:[] for n in animated_names};rot_data={n:[] for n in animated_names}
    for t in times:
        frame=fn(float(t))
        for n in animated_names:
            p,q=frame[n];trans_data[n].append(p);rot_data[n].append(q)
    for n in animated_names:
        ta=add_accessor(np.asarray(trans_data[n],np.float32),'VEC3');ra=add_accessor(np.asarray(rot_data[n],np.float32),'VEC4')
        sidx=len(anim['samplers']);anim['samplers'].append({'input':time_acc,'output':ta,'interpolation':'LINEAR'});anim['channels'].append({'sampler':sidx,'target':{'node':node_idx[n],'path':'translation'}})
        sidx=len(anim['samplers']);anim['samplers'].append({'input':time_acc,'output':ra,'interpolation':'LINEAR'});anim['channels'].append({'sampler':sidx,'target':{'node':node_idx[n],'path':'rotation'}})
    j['animations'].append(anim)

j['buffers'][0]['byteLength']=len(binbuf)
js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
binbuf.extend(b'\x00'*((4-len(binbuf)%4)%4));total=12+8+len(js)+8+len(binbuf)
out=bytearray(struct.pack('<4sII',b'glTF',2,total));out.extend(struct.pack('<II',len(js),0x4E4F534A));out.extend(js);out.extend(struct.pack('<II',len(binbuf),0x004E4942));out.extend(binbuf)
OUT.write_bytes(out)
print('wrote',OUT,'MB',round(len(out)/1024/1024,2),'animations',[a['name'] for a in j['animations']])
