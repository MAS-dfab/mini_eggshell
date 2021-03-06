import Rhino.RhinoMath as rm
import Rhino.Geometry as rg

class Slicer():
    """ Contains various functions to slice a mesh or brep geometry and return contour curves and fabrication points.
    """

    def __init__(self, layer_height, distance_between_points):
        self.layer_height = layer_height
        self.distance_between_points = distance_between_points

    def create_contour_curves_from_mesh(self, input_mesh):
        """ Returns the contour curves from a mesh.
        """
        # get lowest and highest z values of mesh
        min_z, max_z = self.get_min_max_z_from_mesh(input_mesh)

        # contour mesh
        self.contour_curves = rg.Mesh.CreateContourCurves(input_mesh, rg.Point3d(0,0,min_z), rg.Point3d(0,0,max_z), self.layer_height)
        return self.contour_curves
    
    def create_contour_curves_from_brep(self, input_brep):
        """ Returns the contour curves from a brep.
        """
        # get lowest and highest z values of brep
        min_z, max_z = self.get_min_max_z_from_brep(input_brep)
        
        # contour brep
        self.contour_curves = rg.Brep.CreateContourCurves(input_brep, rg.Point3d(0,0,min_z), rg.Point3d(0,0,max_z), self.layer_height)
        return self.contour_curves
    
    def get_min_max_z_from_mesh(self, input_mesh):
        """Gets the bounding box of a mesh and returns the maximum and minimum z values.
        """

        # gets the bounding box and its corners
        bounding_box = input_mesh.GetBoundingBox(True)
        corners = bounding_box.GetCorners()

        # create very high and low placeholder values
        min_z = 999999
        max_z = -999999

        # updates the placeholder values with the real corner values
        for p in corners:
            if p.Z < min_z:
                min_z = p.Z
            elif p.Z > max_z:
                max_z = p.Z
        return min_z, max_z

    def get_min_max_z_from_brep(self, input_brep):
        """Gets the bounding box of a brep and returns the maximum and minimum z values.
        """
        
        # gets the bounding box and its corners
        bounding_box = input_brep.GetBoundingBox(True)
        corners = bounding_box.GetCorners()
        
        # create very high and low placeholder values
        min_z = 999999
        max_z = -999999
        
        # updates the placeholder values with the real corner values
        for p in corners:
            if p.Z < min_z:
                min_z = p.Z
            elif p.Z > max_z:
                max_z = p.Z

        return min_z, max_z
    
    def divide_curves_in_points(self):
        """ Divides a curve into points at a certain distance. 
        """

        pt_list = []
        param_list = []

        for crv in self.contour_curves:
            # get division parameters for the points divided by a certain distance
            div_params = rg.Curve.DivideByLength(crv, self.distance_between_points, False)

            # if there are no division points within the distance, return an empty list
            if div_params == None:
                div_params = []

            # get discontinuity parameters 
            disc_params, disc_pts = self.curve_discontinuity(crv)

            # combine division parameters and discontinuity parameters and sort by value
            all_params = list(div_params) + list(disc_params)
            all_params.sort()

            # create points at the parameters and append to list
            for param in all_params:
                div_pt = rg.Curve.PointAt(crv, param)
                pt_list.append(div_pt)
            
        return pt_list

    def curve_discontinuity(self, crv):
        """ Returns the params and points at the discontinuities of a curve.
        """

        # get domain of curve
        tMin = crv.Domain.Min
        tMax = crv.Domain.Max

        disc_params = []
        disc_pts = []

        getNext = True

        while getNext:
            # search for discontinuity and gets the t value
            getNext, t = crv.GetNextDiscontinuity(rg.Continuity.G1_continuous, tMin, tMax)
            if not rm.IsValidDouble(t):
                # test whether t value is valid or not, returns 0.00 if not
                t = 0.00
            if t > tMax:
                t = tMax
            elif t < tMin:
                t = tMin
            disc_params.append(t)
            disc_pts.append(crv.PointAt(t))
            if getNext:
                tMin = t

        
        return disc_params, disc_pts
    


    def get_center_of_curves(self, curve_list):
        """ Returns the center of a curve
        """

        sum_x = 0
        sum_y = 0
        point_count = 0

        for curve in curve_list:

            divisions = curve.DivideByCount(20, True)
            point_list = [curve.PointAt(d) for d in divisions]

            for p in point_list:

                sum_x += p.X
                sum_y += p.Y

                point_count += 1

        avrg_x = sum_x/point_count
        avrg_y = sum_y/point_count

        avrg_p = rg.Point3d(avrg_x, avrg_y, curve_list[0].PointAtStart.Z)

        return avrg_p
    
    def reorganize_by_height(self, curve_list):
        """ Reorganizes several curves by their z value
        """

        temp_list = []
        nested_list = []

        for i, c in enumerate(curve_list[:-2]):

            c_height_01 = c.PointAtStart.Z
            c_height_02 = curve_list[i+1].PointAtStart.Z

            if self.is_almost_equal(c_height_01, c_height_02):

                temp_list.append(c)

            else:

                temp_list.append(c)
                nested_list.append(temp_list)
                temp_list = []

        return nested_list

    def is_almost_equal(self, x ,y ,epsilon=1*10**(-8)):

        """Return True if two values are close in numeric value
            By default close is withing 1*10^-8 of each other
            i.e. 0.00000001
        """
        return abs(x-y) <= epsilon

    
    def align_curve_seams(self, curve_list):
        """ Aligns the seams of all curves
        """

        nested_curve_list = self.reorganize_by_height(curve_list)

        seam_points = []
        aligned_curves = []

        for i, curve_list in enumerate(nested_curve_list):

            center_point = self.get_center_of_curves(curve_list)
            center_point = rg.Point3d.Add(center_point,rg.Vector3d(-40,-30,0))

            for j, c in enumerate(curve_list):

                if len(curve_list) == 1 and len(seam_points) > 0:

                    closest_seam_point = seam_points[i-1]
                    _, v = c.ClosestPoint(closest_seam_point)

                else:

                    _, v = c.ClosestPoint(center_point)

                c.ChangeClosedCurveSeam(v)
                c.Domain = rg.Interval(0, 1)
                seam_points.append(c.PointAt(0))
                aligned_curves.append(c)

        return aligned_curves, seam_points

