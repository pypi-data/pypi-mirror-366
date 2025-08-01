use anyhow::{anyhow, Context, Result};
use crossbeam::thread;

use crate::io::input::{Contour, ContourPoint, Record};
use crate::io::Geometry;
use crate::processing::comparison::prepare_geometries_comparison;
use crate::processing::contours::{align_frames_in_geometry, hausdorff_distance, AlignLog};
use crate::processing::geometries::GeometryPair;
use crate::processing::process_case::process_case;

use crate::io::output::write_obj_mesh_without_uv;

pub fn geometry_from_array_rs(
    contours: Vec<Contour>,
    walls: Vec<Contour>,
    reference_point: ContourPoint,
    steps: usize,
    range_deg: f64,
    image_center: (f64, f64),
    radius: f64,
    n_points: u32,
    label: &str,
    records: Option<Vec<Record>>,
    delta: f64,
    max_rounds: usize,
    diastole: bool,
    sort: bool,
    write_obj: bool,
    output_path: &str,
) -> Result<(Geometry, Vec<AlignLog>), Box<dyn std::error::Error>> {
    let mut contours = contours;
    let label = label.to_string();

    // Build catheter contours, propagating any errors
    let mut catheter = if n_points == 0 {
        Vec::new()
    } else {
        Contour::create_catheter_contours(
            &contours
                .iter()
                .flat_map(|c| c.points.clone())
                .collect::<Vec<_>>(),
            image_center,
            radius,
            n_points,
        )?
    };

    // Initial geometry setup, possibly reordering by records
    let geometry = if let Some(recs) = records.as_ref() {
        let mut z_coords: Vec<f64> = contours.iter().map(|c| c.centroid.2).collect();
        z_coords.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

        Geometry::reorder_contours(&mut contours, recs, diastole, &z_coords);
        catheter.sort_by_key(|c| c.id);

        Geometry {
            contours,
            catheter,
            walls,
            reference_point,
            label: label.clone(),
        }
    } else {
        Geometry {
            contours,
            catheter,
            walls,
            reference_point,
            label,
        }
    };

    // Optionally align and refine ordering
    let (mut geometry, logs) = if sort {
        let (interim, _) = align_frames_in_geometry(geometry, steps, range_deg);
        let refined = refine_ordering(interim, delta, max_rounds);
        align_frames_in_geometry(refined, steps, range_deg)
    } else {
        align_frames_in_geometry(geometry, steps, range_deg)
    };
    
    geometry = if geometry.walls.is_empty() {
        crate::processing::walls::create_wall_geometry(&geometry, false)
    } else {
        geometry
    };

    geometry = geometry.smooth_contours();

    if write_obj {
        let filename_cont = format!("{}/mesh_000_single.obj", output_path);
        let filename_walls = format!("{}/wall_000_single.obj", output_path);
        let filename_cath = format!("{}/catheter_000_single.obj", output_path);
        write_obj_mesh_without_uv(
            &geometry.contours,
            &filename_cont,
            "mesh_000_single.mtl",
        )?;
        write_obj_mesh_without_uv(&geometry.walls, &filename_walls, "wall_000_single.mtl")?;
        write_obj_mesh_without_uv(
            &geometry.catheter,
            &filename_cath,
            "catheter_000_single.mtl",
        )?;
    }

    Ok((geometry, logs))
}

pub fn refine_ordering(mut geom: Geometry, delta: f64, max_rounds: usize) -> Geometry {
    let mut last_order = Vec::new();
    for _round in 0..max_rounds {
        let cost = build_cost_matrix(&geom.contours, delta);
        let order = if geom.contours.len() <= 15 {
            held_karp(&cost)
        } else {
            two_opt(&cost, 500)
        };
        if order == last_order {
            break;
        }
        last_order = order.clone();
        geom = reorder_geometry(geom, &order);
    }
    geom
}

fn reorder_geometry(mut geom: Geometry, new_order: &[usize]) -> Geometry {
    let reordered_contours = new_order
        .iter()
        .map(|&i| geom.contours[i].clone())
        .collect();
    let reordered_catheter = new_order
        .iter()
        .map(|&i| geom.catheter[i].clone())
        .collect();
    geom.contours = reordered_contours;
    geom.catheter = reordered_catheter;
    geom
}

fn build_cost_matrix(contours: &[Contour], delta: f64) -> Vec<Vec<f64>> {
    let n = contours.len();
    let mut cost = vec![vec![0.0; n]; n];
    for i in 0..n {
        for j in 0..n {
            if i == j {
                cost[i][j] = 0.0;
            } else {
                let h = hausdorff_distance(&contours[i].points, &contours[j].points);
                let jump = (contours[i].id as i32 - contours[j].id as i32).abs() as f64;
                cost[i][j] = h + delta * jump;
            }
        }
    }
    cost
}

