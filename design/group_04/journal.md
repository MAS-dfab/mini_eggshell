# Journal

[Markdown cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## 2019-10-29

Working on design propsal and goals.

* Create column by simultaneous clay printing and concrete casting, with the structural goal of creating supports on the column for (horisontal) beams.
* Explore joint geometry, e.g. articulated joints (inspired by skeletal joints) or restrained joints.
* Exploration of clay overhangs while simultaneously casting.

End goal: 2 colums 1 beam

### Challenges
* clay formwork: max overhang for the support of the beam. Add micro-structure to the faces of the beam 
* structural purpose: opitmize interface column and beam 

### References
* <https://www.instagram.com/p/BizeScmlkPr/?utm_source=ig_web_copy_link>
* <https://www.instagram.com/p/BuGGrv2iORI/>

## 2019-10-30

### Desk crit with Joris and Nizar

Explained concept, joints of different kinds. Noise.

We talked about using axolotl and Emmanuelle's gh script to get the nice boolean operations of volumetric modeling.

Nizar was clear that the joint should be the focus, and noise/texture an addition.

Nizar sketched a column meeting a beam at top of column as a possible design. (Think of a T)

We talked about challenges in clay/concrete printing/casting, overhangs and underhangs, the interaction between concrete and clay.

### Discussion after

Explore joint typolgies, maybe focus on each.

We should branch (maybe) out to look at non console joints, with an imaginary (or real) second vertical element.

The three could be:
* the T-like assemblage
* a angled beam sticking into the column 
* a horisontal beam meeting the vertical column.

### References
* [Polymorf, people Anton worked together with on clayprinting](http://polymorf.se/)
* [Swallow's nest](https://tetov.se/swallows-nests/) and [LISp](https://tetov.se/lisp-non-planar-tile-fabrication/) two clay projects by Anton.
* [Weird wooden laser cut joints](https://gkirdeikis.wordpress.com/portfolio/aggregation-and-graph-based-modeling/) by Gediminias Kirdeikis

## 2019-10-31

Extruder assembly all day, setting up arduino to control stepper motor, heating block & fan (for the plastic extruders), and air pressure for the clay extruders.

## 2019-11-01

### Presentation

Main take-away was to go for some sort of bridging beam between two columns?

### First test prints

During afternoon-evening we printed three test prints, all starting with a circle at z0 and then a spiral. Layer height for the first two were 1 mm and the third was 2 mm.

Issues with "filament loading point" and when to turn on air pressure and extruder that needs to be resolved. Also weird last move during print; goes straight down destroying print.

Aluminium can too close to last joint of robot, need new holder.

## 2019-11-03

New holder for extruder ready to be printed tomorrow.

Added new tool assembly to gh script in ur_online_control, as well as the polymorph slicer cluster.

Created a test geometry we can print to explore overhangs and simultaneous casting.