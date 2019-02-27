# Overview
Function for "clipping" or truncating surface geometry of a vascular tree at a desired diameter. Returns the measured volume of the truncated surface and outputs the truncated surface as a stl file.

## Usage
Specify in *measure_volume.py*
1. Desired truncation diameter(s)
2. Input surface filename (.stl)
3. Output surface filename (.vtp)
4. Output centerlines filename (.vtp)

If above files have been precomputed centerlines and surface generation can be skipped by setting precompute flag=1.

## Example
Example demonstrating truncation of vessel at 1mm (left) and 1.5mm (right)
![Alt Text](Figure.png)

## Requirements
* vtk-8.1.0
* vmtk-1.4.0

