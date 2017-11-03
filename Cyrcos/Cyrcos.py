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
from matplotlib.colors import Colormap
from matplotlib.patches import Wedge, PathPatch, Patch
from matplotlib.path import Path
from matplotlib.collections import PatchCollection

#List of valid image filetypes / extensions that matplotlib's savefig can produce (should all be lowercase!)
mpl_allowed_exts = ["png", "svg", "svgz", "pdf", "pgf", "ps", "rgba", "eps"]

def Angle_to_XY(angles, radius, angles_in_degrees = True, offset = (0.0, 0.0)):
	if angles_in_degrees:
		angles = numpy.deg2rad(angles)

	x = radius * numpy.sin(angles) + offset[0]
	y = radius * numpy.cos(angles) + offset[1]

	if all([hasattr(x, "__iter__"), hasattr(y, "__iter__"), not isinstance(x, str), not isinstance(y, str)]):
		return list(zip(x, y))
	else:
		return (x, y)

class Cyrcos(object):
	"""Class for creation of Circos chord graph-like figures via matplotlib.
	"""

	default_radius = 0.45			#Outer radius of the circle segments, in figure fraction units (from 0.0 to 1.0)
	default_width = 0.04			#Width of the circle segments, yielding an inner radius of radius - width
	default_center = (0.5, 0.5)		#Tuple of (float, float) coordinates for the center of the circle (from 0.0 to 1.0)
	default_gap_size = 10			#The angular width (degrees) used to equally separate the circle segments
	default_start = "top_gap"		#Location by angle or circle location to center the gap between first/last segments
	default_colors = "Set1"			#List of colors or matplotlib colormap/set to use for circle segments
	default_fade_segments = True	#If True, circle segments start out opaque and transition to desired transparency
	default_min_alpha = 0.00005		#The final alpha value of the faded circle segments if fade_segments is True
	default_alpha_steps = 1000		#The number of segment slices to use to interpolate from solid to transparent colors
	default_segment_outline = True	#If True, a border is drawn around the circle segments
	default_outline_black = False	#If True, the circle segment outline is black rather than using the segment coloring
	default_size = (10, 10)			#Tuple of 2 ints or floats giving the dimensions of the image width, height (inches)
	default_min_ribbon_width = 0.1	#Chord start/ end widths < min will be set to min for better visualization (degrees)
	default_arc_splines = 10		#Number of interpolation steps to properly display ribbon start/end chord arcs
	default_max_gap = 60			#Maximum angular width (degrees) for the gaps between circle segments

	def __init__(self, segments, radius = default_radius, width = default_width, center = default_center,
				 angles_in_degrees = True, gap_size = default_gap_size, start = default_start, colors = default_colors,
				 clockwise = True, fade_segments = default_fade_segments, segment_outline = default_segment_outline,
				 outline_black = default_outline_black, size = default_size, fig = None, ax = None):
		"""
		Initializes the bare Cyrcos graph with the circle segments after checking input parameters as described above.
		"""

		self.radius = radius if isinstance(radius, float) and 0.1 < radius < 0.5 else Cyrcos.default_radius
		self.width = width if isinstance(width, float) and 0.01 < width < self.radius else Cyrcos.default_width

		center_x = center[0] if isinstance(center[0], float) and 0.0 < center[0] < 1.0 else Cyrcos.default_center[0]
		center_y = center[1] if isinstance(center[1], float) and 0.0 < center[1] < 1.0 else Cyrcos.default_center[1]
		self.center = (center_x, center_y)

		self.angles_in_degrees = angles_in_degrees if isinstance(angles_in_degrees, bool) else True

		if isinstance(gap_size, int) or isinstance(gap_size, float):
			max_gap = Cyrcos.default_max_gap if angles_in_degrees else numpy.deg2rad(Cyrcos.default_max_gap)
			default_gap = Cyrcos.default_gap_size if angles_in_degrees else numpy.deg2rad(Cyrcos.default_gap_size)
			self.gap_size = gap_size if 0.0 <= gap_size <= max_gap else default_gap
		elif hasattr(gap_size, "__iter__") and not isinstance(gap_size, str):
			pass #ADD CHECKING FOR GAP LENGTHS
		else:
			self.gap_size = Cyrcos.default_gap_size if self.angles_in_degrees else numpy.deg2rad(Cyrcos.default_gap_size)

		if not any([isinstance(start, str), isinstance(start, float), isinstance(start, int)]):
			start = Cyrcos.default_start #Set start position to the default value in case it's wildly wrong in some way

		if isinstance(start, str):
			start = start.lower()
			#Convert description of the first segment's start location to the angular position in degrees:
			if "top" in start or "north" in start:
				pos = 0
			elif "right" in start or "east" in start:
				pos = 90
			elif "bottom" in start or "south" in start:
				pos = 180
			elif "left" in start or "west" in start:
				pos = 270
			else:
				pos = 0
			#If "gap" is requested, the gap before the first segment will be centered at the desired start location
			if "gap" in start:
				pos += self.gap_size / 2

			self.start = pos if self.angles_in_degrees else numpy.deg2rad(pos)
		elif isinstance(start, int) or isinstance(start, float):
			self.start = start % 360 if self.angles_in_degrees else start % numpy.deg2rad(360)
		else:
			self.start = self.gap_size / 2

		if not hasattr(colors, "__iter__") and not isinstance(colors, Colormap):
			colors = Cyrcos.default_colors #The colors parameter should be an iterable/string or a matplotlib Colormap

		if isinstance(colors, str):
			self.colors = plt.get_cmap(colors).colors
		elif hasattr(colors, "__iter__") and not isinstance(colors, str):
			self.colors = colors
		else:
			self.colors = plt.get_cmap("Set1").colors

		self.fade_segments = fade_segments if isinstance(fade_segments, bool) else Cyrcos.default_fade_segments
		self.segment_outline = segment_outline if isinstance(segment_outline, bool) else Cyrcos.default_segment_outline
		self.outline_black = outline_black if isinstance(outline_black, bool) else Cyrcos.default_outline_black
		self.min_alpha = Cyrcos.default_min_alpha
		self.alpha_steps = Cyrcos.default_alpha_steps

		self.min_ribbon_width = Cyrcos.default_min_ribbon_width
		self.arc_splines = Cyrcos.default_arc_splines

		fig_width = size[0] if isinstance(size[0], int) or isinstance(size[0], float) else Cyrcos.default_size[0]
		fig_height = size[1] if isinstance(size[1], int) or isinstance(size[1], float) else Cyrcos.default_size[1]
		self.figsize = (fig_width, fig_height)

		self.fig = plt.figure(figsize = self.figsize) if fig is None else fig
		self.ax = self.fig.add_subplot(1, 1, 1, aspect = "equal") if ax is None else ax
		self.ax.set_axis_off()

		self.clockwise = clockwise if isinstance(clockwise, bool) else True
		if self.clockwise:
			self.ax.invert_xaxis()

		self.total_paths = 0

		whole_circle = 360 if self.angles_in_degrees else numpy.deg2rad(360)
		self.segment_length = (whole_circle - (segments * self.gap_size)) / segments

		self.Create_Circle_Segments(segments)

	def Create_Circle_Segments(self, segments):
		"""Creates the outer circle segments representing the various groups."""

		self.segments_start_end = []
		for i in range(segments):
			cur_start = self.start + i * (self.segment_length + self.gap_size)
			cur_end = cur_start + self.segment_length
			self.segments_start_end.append((cur_start, cur_end))

		mpl_offset = 90 #For some reason matplotlib Patch angles are offset 90 degrees from Path angles???
		offset_segments = [(s + mpl_offset, e + mpl_offset) for (s, e) in self.segments_start_end]

		if not self.angles_in_degrees:
			offset_segments = [(numpy.rad2deg(s), numpy.rad2deg(e)) for (s, e) in offset_segments]

		circle_patches = []

		if self.segment_outline:
			for idx, seg in enumerate(offset_segments):
				ec = "black" if self.outline_black else self.colors[idx]
				cur_outline = Wedge(self.center, self.radius, seg[0], seg[1], self.width, facecolor = "none", edgecolor = ec, lw = 1.0)
				circle_patches.append(cur_outline)

		if self.fade_segments:
			alpha_segment_length = self.segment_length / self.alpha_steps
			alpha_change = (1.0 - self.min_alpha) / self.alpha_steps

			for idx, seg in enumerate(offset_segments):
				from_pos = seg[0]
				color = self.colors[idx]
				cur_alpha = 1.0

				for a in range(self.alpha_steps):
					to_pos = from_pos + alpha_segment_length
					cur_slice = Wedge(self.center, self.radius, from_pos, to_pos, self.width, facecolor = color, edgecolor = "none", alpha = cur_alpha)
					circle_patches.append(cur_slice)

					from_pos += alpha_segment_length
					cur_alpha -= alpha_change

		else:
			for idx, seg in enumerate(offset_segments):
				color = self.colors[idx]
				cur_segment = Wedge(self.center, self.radius, seg[0], seg[1], self.width, facecolor = color, edgecolor = "none")
				circle_patches.append(cur_segment)

		self.circle_patch_collection = PatchCollection(circle_patches, match_original = True)
		self.ax.add_collection(self.circle_patch_collection)

	def Add_Paths(self, start_angles, end_angles, start_widths = None, end_widths = None, color_by = "start",
				  control_points = None, lw = 2.0, alpha = 0.5):
		"""Creates line or ribbon path connections between segments of the outer ring.

		Parameters
		----------
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

			if "start" in color_by or "end" in color_by:
				angles = start_angles if "start" in color_by else end_angles
				for angle in angles:
					path_color = "black"
					for idx, seg in enumerate(self.segments_start_end):
						if seg[0] <= angle <= seg[1]:
							path_color = self.colors[idx]
							break

					path_colors.append(path_color)

			elif "merge" in color_by:
				pass

			else:
				path_colors = ["black"] * total_paths

		elif hasattr(color_by, "__iter__") and not isinstance(color_by, str) and len(color_by) == total_paths:
			for idx, color in enumerate(color_by):
				if isinstance(color, str) and any(["start" in color.lower(), color.lower() == "end"]):
					angle = start_angles[idx] if "start" in color.lower() else end_angles[idx]
					path_color = "black"
					for sid, seg in enumerate(self.segments_start_end):
						if seg[0] <= angle <= seg[1]:
							path_color = self.colors[sid]
							break

					path_colors.append(path_color)
				else:
					path_colors.append(color)

		else:
			path_colors = ["black"] * total_paths

		lw = lw if 0.0 < lw <= 20.0 else 2.0
		alpha = alpha if 0.0 < alpha <= 1.0 else 0.5

		if not self.angles_in_degrees:
			start_angles = numpy.rad2deg(start_angles)
			end_angles = numpy.rad2deg(end_angles)
			start_widths = numpy.rad2deg(start_widths)
			end_widths = numpy.rad2deg(end_widths)

		if self.clockwise:
			start_angles = [-a for a in start_angles]
			end_angles = [-a for a in end_angles]

		inner_radius = self.radius - self.width
		path_patches = []

		start_widths_correct = hasattr(start_widths, "__iter__") and not isinstance(start_widths, str) and len(start_widths) == total_paths
		end_widths_correct = hasattr(end_widths, "__iter__") and not isinstance(end_widths, str) and len(end_widths) == total_paths

		#If start_widths or end_widths is None, the paths will be lines with width lw (not ribbons)
		if start_widths is None or end_widths is None:
			start_xys = Angle_to_XY(start_angles, inner_radius, offset = self.center)
			end_xys = Angle_to_XY(end_angles, inner_radius, offset = self.center)

			line_path_codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]

			for start, end, control, color in zip(start_xys, end_xys, control_points, path_colors):
				path_points = [start, control, end]

				cur_path = Path(path_points, line_path_codes)
				path_patches.append(PathPatch(cur_path, facecolor = "none", edgecolor = color, lw = lw, alpha = alpha))

		#Otherwise start_widths and end_widths must be a list of angular widths of the same length as start_angles
		elif start_widths_correct and end_widths_correct:
			start_widths = [w if w >= self.min_ribbon_width else self.min_ribbon_width for w in start_widths]
			end_widths = [w if w >= self.min_ribbon_width else self.min_ribbon_width for w in end_widths]

			start_mid_ribbons = [w / 2 for w in start_widths]
			end_mid_ribbons = [w / 2 for w in end_widths]

			#Calculate width per spline of the ribbons at the ring intersection arc to use as the Bezier curve-4 control points
			#Multipied by three due to CURVE4 requiring three points
			start_arc_spline_delta = [w / (self.arc_splines * 3) for w in start_widths]
			end_arc_spline_delta = [w / (self.arc_splines * 3) for w in end_widths]

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
				for i in range(self.arc_splines * 3 - 1):
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
			arc_interpolation_curve_codes = [Path.CURVE4] * 3 * self.arc_splines

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

		self.total_paths += total_paths

	def Add_Paths_By_Segment(self, from_segments, to_segments, starts, ends, start_ratios = None, end_ratios = None,
							 color_by = "start", control_points = None, lw = 2.0, alpha = 0.5, segments_start_at_1 = True):
		if hasattr(from_segments, "__iter__") and not isinstance(from_segments, str):
			total_paths = len(from_segments)
		else:
			print("Error: Cyrcos.Add_Paths_By_Segment from_segments requires a list/iterable of ints describing each segment the path starts from (starting from 0)!")
			return None

		if hasattr(to_segments, "__iter__") and not isinstance(to_segments, str):
			if len(to_segments) != total_paths:
				print("Error: Cyrcos.Add_Paths_By_Segment to_segments must be the same length as from_segments!")
				return None
		else:
			print("Error: Cyrcos.Add_Paths_By_Segment to_segments requires a list/iterable of ints describing each segment the path starts from (starting from 0)!")
			return None

		if hasattr(starts, "__iter__") and not isinstance(starts, str):
			if len(starts) != total_paths:
				print("Error: Cyrcos.Add_Paths_By_Segment starts must be the same length as from_segments!")
				return None
		else:
			print("Error: Cyrcos.Add_Paths_By_Segment starts requires a list/iterable of ints describing each segment the path starts from (starting from 0)!")
			return None

		if hasattr(ends, "__iter__") and not isinstance(ends, str):
			if len(ends) != total_paths:
				print()
				return None
		else:
			print("Error: Cyrcos.Add_Paths_By_Segment ends requires a list/iterable of ints describing each segment the path starts from (starting from 0)!")

		#Remaining arg checking

		from_angles = []
		to_angles = []
		from_widths = []
		to_widths = []

		seg_lens = [end - start for (start, end) in self.segments_start_end]

		if segments_start_at_1:
			starts = [1.0 - start for start in starts]
			ends = [1.0 - end for end in ends]

		for from_seg, to_seg, from_pos, to_pos, start_ratio, end_ratio in zip(from_segments, to_segments, starts, ends, start_ratios, end_ratios):
			from_seg_len = seg_lens[from_seg]
			to_seg_len = seg_lens[to_seg]

			begin_start = self.segments_start_end[from_seg][0] + from_pos * from_seg_len
			begin_end = self.segments_start_end[to_seg][0] + to_pos * to_seg_len

			start_wid = start_ratio * from_seg_len
			end_wid = end_ratio * to_seg_len

			if begin_start + start_wid > self.segments_start_end[from_seg][1]:
				mid_start = self.segments_start_end[from_seg][1] - (start_wid / 2.0)
			else:
				mid_start = begin_start + (start_wid / 2.0)

			if begin_end + end_wid > self.segments_start_end[to_seg][1]:
				mid_end = self.segments_start_end[to_seg][1] - (start_wid / 2.0)
			else:
				mid_end = begin_end + (end_wid / 2.0)

			from_angles.append(mid_start)
			to_angles.append(mid_end)
			from_widths.append(start_wid)
			to_widths.append(end_wid)

		self.Add_Paths(from_angles, to_angles, start_widths = from_widths, end_widths = to_widths, color_by = color_by,
					   control_points = control_points, lw = lw, alpha = alpha)

	def Add_Text(self, text, x, y, **kwargs):
		if self.clockwise:
			x = 1.0 - x

		self.ax.text(x, y, text, **kwargs)

	def Add_Legend(self, title = "", labels = None, colors = None, **kwargs):
		if not isinstance(title, str):
			title = ""

		if isinstance(labels, str):
			labels = [labels + " " + str(i + 1) for i in range(len(self.segments_start_end))]
		elif labels is None:
			labels = ["Segment " + str(i + 1) for i in range(len(self.segments_start_end))]

		if isinstance(colors, str):
			colors = plt.get_cmap(colors).colors
		elif hasattr(colors, "__iter__") and not isinstance(colors, str) and len(colors) != len(labels):
			print("Error: Cyrcos.Add_Legend colors must be a colormap name, a list of colors of the same length as the labels / number of segments, or None!")
			return None
		else:
			colors = [color for color in self.colors]

		legend_handles = []

		for label, color in zip(labels, colors):
			legend_handles.append(Patch(color = color, label = label))

		self.legend = self.ax.legend(title = title, handles = legend_handles, **kwargs)

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
