"""Line-art 'IKEA style' renderer used for the v2 previews (painter's algorithm + crease lines).
render([(mesh, colour), ...], 'out.png', Wm=3x3 world matrix, view=direction)"""
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
# pump-body frame -> upright world (motor at top): world = (z, y, -x)
BODY_UP = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
STYLE={'white':(1,1,1),'part':(0.97,0.97,0.97),'metal':(0.86,0.87,0.89),'dark':(0.55,0.56,0.58),
       'glass':(0.93,0.97,1.0),'blue':(0.80,0.90,0.98),'hl':(1.0,0.93,0.70),'red':(1,0.85,0.85)}
def render(items, out, Wm=None, view=(0.75,1.0,0.55), up=(0,0,1), arrows=(), texts=(), circles=(), size=(6,6),
           fit=None, margin=8, dpi=300, lw=0.8, crosses=(), rot_arrows=()):
    """items: list of (mesh_in_body_coords, colorname). arrows: (p0,p1) body coords; texts: (p, str, dx,dy)"""
    Wm = np.eye(3) if Wm is None else np.asarray(Wm, float)
    def W(P): return np.asarray(P, float) @ Wm.T
    d=np.array(view,float); d/=np.linalg.norm(d); upv=np.array(up,float)
    r=np.cross(upv,d); r/=np.linalg.norm(r); u=np.cross(d,r)
    L=np.array([0.35,0.6,0.9]); L/=np.linalg.norm(L)
    def P2(P):
        Q=W(P); return np.c_[Q@r,Q@u], Q@d
    polys=[];cols=[];ecs=[];lws=[];dep=[]
    allpts=[]
    for m,cn in items:
        if len(m.faces)<4000 and m.extents.max()>8: m=m.subdivide_to_size(max_edge=5,max_iter=8)
        base=np.array(STYLE.get(cn,cn) if isinstance(cn,str) else cn,float)
        V2,Vd=P2(m.vertices); allpts.append(V2)
        N=W(m.face_normals); front=N@d>1e-6
        sh=N@L
        lev=np.where(sh>0.55,1.0,np.where(sh>0.1,0.90,0.80))
        F=m.faces
        fd=Vd[F].mean(1)
        for i in np.nonzero(front)[0]:
            c=np.clip(base*lev[i],0,1)
            polys.append(V2[F[i]]); cols.append((*c,1)); ecs.append((*c,1)); lws.append(0.3); dep.append(fd[i])
        adj=m.face_adjacency; ang=m.face_adjacency_angles; ed=m.face_adjacency_edges
        f0,f1=front[adj[:,0]],front[adj[:,1]]
        sil=f0^f1; crease=(f0&f1)&(ang>np.radians(28))
        sel=np.nonzero(sil|crease)[0]
        for k in sel:
            a,b=adj[k]; dd=max(fd[a] if front[a] else -1e9, fd[b] if front[b] else -1e9)
            polys.append(V2[ed[k]]); cols.append((0,0,0,0)); ecs.append((0,0,0,1)); lws.append(lw); dep.append(dd+0.05)
        # boundary edges (non-watertight)
    order=np.argsort(dep)
    fig=plt.figure(figsize=size); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
    pc=PolyCollection([polys[i] for i in order],facecolors=[cols[i] for i in order],edgecolors=[ecs[i] for i in order],
                      linewidths=[lws[i] for i in order],closed=True,joinstyle='round',capstyle='round')
    ax.add_collection(pc)
    if fit is None: pts=np.vstack(allpts)
    else: pts=P2(np.asarray(fit,float))[0]
    lo,hi=pts.min(0)-margin,pts.max(0)+margin
    w,h=hi-lo; asp=size[0]/size[1]
    if w/h>asp: c=(lo[1]+hi[1])/2; h=w/asp; lo[1]=c-h/2; hi[1]=c+h/2
    else: c=(lo[0]+hi[0])/2; w=h*asp; lo[0]=c-w/2; hi[0]=c+w/2
    ax.set_xlim(lo[0],hi[0]); ax.set_ylim(lo[1],hi[1]); ax.set_aspect('equal')
    for a in arrows:
        p0,p1=a[0],a[1]; s=P2(np.array([p0,p1]))[0]
        ax.annotate('',xy=s[1],xytext=s[0],arrowprops=dict(arrowstyle='-|>,head_length=0.9,head_width=0.45',lw=2.4,color='k',shrinkA=0,shrinkB=0))
    for a in rot_arrows:
        from matplotlib.patches import FancyArrowPatch
        c=P2(np.array([a[0]]))[0][0]; rr=a[1]
        ax.add_patch(FancyArrowPatch((c[0]+rr,c[1]),(c[0]-rr*0.2,c[1]+rr*0.98),connectionstyle='arc3,rad=0.6',arrowstyle='-|>,head_length=6,head_width=4',lw=2,color='k'))
    for t in texts:
        s=P2(np.array([t[0]]))[0][0]
        ax.text(s[0]+t[2],s[1]+t[3],t[1],fontsize=t[4] if len(t)>4 else 15,fontweight='bold',ha='center',va='center',family='DejaVu Sans')
    for cpt in circles:
        s=P2(np.array([cpt[0]]))[0][0]
        ax.add_patch(plt.Circle(s,cpt[1],fill=False,lw=1.6,ls=(0,(4,3)),color='k'))
    for cpt in crosses:
        s=P2(np.array([cpt[0]]))[0][0]; q=cpt[1]
        ax.plot([s[0]-q,s[0]+q],[s[1]-q,s[1]+q],color=(0.8,0.1,0.1),lw=5); ax.plot([s[0]-q,s[0]+q],[s[1]+q,s[1]-q],color=(0.8,0.1,0.1),lw=5)
    fig.savefig(out,dpi=dpi,facecolor='white'); plt.close(fig)
    return P2
