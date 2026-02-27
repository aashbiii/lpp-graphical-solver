# LPP Graphical Solver

A fully interactive, browser-based **Linear Programming Problem (LPP) Solver** using the **Graphical Method** — built with pure HTML5, CSS3, and Vanilla JavaScript. No frameworks. No installation. Just open and solve.

---

## 🖥️ Demo Preview

> Dark-themed interface with real-time graph plotting, feasible region shading, corner point detection, and optimal solution highlighting.

---

## ✨ Features

- **Maximize or Minimize** any two-variable objective function Z = cx + dy
- **Dynamic constraints** — add or remove constraints (≤, ≥, =) on the fly
- **Auto non-negativity** — x ≥ 0, y ≥ 0 always enforced
- **Live graph rendering** via HTML5 Canvas API
- **Feasible region** drawn as a shaded convex polygon
- **Color-coded constraint lines** with a dynamic legend
- **Corner point enumeration** with Z evaluated at each vertex
- **Optimal point** highlighted in gold with iso-profit line overlay
- **Infeasibility detection** — graceful error if no feasible region exists
- **Fully client-side** — no server, no dependencies, no build step

---

## 🚀 Getting Started

### Run Locally
```bash
# Clone the repo
git clone https://github.com/aashbiii/lpp-graphical-solver.git

# Open in browser
cd lpp-graphical-solver
open index.html      # macOS
start index.html     # Windows
xdg-open index.html  # Linux
```

That's it. No `npm install`. No build tools.

### Or just open `index.html` directly in any modern browser.

---

## 🧮 How It Works

The solver follows the classical **Corner Point (Vertex) Method**:

1. **Parse inputs** — read objective coefficients and all constraints
2. **Find intersections** — compute pairwise intersections of all constraint lines, plus their x-axis and y-axis intercepts
3. **Filter feasible points** — keep only points satisfying every constraint (with tolerance 1e-9)
4. **Convex hull ordering** — sort surviving points angularly around their centroid
5. **Evaluate Z** — compute the objective function at every corner point
6. **Pick optimal** — select max or min Z; highlight all optimal points (handles degenerate cases)
7. **Render** — draw everything on the Canvas: region, lines, axes, points, results table

---

## 📐 Usage

**Step 1 — Choose optimization type:**
Select **Maximize** or **Minimize**.

**Step 2 — Enter objective function:**
```
Z = [c] x + [d] y
```

**Step 3 — Add constraints:**
```
[a] x + [b] y  ≤ / ≥ / =  [RHS]
```
Click **+ Add Constraint** to add more. Click **✕** to remove.

**Step 4 — Click Solve:**
The graph and results table update instantly.

---

## 📦 Default Example

| Component | Value |
|---|---|
| Objective | Maximize Z = 5x + 4y |
| Constraint 1 | 6x + 4y ≤ 24 |
| Constraint 2 | x + 2y ≤ 6 |
| Non-negativity | x ≥ 0, y ≥ 0 |

**Result:** Z = **21** at **(x, y) = (3, 1.5)**

---

## 🗂️ Project Structure

```
lpp-graphical-solver/
│
├── index.html        # Entire app (self-contained single file)
└── README.md         # This file
```

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| HTML5 | Structure and layout |
| CSS3 | Dark theme, animations, responsive grid |
| Vanilla JavaScript | Solver logic and math |
| HTML5 Canvas API | 2D graph rendering |
| Google Fonts (Syne + Space Mono) | Typography |

---

## ⚠️ Limitations

- Only supports **two decision variables** (x and y) — inherent to the graphical method
- Does not handle **unbounded feasible regions**
- Variables are **continuous** — no integer programming support
- Near-degenerate systems may have minor numerical precision issues

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

```bash
# Fork the repo, make your changes, then:
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
# Open a Pull Request
```

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

> Built with HTML5 · CSS3 · Vanilla JavaScript · Canvas API
