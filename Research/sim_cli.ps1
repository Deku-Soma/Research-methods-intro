param (
    [Parameter(Position=0)]
    [ValidateSet("build", "sim", "benchmark", "batch", "speed_test", "speed_test_all", "benchmark_all", "run_all", "record_all", "summary", "shell", "cleanup", "help")]
    [string]$Command = "help",

    [Parameter(Position=1)]
    [ValidateSet("ssl_robot", "turtlebot3_burger", "jetbot", "all")]
    [string]$Robot = "all",

    [Parameter(Position=2)]
    [ValidateSet("straight_line", "circular_arc", "m_shape", "all")]
    [string]$Scenario = "all",

    [Parameter(Position=3)]
    [int]$Trials = 1,

    [Parameter(Position=4)]
    [switch]$Gui
)

function Show-Help {
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host " RoboCup SSL Simulation & Benchmarking CLI (PowerShell)" -ForegroundColor Cyan
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host "Commands:"
    Write-Host "  run_all [trials]                      - Run ALL robots back-to-back across ALL tests with 3D GUI"
    Write-Host "  record_all [trials]                   - Alias for run_all (ready for video screen recording)"
    Write-Host "  sim [robot] [scenario]                - Launch Gazebo simulation with visual 3D GUI"
    Write-Host "  benchmark [robot] [scenario] [-Gui]   - Run single trajectory tracking benchmark"
    Write-Host "  batch [robot] [scenario] [trials][-Gui]- Run repeated batch trials back-to-back"
    Write-Host "  speed_test [robot] [-Gui]             - Run unconstrained straight-line top speed test"
    Write-Host "  speed_test_all [-Gui]                 - Test top speed across all 3 platforms"
    Write-Host "  benchmark_all [trials] [-Gui]         - Run comparative matrix across all robots & scenarios"
    Write-Host "  summary                               - Display statistical summary table (Mean ± SD)"
    Write-Host "  build                                 - Rebuild colcon packages inside container"
    Write-Host "  shell                                 - Open interactive bash shell inside container"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Trials [N]                           - Repetitions per scenario (default: 1 for run_all)"
    Write-Host "  -Gui                                  - Open the 3D Gazebo GUI in browser (noVNC)"
    Write-Host ""
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerDir = Join-Path $ScriptDir "docker"

function Ensure-Docker {
    Set-Location $DockerDir
    docker compose up -d | Out-Null
    Set-Location $ScriptDir
}

function Open-Browser-Viewer {
    Write-Host "--> Opening 3D simulation viewer in your browser at http://localhost:6080/vnc.html" -ForegroundColor Cyan
    Write-Host "    (Click 'Connect' in the browser window to see the 3D Gazebo arena)" -ForegroundColor Yellow
    Start-Process "http://localhost:6080/vnc.html"
}

$GuiFlag = if ($Gui) { "export GUI=true;" } else { "export GUI=false;" }

switch ($Command) {
    "run_all" {
        Ensure-Docker
        Write-Host "====================================================" -ForegroundColor Cyan
        Write-Host " Starting Full Multi-Robot Visual Benchmark Suite" -ForegroundColor Cyan
        Write-Host "====================================================" -ForegroundColor Cyan
        Write-Host "Robots:    ssl_robot -> turtlebot3_burger -> jetbot" -ForegroundColor White
        Write-Host "Scenarios: straight_line -> circular_arc -> m_shape -> speed_test" -ForegroundColor White
        Write-Host "Trials:    $Trials repetition(s) per test" -ForegroundColor White
        Write-Host ""
        Open-Browser-Viewer
        Write-Host "Ready to record! Click 'Connect' in your browser and start your screen recorder." -ForegroundColor Yellow
        Write-Host "Starting automated test sequence in 6 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 6
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh run_all $Trials"
        Set-Location $ScriptDir
    }
    "record_all" {
        Ensure-Docker
        Write-Host "====================================================" -ForegroundColor Cyan
        Write-Host " Starting Full Multi-Robot Visual Benchmark Suite" -ForegroundColor Cyan
        Write-Host "====================================================" -ForegroundColor Cyan
        Write-Host "Robots:    ssl_robot -> turtlebot3_burger -> jetbot" -ForegroundColor White
        Write-Host "Scenarios: straight_line -> circular_arc -> m_shape -> speed_test" -ForegroundColor White
        Write-Host "Trials:    $Trials repetition(s) per test" -ForegroundColor White
        Write-Host ""
        Open-Browser-Viewer
        Write-Host "Ready to record! Click 'Connect' in your browser and start your screen recorder." -ForegroundColor Yellow
        Write-Host "Starting automated test sequence in 6 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 6
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh run_all $Trials"
        Set-Location $ScriptDir
    }
    "build" {
        Ensure-Docker
        Write-Host "Building ROS 2 workspace packages inside container..." -ForegroundColor Green
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "source /opt/ros/humble/setup.bash && cd /ros2_ws && colcon build --symlink-install --packages-select ssl_robot_benchmarking ssl_robot_control ssl_robot_description ssl_robot_gazebo"
        Set-Location $ScriptDir
    }
    "sim" {
        Ensure-Docker
        Write-Host "Launching Gazebo simulation with visual 3D GUI for $Robot ($Scenario)..." -ForegroundColor Green
        Open-Browser-Viewer
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && pkill -9 -f 'gz' 2>/dev/null || true; sleep 1; ros2 launch ssl_robot_gazebo sim.launch.py robot_model:=$Robot scenario:=$Scenario gui:=true rviz:=false"
        Set-Location $ScriptDir
    }
    "benchmark" {
        Ensure-Docker
        if ($Gui) { Open-Browser-Viewer }
        $guiText = if ($Gui) { "with 3D GUI" } else { "headless" }
        Write-Host "Running benchmarking trial for $Robot ($Scenario) [$guiText]..." -ForegroundColor Green
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "$GuiFlag source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh benchmark $Robot $Scenario"
        Set-Location $ScriptDir
    }
    "batch" {
        Ensure-Docker
        if ($Gui) { Open-Browser-Viewer }
        $guiText = if ($Gui) { "with 3D GUI" } else { "headless" }
        Write-Host "Executing batch simulation suite for $Robot on $Scenario ($Trials iterations, $guiText)..." -ForegroundColor Green
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "$GuiFlag source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh batch $Robot $Scenario $Trials"
        Set-Location $ScriptDir
    }
    "speed_test" {
        Ensure-Docker
        if ($Gui) { 
            Open-Browser-Viewer 
            Write-Host "Waiting 5 seconds for 3D simulation viewer to connect..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
        $guiText = if ($Gui) { "with 3D GUI" } else { "headless" }
        Write-Host "Running unconstrained straight-line speed test for $Robot [$guiText]..." -ForegroundColor Green
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "$GuiFlag source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh speed_test $Robot"
        Set-Location $ScriptDir
    }
    "speed_test_all" {
        Ensure-Docker
        if ($Gui) { 
            Open-Browser-Viewer 
            Write-Host "Waiting 5 seconds for 3D simulation viewer to connect..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
        $guiText = if ($Gui) { "with 3D GUI" } else { "headless" }
        Write-Host "Running unconstrained straight-line speed tests across all platforms [$guiText]..." -ForegroundColor Green
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "$GuiFlag source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh speed_test_all"
        Set-Location $ScriptDir
    }
    "benchmark_all" {
        Ensure-Docker
        if ($Gui) { Open-Browser-Viewer }
        $guiText = if ($Gui) { "with 3D GUI" } else { "headless" }
        Write-Host "Running full comparative batch suite across all robots & scenarios ($Trials trials each, $guiText)..." -ForegroundColor Green
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "$GuiFlag source /opt/ros/humble/setup.bash && [ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash && /ros2_ws/scripts/sim_cli.sh batch all all $Trials"
        Set-Location $ScriptDir
    }
    "summary" {
        Ensure-Docker
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "python3 /ros2_ws/scripts/aggregate_benchmarks.py"
        Set-Location $ScriptDir
    }
    "cleanup" {
        Ensure-Docker
        Set-Location $DockerDir
        docker compose exec ros2_sim bash -c "/ros2_ws/scripts/sim_cli.sh cleanup"
        Set-Location $ScriptDir
    }
    "shell" {
        Ensure-Docker
        Set-Location $DockerDir
        docker compose exec ros2_sim bash
        Set-Location $ScriptDir
    }
    default {
        Show-Help
    }
}
