```
Deep Learning in Resource and Data-Constrained Edge Computing Systems: A Related Works Chapter

Introduction

The proliferation of edge computing has enabled the deployment of deep learning models closer to data sources, facilitating real-time processing and reducing latency. However, edge devices often operate under significant resource constraints, including limited computational power, memory, and energy. This chapter provides a comprehensive overview of related works addressing the challenges and opportunities of deep learning in resource and data-constrained edge computing systems. It thematically categorizes existing research, critically discusses the current state of the art, identifies research gaps, and concludes with a synthesis of how these works inform the present study and future research directions. All works discussed are based exclusively on the provided processed research findings.

Thematic Organization of Related Works

This section organizes the related works into several key themes, reflecting the diverse approaches to enabling deep learning on resource-constrained edge devices.

Federated Learning and Collaborative Inference at the Edge

A significant body of research focuses on federated learning and collaborative inference to address the limitations of edge devices. Yao et al. (2025) introduced FedMHO, a federated learning framework designed for heterogeneous edge devices, employing deep classification models on resource-rich clients and lightweight generative models on constrained devices. This approach tackles model heterogeneity and knowledge-forgetting problems inherent in federated learning. Palena et al. (2024) explored edge-device collaborative computing for multi-view classification, demonstrating that selective collaboration schemes can achieve substantial communication savings while maintaining high inference accuracy. These works highlight the potential of distributed learning paradigms to overcome resource limitations and improve performance in edge environments.

Model Partitioning, Dynamic Switching, and Adaptive Inference

Another prominent theme involves model partitioning, dynamic switching, and adaptive inference techniques. Zhang et al. (2025) presented AMP4EC, an adaptive model partitioning framework that optimizes deep learning inference in edge computing environments through real-time resource monitoring, dynamic model partitioning, and adaptive task scheduling. Their framework achieves significant reductions in latency and improvements in throughput. Matathammal et al. (2025) proposed EdgeMLBalancer, a self-adaptive approach for dynamic model switching on resource-constrained edge devices, optimizing CPU utilization and adapting to varying workloads by balancing computational efficiency and accuracy. These approaches demonstrate the effectiveness of dynamically adapting model complexity and execution strategies to match the available resources and workload demands of edge devices.

Lightweight Deep Learning Models and Early Exit Strategies

Researchers have also focused on developing lightweight deep learning models and early exit strategies to reduce the computational overhead on edge devices. Suman and Qu (2025) introduced a low-complexity deep learning model (DP-DRSN) for automatic modulation classification, optimized for resource-constrained edge devices. Their model achieves a strong balance between model efficiency and classification performance. Dong et al. (2022) explored early exit prediction mechanisms to reduce on-device computation overhead in device-edge co-inference systems. By guiding "hard" samples to bypass early exits, they improve the accuracy-computation tradeoff. These techniques offer promising avenues for deploying deep learning models on devices with limited resources.

Resource Allocation, Security, and Robustness

Addressing resource allocation, security, and robustness is crucial for the reliable deployment of deep learning in edge computing environments. Sun et al. (2025) presented SARMTO, a framework that integrates an action-constrained DRL model to dynamically balance resource allocation, task offloading, security, and performance in multi-cloud edge computing environments. Their framework achieves significant cost reduction and energy efficiency improvements. Moitra et al. (2023) introduced RobustEdge, a quantization-enabled energy separation training method with "early detection and exit" for low-power adversarial detection at the edge, improving adversarial robustness and energy efficiency in cloud-edge systems. These works emphasize the importance of considering resource management, security, and robustness when designing deep learning systems for edge deployment.

DNN Placement and General Edge Deep Learning Strategies

Bensalem et al. (2020) focused on DNN placement and inference modeling, finding that increasing model co-location decreases average latency, particularly under low load conditions. Qu (2022) provided an overview of enabling deep learning on edge devices, covering inference, adaptation, learning, and edge-server systems, highlighting the need to reduce DNN size and redundancy for effective edge deployment.

Critical Discussion

The reviewed works collectively demonstrate the diverse strategies employed to address the challenges of deep learning in resource and data-constrained edge computing systems. Federated learning and collaborative inference enable distributed learning and efficient resource utilization. Model partitioning, dynamic switching, and adaptive inference allow for flexible adaptation to varying resource availability and workload demands. Lightweight models and early exit strategies reduce computational overhead, while resource allocation, security, and robustness mechanisms ensure reliable and secure deployment.

However, the existing research also exhibits certain limitations. The performance of federated learning algorithms can be sensitive to data heterogeneity and communication constraints. Model partitioning and dynamic switching techniques may introduce additional overhead and complexity. Lightweight models and early exit strategies may sacrifice accuracy for efficiency. Furthermore, security and privacy concerns remain a significant challenge in edge computing environments.

Identified Research Gaps

Based on the reviewed literature, several research gaps can be identified:

*   **Standardized Benchmarks:** A lack of standardized benchmarks hinders the objective evaluation and comparison of different deep learning techniques on resource-constrained edge devices.
*   **Hardware-Aware Optimization:** More research is needed on hardware-aware optimization techniques that can exploit the specific capabilities of edge devices.
*   **Scalability and Robustness of Federated Learning:** Further research is required to improve the scalability and robustness of federated learning algorithms in highly heterogeneous edge environments.
*   **Security and Privacy:** Addressing security and privacy concerns in edge computing, especially in collaborative and federated learning scenarios, remains a critical challenge.
*   **Energy Efficiency:** Optimizing energy efficiency is crucial for prolonging the battery life of edge devices and reducing the overall energy consumption of edge computing systems.

Conclusion

The reviewed publications highlight the significant progress made in enabling deep learning in resource and data-constrained edge computing systems. The research addresses various challenges, including model heterogeneity, resource limitations, security concerns, and the need for energy efficiency. Emerging trends such as edge-AI convergence, TinyML, federated learning, hardware acceleration, and adaptive resource management are shaping the future of this field. Further research is needed to address the identified research gaps and fully realize the potential of deep learning in edge computing environments. The works reviewed provide a strong foundation for future research directions, including the development of more robust and scalable federated learning algorithms, hardware-aware optimization techniques, and comprehensive security and privacy solutions.

References

Bensalem, M., Dizdarević, J., & Jukan, A. (2020). Modeling of Deep Neural Network (DNN) Placement and Inference in Edge Computing. *arXiv*. [https://arxiv.org/abs/2001.06901v1](https://arxiv.org/abs/2001.06901v1)

Dong, R., Mao, Y., & Zhang, J. (2022). Resource-Constrained Edge AI with Early Exit Prediction. *arXiv*. [https://arxiv.org/abs/2206.07269v2](https://arxiv.org/abs/2206.07269v2)

Matathammal, A., Gupta, K., Lavanya, L., Halgatti, A. V., Gupta, P., & Vaidhyanathan, K. (2025). EdgeMLBalancer: A Self-Adaptive Approach for Dynamic Model Switching on Resource-Constrained Edge Devices. *arXiv*. [https://arxiv.org/abs/2502.06493v1](https://arxiv.org/abs/2502.06493v1)

Moitra, A., Bhattacharjee, A., Kim, Y., & Panda, P. (2023). RobustEdge: Low Power Adversarial Detection for Cloud-Edge Systems. *arXiv*. [https://arxiv.org/abs/2310.06845v1](https://arxiv.org/abs/2310.06845v1)

Palena, M., Cerquitelli, T., & Chiasserini, C. F. (2024). Edge-device Collaborative Computing for Multi-view Classification. *arXiv*. [https://arxiv.org/abs/2409.15973v1](https://arxiv.org/abs/2409.15973v1)

Qu, Z. (2022). Enabling Deep Learning on Edge Devices. *arXiv*. [https://doi.org/10.3929/ethz-b-000574442](https://doi.org/10.3929/ethz-b-000574442)

Suman, P. & Qu, Y. (2025). A Lightweight Deep Learning Model for Automatic Modulation Classification using Dual Path Deep Residual Shrinkage Network. *arXiv*. [https://arxiv.org/abs/2507.04586v1](https://arxiv.org/abs/2507.04586v1)

Sun, J., Gao, Q., Wu, C., Li, Y., Wang, J., & Niyato, D. (2025). Secure Resource Allocation via Constrained Deep Reinforcement Learning. *arXiv*. [https://arxiv.org/abs/2501.11557v1](https://arxiv.org/abs/2501.11557v1)

Yao, D., Shi, Y., Liu, T., & Xu, Z. (2025). FedMHO: Heterogeneous One-Shot Federated Learning Towards Resource-Constrained Edge Devices. *arXiv*. [https://arxiv.org/abs/2502.08518v1](https://arxiv.org/abs/2502.08518v1)

Zhang, G., Guo, W., Tan, Z., & Jiang, H. (2025). AMP4EC: Adaptive Model Partitioning Framework for Efficient Deep Learning Inference in Edge Computing Environments. *arXiv*. [https://arxiv.org/abs/2504.00407v2](https://arxiv.org/abs/2504.00407v2)
```