/// Solve the shortest Hamiltonian path from 0 through all nodes exactly.
fn held_karp(cost: &[Vec<f64>]) -> Vec<usize> {
    let n = cost.len();
    let full_mask = (1 << n) - 1;
    // dp[mask][j] = best cost to start at 0, visit mask, end at j
    let mut dp = vec![vec![f64::INFINITY; n]; 1 << n];
    let mut parent = vec![vec![None; n]; 1 << n];

    dp[1 << 0][0] = 0.0;
    for mask in 1..=full_mask {
        if (mask & 1) == 0 {
            continue;
        } // must always include node 0
        for j in 0..n {
            if mask & (1 << j) == 0 {
                continue;
            }
            if j == 0 && mask != (1 << 0) {
                continue;
            }
            let prev_mask = mask ^ (1 << j);
            for i in 0..n {
                if prev_mask & (1 << i) == 0 {
                    continue;
                }
                let cost_ij = cost[i][j];
                let cand = dp[prev_mask][i] + cost_ij;
                if cand < dp[mask][j] {
                    dp[mask][j] = cand;
                    parent[mask][j] = Some(i);
                }
            }
        }
    }
    // Pick endpoint with minimal cost
    let (mut end, _) = (1..n)
        .map(|j| (j, dp[full_mask][j]))
        .min_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
        .unwrap();
    // Reconstruct path
    let mut order = Vec::with_capacity(n);
    let mut mask = full_mask;
    while let Some(p) = parent[mask][end] {
        order.push(end);
        mask ^= 1 << end;
        end = p;
    }
    order.push(0);
    order.reverse();
    order
}

/// Start with identity ordering, then do repeated 2‑opt swaps
fn two_opt(cost: &[Vec<f64>], max_iters: usize) -> Vec<usize> {
    let n = cost.len();
    let mut order: Vec<usize> = (0..n).collect();

    let mut best_impr = true;
    for _ in 0..max_iters {
        if !best_impr {
            break;
        }
        best_impr = false;
        for a in 1..n - 1 {
            for b in a + 1..n {
                // compute delta cost of reversing order[a..=b]
                let i = order[a - 1];
                let j = order[a];
                let k = order[b];
                let l = if b + 1 < n { order[b + 1] } else { usize::MAX };

                let before = cost[i][j] + if l != usize::MAX { cost[k][l] } else { 0.0 };
                let after = cost[i][k] + if l != usize::MAX { cost[j][l] } else { 0.0 };
                if after + 1e-9 < before {
                    order[a..=b].reverse();
                    best_impr = true;
                }
            }
        }
    }
    order
}

fn geometry_pair_from_array_rs(
    geometry_dia: Geometry,
    geometry_sys: Geometry,
    steps_best_rotation: usize,
    range_rotation_deg: f64,
    image_center: (f64, f64),
    radius: f64,
    n_points: u32,
) -> anyhow::Result<(GeometryPair, (Vec<AlignLog>, Vec<AlignLog>))> {
    let mut catheters_dia = if geometry_dia.catheter.is_empty() {
        Contour::create_catheter_contours(
            &geometry_dia
                .contours
                .iter()
                .flat_map(|c| c.points.clone())
                .collect::<Vec<_>>(),
            image_center,
            radius,
            n_points,
        )?
    } else {
        geometry_dia.catheter.clone()
    };
    let mut catheters_sys = if geometry_dia.catheter.is_empty() {
        Contour::create_catheter_contours(
            &geometry_sys
                .contours
                .iter()
                .flat_map(|c| c.points.clone())
                .collect::<Vec<_>>(),
            image_center,
            radius,
            n_points,
        )?
    } else {
        geometry_sys.catheter.clone()
    };

    // Ensure catheter contour are sorted by ID in same manner as contours
    catheters_dia.sort_by_key(|c| c.id);
    catheters_sys.sort_by_key(|c| c.id);

    // Insert in Geometry
    let geometry_dia = Geometry {
        contours: geometry_dia.contours,
        catheter: catheters_dia,
        walls: geometry_dia.walls,
        reference_point: geometry_dia.reference_point,
        label: "Diastole".to_string(),
    };
    let geometry_sys = Geometry {
        contours: geometry_sys.contours,
        catheter: catheters_sys,
        walls: geometry_sys.walls,
        reference_point: geometry_sys.reference_point,
        label: "Systole".to_string(),
    };

    let mut geometries = GeometryPair {
        dia_geom: geometry_dia,
        sys_geom: geometry_sys,
    };
    geometries = geometries.adjust_z_coordinates();

    let (mut geometries, (dia_logs, sys_logs)) =
        geometries.process_geometry_pair(steps_best_rotation, range_rotation_deg, true);
    geometries = geometries.trim_geometries_same_length();
    geometries = geometries.thickness_adjustment();

    let dia_geom = geometries.dia_geom;
    let dia_geom = dia_geom.smooth_contours();
    let sys_geom = geometries.sys_geom;
    let sys_geom = sys_geom.smooth_contours();

    Ok((
        GeometryPair {
            dia_geom: dia_geom,
            sys_geom: sys_geom,
        },
        (dia_logs, sys_logs),
    ))
}

