"""One Ansys Mechanical Static Structural case. Run with AnsysWBU, not CPython."""
import math
import os
import json
import shutil
import traceback

root = os.environ['CAPY_VALIDATION_OUT']
case = os.environ['CAPY_PIN_CASE']
size, support_inner, support_outer = {
    'coarse': (8, 46, 72), 'medium': (5, 46, 72), 'fine': (3, 46, 72),
    'sensitivity': (3, 52, 72),
}[case]
directory = root + '/ansys/' + case
if not os.path.isdir(directory):
    os.makedirs(directory)


def distance(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def triangle_area(a, b, c):
    u, v, w = distance(a, b), distance(b, c), distance(c, a)
    s = (u+v+w)/2
    return math.sqrt(max(0, s*(s-u)*(s-v)*(s-w)))


def load_weights(mesh, points, side):
    """Lump side facet area to vertices. Split quadratic tet faces into four triangles."""
    # Mesh element ordering uses the first four nodes as tetrahedron corners.
    boundary = {}
    for eid in mesh.ElementIds:
        ids = list(mesh.ElementById(eid).NodeIds)
        if len(ids) != 10:
            raise ValueError('Expected quadratic tetrahedra, got {} element nodes'.format(len(ids)))
        for omitted in range(4):
            corners = tuple(sorted(ids[j] for j in range(4) if j != omitted))
            if set(corners).issubset(side):
                boundary[corners] = None if corners in boundary else ids[4:]
    weights = dict((n, 0.) for n in side)
    area = 0.
    for (a, b, c), mids in boundary.items():
        if mids is None:
            continue
        def edge_mid(x, y):
            midpoint = [(p+q)/2 for p, q in zip(points[x], points[y])]
            return min(mids, key=lambda n: distance(points[n], midpoint))
        ab, bc, ca = edge_mid(a,b), edge_mid(b,c), edge_mid(c,a)
        if len(set([ab,bc,ca])) != 3 or not set([ab,bc,ca]).issubset(side):
            raise ValueError('Side face midside node identification failed')
        for tri in [(a,ab,ca), (ab,b,bc), (ca,bc,c), (ab,bc,ca)]:
            patch = triangle_area(*(points[n] for n in tri))
            area += patch
            for n in tri:
                x, y, _ = points[n]
                shape = max(-x/42., 0.)**2 * max(1-(y/38.)**2, 0.)
                weights[n] += patch*shape/3
    if abs(area/(2*math.pi*42*170)-1)>0.015:
        raise ValueError('Cylindrical surface area check failed: {}'.format(area))
    # Report any small axial eccentricity from the surface discretization.
    total, moment = 0., 0.
    for n, w in weights.items():
        total += w
        moment += w*points[n][1]
    if abs(moment/total) > 1.0:
        raise ValueError('Load distribution has an excessive axial eccentricity')
    return weights, total, moment/total, area


def run():
    with open(root+'/matlab/summary.json') as stream:
        force = json.load(stream)['force_single_N'][0]
    Model.GeometryImportGroup.AddGeometryImport().Import(root+'/ansys/boom_rod_pin_shank.step')
    body = Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)[0]
    geo = body.GetGeoBody()
    facelist = list(geo.Faces)
    volume_ratio = geo.Volume/(math.pi*42**2*170)
    if len(facelist) != 3 or min(abs(volume_ratio*factor-1) for factor in (1,1e9))>0.01:
        raise ValueError('Expected cylindrical STEP shank, found {} faces, volume {}'.format(len(facelist), geo.Volume))
    side_face = max(geo.Faces, key=lambda f:f.Area)
    body.Material = 'Structural Steel'
    analysis = Model.AddStaticStructuralAnalysis()
    method = Model.Mesh.AddAutomaticMethod()
    scope = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    scope.Ids = [geo.Id]
    method.Location = scope
    method.Method = MethodType.AllTriAllTet
    Model.Mesh.ElementOrder = ElementOrder.Quadratic
    Model.Mesh.ElementSize = Quantity('{} [mm]'.format(size))
    Model.Mesh.GenerateMesh()
    mesh = ExtAPI.DataModel.MeshDataByName('Global')
    unit = str(mesh.Unit)
    scale = {'m':1000., 'mm':1.}[unit]
    points = {}
    for n in mesh.NodeIds:
        node = mesh.NodeById(n)
        points[n] = tuple(scale*x for x in (node.X,node.Y,node.Z))
    if abs(max(p[1] for p in points.values())-85)>1e-5:
        raise ValueError('Coordinate unit check failed: '+unit)
    side = set(mesh.MeshRegionById(side_face.Id).NodeIds)
    weights, denominator, eccentricity, area = load_weights(mesh, points, side)
    support = sorted(n for n in side if support_inner <= abs(points[n][1]) <= support_outer)
    if min(sum(points[n][1]*sign>0 for n in support) for sign in [-1,1]) < 10:
        raise ValueError('Support band coverage inadequate')
    anchor=min(support, key=lambda n:distance(points[n], (0,62,42)))
    probe=min(side,key=lambda n:distance(points[n], (42,0,0)))
    solver = analysis.AddCommandSnippet()
    solver.Name = 'Bearing strip displacement and prescribed eye load (DRAFT)'
    commands = ['/COM, CAPY single-cylinder shank scenario', 'FINISH', '/PREP7', 'ALLSEL,ALL', 'SHPP,ON']
    for n in support:
        commands.extend(['D,{},UX,0'.format(n), 'D,{},UZ,0'.format(n)])
    commands.append('D,{},UY,0'.format(anchor))
    for n, weight in sorted(weights.items()):
        if weight > 0:
            commands.append('F,{},FX,{:.13g}'.format(n,force*weight/denominator))
    commands.extend(['CHECK', 'FINISH', '/SOLU'])
    solver.Input = '\n'.join(commands)
    sol = analysis.Solution
    stress = sol.AddEquivalentStress()
    displacement = sol.AddTotalDeformation()
    post = sol.AddCommandSnippet()
    post.Name = 'Sum solver reactions at constrained nodes'
    post.Input = '\n'.join(['/POST1','SET,LAST','ALLSEL,ALL','PRRSOL'])
    ExtAPI.DataModel.Project.SaveAs(directory+'/pin_'+case+'.mechdat', True)
    sol.Solve(True)
    working = analysis.WorkingDir
    for name in ['solve.out','file.rst','ds.dat']:
        path = os.path.join(working,name)
        if os.path.isfile(path):
            shutil.copyfile(path,os.path.join(directory,name))
    status = dict(case=case,mesh_size_mm=size,mesh_nodes=mesh.NodeCount,mesh_elements=mesh.ElementCount,
                  side_facet_area_mm2=area,support_inner_mm=support_inner,support_outer_mm=support_outer,
                  support_nodes=len(support),load_nodes=sum(w>0 for w in weights.values()),load_N=force,
                  load_eccentricity_y_mm=eccentricity,probe_id=probe,probe_xyz_mm=points[probe],solution_status=str(sol.Status))
    with open(directory+'/case.json','w') as stream:
        json.dump(status,stream,indent=2)
    with open(directory+'/nodes_mm.csv','w') as stream:
        stream.write('node_id,x_mm,y_mm,z_mm\n')
        for n, (x, y, z) in sorted(points.items()):
            stream.write('{},{:.10g},{:.10g},{:.10g}\n'.format(n,x,y,z))
    sol.EvaluateAllResults()
    for result, name in [(stress,'von_mises'),(displacement,'total_deformation')]:
        result.ExportToTextFile(directory+'/'+name+'.txt')
        result.Activate()
        try:
            ExtAPI.Graphics.ExportImage(directory+'/'+name+'.png')
        except Exception as error:
            ExtAPI.Log.WriteWarning(str(error))
    ExtAPI.DataModel.Project.Save()


try:
    run()
except:
    with open(directory+'/execution_error.txt','w') as stream:
        stream.write(traceback.format_exc())
    raise
