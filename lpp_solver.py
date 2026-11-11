#!/usr/bin/env python3
"""
LPP Graphical Solver - Python Implementation
Author: Ashbi Saju
Course: MCA — Operations Research / Optimization Techniques

A two-variable Linear Programming Problem (LPP) solver using the Graphical Method (Corner Point Method).
Features:
- Solves Maximize / Minimize Z = c*x + d*y
- Arbitrary linear constraints (<=, >=, =) with non-negativity constraints (x >= 0, y >= 0)
- Corner point detection via pairwise line and axis intersections
- Feasible region polygon identification and angular sorting
- Optimal value detection (single and multiple alternative optima)
- Dark-themed Matplotlib visualization matching the web interface
- CLI arguments, programmatic API, and interactive terminal mode
"""

import sys
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


class LPPSolver:
    """Solves two-variable Linear Programming Problems using the Graphical Method."""

    COLORS = ['#00f5c4', '#ff6b6b', '#ffd93d', '#a78bfa', '#60a5fa', '#f97316', '#34d399']

    def __init__(self, obj_c=5.0, obj_d=4.0, opt_type='max'):
        """
        Initialize the LPP Solver.
        :param obj_c: Coefficient of x in the objective function
        :param obj_d: Coefficient of y in the objective function
        :param opt_type: 'max' for Maximization or 'min' for Minimization
        """
        self.obj_c = float(obj_c)
        self.obj_d = float(obj_d)
        self.opt_type = opt_type.lower().strip()
        if self.opt_type not in ('max', 'min'):
            raise ValueError("opt_type must be either 'max' or 'min'")
        self.constraints = []

    def add_constraint(self, a, b, sign, rhs):
        """
        Adds a linear constraint of the form: a*x + b*y [<= | >= | =] rhs
        """
        sign_clean = sign.strip().replace('≤', '<=').replace('≥', '>=')
        if sign_clean not in ('<=', '>=', '='):
            raise ValueError(f"Invalid constraint operator: {sign}. Use '<=', '>=', or '='")
        self.constraints.append({
            'a': float(a),
            'b': float(b),
            'sign': sign_clean,
            'rhs': float(rhs)
        })

    def _line_y(self, a, b, rhs, x):
        """Returns y for a given x on line a*x + b*y = rhs."""
        if abs(b) < 1e-12:
            return None
        return (rhs - a * x) / b

    def _line_x(self, a, b, rhs, y):
        """Returns x for a given y on line a*x + b*y = rhs."""
        if abs(a) < 1e-12:
            return None
        return (rhs - b * y) / a

    def _intersect(self, c1, c2):
        """Computes the intersection point between two linear lines."""
        a1, b1, r1 = c1['a'], c1['b'], c1['rhs']
        a2, b2, r2 = c2['a'], c2['b'], c2['rhs']
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-12:
            return None  # Parallel or collinear lines
        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det
        return (x, y)

    def _satisfies(self, x, y, c, tol=1e-8):
        """Checks if point (x, y) satisfies a specific constraint."""
        lhs = c['a'] * x + c['b'] * y
        if c['sign'] == '<=':
            return lhs <= c['rhs'] + tol
        elif c['sign'] == '>=':
            return lhs >= c['rhs'] - tol
        elif c['sign'] == '=':
            return abs(lhs - c['rhs']) <= tol
        return False

    def is_feasible(self, x, y, tol=1e-8):
        """Checks if point (x, y) is in the first quadrant and satisfies all constraints."""
        if x < -tol or y < -tol:
            return False
        return all(self._satisfies(x, y, c, tol) for c in self.constraints)

    def get_corner_points(self):
        """Identifies all candidate corner points and filters for feasibility."""
        candidates = []
        n = len(self.constraints)

        # 1. Origin
        candidates.append((0.0, 0.0))

        # 2. Axis intercepts
        for c in self.constraints:
            if abs(c['a']) > 1e-12:
                x_val = c['rhs'] / c['a']
                if x_val >= -1e-8:
                    candidates.append((max(0.0, x_val), 0.0))
            if abs(c['b']) > 1e-12:
                y_val = c['rhs'] / c['b']
                if y_val >= -1e-8:
                    candidates.append((0.0, max(0.0, y_val)))

        # 3. Pairwise line intersections
        for i in range(n):
            for j in range(i + 1, n):
                p = self._intersect(self.constraints[i], self.constraints[j])
                if p is not None:
                    candidates.append(p)

            # Constraint intersection with x-axis (y = 0)
            ix = self._line_x(self.constraints[i]['a'], self.constraints[i]['b'], self.constraints[i]['rhs'], 0.0)
            if ix is not None and not math.isnan(ix):
                candidates.append((ix, 0.0))

            # Constraint intersection with y-axis (x = 0)
            iy = self._line_y(self.constraints[i]['a'], self.constraints[i]['b'], self.constraints[i]['rhs'], 0.0)
            if iy is not None and not math.isnan(iy):
                candidates.append((0.0, iy))

        # Deduplicate and filter for feasibility
        unique_feasible = []
        for x, y in candidates:
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            cx = max(0.0, round(x, 7))
            cy = max(0.0, round(y, 7))
            if self.is_feasible(cx, cy):
                if not any(abs(cx - ux) < 1e-6 and abs(cy - uy) < 1e-6 for ux, uy in unique_feasible):
                    unique_feasible.append((cx, cy))

        return unique_feasible

    def order_convex_hull(self, points):
        """Orders points counter-clockwise around their geometric centroid."""
        if len(points) < 3:
            return points
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        return sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    def solve(self):
        """
        Solves the LPP by evaluating Z at every feasible corner point.
        Returns a dictionary containing corner points, evaluations, and optimal solution.
        """
        feasible_points = self.get_corner_points()
        if not feasible_points:
            return {
                'status': 'Infeasible',
                'corner_points': [],
                'evaluations': [],
                'optimal_value': None,
                'optimal_points': []
            }

        evaluations = []
        for x, y in feasible_points:
            z = self.obj_c * x + self.obj_d * y
            evaluations.append({'x': x, 'y': y, 'z': z})

        if self.opt_type == 'max':
            opt_val = max(e['z'] for e in evaluations)
        else:
            opt_val = min(e['z'] for e in evaluations)

        optimal_points = [
            (e['x'], e['y']) for e in evaluations if abs(e['z'] - opt_val) < 1e-6
        ]

        ordered_hull = self.order_convex_hull(feasible_points)

        return {
            'status': 'Optimal',
            'corner_points': feasible_points,
            'hull_points': ordered_hull,
            'evaluations': evaluations,
            'optimal_value': opt_val,
            'optimal_points': optimal_points
        }

    def print_summary(self, result):
        """Prints a structured ASCII report of the LPP solution."""
        print("=" * 65)
        print("       LPP GRAPHICAL SOLVER (CORNER POINT METHOD)       ")
        print("=" * 65)
        opt_str = "Maximize" if self.opt_type == 'max' else "Minimize"
        print(f"Objective Function : {opt_str} Z = {self.obj_c}*x + {self.obj_d}*y")
        print("Subject to Constraints:")
        for idx, c in enumerate(self.constraints, 1):
            sign_sym = '<=' if c['sign'] == '<=' else ('>=' if c['sign'] == '>=' else '=')
            print(f"  ({idx}) {c['a']:>4.1f}*x + {c['b']:>4.1f}*y {sign_sym} {c['rhs']:>5.1f}")
        print("  (N)    x >= 0,  y >= 0 (Non-negativity)")
        print("-" * 65)

        if result['status'] != 'Optimal':
            print("Status : INFEASIBLE (No points satisfy all constraints simultaneously)")
            print("=" * 65)
            return

        print(f"Status : OPTIMAL SOLUTION FOUND ({len(result['corner_points'])} Feasible Corner Points)")
        print("-" * 65)
        print(f"{'Corner Point (x, y)':<25} | {'Z = ' + str(self.obj_c) + 'x + ' + str(self.obj_d) + 'y':<20} | Status")
        print("-" * 65)

        for item in sorted(result['evaluations'], key=lambda e: (e['x'], e['y'])):
            is_opt = any(abs(item['x'] - ox) < 1e-6 and abs(item['y'] - oy) < 1e-6 for ox, oy in result['optimal_points'])
            pt_str = f"({item['x']:.2f}, {item['y']:.2f})"
            z_str = f"{item['z']:.4f}"
            status_str = "★ OPTIMAL" if is_opt else "Feasible"
            print(f"{pt_str:<25} | {z_str:<20} | {status_str}")

        print("=" * 65)
        print(f"Optimal Value (Z*) : {result['optimal_value']:.4f}")
        for op in result['optimal_points']:
            print(f"Optimal Point (x*, y*) : x = {op[0]:.4f}, y = {op[1]:.4f}")
        if len(result['optimal_points']) > 1:
            print("Note: Multiple alternative optimal solutions exist along the boundary segment.")
        print("=" * 65)

    def plot(self, result, save_path=None, show=True):
        """
        Renders the graphical method plot using Matplotlib with dark cyberpunk aesthetics.
        """
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0a0a0f')
        ax.set_facecolor('#12121a')

        # Determine plotting bounds
        all_x = [p[0] for p in result.get('corner_points', [])]
        all_y = [p[1] for p in result.get('corner_points', [])]
        for c in self.constraints:
            if abs(c['a']) > 1e-12:
                all_x.append(abs(c['rhs'] / c['a']))
            if abs(c['b']) > 1e-12:
                all_y.append(abs(c['rhs'] / c['b']))

        max_x = max(max(all_x) * 1.25, 10.0) if all_x else 10.0
        max_y = max(max(all_y) * 1.25, 10.0) if all_y else 10.0

        x_vals = np.linspace(0, max_x, 500)

        # 1. Feasible Region Polygon
        if result['status'] == 'Optimal' and len(result['hull_points']) >= 3:
            hull_arr = np.array(result['hull_points'])
            polygon = Polygon(hull_arr, closed=True,
                              facecolor='#00f5c4', alpha=0.15,
                              edgecolor='#00f5c4', linewidth=2,
                              label='Feasible Region')
            ax.add_patch(polygon)

        # 2. Plot Constraint Boundary Lines
        for idx, con in enumerate(self.constraints):
            color = self.COLORS[idx % len(self.COLORS)]
            sign_sym = '≤' if con['sign'] == '<=' else ('≥' if con['sign'] == '>=' else '=')
            label = f"{con['a']:g}x + {con['b']:g}y {sign_sym} {con['rhs']:g}"

            if abs(con['b']) > 1e-12:
                y_line = (con['rhs'] - con['a'] * x_vals) / con['b']
                valid_mask = (y_line >= 0) & (y_line <= max_y * 1.1)
                ax.plot(x_vals[valid_mask], y_line[valid_mask],
                        linestyle='--', color=color, linewidth=2, label=label)
            else:
                # Vertical line a*x = rhs -> x = rhs / a
                vx = con['rhs'] / con['a']
                if 0 <= vx <= max_x:
                    ax.axvline(x=vx, linestyle='--', color=color, linewidth=2, label=label)

        # 3. Corner Points & Optimal Highlight
        if result['status'] == 'Optimal':
            for e in result['evaluations']:
                is_opt = any(abs(e['x'] - ox) < 1e-6 and abs(e['y'] - oy) < 1e-6 for ox, oy in result['optimal_points'])
                if is_opt:
                    ax.plot(e['x'], e['y'], marker='o', markersize=10,
                            color='#ffd93d', markeredgecolor='#ffffff', markeredgewidth=2, zorder=5)
                    # Outer halo ring
                    ax.plot(e['x'], e['y'], marker='o', markersize=18,
                            color='#ffd93d', fillstyle='none', markeredgewidth=2, zorder=5)
                    ax.text(e['x'] + max_x * 0.02, e['y'] + max_y * 0.02,
                            f"Optimal ({e['x']:.2g}, {e['y']:.2g})\nZ* = {e['z']:.2g}",
                            color='#ffd93d', fontsize=10, fontweight='bold', zorder=6)
                else:
                    ax.plot(e['x'], e['y'], marker='o', markersize=6,
                            color='#e0e0f0', alpha=0.8, zorder=4)
                    ax.text(e['x'] + max_x * 0.015, e['y'] + max_y * 0.015,
                            f"({e['x']:.2g}, {e['y']:.2g})",
                            color='#a0a0c0', fontsize=8, zorder=4)

            # 4. Iso-profit / Iso-cost objective function line through optimal point
            if result['optimal_points']:
                opt_z = result['optimal_value']
                if abs(self.obj_d) > 1e-12:
                    y_iso = (opt_z - self.obj_c * x_vals) / self.obj_d
                    valid_iso = (y_iso >= 0) & (y_iso <= max_y * 1.1)
                    ax.plot(x_vals[valid_iso], y_iso[valid_iso],
                            color='#ffd93d', linestyle=':', linewidth=2.2, alpha=0.8,
                            label=f'Iso-Line (Z = {opt_z:.2g})')

        # Axes & Styling
        ax.set_xlim(-max_x * 0.02, max_x)
        ax.set_ylim(-max_y * 0.02, max_y)
        ax.axhline(0, color='#5a5a7a', linewidth=1.5)
        ax.axvline(0, color='#5a5a7a', linewidth=1.5)

        opt_str = "Maximize" if self.opt_type == 'max' else "Minimize"
        ax.set_title(f"LPP Graphical Solution: {opt_str} Z = {self.obj_c}x + {self.obj_d}y",
                     color='#00f5c4', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel("Decision Variable (x)", color='#e0e0f0', fontsize=11, labelpad=8)
        ax.set_ylabel("Decision Variable (y)", color='#e0e0f0', fontsize=11, labelpad=8)

        ax.tick_params(colors='#e0e0f0')
        for spine in ax.spines.values():
            spine.set_color('#1e1e2e')

        ax.grid(True, linestyle='-', color='#ffffff', alpha=0.06)
        legend = ax.legend(loc='upper right', facecolor='#12121a', edgecolor='#1e1e2e',
                           labelcolor='#e0e0f0', fontsize=9)
        legend.get_frame().set_alpha(0.9)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
            print(f"Saved plot to '{save_path}'")

        if show:
            plt.show()
        else:
            plt.close()


def main():
    parser = argparse.ArgumentParser(description="Two-Variable LPP Graphical Solver (Corner Point Method)")
    parser.add_argument("--opt", type=str, default="max", choices=["max", "min"], help="Optimization direction (max or min)")
    parser.add_argument("--obj", type=float, nargs=2, default=[5.0, 4.0], metavar=('C', 'D'), help="Objective function coefficients for Z = c*x + d*y")
    parser.add_argument("--constraint", "-c", type=str, action="append", help="Constraint in format 'a b sign rhs' e.g. '6 4 <= 24'")
    parser.add_argument("--plot", action="store_true", help="Display Matplotlib graphical plot")
    parser.add_argument("--save", type=str, default=None, help="Save graphical plot to an image file (e.g. solution.png)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive step-by-step console wizard")

    args = parser.parse_args()

    if args.interactive:
        print("\n--- LPP Graphical Solver Interactive Mode ---")
        opt_choice = input("Optimization type (max/min) [max]: ").strip().lower() or 'max'
        c_val = float(input("Objective coefficient for x (c): ").strip() or 5)
        d_val = float(input("Objective coefficient for y (d): ").strip() or 4)

        solver = LPPSolver(obj_c=c_val, obj_d=d_val, opt_type=opt_choice)

        num_c = int(input("How many constraints to add? [2]: ").strip() or 2)
        print("Enter constraints (e.g., '6 4 <= 24'):")
        for i in range(num_c):
            raw = input(f"  Constraint #{i+1}: ").strip()
            parts = raw.split()
            if len(parts) == 4:
                solver.add_constraint(parts[0], parts[1], parts[2], parts[3])
            else:
                print(f"  Skipping invalid format: {raw}. Expected 'a b <= rhs'")

        result = solver.solve()
        solver.print_summary(result)
        save_file = input("Save plot image filename (press Enter to skip): ").strip() or None
        solver.plot(result, save_path=save_file, show=True)
        return

    # Default or CLI arguments
    solver = LPPSolver(obj_c=args.obj[0], obj_d=args.obj[1], opt_type=args.opt)

    if args.constraint:
        for con_str in args.constraint:
            parts = con_str.strip().split()
            if len(parts) == 4:
                solver.add_constraint(parts[0], parts[1], parts[2], parts[3])
            else:
                print(f"Warning: Invalid constraint format '{con_str}'. Expected 'a b <= rhs'")
    else:
        # Default MCA classroom example
        solver.add_constraint(6, 4, '<=', 24)
        solver.add_constraint(1, 2, '<=', 6)

    result = solver.solve()
    solver.print_summary(result)

    if args.plot or args.save:
        solver.plot(result, save_path=args.save, show=args.plot)


if __name__ == "__main__":
    main()
