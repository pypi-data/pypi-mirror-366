from vtkmodules.vtkCommonDataModel import vtkDataSet
from ..vtk_methods.converters import vtk_to_numpy
from ..vtk_methods.finder import get_cell_ids

def write_to_elem(filename, mesh, tag):
    """

    :param filename: Filename with .elem extension
    :param mesh: Mesh which should be stored as element file.
    :param tag: Tags which are attached to the mesh
    :return:
    """
    if not filename.endswith('.elem'):
        raise ValueError(f'Filename must end with .elem extension but was {filename}')
    with open(filename, "w") as f:
        f.write(f"{mesh.GetNumberOfCells()}\n")
        for i in range(mesh.GetNumberOfCells()):
            cell = mesh.GetCell(i)
            if cell.GetNumberOfPoints() == 2:
                f.write(
                    f"Ln {cell.GetPointIds().GetId(0)} {cell.GetPointIds().GetId(1)} {tag[i]}\n")
            elif cell.GetNumberOfPoints() == 3:
                f.write("Tr {} {} {} {}\n".format(cell.GetPointIds().GetId(0), cell.GetPointIds().GetId(1),
                                                  cell.GetPointIds().GetId(2), tag[i]))
            elif cell.GetNumberOfPoints() == 4:
                f.write("Tt {} {} {} {} {}\n".format(cell.GetPointIds().GetId(0), cell.GetPointIds().GetId(1),
                                                     cell.GetPointIds().GetId(2), cell.GetPointIds().GetId(3),
                                                     tag[i]))
            else:
                print("strange " + str(cell.GetNumberOfPoints()))


def write_to_lon(filename_lon, elem, sheet, precession=4):
    if not filename_lon.endswith('.lon'):
        raise ValueError(f'Filename must end with .lon extension but was {filename_lon}')
    with open(filename_lon, "w") as f:
        f.write("2\n")
        for i in range(len(elem)):
            f.write(
                f"{elem[i][0]:.{precession}f} {elem[i][1]:.{precession}f} {elem[i][2]:.{precession}f} {sheet[i][0]:.{precession}f} {sheet[i][1]:.{precession}f} {sheet[i][2]:.{precession}f}\n")


def write_to_pts(filename_pts, pts):
    if not filename_pts.endswith('.pts'):
        raise ValueError(f'Filename must end with .pts extension but was {filename_pts}')
    with open(filename_pts, "w") as f:
        f.write(f"{len(pts)}\n")
        for i in range(len(pts)):
            f.write(f"{pts[i][0]} {pts[i][1]} {pts[i][2]}\n")


def write_mesh(filename, pts, mesh:vtkDataSet, elem_tags, fiber_long=None, fiber_sheet=None):
    write_to_pts(filename + ".pts", pts)
    write_to_elem(filename + ".elem", mesh, elem_tags)
    if fiber_sheet is not None and fiber_long is not None:
        write_to_lon(filename + ".lon", fiber_long, fiber_sheet)


def write_mesh_from_vtk_obj(filename: str, mesh, tag_name, fiber_name, sheet_name):
    pts = vtk_to_numpy(mesh.GetPoints().GetData())
    fibers = get_cell_ids(mesh, fiber_name)
    sheet = get_cell_ids(mesh, sheet_name)
    tags = get_cell_ids(mesh, tag_name)
    write_mesh(filename, pts, mesh, tags, fibers, sheet)
