# Liquidity-Sentry-Core

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AsyncIO](https://img.shields.io/badge/Architecture-AsyncIO-green)
![License](https://img.shields.io/badge/License-MIT-purple)
![Status](https://img.shields.io/badge/Status-Production-red)

> **Institutional-grade real-time surveillance system for Binance Futures.**
> 
> *Monitors liquidity anomalies, detects whale movements, and generates visual risk alerts via Telegram. Powered by AsyncIO & WebSockets.*

---

## 🦅 Overview | 项目概述

**Liquidity-Sentry-Core** is not a trading bot; it is a **Risk Detection Radar**.

In a market filled with noise and delayed news, this system provides **Information Asymmetry** by monitoring the raw flow of money. It utilizes a high-frequency, event-driven architecture to detect volume anomalies in milliseconds, generating visual intelligence for decision-makers.

**Core Philosophy:**
* **Zero Latency:** Direct connection to Binance market streams via WebSockets.
* **Visual Intelligence:** "CEO-Dashboard" style alerts. No complex data, just signals.
* **Tiered Risk Logic:** Filters noise to distinguish between "Scalping Opportunities" (Tier A) and "Whale Movements" (Tier S).

---

## ⚡ Key Features | 核心特性

### 1. 🚀 Async Event-Driven Engine (异步事件驱动引擎)
Abandoning the traditional HTTP polling model, the core is built on **Python AsyncIO** and **WebSockets**.
* **Sub-100ms Latency:** Reacts to market moves instantly.
* **Non-Blocking:** Chart rendering and notifications do not block the surveillance radar.
* **High Concurrency:** Monitors dozens of assets simultaneously with minimal resource usage.

### 2. 🐋 Tiered Signal System (分级信号系统)
Smart filtering to prevent alert fatigue:
* **🚨 S-Tier (Nuclear Alert):** Volume > 3.5x baseline. Indicates institutional entry/exit. Immediate attention required.
* **⚡ A-Tier (Activity Alert):** Volume > 2.0x baseline. Indicates short-term volatility. Good for scalping.

### 3. 📊 Institutional Visualization (机构级可视化)
Auto-generates professional financial charts:
* **Dark Mode UI:** Optimized for low-light environments.
* **HUD Display:** Real-time volume deviation, price change, and signal status.
* **Privacy First:** Deployed on private servers, ensuring data sovereignty.

---

## 🛠️ Architecture | 技术架构

```mermaid
graph TD
    A[Binance WebSocket Stream] -->|Real-time Data| B(Async Data Fetcher)
    B -->|Event Loop| C{Logic Analyzer}
    C -->|Threshold Triggered| D[Task Queue]
    D -->|Non-blocking| E[Processor Worker]
    E -->|Matplotlib (Agg)| F[Chart Generator]
    F -->|Aiohttp| G[Telegram Bot]
    G -->|Push Notification| H((User/Channel))
