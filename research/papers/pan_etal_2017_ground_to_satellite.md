# Ground-to-Satellite Quantum Teleportation

**Authors:** Ji-Gang Ren, Ping Xu, Hai-Lin Yong, Liang Zhang, Sheng-Kai Liao, Juan Yin, Wei-Yue Liu, Wen-Qi Cai, Meng Yang, Li Li, Kui-Xing Yang, Xuan Han, Yong-Qiang Yao, Jian Li, Hai-Yan Wu, Song Wan, Lei Liu, Ding-Quan Liu, Yun-Wei Kuang, Zhi-Ping He, Peng Shang, Cheng Guo, Ru-Hua Zheng, Kai Tian, Zhen-Cai Zhu, Nai-Le Liu, Chao-Yang Lu, Rong Shu, Yu-Ao Chen, Cheng-Zhi Peng, Jian-Yu Wang, Jian-Wei Pan (and additional members)  
**Year:** 2017  
**Published:** Nature, 549, 70–73 (September 7, 2017)  
**arXiv:** 1707.00934  
**DOI:** 10.1038/nature23675

---

## Summary
First demonstration of quantum teleportation from a ground station to a low-Earth orbit satellite — the Micius satellite — over distances up to **1,400 km**. This is the current distance record for quantum teleportation (as of 2025).

---

## Experimental Setup

**Satellite:** Micius (墨子号) — Chinese quantum science satellite, LEO orbit ~500 km altitude  
**Ground station:** Ngari, Tibet (altitude 5,100 m, chosen for thin atmosphere)  
**Distance range:** 500–1,400 km (varies as satellite passes overhead)  
**Carrier:** Single photon qubits (polarization encoding)

### Why Satellite?
- Fiber optic quantum teleportation degrades exponentially with distance due to absorption (~0.2 dB/km for telecom fiber)
- Free space (satellite) path has most loss in the first ~10 km of atmosphere; above that, loss is minimal
- 1,400 km free-space link loses less quantum signal than ~200 km of fiber

### Technical Innovations
- Ultra-bright entangled photon source on the ground (10^7 pairs/second)
- Narrow-beam divergence pointing system (angular precision ~0.5 μrad)
- High-bandwidth adaptive optics and tracking (APT — Acquiring, Pointing, Tracking)
- Real-time Bell state measurement synchronized with satellite pass

---

## Results

| Metric | Value |
|--------|-------|
| Distance achieved | Up to 1,400 km |
| Average fidelity (6 input states) | **0.80 ± 0.01** |
| Classical limit fidelity | 2/3 ≈ 0.667 |
| Statistical significance above classical limit | >3.5σ for all states |
| Photon detection rate at satellite | ~1 photon per 6 minutes at max distance |
| Total teleported qubits in experiment | ~900 over ~32 satellite passes |

Fidelity of 0.80 > 2/3 threshold confirms genuine quantum teleportation (not simulable by classical communication alone).

---

## Significance

1. **Distance record:** 1,400 km is ~10× larger than previous records (~143 km, Canary Islands 2012)
2. **Space quantum network:** Proves satellite-based quantum repeater links are feasible — a key step toward a global quantum internet
3. **Atmosphere is not a fundamental barrier:** Loss from 1,400 km free-space is comparable to ~30 km of deployed fiber
4. **Complementary work:** Pan's team simultaneously demonstrated satellite-based entanglement distribution over 1,200 km (a separate Nature paper in the same issue)

---

## Context in Global Quantum Network Development
- This experiment + the Micius entanglement distribution experiment established satellite-based quantum communication as viable
- China has since proposed a global quantum communication satellite network
- ESA and NASA have proposed similar systems
- Long-term vision: quantum repeater network enabling truly secure (quantum key distribution) global communications and potentially distributed quantum computing

---

## Assessment

**What this demonstrates:** Quantum teleportation of photon polarization states works over continental distances via satellite, with high fidelity and without degradation from atmospheric effects.

**What this does NOT demonstrate:** Matter teleportation, human teleportation, or any transfer of physical objects. The photon is still a photon at the destination — only its quantum state (polarization) was teleported, not the photon itself.
