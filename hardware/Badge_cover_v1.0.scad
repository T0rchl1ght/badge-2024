// Please feel free to remix or use this badge cover in any way that keeps with the limits of OpenTexus

// Depending on filament used, the dimensions might need to be adjusted due to shrinking or expanding

// Define constants for reusable values
cylinderOffset = 2;
cylinderYSpacing = 42;
cornerRadius = 5;

// Outer rectangle parameters
length = 86.00;
width = 66.70;
height = 12.00;

// Hole parameters
holeParams = [
    // Bottom Hole
    [4.82, 42.94, height], // Display Hole
    [27.50, 29.00, height],  // Body Hole
    [67.45 + 1.25, 63.70, 10.08], // Battery Hole
    [17.80, 58.00, 3.00],    // Top Hole
    [10.34, 49.00, 10.08],   // D5 Joystick Hole
    [17.00, 17.00, 2.00]     
];

// Function to create a rectangular hole
module rectangular_hole(x, y, z, len, wid, height) {
    translate([x, y, z])
        cube([len, wid, height]);
}

// Function to create a cylindrical hole
module cylindrical_hole(x, y, z, r, height) {
    translate([x, y, z])
        cylinder(r=r, h=height, $fn=100); // $fn sets the resolution of the cylinder
}

// Create the rounded rectangle using hull() for 3D rounded corners
module rounded_rectangle(len, wid, h, rad) {
    hull() {
        translate([rad, rad, 0])
            cylinder(h=h, r=rad);
        translate([len-rad, rad, 0])
            cylinder(h=h, r=rad);
        translate([rad, wid-rad, 0])
            cylinder(h=h, r=rad);
        translate([len-rad, wid-rad, 0])
            cylinder(h=h, r=rad);
    }
}

// Module for the left torus
module left_torus(r1, r2) {
    rotate_extrude(angle = 360)
        translate([r1, 0, 0])  // Keep original center for rotation
        circle(r = r2);
}

// Module for the right torus
module right_torus(r1, r2) {
    rotate_extrude(angle = 360)
        translate([r1, 0, 0])
        circle(r = r2);
}

difference() {
    // Create outer rounded rectangle
    rounded_rectangle(length, width, height, cornerRadius);

    // Create all holes using loop
    // BottomHole
    rectangular_hole(0, (width - holeParams[0][1]) / 2, 0, holeParams[0][0], holeParams[0][1], holeParams[0][2]); 
    // DisplayHole
    rectangular_hole(0, (width - holeParams[1][1]) / 2, 0, holeParams[1][0], holeParams[1][1], holeParams[1][2]); // BodyHole
    rectangular_hole((length - holeParams[2][0]) / 2, (width - holeParams[2][1]) / 2, height - holeParams[2][2], holeParams[2][0], holeParams[2][1], holeParams[2][2]); // BatteryHole
    rectangular_hole(length - holeParams[3][0] - 8.7, (width - holeParams[3][1]) / 2, 0, holeParams[3][0], holeParams[3][1], holeParams[3][2]); // TopHole
    rectangular_hole(length - holeParams[4][0], (width - holeParams[4][1]) / 2, height - holeParams[4][2], holeParams[4][0], holeParams[4][1], holeParams[4][2]); // D5JoystickHole
    rectangular_hole(length - 34.6 - holeParams[5][0], (width - holeParams[5][1]) / 2, 0, holeParams[5][0], holeParams[5][1], holeParams[5][2]);
    
    // Right screw hole
    cylindrical_hole(80, 4.5, 1.5, 1.55, 10.50);
    
    // Left screw hole
    cylindrical_hole(80, 62, 1.5, 1.55, 10.50);
}

// Right torus (Lanyard connector)
translate([length + 2, width - holeParams[4][1] / 5.2, height - holeParams[4][2] - 1.17]) {  // Move torus
    right_torus(r1 = 8 / 2, r2 = 1.56 / 2); 
}

// Left torus (Lanyard connector)
translate([length + 2, (width - holeParams[4][1]) / 2, height - holeParams[4][2] - 1.17]) {  // Move torus
    left_torus(r1 = 8 / 2, r2 = 1.56 / 2);
}
