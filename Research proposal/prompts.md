# Research Proposal Prompts

This document provides section-by-section prompts to help you draft your research proposal on **Developing a low-cost, 3D-printed, ROS-based differential-drive robotic platform for the RoboCup Small Size League (SSL)**. It incorporates your specific structural and stylistic writing rules.

## 1. Introduction
*Goal: The reader must understand the full arc of your argument by the end of this section.*

*   **Prompt 1:** Open with the general problem stated plainly. What is the overarching issue with accessibility in robotics education and research (e.g., the cost barrier of specialized hardware)?
*   **Prompt 2:** Provide a concrete, easy-to-understand example before going technical. What does this financial barrier look like in practice for under-resourced schools or universities?
*   **Prompt 3:** Transition from the conceptual solution to the specific problem. Why is a low-cost, standardized platform needed in the context of the RoboCup SSL?
*   **Prompt 4:** Explain why it matters and why it is hard. What are the engineering challenges in replacing expensive omnidirectional drives and proprietary systems with 3D-printed differential drives and open-source middleware (ROS)?
*   **Prompt 5:** State your specific solution clearly. What exactly are you building and benchmarking to solve this problem?

## 2. Background
*Goal: Explain how things mechanically work. Be mathematically precise.*

*   **Prompt 1:** Explain the RoboCup SSL environment and its technical standards. What are the spatial constraints, temporal constraints, and information constraints (e.g., overhead vision)?
*   **Prompt 2:** Describe the mechanics of holonomic versus non-holonomic drives. Define the variables and equations that govern a differential drive system. 
*   **Prompt 3:** Detail the control theory required to meet SSL safety protocols. State the update rules for your PID or MPC loop used for rapid deceleration and speed regulation.
*   **Prompt 4:** Explain the distributed system architecture. Describe the data structures and communication protocols used when bridging centralized SSL-Vision data to local motor execution via ROS.

## 3. Related Work
*Goal: Write as a narrative with a clear storyline. Group by theme.*

*   **Prompt 1 (Theme 1: Locomotion Strategies):** Establish the dominance of omnidirectional drives in SSL, identify the complexity limitation, and introduce the differential drive as a cost-effective alternative. How have previous researchers quantified the "Non-Holonomic Penalty"?
*   **Prompt 2 (Theme 2: Middleware Evolution):** Describe the shift from centralized processing to distributed architectures. How did the transition from ROS1 to ROS2 (DDS) solve networking issues but introduce real-time determinism challenges?
*   **Prompt 3 (Theme 3: Additive Manufacturing):** Discuss the move toward 3D-printed components. How does your platform build upon previous micro-scale testbeds (like MICROMVP) to increase accessibility?
*   **Prompt 4 (Theme 4: Simulation vs. Reality):** Explain the "reality gap" in virtual simulations. Ensure your final sentence naturally leads into your own contribution: the necessity of building this physical benchmarking platform.

## 4. Methodology
*Goal: State explicitly what you will do with no ambiguity.*

*   **Prompt 1:** Outline the hardware design phase. What specific off-the-shelf electronics and 3D-printed components will you use, and how do you justify these choices?
*   **Prompt 2:** Detail the software architecture implementation. Name the specific algorithms, describe their setup, and justify your choices for ROS nodes and intra-process communication. 
*   **Prompt 3:** Describe the benchmarking pipeline. Outline the pipeline from raw SSL-Vision data to evaluable output in logical steps (e.g., measuring latency, "Time-to-Target", trajectory accuracy).
*   **Prompt 4:** Plan the experimental setup. How will you physically construct the test environment to measure these metrics against league regulations? Support the pipeline description with a figure.

## 5. Results
*Goal: Present your findings clearly and objectively.*

*   **Prompt 1:** How will you report the mechanical performance metrics (e.g., velocity, deceleration time) compared to the SSL standards?
*   **Prompt 2:** What data will show the software latency and control loop stability of your ROS implementation?
*   **Prompt 3:** How will you present the cost analysis of your platform versus traditional high-end SSL robots?

## 6. Discussion
*Goal: Interpret the results in the context of your original problem.*

*   **Prompt 1:** Did the differential-drive approach successfully meet the minimum maneuverability requirements despite the "Non-Holonomic Penalty"?
*   **Prompt 2:** How effectively did the ROS-based architecture manage the temporal constraints?
*   **Prompt 3:** To what extent does your platform bridge the "reality gap" compared to pure simulation, and does it serve as a viable entry point for under-resourced institutions?

## 7. Conclusion
*Goal: Summarize the contribution without introducing new information.*

*   **Prompt 1:** Restate the main problem and your proposed solution without using generic connectors.
*   **Prompt 2:** Summarize the key findings from your benchmarking experiments. Ensure that all research questions stated in the introduction are explicitly answered here.
*   **Prompt 3:** Conclude with the broader impact of this work on robotics accessibility and multi-agent systems research. 

---
**Reminder of Key Writing Rules:**
*   Always use present tense when referencing authors (e.g., "Smith argues").
*   Maintain the same tense, person, and voice throughout each section.
*   Define every acronym on first use and never redefine it.
*   Ensure every figure and table is mentioned in the body text before it appears.
*   Every statement of fact must be precise and specific.
*   Use `\citep{}` for parenthetical citations and `\citet{}` for narrative citations.
*   Cite seminal/foundational works every time you introduce a concept.
*   Avoid filler phrases, em-dashes, and generic transitions.
