
import pyvista as pv
import numpy as np
from tqdm import tqdm

from .Point3 import Point3
from .Color4 import Color4

from jerboapy import *

def convert_vertices_attributes(gmap):
    vertices = []
    normals = []
    colors = []
    for dart in tqdm(gmap, desc="Extraction of vertices attributes"):
        p = dart.ebd123.get("pos", Point3(0.0, 0.0, 0.0))
        if isinstance(p, Point3) or isinstance(p, Color4):
            p = p.toNumpy()
        vertices.append(p)
        
        n = dart.ebd01.get("normal", Point3(0.0, 0.0, 1.0))
        if isinstance(n, Point3) or isinstance(n, Color4):
            n = n.toNumpy()
        else:
            print(">>> normal is not a Point3 or Color4: ", n)
        normals.append(n)
        
        c = dart.ebd01.get("color", Color4(1.0, 1.0, 1.0))
        if isinstance(c, Point3) or isinstance(c, Color4):
            c = c.toNumpy()
        # else:
        #     print(">>> color is not a Point3 or Color4: ", c)
        c = np.resize(c, 4) if len(c) > 4 else np.pad(c, (0, 4 - len(c)), constant_values=1.0)
        colors.append(c)
    return (
        np.array(vertices, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(colors, dtype=np.float32),
    )


def convert_faces(gmap):
    islet01 = Islet([0,1])
    ilot01 = islet01(gmap)
    # print(">>> ilot01 : ", ilot01)
    faces_flat = []
    # print("islet done.")
    faces_darts = set(ilot01)
    
    for id in tqdm(faces_darts, desc="Extraction of faces"):
        # print(">>> FaceID: ", id)
        face = []
        size = 0
        cur = id
        marks = []
        while cur not in marks:
            if size%2 == 0:
                # print("    >>> point : ", cur, " -> ", gmap[cur].ebd123.get("pos", [-10.0, -11.0, -12.0]))
                face.append(cur)
            marks.append(cur)
            cur = gmap.alpha(cur, size%2)
            size += 1
        # print(">>> new face : {} - size : {}".format(id, len(face)))
        faces_flat.append(len(face))
        faces_flat.extend(face)
    
    return faces_flat
def extract_geometries(gmap,ebdpos="pos", ebdnormal="normal", ebdcolor="color"):
    """
    Extracts vertices, normals, colors and faces from the given gmap.
    
    Parameters:
    - gmap: The GMap3D object to extract geometries from.
    - ebdpos: The key for position in the edge-based data (default is "pos").
    - ebdnormal: The key for normal in the edge-based data (default is "normal").
    - ebdcolor: The key for color in the edge-based data (default is "color").
    
    Returns:
    - A tuple containing vertices, normals, colors, and faces.
    """
    (vertdart, faces_flat) = gmap.extractGeometryCompacted3D()

    vertices = []
    normals = []
    colors = []
    for did in tqdm(vertdart, desc="Extraction of the geometry"):
        p = gmap[did].ebd123.get(ebdpos, Point3(0.0, 0.0, 0.0)).toNumpy()
        vertices.append(p)

        n = gmap[did].ebd01.get(ebdnormal, Point3(0.0, 0.0, 1.0)).toNumpy()
        normals.append(n)

        c = gmap[did].ebd01.get(ebdcolor, Color4.LIGHTGRAY).toNumpy()
        c = np.resize(c, 4) if len(c) > 4 else np.pad(c, (0, 4 - len(c)), constant_values=1.0)
        colors.append(c)

    faces_flat = [item for sublist in faces_flat for item in [len(sublist)] + sublist]

    return (
        np.array(vertices, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(colors, dtype=np.float32),
        faces_flat
    )



# @numba.jit(nopython=True, parallel=True)
def extract_geometries_old(gmap,ebdpos="pos", ebdnormal="normal", ebdcolor="color"):
    vertices = []
    normals = []
    colors = []
    faces_flat = []
    # islet01 = Islet([0,1])
    # ilot01 = islet01(gmap)
    

    for dart in tqdm(gmap, desc="Extraction of the geometry"):
        
        p = dart.ebd123.get(ebdpos, Point3(0.0, 0.0, 0.0)).toNumpy()
        vertices.append(p)
        
        n = dart.ebd01.get(ebdnormal, Point3(0.0, 0.0, 1.0)).toNumpy()
        normals.append(n)
        
        c = dart.ebd01.get(ebdcolor, Color4.LIGHTGRAY).toNumpy()
        c = np.resize(c, 4) if len(c) > 4 else np.pad(c, (0, 4 - len(c)), constant_values=1.0)
        colors.append(c)
        
    
    faces_flat = gmap.extractFaces2D()
    faces_flat = [item for sublist in faces_flat for item in [len(sublist)] + sublist]

    return (
        np.array(vertices, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(colors, dtype=np.float32),
        faces_flat
    )


def extract_geometries_compact(gmap,ebdpos="pos", ebdnormal="normal", ebdcolor="color"):
    vertices = []
    normals = []
    colors = []
    faces_flat = []
    islet01 = Islet([0,1])
    ilot01 = islet01(gmap)
    

    for dart in tqdm(gmap, desc="Extraction of the geometry"):
        id = dart.id
        
        if id == ilot01[id]:
            # print(">>> FaceID: ", id)
            face = []
            size = 0
            cur = id
            marks = []
            while cur not in marks:
                if size%2 == 0:
                    # print("    >>> point : ", cur, " -> ", gmap[cur].ebd123.get("pos", [-10.0, -11.0, -12.0]))
                    newid = len(vertices)
                    p = dart.ebd123.get(ebdpos, Point3(0.0, 0.0, 0.0))
                    if isinstance(p, Point3) or isinstance(p, Color4):
                        p = p.toNumpy()
                    vertices.append(p)
                    
                    n = dart.ebd01.get(ebdnormal, Point3(0.0, 0.0, 1.0))
                    if isinstance(n, Point3) or isinstance(n, Color4):
                        n = n.toNumpy()
                    else:
                        print(">>> normal is not a Point3 or Color4: ", n)
                    normals.append(n)
                    
                    c = dart.ebd01.get(ebdcolor, Color4(1.0, 1.0, 1.0))
                    if isinstance(c, Point3) or isinstance(c, Color4):
                        c = c.toNumpy()
                    c = np.resize(c, 4) if len(c) > 4 else np.pad(c, (0, 4 - len(c)), constant_values=1.0)
                    colors.append(c)
                    face.append(newid)
                    # face.append(cur)
                marks.append(cur)
                cur = gmap.alpha(cur, size%2)
                size += 1
            # print(">>> new face : {} - size : {}".format(id, len(face)))
            faces_flat.append(len(face))
            faces_flat.extend(face)


    return (
        np.array(vertices, dtype=np.float32),
        np.array(normals, dtype=np.float32),
        np.array(colors, dtype=np.float32),
        faces_flat
    )


def show(gmap, title="Jerboa display"):
    # vertices, normals, colors = convert_vertices_attributes(gmap)
    # faces = convert_faces(gmap)

    vertices, normals, colors, faces = extract_geometries(gmap)
    # vertices, normals, colors, faces = extract_geometries_compact(gmap)

    print("Prepare polydata by pyvista...")
    # Create a PyVista PolyData object
    mesh = pv.PolyData(vertices, faces)

    # Add normals and colors to the mesh
    mesh["Normals"] = normals
    mesh["Colors"] = colors
    
    print("Prepare plotter for pyvista...")
    # Create a PyVista plotter
    plotter = pv.Plotter(window_size=(1280, 960), notebook=False, off_screen=False, title=title)

    # Ajouter les normales sous forme de flèches
    plotter.add_mesh(mesh, scalars="Colors", rgb=True, show_edges=True, line_width=6.0)

    plotter.add_axes(interactive=True)
    plotter.show()