# RoboCup SSL Honours Report: Project To-Do List

## Phase 1: Supervisor Feedback (Must-Fix) — Status: COMPLETED
- [x] **Reframe as a Simulation-Based Feasibility Study**
  - [x] Retitle document to *Bridging the Cost Barrier: A Simulation-Based Feasibility Study of a 3D-Printed ROS 2 Platform for RoboCup SSL Benchmarking* in `thesis.tex`.
  - [x] Remove and reword all physical claims in Abstract, §1.1, §3.4, §5.4, §6.1, §6.2, and §6.3.
  - [x] Add **Hardware Implementation Status** subsection (§4.1) documenting component supply delays and scoping Chapter 4 as the intended physical specification for Gazebo simulation.
- [x] **Correct the 1.5 m/s Rule & Split Hypothesis 1**
  - [x] Clarify in Abstract, Table 2.1, §2.2, §5.4, and Chapter 6 that 1.5 m/s is the referee **Stop** condition cap, not a blanket league maximum.
  - [x] Split H1 into **H1a (Regulatory Compliance: Stop speed cap & 2.0 s Halt braking)** and **H1b (Dynamic Capability: Unconstrained motor/wheel top speed & acceleration)**.
- [x] **Resolve H2 & Wi-Fi Latency Claims**
  - [x] Remove the unverified 12 ms hardware link measurement claim.
  - [x] Add §5.5 investigating simulated command delay injection ($\tau_d \in \{0, 10, 20, 40\}\text{ ms}$) to evaluate latency degradation and resolve RQ2.
- [x] **Correct TurtleBot3 Metrics & Comparisons**
  - [x] Define $E_{\text{path}}$ in Eq. 5.1 as orthogonal cross-track RMSE to the nearest path waypoint rather than time-indexed error.
  - [x] Replace "order of magnitude" and "84.8%" with the verified factor of 6.59 (0.1437 / 0.0218) and document that the TurtleBot's error stemmed from actuator velocity clipping at 0.22 m/s.
- [x] **Update AI Declarations**
  - [x] Mark **Box 6 (Code Development)** on the official Faculty of Science declaration form (`declaration.pdf`) and specify tool assistance.
  - [x] Update the declaration environment in `thesis.tex`.

---

## Phase 2: Supervisor Feedback (Should-Fix) — Status: PARTIALLY COMPLETED

### Completed:
- [x] **Simulation Validity & Model Parameters Table**
  - [x] Added **Table 4.2** documenting mass ($m$), yaw inertia ($I_z$), contact friction ($\mu$), speed limits, and sensor noise along with CAD and datasheet verification sources.
- [x] **Remove Unsupported Causal Claims (Torque-to-Mass)**
  - [x] Removed claims attributing tracking accuracy to torque-to-mass ratio.
  - [x] Added ground traction calculation showing that the platform is tire-grip limited ($F_{\text{grip}} \approx 3.4\text{ N} \ll 80\text{ N}$) rather than torque-limited.
- [x] **MPC Reproducibility & Horizon Justification**
  - [x] Standardized the MPC rate to 20 Hz ($\Delta t = 50\text{ ms}$) across all chapters.
  - [x] Documented cost matrices ($\mathbf{Q}, \mathbf{R}, \mathbf{Q}_N$), low-level discrete PID gains ($K_p = 1.85, K_i = 0.42, K_d = 0.015$).
  - [x] Added mathematical justification for $N = 5$ (0.25 s / 37.5 cm lookahead) with an $N \in \{5, 10, 20\}$ comparison and added the repository citation.

### Pending / Remaining Decisions:
- [ ] **Unconstrained Top Speed & Peak Acceleration Benchmarking (Optional / Pending Decision)**
  - *Objective:* Provide empirical simulation backing for Hypothesis 1b by removing the software $1.5\text{ m/s}$ velocity constraint.
  - *Pending Action:* Run an unconstrained sprint trial in Gazebo across all three platforms (Custom SSL, TurtleBot3 Burger, NVIDIA JetBot) using full actuator effort to record the simulated terminal velocity and peak acceleration derived from motor datasheet torque-speed curves and contact friction.
- [ ] **Table 5.1 Uncertainty & Repetitions (Optional / Pending Decision)**
  - *Current State:* Table 5.1 displays single-run deterministic numbers (0.0145 m, 0.0218 m, 0.0238 m).
  - *Pending Action:* Decide whether to run batch simulations (5–10 runs per cell with injected vision noise) to report Mean $\pm$ SD with 95% Confidence Intervals, or retain the baseline deterministic table as currently contextualized.
- [ ] **Per-Robot Reference Scaling for Arc (Optional / Pending Decision)**
  - *Current State:* The text explains that the TurtleBot3's large error was due to actuator saturation under the common competitive reference path.
  - *Pending Action:* Decide whether to keep this baseline comparison narrative or run a separate simulation where the reference trajectory is capped at 0.22 m/s specifically for the TurtleBot3.

---

## Phase 3: Manuscript Front Matter & Formatting Polish — Status: PENDING REVIEW
- [ ] **Acknowledgements Section (`thesis.tex`)**
  - Add text acknowledging your supervisor (Branden Ingram), the School of Computer Science & Applied Mathematics, and any peers/family.
- [ ] **List of Figures & List of Tables**
  - Check Wits submission guidelines to determine if `\listoffigures` and `\listoftables` are required after `\tableofcontents`.
- [ ] **Visual Inspection of Appendices**
  - Inspect Appendix A (CAD renderings on page 24 of `thesis.pdf`) to ensure images are sharp and scaled properly.
  - Inspect Appendix B (RP2040 board layout and appended declaration form on pages 25–26).

---

## Phase 4: Final Submission & Codebase Readiness — Status: PENDING FINAL CHECK
- [ ] **GitHub Repository Readiness (`references.bib`)**
  - Ensure `https://github.com/Deku-Soma/Research-methods-intro` is public.
  - Update root `README.md` to match the simulation feasibility framing.
- [ ] **Final LaTeX Compilation & Archival**
  - Run a clean build of `thesis.pdf` and verify page numbering, hyperref links, and bibliography citations.
