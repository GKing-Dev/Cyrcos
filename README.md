
# Cyrcos: Circos-esque Figures using Python

Cyrcos is a very limited Python implementation of Circos-like chord graphs created via Matplotlib! See http://circos.ca for the real deal, which I have nothing to do with and is better in every way :) I made Cyrcos because I wanted to make very specific types of chord-graph figures for comparing immune repertoire datasets from differet cell subsets within a single donor. The format for input data can be either a specific set of positions to connect or you can describe the relative positions from 0.0 to 1.0 within each group for a specific member.

I plan on at the very least adding some more customization for changing the relative sizes for the groups - as things currently stand each circle segment is displayed as the same length. I'll also have a more robust method of providing input via JSON and/or pandas DataFrames soon!

To start things out, first import Cyrcos (or just import Cyrcos from Cyrcos to avoid repetititon):


```python
%matplotlib inline
from Cyrqos import Cyrcos
```

The simplest basic chord graph is just a few segments representing the different groups to compare; let's say we have five groups.
To create a graph object with a specific number of groups, we can instantiate a Cyrcos object with an integer:
<i>(If you're working in a Jupyter notebook, just use the magic %matplotlib inline command as I did above. You could also show your plots using the Show method, or save them as an image using Save ie: cyr_plot.Save("my_chord_figure.png"))</i>


```python
cyr_plot = Cyrcos(5)
#cyr_plot.fig.set_facecolor("white") #In case notebook background color makes the graph hard to see
```


[[examples/Cyrcos_example_1.png]]


This graph doesn't show much of anything yet, so let's add some paths connecting the groups!
One method of doing this (basically by hand) is by the Cyrcos Add_Paths method, which requires at minimum a list/iterable of start and stop angles.

For example, setting up four lines starting at 20°, 115°, 330°, and 160° ending at 250°, 195°, 50° and 310° repectively is demonstrated below.

Note that angles are given by default in degrees, with 0° at top center and increasing clockwise.


```python
cyr_plot = Cyrcos(5)
cyr_plot.Add_Paths([20, 115, 330, 160], [250, 195, 50, 310])
```


[[examples/Cyrcos_example_2.png]]


You'll notice the outer circle segment colors transition from solid-shaded to transparent, which could (for example) suggest the prevalence of a member in a group; the segments can be set to completely solid during creation by Cyrcos(fade_segments = False).

While simple lines may be useful for some figures, a major selling point of chord graphs is the connecting ribbons with varying end widths that quickly and clearly show the varying relationships between the members of groups. To change the previous chords to filled ribbons, Add_Paths requires two additional lists that give the ribbon start and end widths (once again, in degrees by default).


```python
cyr_plot = Cyrcos(5)
cyr_plot.Add_Paths([20, 115, 330, 160], [250, 195, 50, 310], [13, 2, 4, 15], [5, 8, 0.2, 28])
```


[[examples/Cyrcos_example_3.png]]


Now things are a bit more appealing! If certain relationships are more important to highlight than others, changing the order of the paths to draw can show them off - subsequent paths are drawn on top of the previous inputs. Swapping the first and last ribbons gives the following z-order:

(Note the easy text annotation with Add_Text, which takes a string and the x and y figure positions and transferring keyword arguments for text properties to matplotlib!)


```python
cyr_plot = Cyrcos(5)
cyr_plot.Add_Paths([160, 115, 330, 20], [310, 195, 50, 250], [15, 2, 4, 13], [28, 8, 0.2, 5])
cyr_plot.Add_Text("Note the\nchange in\nz-order!", x = 0.32, y = 0.57, color = "white")
```


[[examples/Cyrcos_example_4.png]]


The chord color is automatically set to the color of the originating group, but this can be easily changed using the color_by argument of Add_Paths. A list of colors (any color type accepted by matplotlib) of the same length as the number of paths will color each manually, or "end" to use the color of the ending segment:


```python
cyr_plot = Cyrcos(5)
cyr_plot.Add_Paths([160, 115, 330, 20], [310, 195, 50, 250], [15, 2, 4, 13], [28, 8, 0.2, 5], color_by = "end")
```


[[examples/Cyrcos_example_5.png]]



```python
cyr_plot = Cyrcos(5)
cyr_plot.Add_Paths([160, 115, 330, 20], [310, 195, 50, 250], [15, 2, 4, 13], [28, 8, 0.2, 5], color_by = ["black", "black", "red", "teal"])
```


[[examples/Cyrcos_example_6.png]]


Additionally, path color names can be intermixed with "start" or "end" to use the corresponding segments at will per path:


```python
cyr_plot = Cyrcos(5)
cyr_plot.Add_Paths([160, 115, 330, 20], [310, 195, 50, 250], [15, 2, 4, 13], [28, 8, 0.2, 5], color_by = ["black", "start", "yellow", "end"])
```


[[examples/Cyrcos_example_7.png]]


If you prefer to have all of the group segments touching, just change the gap_size setting to 0 during creation:


```python
cyr_plot = Cyrcos(5, gap_size = 0)
cyr_plot.Add_Paths([160, 115, 330, 20], [310, 195, 50, 250], [15, 2, 4, 13], [28, 8, 0.2, 5])
```


[[examples/Cyrcos_example_8.png]]


You may have noticed a potential problem with the above change, one that will be even more apparent if you decide to try out a wider gap size:


```python
cyr_plot = Cyrcos(5, gap_size = 25)
cyr_plot.Add_Paths([160, 115, 330, 20], [310, 195, 50, 250], [15, 2, 4, 13], [28, 8, 0.2, 5])
```


[[examples/Cyrcos_example_9.png]]


Now the problem with Add_Paths is clearer - using fixed angles and widths for our placement of connecting paths means that a change to the order or relative size of the group segments can break the figure completely.


Let's try out describing the members by their positions in a group instead, using Add_Paths_By_Segment! We'll add a few more ribbons for this faux dataset:


```python
#First describe the start and end segments for each path, starting from 0
starting_segments = [0, 0, 1, 4, 3, 2]
ending_segments = [1, 2, 3, 0, 4, 1]
#Next is the relative position of the path within a segment: 1.0 is the start of the segment, and 0.0 is the end
start_ratio_positions = [1.0, 1.0, 0.5, 0.5, 0.2, 0.16]
end_ratio_positions = [1.0, 0.9, 0.8, 0.3, 0.3, 0.85]
#Finally the start and end widths 
start_thicknesses = [0.1, 0.2, 0.05, 0.1, 0.3, 0.15]
end_thicknesses = [0.2, 0.3, 0.125, 0.2, 0.09, 0.1]

group_cyrcos = Cyrcos(5)
group_cyrcos.Add_Paths_By_Segment(starting_segments, ending_segments, start_ratio_positions, end_ratio_positions, start_thicknesses, end_thicknesses)
```


[[examples/Cyrcos_example_10.png]]


By describing paths in relative terms of their locations per segment, you can much more easily change the relative sizes in the figure without breaking the relationships:


```python
group_cyrcos = Cyrcos(5, gap_size = 0)
group_cyrcos.Add_Paths_By_Segment(starting_segments, ending_segments, start_ratio_positions, end_ratio_positions, start_thicknesses, end_thicknesses)
```


[[examples/Cyrcos_example_11.png]]



```python
group_cyrcos = Cyrcos(5, gap_size = 25)
group_cyrcos.Add_Paths_By_Segment(starting_segments, ending_segments, start_ratio_positions, end_ratio_positions, start_thicknesses, end_thicknesses)
```


[[examples/Cyrcos_example_12.png]]


Additional visual attributes for Cyrcos graphs:


```python
group_cyrcos = Cyrcos(5, gap_size = 20)
group_cyrcos.Add_Paths_By_Segment(starting_segments, ending_segments, start_ratio_positions, end_ratio_positions, start_thicknesses, end_thicknesses)
group_cyrcos.Add_Legend("Groups", shadow = True)
```


[[examples/Cyrcos_example_13.png]]



```python
group_cyrcos = Cyrcos(5, gap_size = 20)
group_cyrcos.Add_Paths_By_Segment(starting_segments, ending_segments, start_ratio_positions, end_ratio_positions, start_thicknesses, end_thicknesses)
group_cyrcos.Add_Legend("Groups", labels = ["Peripheral Blood", "Plasmablasts", "Memory B Cells", "Bone Marrow", "Plasma Cells"], shadow = True)
```


[[examples/Cyrcos_example_14.png]]

