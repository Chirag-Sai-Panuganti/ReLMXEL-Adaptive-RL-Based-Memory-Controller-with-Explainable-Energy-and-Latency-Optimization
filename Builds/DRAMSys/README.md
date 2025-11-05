# DRAMSys Simulator

**DRAMSys** is a flexible DRAM subsystem design space exploration framework based on SystemC TLM-2.0. It was developed by the Microelectronic Systems Design Research Group at RPTU Kaiserslautern-Landau, by Fraunhofer IESE and by the Computer Engineering Group at JMU Würzburg.

## Dependencies
### Compiler and Build Tools:

- **C++17 Compiler**: DRAMSys requires a C++17 compatible compiler.
- **CMake**: Minimum version 3.24 is required for the build process.

### SystemC:

- DRAMSys is based on **SystemC**. SystemC is included with FetchContent and will be built automatically with the project.
- If you prefer to use a preinstalled version of SystemC, export the environment variable `SYSTEMC_HOME` (the SystemC installation directory) and enable the `DRAMSYS_USE_EXTERNAL_SYSTEMC` CMake option.
- Make sure that the preinstalled SystemC library is built with the same C++ version as the one you are using for DRAMSys.


## Setting up DRAMSys
### Steps:

1. Replace the files `Controller.h` and `Controller.cpp` in `DRAMSys/src/libdramsys/DRAMSys/controller` with the corresponding files in the **Modifications** directory.

2. Replace the files `StlPlayer.h` and `StlPlayer.cpp` in `DRAMSys/src/simulator/simulator/player` with the corresponding files in the **Modifications** directory.

3. Change the trace file to be used from the `name` parameter in `DRAMSys/configs/ddr4-example.json` file.

4. Build the simulator: 
```console
$ cd DRAMSys
$ cmake -B build -D DRAMSYS_WITH_DRAMPOWER=Y
$ cmake --build build
```

5. Change the `PowerAnalysis` parameter from .json files in `DRAMSys/configs/simconfig/` to **true**

6. Verify the working of simulator by: 
```console
$ ./DRAMSys/build/bin/DRAMSys ./configs/ddr4-example.json
```

## References
L. Steiner, M. Jung, F. S. Prado, K. Bykov, N. Wehn. International Conference on Embedded Computer Systems: Architectures, Modeling, and Simulation (SAMOS), July, 2020, Samos Island, Greece.
