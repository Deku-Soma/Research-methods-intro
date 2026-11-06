# RoboCup SSL Honours Report: Project To-Do List

## Phase 1: Supervisor Feedback (Must-Fix) - Status: COMPLETED
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

## Phase 2: Supervisor Feedback (Should-Fix) - Status: COMPLETED

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
- [x] **Unconstrained Top Speed & Peak Acceleration Benchmarking (H1b)**
  - [x] Implemented unconstrained sprint test evaluator (`sprint_halt_evaluator.py`) with active proportional heading hold and acceleration ramping ($3.0\text{ m/s}^2$).
  - [x] Executed empirical tests across all three platforms: custom SSL platform reached $2.001\text{ m/s}$ ($t_{\text{stop}} = 0.434\text{ s}$, $d_{\text{stop}} = 0.571\text{ m}$), TurtleBot3 reached $0.300\text{ m/s}$ ($t_{\text{stop}} = 0.137\text{ s}$), and JetBot reached $0.501\text{ m/s}$ ($t_{\text{stop}} = 0.190\text{ s}$).
  - [x] Logged empirical velocity profiles directly into `benchmark_comparative_master.csv`.
- [x] **Multi-Trial Batch Evaluation & Statistical Uncertainty**
  - [x] Automated batch simulation execution (`.\sim_cli.ps1 batch` and `benchmark_all`) with live cross-track RMSE and stopping telemetry.
  - [x] Built automated statistical aggregator (`aggregate_benchmarks.py` / `.\sim_cli.ps1 summary`) generating sample statistics ($N$, $\text{Mean} \pm \text{SD}$, and pass rates) in `benchmark_statistical_summary.csv`.
- [x] **Visual 3D Simulation Streaming & Recording**
  - [x] Configured noVNC web streaming on port 6080 (`http://localhost:6080/vnc.html`) with framed camera pose $(2.5, -6.0, 4.0)$ centered on the sprint lane.
  - [x] Added `run_all` / `record_all` visual suites with automated recording delays and process lifecycle management (`pkill` process cleanup).

### Remaining Optional Decision:
- [ ] **Per-Robot Reference Scaling for Arc (Optional / Pending Decision)**
  - *Current State:* The text explains that the TurtleBot3's large error was due to actuator saturation under the common competitive reference path.
  - *Pending Action:* Decide whether to keep this baseline comparison narrative or run a separate simulation where the reference trajectory is capped at 0.22 m/s specifically for the TurtleBot3.

---

## Phase 3: Manuscript Front Matter & Formatting Polish - Status: COMPLETED
- [x] **Acknowledgements Section (`thesis.tex`)**
  - Added acknowledgements recognizing supervisor Branden Ingram, the School of Computer Science & Applied Mathematics, and family/peers.
- [x] **List of Figures & List of Tables**
  - Added `\listoffigures` and `\listoftables` with matching roman numeral pagination and table-of-contents bookmarks.
  - Disabled `ltablex` package conflict to ensure correct sequential numbering across tables (Table 4.1, Table 4.2, Table 5.1).
- [x] **Visual Inspection of Appendices**
  - Verified 3D CAD multi-view renderings in Appendix A.
  - Verified RP2040 pinout diagram and appended postgraduate AI declaration form in Appendix B.

---

## Phase 4: Final Submission & Codebase Readiness - Status: COMPLETED
- [x] **GitHub Repository Readiness (`references.bib`)**
  - [x] Ensured `https://github.com/Deku-Soma/Research-methods-intro` is public.
  - [x] Verified `@misc{ssl_robot_code_2026}` BibTeX entry and added `retrieved` metadata resolving BibTeX warnings.
  - [x] Updated root `README.md` to match the simulation feasibility study framing, hardware implementation status, 20 Hz MPC formulation, empirical hypothesis results, and repository citation.
- [x] **Final LaTeX Compilation & Archival**
  - [x] Fixed Chapter 3 subsection hierarchy to proper top-level sections (`§3.1`–`§3.4`).
  - [x] Executed clean compilation cycle (`pdflatex` + `bibtex` + `pdflatex` x2) with zero BibTeX warnings and zero undefined references.
  - [x] Verified roman (`i`–`vii`) front matter pagination, arabic (`1`–`26`) body pagination, PDF outline bookmarks, and appendix declaration inclusion (34 total pages).
