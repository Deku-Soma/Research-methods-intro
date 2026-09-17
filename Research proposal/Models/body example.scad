$fn = 128;

// Dimensions
diameter = 10;
radius = diameter / 2;
height = 10;
wall = 0.5;

module shell() {
    difference() {
        cylinder(h = height, r = radius, center = false);
        
        // Hollow inside
        translate([0, 0, wall])
            cylinder(h = height, r = radius - wall, center = false);
        
        // Wheel arch front - shifted back slightly
        translate([radius - 0.1, 1.0, 0])
            rotate([0, 90, 0])
                scale([1.2, 1, 1])
                    cylinder(h = radius + 0.5, r = 2.5, center = true);
        
        // Wheel arch back - shifted back slightly
        translate([-radius + 0.1, 1.0, 0])
            rotate([0, 90, 0])
                scale([1.2, 1, 1])
                    cylinder(h = radius + 0.5, r = 2.5, center = true);

        // Caster wheel rectangular cutout at front base
        translate([-0.5, radius - wall - 8, 0])
            cube([1, 1.5, wall + 1S]);
    }
}

module mounting_cone() {
    cone_h = 2.5;
    base_r = 0.8;
    tip_r  = 0.05;

    cylinder(h = cone_h, r1 = base_r, r2 = tip_r, center = false);
}

module mounting_points() {
    inner_radius = radius - wall -0.3;
    angles = [45, 135, 225, 315];
    mount_z = height;

    for (a = angles) {
        translate([
            cos(a) * inner_radius,
            sin(a) * inner_radius,
            mount_z
        ])
        rotate([0, 180, a])
            mounting_cone();
    }
}

shell();
mounting_points();