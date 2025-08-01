README.txt

Maintained by Will Gardner - wgardne9@vols.utk.edu

this Python script finds the amorphous fraction of a material by combining a fully crystalline and a fully amorphous data series (endmembers) using a weighing factor and curve fitting.  To find the amorphous fraction, both endmembers must be provided as well as the data in which the amorphous fraction needs to be found. From this, the amorphous fraction, a graph of the data and curve fit, and a comparison of the amorphous fractions will be provided. 

Running the script will open a window allowing for each data series to be imported. Once both endmembers and the data is imported, pressing 'Calculate Amorphous Fraction' will give the amorphous fraction and both graphs. The calculation will not run unless data is placed within each of these fields. The script should run with any data given, but for best results it can be useful to comment out any non-data lines using '#' at the beginning of the line. 

------------------------------------------------------------------------------------------------------

the following libraries must be imported if using the python script:

py -m pip install numpy
py -m pip install matplotlib
py -m pip install scipy

if using the executable, these should be included

------------------------------------------------------------------------------------------------------
Known Issues:

1. amorphous fraction rounding will not work if fully amorphous datafile is inserted for fraction calculation
--FIXED (7/24/25): problem with rounding, now works as intended

2. if fully crystalline datafile is input for fraction calculation, amorphous fraction will not be shown 
-- FIXED (7/24/25): if crystalline now input after another fraction, then it copies fraction of what came before (linked with 3.)

3. if the calculation datafiles are not put in increasing amorphous fraction order, files with lower amorphous fractions than the file that came before it will copy the amorphous fraction of the file before it. (connected to i_all and max)
-- FIXED (7/24/25): amorphous fraction no longer copies one before, works as intended

4. amorphous fraction graph can have annotations placed weirdly instead of directly next to point

5. Weighted Combination can provide amorphous fraction that provides lowest sum of squared differences, but is visually not as good as other fits (log scale maybe?)
------------------------------------------------------------------------------------------------------
Future Additions:

Allow amorphous fraction to be manually input and for resulting data to be plotted

Data initially cuts off at 0.5 for all data to prevent noise, could change to work dynamically based on data


------------------------------------------------------------------------------------------------------
Further information on this method of amorphous fraction calculation can be found at:

Include Citation Here