pub fn from_array_full_rs(
    rest_geometry_dia: Geometry,
    rest_geometry_sys: Geometry,
    stress_geometry_dia: Geometry,
    stress_geometry_sys: Geometry,
    steps_best_rotation: usize,
    range_rotation_deg: f64,
    interpolation_steps: usize,
    rest_output_path: &str,
    stress_output_path: &str,
    diastole_output_path: &str,
    systole_output_path: &str,
    image_center: (f64, f64),
    radius: f64,
    n_points: u32,
) -> anyhow::Result<(
    (GeometryPair, GeometryPair, GeometryPair, GeometryPair),
    (Vec<AlignLog>, Vec<AlignLog>, Vec<AlignLog>, Vec<AlignLog>),
)> {
    let result = thread::scope(
        |s| -> Result<(
            GeometryPair,
            GeometryPair,
            GeometryPair,
            GeometryPair,
            Vec<AlignLog>,
            Vec<AlignLog>,
            Vec<AlignLog>,
            Vec<AlignLog>,
        )> {
            // REST thread
            let rest_handle = s.spawn(|_| -> anyhow::Result<_> {
                let (mut geom, (dia_logs, sys_logs)) = geometry_pair_from_array_rs(
                    rest_geometry_dia,
                    rest_geometry_sys,
                    steps_best_rotation,
                    range_rotation_deg,
                    image_center,
                    radius,
                    n_points,
                )
                .context("create_geometry_pair(rest) failed")?;
                geom = process_case("rest", geom, rest_output_path, interpolation_steps)
                    .context("process_case(rest) failed")?;
                Ok((geom, dia_logs, sys_logs))
            });

            // STRESS thread
            let stress_handle = s.spawn(|_| -> anyhow::Result<_> {
                let (mut geom, (dia_logs_stress, sys_logs_stress)) = geometry_pair_from_array_rs(
                    stress_geometry_dia,
                    stress_geometry_sys,
                    steps_best_rotation,
                    range_rotation_deg,
                    image_center,
                    radius,
                    n_points,
                )
                .context("create_geometry_pair(stress) failed")?;
                geom = process_case("stress", geom, stress_output_path, interpolation_steps)
                    .context("process_case(stress) failed")?;
                Ok((geom, dia_logs_stress, sys_logs_stress))
            });

            // Join REST & STRESS
            let (rest_pair, dia_logs, sys_logs) = rest_handle.join().unwrap()?;
            let (stress_pair, dia_logs_stress, sys_logs_stress) = stress_handle.join().unwrap()?;

            // Prepare diastolic & systolic geometry pairs
            let (dia_pair, sys_pair) =
                prepare_geometries_comparison(rest_pair.clone(), stress_pair.clone());

            // DIASTOLIC thread
            let dia_handle = s.spawn(move |_| {
                process_case(
                    "diastolic",
                    dia_pair.clone(),
                    diastole_output_path,
                    interpolation_steps,
                )
                .context("process_case(diastolic) failed")
            });

            // SYSTOLIC thread
            let sys_handle = s.spawn(move |_| {
                process_case(
                    "systolic",
                    sys_pair.clone(),
                    systole_output_path,
                    interpolation_steps,
                )
                .context("process_case(systolic) failed")
            });

            // Join DIASTOLIC & SYSTOLIC
            let dia_geom = dia_handle.join().unwrap()?;
            let sys_geom = sys_handle.join().unwrap()?;

            Ok((
                rest_pair,
                stress_pair,
                dia_geom,
                sys_geom,
                dia_logs,
                sys_logs,
                dia_logs_stress,
                sys_logs_stress,
            ))
        },
    )
    .map_err(|panic| anyhow!("Parallel processing threads panicked: {:?}", panic))?;

    let (
        rest_geom,
        stress_geom,
        dia_geom,
        sys_geom,
        dia_logs,
        sys_logs,
        dia_logs_stress,
        sys_logs_stress,
    ) = result?;

    Ok((
        (rest_geom, stress_geom, dia_geom, sys_geom),
        (dia_logs, sys_logs, dia_logs_stress, sys_logs_stress),
    ))
}

