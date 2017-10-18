"""
MIT License

Copyright (c) 2017 Gregory King (GKing-Dev)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import matplotlib.pyplot as plt
import numpy
import pandas
from matplotlib.patches import Wedge, PathPatch
from matplotlib.path import Path
from matplotlib.collections import PatchCollection, PathCollection

#List of valid image filetypes / extensions that matplotlib's savefig can produce (should all be lowercase!)
mpl_allowed_exts = ["png", "svg", "svgz", "pdf", "pgf", "ps", "rgba", "eps"]

def Angle_to_XY(angles, radius, angles_in_degrees = True, offset = (0.0, 0.0)):
	if angles_in_degrees:
		angles = numpy.deg2rad(angles)

	x = radius * numpy.sin(angles) + offset[0]
	y = radius * numpy.cos(angles) + offset[1]

	if isinstance(x, float) and isinstance(y, float):
		return (x, y)
	else:
		return list(zip(x, y))

class Cyrcos(object):
	def __init__(self, segments = 0, radius = 0.45, ring_width = 0.04, center = (0.5, 0.5), gap_size = 10,
				 start_position = "top_gap", sample_colors = "Set1", fade_segments = True, normalized = True,
				 size_inches = (10, 10), dpi = None, ax = None, fig = None, angles_in_degrees = True,
				 slice_borders = True, clockwise = True):
		if isinstance(radius, float) and 0.1 < radius < 0.5:
			self.radius = radius
		else:
			self.radius = 0.45

		if isinstance(ring_width, float) and 0.01 < ring_width < self.radius:
			self.ring_width = ring_width
		else:
			self.ring_width = 0.04

		if isinstance(center[0], float) and 0.0 < center[0] < 1.0:
			x = center[0]
		else:
			x = 0.5

		if isinstance(center[1], float) and 0.0 < center[1] < 1.0:
			y = center[1]
		else:
			y = 0.5

		self.center = (x, y)

		if any([isinstance(gap_size, int), isinstance(gap_size, float)]) and 0 <= gap_size <= 60 and angles_in_degrees:
			self.gap_size = gap_size
			self.angles_in_degrees = True
		elif isinstance(gap_size, float) and 0.0 <= gap_size <= (numpy.pi / 3.0) and not angles_in_degrees:
			self.gap_size = gap_size
			self.angles_in_degrees = False
		else:
			if angles_in_degrees:
				self.gap_size = 10
				self.angles_in_degrees = True
			else:
				self.gap_size = numpy.pi / 18.0
				self.angles_in_degrees = False

		if isinstance(start_position, str) and "gap" in start_position.lower():
			start_position = start_position.lower()

			if "top" in start_position:
				self.start_position = "top_gap"
			elif "left" in start_position:
				self.start_position = "left_gap"
			elif "bottom" in start_position:
				self.start_position = "bottom_gap"
			elif "right" in start_position:
				self.start_position = "right_gap"

		elif isinstance(start_position, int) or isinstance(start_position, float):
			self.start_position = start_position

		else:
			self.start_position = "top_gap"

		if isinstance(sample_colors, str):
			self.sample_colors = plt.get_cmap(sample_colors).colors
		elif hasattr(sample_colors, "__iter__") and not isinstance(sample_colors, str):
			self.sample_colors = sample_colors
		else:
			self.sample_colors = plt.get_cmap("Set1").colors

		if isinstance(fade_segments, bool):
			self.fade_segments = fade_segments
		else:
			self.fade_segments = True

		if isinstance(normalized, bool):
			self.normalized = normalized
		else:
			self.normalized = True

		if isinstance(size_inches[0], int) or isinstance(size_inches[0], float):
			image_width = size_inches[0]
		else:
			image_width = 10

		if isinstance(size_inches[1], int) or isinstance(size_inches[1], float):
			image_height = size_inches[1]
		else:
			image_height = 10

		self.size_inches = (image_width, image_height)

		if fig is None:
			self.fig = plt.figure(figsize = self.size_inches)
		else:
			self.fig = fig

		if ax is None:
			self.ax = self.fig.add_subplot(1, 1, 1, aspect = "equal")
		else:
			self.ax = ax

		self.ax.set_axis_off()

		if isinstance(slice_borders, bool):
			self.slice_borders = slice_borders
		else:
			self.slice_borders = True

		if clockwise:
			self.ax.invert_xaxis()
			self.clockwise = clockwise

		if isinstance(segments, int) and segments != 0:
			self.Create_Ring_Slices(segments = segments)

	def Create_Ring_Slices(self, segments, min_alpha = 0.00005, alpha_steps = 1000):
		if self.angles_in_degrees:
			whole_circle = 360
			quarter_circle = 90
		else:
			whole_circle = numpy.pi * 2.0
			quarter_circle = numpy.pi / 2.0

		#if self.normalized:
		if isinstance(segments, int) or isinstance(segments, float):
			segment_length = whole_circle - (segments * self.gap_size)
			segment_length /= segments
		elif isinstance(segments, list):
			pass #Weight ring segment lengths by overall unique clone counts
		else:
			pass #Error

		if isinstance(self.start_position, str):
			mid_gap = self.gap_size / 2

			if "top" in self.start_position:
				self.offset_angle = quarter_circle
			elif "left" in self.start_position:
				self.offset_angle = quarter_circle * 2
			elif "bottom" in self.start_position:
				self.offset_angle = quarter_circle * 3
			elif "right" in self.start_position:
				self.offset_angle = 0
			else:
				self.offset_angle = quarter_circle

			self.first_segment_start = self.offset_angle + mid_gap

		else:
			self.first_segment_start = self.start_position

		self.segment_length = segment_length
		self.start_to_start = self.segment_length + self.gap_size

		self.segments_start_end = []
		for i in range(segments):
			cur_seg_start = self.first_segment_start + i * (self.segment_length + self.gap_size)
			cur_seg_end = cur_seg_start + self.segment_length

			self.segments_start_end.append((cur_seg_start, cur_seg_end))

		ring_patches = []

		if self.fade_segments:
			alpha_segment_len = self.segment_length / alpha_steps
			alpha_decrease = (1.0 - min_alpha) / alpha_steps

			for idx, seg in enumerate(self.segments_start_end):
				from_pos = seg[0]
				to_pos = seg[1]
				cur_color = self.sample_colors[idx]
				cur_alpha = 1.0

				if self.slice_borders:
					slice_outline = Wedge(self.center, self.radius, from_pos, to_pos, self.ring_width, facecolor = "none", edgecolor = "black", lw = 1.0)
					ring_patches.append(slice_outline)

				for a in range(alpha_steps):
					to_pos = from_pos + alpha_segment_len

					cur_slice = Wedge(self.center, self.radius, from_pos, to_pos, self.ring_width, facecolor = cur_color, edgecolor = "none", alpha = cur_alpha)
					ring_patches.append(cur_slice)

					from_pos += alpha_segment_len
					cur_alpha -= alpha_decrease

		else:
			if self.slice_borders:
				outline = "black"
			else:
				outline = "none"

			for idx, seg in enumerate(self.segments_start_end):
				from_pos = seg[0]
				to_pos = seg[1]
				cur_color = self.sample_colors[idx]

				cur_slice = Wedge(self.center, self.radius, from_pos, to_pos, self.ring_width, facecolor = cur_color, edgecolor = outline, lw = 1.0)
				ring_patches.append(cur_slice)

		self.ring_collection = PatchCollection(ring_patches, match_original = True)
		self.ax.add_collection(self.ring_collection)

	def Add_Paths(self, start_angles, end_angles, start_widths = None, end_widths = None, color_by = "start",
				  control_points = None, arc_splines = 10, lw = 2.0, alpha = 0.5, angles_in_degrees = True):
		"""Creates line or ribbon path connections between segments of the outer ring.

		Parameters
		----------
		start_angles:
		end_angles:
		start_widths:
		end_widths:
		color_by:
		control_points:
		arc_splines:
		lw:
		alpha:
		angles_in_degrees:
		"""

		if hasattr(start_angles, "__iter__") and not isinstance(start_angles, str):
			total_paths = len(start_angles)
		else:
			print("Error: Cyrcos.Add_Paths requires a list/iterable of start and end angles!")
			return None

		if not hasattr(end_angles, "__iter__") or isinstance(end_angles, str) or len(end_angles) != total_paths:
			print("Error: Cyrcos.Add_Paths end_angles must be a list/iterable of the same length as start_angles!")
			return None

		#Control points for the midpoint of the curve by default are set as the center of the circle
		if hasattr(control_points, "__iter__"):
			if len(control_points) != total_paths or isinstance(control_points, str):
				print("Error: Cyrcos.Add_Paths control_points must be a list/iterable of the same length as start_angles or None to use the circle center for all paths.")
				return None
		else:
			control_points = [self.center] * total_paths

		path_colors = []

		if isinstance(color_by, str):
			color_by = color_by.lower()

			if "start" in color_by:
				for start in start_angles:
					no_start_found = True

					for idx, seg in enumerate(self.segments_start_end):
						if seg[0] <= start + self.offset_angle <= seg[1]:
							path_colors.append(self.sample_colors[idx])
							no_start_found = False
							break

					if no_start_found:
						path_colors.append("black")

			elif "end" in color_by:
				for end in end_angles:
					no_end_found = True

					for idx, seg in enumerate(self.segments_start_end):
						if seg[0] <= end + self.offset_angle <= seg[1]:
							path_colors.append(self.sample_colors[idx])
							no_end_found = False
							break

					if no_end_found:
						path_colors.append("black")

			elif "merge" in color_by:
				pass
			else:
				path_colors = ["black"] * total_paths

		if not isinstance(arc_splines, int) or not arc_splines > 0:
			arc_splines = 10

		if not isinstance(lw, float) or not isinstance(lw, int) or not lw > 0:
			lw = 2.0

		if not isinstance(alpha, float) or alpha < 0.0 or alpha > 1.0:
			alpha = 0.5

		if not angles_in_degrees:
			start_angles = numpy.rad2deg(start_angles)
			end_angles = numpy.rad2deg(end_angles)
			start_widths = numpy.rad2deg(start_widths)
			end_widths = numpy.rad2deg(end_widths)

		if self.clockwise:
			start_angles = [-a for a in start_angles]
			end_angles = [-a for a in end_angles]

		inner_radius = self.radius - self.ring_width
		path_patches = []

		start_widths_correct = hasattr(start_widths, "__iter__") and not isinstance(start_widths, str) and len(start_widths) == total_paths
		end_widths_correct = hasattr(end_widths, "__iter__") and not isinstance(end_widths, str) and len(end_widths) == total_paths

		#If start_widths or end_widths is None, the paths will be lines with width lw (not ribbons)
		if start_widths is None or end_widths is None:
			start_xys = Angle_to_XY(start_angles, inner_radius, offset = self.center)
			end_xys = Angle_to_XY(end_angles, inner_radius, offset = self.center)

			line_path_codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]

			for start, end, control in zip(start_xys, end_xys, control_points):
				path_points = [start, control, end]

				cur_path = Path(path_points, line_path_codes)
				path_patches.append(PathPatch(cur_path, facecolor = "none", edgecolor = "black", lw = lw, alpha = alpha))

		#Otherwise start_widths and end_widths must be a list of angular widths of the same length as start_angles
		elif start_widths_correct and end_widths_correct:
			start_mid_ribbons = [w / 2 for w in start_widths]
			end_mid_ribbons = [w / 2 for w in end_widths]

			#Calculate width per spline of the ribbons at the ring intersection arc to use as the Bezier curve-4 control points
			#Multipied by three due to CURVE4 requiring three points
			start_arc_spline_delta = [w / (arc_splines * 3) for w in start_widths]
			end_arc_spline_delta = [w / (arc_splines * 3) for w in end_widths]

			start1_angles = []
			end1_angles = []
			start_arc_control_angles = []
			start2_angles = []
			end2_angles = []
			end_arc_control_angles = []

			for idx, start_mid_width in enumerate(start_mid_ribbons):
				cur_start = start_angles[idx]
				cur_end = end_angles[idx]
				end_mid_width = end_mid_ribbons[idx]
				cur_start_arc_spline_len = start_arc_spline_delta[idx]
				cur_end_arc_spline_len = end_arc_spline_delta[idx]

				start1_angles.append(cur_start - start_mid_width)
				end1_angles.append(cur_end + end_mid_width)
				start2_angles.append(cur_start + start_mid_width)
				end2_angles.append(cur_end - end_mid_width)

				cur_start_arc_control_angles = []
				cur_end_arc_control_angles = []

				cur_start_arc_pos = cur_start + start_mid_width - cur_start_arc_spline_len
				cur_end_arc_pos = cur_end + end_mid_width - cur_end_arc_spline_len
				for i in range(arc_splines * 3 - 1):
					cur_start_arc_control_angles.append(cur_start_arc_pos)
					cur_start_arc_pos -= cur_start_arc_spline_len

					cur_end_arc_control_angles.append(cur_end_arc_pos)
					cur_end_arc_pos -= cur_end_arc_spline_len

				start_arc_control_angles.append(cur_start_arc_control_angles)
				end_arc_control_angles.append(cur_end_arc_control_angles)

			start1_xys = Angle_to_XY(start1_angles, inner_radius, offset = self.center)
			end1_xys = Angle_to_XY(end1_angles, inner_radius, offset = self.center)
			start2_xys = Angle_to_XY(start2_angles, inner_radius, offset = self.center)
			end2_xys = Angle_to_XY(end2_angles, inner_radius, offset = self.center)

			start_arc_splines_xys = []
			end_arc_splines_xys = []

			for start, end in zip(start_arc_control_angles, end_arc_control_angles):
				start_arc_splines_xys.append(Angle_to_XY(start, inner_radius, offset = self.center))
				end_arc_splines_xys.append(Angle_to_XY(end, inner_radius, offset = self.center))

			#Creating the multiple interpolated control points (Bezier-4 curves) for the ribbon arc intersections
			arc_interpolation_curve_codes = [Path.CURVE4] * 3 * arc_splines

			ribbon_path_codes = [
				Path.MOVETO,	#Set Artist to first starting point
				Path.CURVE3,	#Control point for the first side of the ribbon curve (Bezier-3)
				Path.CURVE3		#End point for the first side of the ribbon curve (Bezier-3)
			]
			ribbon_path_codes += arc_interpolation_curve_codes
			ribbon_path_codes += [
				Path.CURVE3,	#Control point for the second side of the ribbon curve (Bezier-3)
				Path.CURVE3		#End point for the second side of the ribbon curve (Bezier-3)
			]
			ribbon_path_codes += arc_interpolation_curve_codes
			ribbon_path_codes += [
				Path.CLOSEPOLY	#Signals completion of the full ribbon path
			]

			ribbon_xys = zip(start1_xys, end1_xys, start2_xys, end2_xys, control_points, start_arc_splines_xys, end_arc_splines_xys, path_colors)
			for start1, end1, start2, end2, control, start_arc_splines, end_arc_splines, color in ribbon_xys:
				path_points = [start1, control, end1]	#Positions of the first ribbon curve start, control, and end
				path_points.extend(end_arc_splines)		#Positions of the arc intersection for the ribbon end
				path_points += [end2, control, start2]	#Positions of the second ribbon curve start, control, and end
				path_points.extend(start_arc_splines)	#Positions of the arc intersection for the ribbon start
				path_points += [start1, start1]			#Returning to start point and close path

				cur_path = Path(path_points, ribbon_path_codes)
				path_patches.append(PathPatch(cur_path, facecolor = color, edgecolor = "none", alpha = alpha))

		else:
			print("Error: Cyrcos.Add_Paths ribbon_widths must be a list/iterable of the same length as start_angles or None to make simple lines instead of ribbons.")
			return None

		self.path_collection = PatchCollection(path_patches, match_original = True)
		self.ax.add_collection(self.path_collection)

	def Add_Text(self, text, x, y, **kwargs):
		if self.clockwise:
			x = 1.0 - x

		self.ax.text(x, y, text, **kwargs)

	def Show(self):
		plt.show()

	def Save(self, file_name, ext = "png", dpi = 600, bbox_inches = "tight", transparent = False, valid_exts = mpl_allowed_exts, **kwargs):
		"""Utility function for saving figures via Matplotlib.

		Parameters
		----------
		file_name: str
			Filename to save as; if the name doesn't end with a viable image type extension then ext is appended automatically.
		ext: str
			Type of image file to save; matplotlib allows any of "png", "svg", "svgz", "pdf", "pgf", "ps", "rgba", "eps".
			Default: "png"
		dpi: int
			Dots per inch used by Matplotlib plotter.
			Default: 600
		bbox_inches: "tight", or float or int
			Passed directly to matplotlib.pyplot.savefig; determines the border spacing around the image.
			Default: "tight", savefig will find the smallest calculated border spacing.
		transparent: bool
			Bool stating whether the figure background should be set to transparent when saved (sent directly to savefig).
			Default: False
		valid_exts: list of str
			List of the file extensions that matplotlib can write; if given an invalid type matplotlib will scold the user (you).
			Default: see mpl_allowed_exts

		Additional keyword arguments are passed to matplotlib.pyplot savefig.
		"""

		#Validation to make sure the provided ext is usable by matplotlib, otherwise forced to default value "png"
		if ext.lower() not in valid_exts:
			ext = "png"

		#Check if the intended file name already has a valid extension for matplotlib.pyplot, otherwise use provided ext.
		if file_name.split(".")[-1].lower() not in valid_exts:
			file_name += "." + ext

		plt.savefig(file_name, dpi = dpi, bbox_inches = bbox_inches, transparent = transparent, **kwargs)
		plt.clf()

if __name__ == "__main__":
	start_colored_example = Cyrcos(4)
	start_colored_example.Add_Paths([10, 60, 108], [210, 120, 240], start_widths = [10, 11, 22], end_widths = [10, 5, 15])
	start_colored_example.Add_Paths([35], [330], start_widths = [2], end_widths = [6])
	start_colored_example.Add_Text("Ribbons colored by\nstarting segment!", 0.85, 0.85)

	end_colored_example = Cyrcos(4)
	end_colored_example.Add_Paths([10, 60, 108], [210, 120, 240], start_widths = [10, 11, 22], end_widths = [10, 5, 15], color_by = "end")
	end_colored_example.Add_Paths([35], [330], start_widths = [2], end_widths = [6], color_by = "end")
	end_colored_example.Add_Text("Ribbons colored by\nending segment!", 0.85, 0.85)

	start_colored_example.Show()
