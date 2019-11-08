# Workflow and troubleshooting

## Workflow

### Open files

1.  Open VSCode, open folder with git repo `mini_eggshell`
2.  Open Base.3dm (in git/design)
3.  Open `ur_online_control_gh_group_04.gh` in `mini_eggshell/ur_online_control/grasshopper`

### Settings (in grasshopper)

1.  Ping robot using the ping node in the grasshopper document.
2.  Set base if needed using `get_pose_cartesian` and copy the output to `base` node
3.  Measure distance from nozzle to bottom of plastic holder, input the result using the slider connected to the tool cluster.

### Input geometry

1.  Create points or frames using slicer in grasshopper document or loading from `ghdata` file using `Data Input` node. (If you get an error on the `Data Input` node right click and double check that it's loading from the right folder, then disable and enable it)
2.  Move the `safe_pt` point to a good location, best is above the geometry to be printed.
3.  Rotate planes if needed so that the tool is in a good position, including the safe\_pt plane.

### Run script

1.  Run the script using the bat-file located on your Desktop. `Win+D` shows the Desktop, which is a quick way to get to the `run_print.bat` file.

### Sharing and updating files

Changes to these files should be pushed at least at the end of day: \* `ur_online_control_gh_group_04.gh` \* `main_direct_send_group_04.py` \* `base.3dm` \* and any other files that's used in the printing

Other files not directly linked to running the robot should be shared using our Dropbox folder.

## Troubleshooting

### No clay coming out

-   Make sure the clay is wet.
-   Make sure that the top caps plastic seal is clean and that the top cap is screwed on hard.
-   Make sure that there's not dry clay in the end of the nozzle.

### Slow grasshopper document

-   Don't send too many planes, send a few using split list and then rerun it using the rest.
