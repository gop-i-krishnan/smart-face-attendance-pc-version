# fpga-cnn-accelerator

# 🚀 CNN Conv1 Hardware Accelerator using Vitis HLS (Zynq-7020)

## 📌 Overview

This project implements the first convolution layer (Conv1) of a quantized CNN model using **Vitis HLS 2023.2**, targeting the **Zynq-7020 FPGA (PYNQ-Z2 board)**.

The design accelerates a 3×3 stride-2 convolution layer using int8 quantization and fixed-point requantization, demonstrating FPGA-based parallel CNN acceleration.

---

## 🧠 Layer Configuration

- **Input:** 160 × 160 × 3  
- **Kernel:** 3 × 3  
- **Stride:** 2  
- **Output:** 79 × 79 × 32  
- **Data type:** int8 (quantized)

The accelerator performs:

1. 3×3×3 Multiply-Accumulate (MAC)
2. Bias addition
3. Fixed-point scaling (requantization)
4. Saturation to int8

---

## ⚙️ Hardware Architecture

The design uses:

- AXI4 Master interface for input/output memory access
- On-chip BRAM buffering of the input feature map
- Loop pipelining (Initiation Interval = 1)
- Partial output-channel parallelization (4 channels processed in parallel)
- Fully unrolled 3×3×3 MAC computation

### Dataflow
AXI Input → BRAM Buffer → Parallel MAC → Bias → Requantization → Clamp → AXI Output


---

## 🚀 Optimization Journey

| Version | Latency (cycles) | Description |
|----------|------------------|-------------|
| Baseline | ~5.3M | Sequential convolution |
| BRAM Buffered | ~276k | Eliminated AXI bottleneck |
| 4-Channel Parallel | ~326k | Output-channel parallelization |

- **Clock frequency:** 100 MHz  
- **Execution time:** ~3.2 ms per Conv1 inference  

---

## 📊 Resource Utilization (Zynq-7020)

- **BRAM:** ~50  
- **DSP:** ~21  
- **LUT:** ~11k  
- **Timing achieved:** 7.3 ns (Target: 10 ns)

---

## 🛠 Tools Used

- Vitis HLS 2023.2  
- Vivado (Target device: xc7z020clg400-1)  
- C/C++ (High-Level Synthesis)

---

## 🎯 Project Objective

This project demonstrates:

- Efficient FPGA acceleration of CNN layers
- Data reuse through BRAM buffering
- Parallel multiply-accumulate architecture
- Fixed-point quantization handling
- Performance vs resource trade-off optimization

---

## 📂 Repository Structure

- `first_conv.cpp` — Top-level HLS implementation  
- `first_conv.h` — Function declaration  
- `conv_params.h` — Quantized weights, bias, and scaling parameters  

---

## 📌 Future Improvements

- Implement sliding-window line buffer architecture  
- Integrate HLS IP into Vivado block design  
- Extend design to full CNN pipeline acceleration  

---

## 👤 Authors

- Gopi Krishnan  
- Milan Martin  
- Gilbert Franco  

Electronics & Communication Engineering  
Focused on FPGA acceleration, embedded AI, and hardware optimization.