pub fn from_array_doublepair_rs(
    rest_geometry_dia: Geometry,
    rest_geometry_sys: Geometry,
    stress_geometry_dia: Geometry,
    stress_geometry_sys: Geometry,
    steps_best_rotation: usize,
    range_rotation_deg: f64,
    interpolation_steps: usize,
    rest_output_path: &str,
    stress_output_path: &str,
    image_center: (f64, f64),
    radius: f64,
    n_points: u32,
) -> Result<(
    (GeometryPair, GeometryPair),
    (Vec<AlignLog>, Vec<AlignLog>, Vec<AlignLog>, Vec<AlignLog>),
)> {
    let result = thread::scope(
        |s| -> Result<(
            GeometryPair,
            GeometryPair,
            Vec<AlignLog>,
            Vec<AlignLog>,
            Vec<AlignLog>,
            Vec<AlignLog>,
        )> {
            // REST thread
            let rest_handle = s.spawn(|_| -> anyhow::Result<_> {
                let (geom_rest, (dia_log, sys_log)) = geometry_pair_from_array_rs(
                    rest_geometry_dia,
                    rest_geometry_sys,
                    steps_best_rotation,
                    range_rotation_deg,
                    image_center,
                    radius,
                    n_points,
                )
                .context("create_geometry_pair(rest) failed")?;

                let processed_rest =
                    process_case("rest", geom_rest, rest_output_path, interpolation_steps)
                        .context("process_case(rest) failed")?;

                Ok((processed_rest, dia_log, sys_log))
            });

            // STRESS thread
            let stress_handle = s.spawn(|_| -> anyhow::Result<_> {
                let (geom_stress, (dia_logs_stress, sys_logs_stress)) =
                    geometry_pair_from_array_rs(
                        stress_geometry_dia,
                        stress_geometry_sys,
                        steps_best_rotation,
                        range_rotation_deg,
                        image_center,
                        radius,
                        n_points,
                    )
                    .context("create_geometry_pair(stress) failed")?;

                let processed_stress = process_case(
                    "stress",
                    geom_stress,
                    stress_output_path,
                    interpolation_steps,
                )
                .context("process_case(stress) failed")?;

                Ok((processed_stress, dia_logs_stress, sys_logs_stress))
            });
            // Join threads & propagate any processing errors
            let (rest_geom_pair, dia_logs, sys_logs) = rest_handle.join().unwrap()?;
            let (stress_geom_pair, dia_logs_stress, sys_logs_stress) =
                stress_handle.join().unwrap()?;

            Ok((
                rest_geom_pair,
                stress_geom_pair,
                dia_logs,
                sys_logs,
                dia_logs_stress,
                sys_logs_stress,
            ))
        },
    )
    .map_err(|panic_payload| {
        anyhow!("Parallel processing threads panicked: {:?}", panic_payload)
    })?;

    let (rest_geom, stress_geom, dia_logs, sys_logs, dia_logs_stress, sys_logs_stress) = result?;
    Ok((
        (rest_geom, stress_geom),
        (dia_logs, sys_logs, dia_logs_stress, sys_logs_stress),
    ))
}

pub fn from_array_singlepair_rs(
    rest_geometry_dia: Geometry,
    rest_geometry_sys: Geometry,
    output_path: &str,
    steps_best_rotation: usize,
    range_rotation_deg: f64,
    interpolation_steps: usize,
    image_center: (f64, f64),
    radius: f64,
    n_points: u32,
) -> Result<(GeometryPair, (Vec<AlignLog>, Vec<AlignLog>))> {
    // Build the raw pair
    let (geom_pair, (dia_logs, sys_logs)) = geometry_pair_from_array_rs(
        rest_geometry_dia,
        rest_geometry_sys,
        steps_best_rotation,
        range_rotation_deg,
        image_center,
        radius,
        n_points,
    )
    .context("create_geometry_pair(single) failed")?;

    // Process it (e.g. align, interpolate, write meshes)
    let processed_pair = process_case("single", geom_pair, output_path, interpolation_steps)
        .context("process_case(single) failed")?;

    Ok((processed_pair, (dia_logs, sys_logs)))
}
