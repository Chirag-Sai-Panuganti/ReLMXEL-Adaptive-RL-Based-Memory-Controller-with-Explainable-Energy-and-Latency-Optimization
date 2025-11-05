# ChampSim Simulator

**ChampSim** is a trace-based simulator designed for microarchitecture research, providing detailed simulation and analysis of cache architectures and memory subsystems. It is an invaluable tool for studying modern CPU architectures, optimizing cache hierarchies, and improving both energy efficiency and performance. 

## Dependencies

ChampSim relies on **[vcpkg](https://vcpkg.io)** for managing its external dependencies. The repository includes vcpkg as a submodule to streamline this process. Below are the steps required to install and configure the necessary dependencies:

1. **Initialize submodules**:
    ```bash
    git submodule update --init
    ```

2. **Bootstrap vcpkg**:
    ```bash
    vcpkg/bootstrap-vcpkg.sh
    ```

3. **Install the dependencies**:
    ```bash
    vcpkg/vcpkg install
    ```

### Required Software:

- **C++ Compiler** (C++11 or later)
- **CMake** (for project configuration and build)
- **GNU Make** (for building the simulator)

## Modifications for DRAM Memory Controller

To simulate traces for the DRAM Memory Controller, you need to replace the existing `dram_controller.cc` file in the `Champsim/src` directory with the version provided in the **Modifications** directory. 

### Steps:

1. Replace the file `Champsim/src/dram_controller.cc` with the corresponding file in the **Modifications** directory.

2. **Build the ChampSim simulator** following the usual build process.

## Generating Traces

Once the setup and modifications are complete, you can generate memory traces using the following command format:

```bash
bin/champsim --warmup-instructions 1000000 --simulation-instructions {number_of_instructions} {workload_from_SPEC_2016}```
