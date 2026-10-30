# RoboCup SSL Interactive Simulation & Benchmark CLI for Windows PowerShell
$ErrorActionPreference = "Stop"

Clear-Host
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  RoboCup SSL Research Simulation Control Hub (PowerShell)" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "Interactive CLI for simulation, baseline benchmarking, and analysis."
Write-Host ""
Write-Host "Select an operation:"
Write-Host "  [1] Launch Interactive Simulation (Gazebo GUI + RViz)" -ForegroundColor Green
Write-Host "  [2] Run Automated Benchmark Test (Single Platform)" -ForegroundColor Green
Write-Host "  [3] Run Comparative Benchmarks (All 3 Platforms: SSL vs TB3 vs JetBot)" -ForegroundColor Green
Write-Host "  [4] Launch Official RoboCup SSL Match Field" -ForegroundColor Green
Write-Host "  [5] View Benchmark Results (CSV Summaries)" -ForegroundColor Green
Write-Host "  [6] Open Interactive Terminal Inside Container" -ForegroundColor Green
Write-Host "  [7] Stop All Simulation Services and Clean Up" -ForegroundColor Green
Write-Host "  [q] Quit" -ForegroundColor Red
Write-Host ""

$mainChoice = Read-Host "Enter choice [1-7 or q] (default: 1)"
if ([string]::IsNullOrWhiteSpace($mainChoice)) { $mainChoice = "1" }

if ($mainChoice -match "^[qQ]$") {
    Write-Host "Exiting."
    exit 0
}

function Select-RobotModel {
    Write-Host ""
    Write-Host "Select Robot Platform:" -ForegroundColor Yellow
    Write-Host "  [1] Custom SSL Differential Robot (Standard)"
    Write-Host "  [2] TurtleBot3 Burger (Commercial Baseline 1)"
    Write-Host "  [3] NVIDIA JetBot (Commercial Baseline 2)"
    $robotChoice = Read-Host "Enter choice [1-3] (default: 1)"
    switch ($robotChoice) {
        "2" { return "turtlebot3_burger" }
        "3" { return "jetbot" }
        default { return "ssl_robot" }
    }
}

function Select-Scenario {
    Write-Host ""
    Write-Host "Select Evaluation Scenario:" -ForegroundColor Yellow
    Write-Host "  [1] Straight-Line 5m Sprint & Halt"
    Write-Host "  [2] Circular Arc (Steady-State Radius R=1.0m)"
    Write-Host "  [3] M-Shape Path (Transient Cornering)"
    $scenarioChoice = Read-Host "Enter choice [1-3] (default: 1)"
    switch ($scenarioChoice) {
        "2" { return "circular_arc" }
        "3" { return "m_shape" }
        default { return "straight_line" }
    }
}

function Select-DisplayMode {
    Write-Host ""
    Write-Host "Select Display Interface:" -ForegroundColor Yellow
    Write-Host "  [1] Native Desktop Window (WSLg / GPU Accelerated, default)"
    Write-Host "  [2] Web Browser Interface (noVNC at http://localhost:6080/vnc.html)"
    $dispChoice = Read-Host "Enter choice [1-2] (default: 1)"
    switch ($dispChoice) {
        "2" { return "novnc" }
        default { return "auto" }
    }
}

$researchDirWsl = "/mnt/d/'Wits work'/honors/'Research methods intro'/Research"

switch ($mainChoice) {
    "1" {
        $robot = Select-RobotModel
        $scenario = Select-Scenario
        $display = Select-DisplayMode
        Write-Host "`nStarting visual simulation for [$robot] on [$scenario] in mode [$display]..." -ForegroundColor Cyan
        wsl -e bash -c "cd $researchDirWsl && export ROBOT_MODEL=$robot && export SCENARIO=$scenario && export SIM_DISPLAY_MODE=$display && ./scripts/run_sim.sh"
    }
    "2" {
        $robot = Select-RobotModel
        $scenario = Select-Scenario
        Write-Host "`nEnable Gazebo GUI during test?" -ForegroundColor Yellow
        Write-Host "  [1] No (Headless fast execution, default)"
        Write-Host "  [2] Yes (Show visual simulation)"
        $guiChoice = Read-Host "Enter choice [1-2] (default: 1)"
        $gui = if ($guiChoice -eq "2") { "true" } else { "false" }

        Write-Host "`nExecuting Benchmark: $robot on $scenario..." -ForegroundColor Cyan
        wsl -e bash -c "cd $researchDirWsl && export ROBOT_MODEL=$robot && export SCENARIO=$scenario && ./scripts/run_benchmarks.sh"
    }
    "3" {
        $scenario = Select-Scenario
        Write-Host "`nRunning 3-Platform Comparative Suite on scenario: $scenario..." -ForegroundColor Cyan
        wsl -e bash -c "cd $researchDirWsl && ./scripts/run_comparative_benchmarks.sh $scenario"
    }
    "4" {
        Write-Host "`nLaunching Official RoboCup SSL Match Field..." -ForegroundColor Cyan
        wsl -e bash -c "cd $researchDirWsl && make field"
    }
    "5" {
        $csvPath = Join-Path $PSScriptRoot "benchmark_results\benchmark_comparative_master.csv"
        if (Test-Path $csvPath) {
            Write-Host "`nRecent Comparative Benchmark Log:" -ForegroundColor Green
            Write-Host "Path: $csvPath`n" -ForegroundColor DarkGray
            Import-Csv $csvPath | Format-Table -AutoSize
        } else {
            Write-Host "`nNo benchmark results found yet. Run an evaluation from option [2] or [3]." -ForegroundColor Yellow
        }
    }
    "6" {
        Write-Host "`nOpening interactive terminal in container..." -ForegroundColor Cyan
        wsl -e bash -c "cd $researchDirWsl && ./scripts/shell.sh"
    }
    "7" {
        Write-Host "`nStopping all container services..." -ForegroundColor Yellow
        wsl -e bash -c "cd $researchDirWsl && make down"
        Write-Host "Containers stopped and cleaned." -ForegroundColor Green
    }
    default {
        Write-Host "Invalid selection." -ForegroundColor Red
    }
}
