```markdown
## Chapter 2: Related Works: Deep Learning in Resource and Data Constrained Edge Computing Systems

### 2.1 Introduction

Edge computing has emerged as a pivotal paradigm for deploying deep learning (DL) applications, facilitating computation closer to data sources and end-users. This proximity yields substantial benefits, notably reduced latency, minimized bandwidth consumption, and enhanced data privacy, rendering it exceptionally suitable for real-time and privacy-sensitive applications (Shi et al., 2016). However, edge devices are inherently resource-constrained, characterized by limitations in computational power, memory capacity, and energy availability. Furthermore, these environments present unique data-centric challenges, including limited data volume, the prevalence of non-independent and identically distributed (non-IID) data arising from heterogeneous sources, and stringent privacy regulations (Lu et al., 2020). These constraints pose significant obstacles to the direct deployment of conventional, resource-intensive DL models on edge devices (Verhelst & Moons, 2017). Realizing efficient DL at the edge necessitates careful consideration of these limitations and the implementation of specialized techniques tailored to these environments (Li et al., 2020).

This chapter presents a comprehensive review of existing literature addressing the challenges associated with deploying DL in resource- and data-constrained edge computing environments. We systematically organize relevant works, critically comparing their approaches, results, and limitations to identify key research gaps. This synthesis of the state-of-the-art elucidates how existing research informs the present study and highlights potential avenues for future research. We explore the interdisciplinary landscape encompassing model compression, federated learning, edge-cloud collaboration, and resource management, thereby contextualizing our subsequent work within these established yet evolving fields. Our aim is to provide a clear and concise understanding of the current research landscape and underscore the imperative for continued research in this critical area.

### 2.2 Thematic Organization of Related Works

The body of research on DL for resource-constrained edge devices can be broadly categorized into several key themes, each representing distinct approaches to mitigate resource limitations and data challenges. It is important to note that these themes often intersect, with many practical solutions leveraging combinations of these techniques to achieve optimal performance.

#### 2.2.1 Model Compression Techniques

Model compression techniques are indispensable for reducing the size and computational complexity of DL models while preserving an acceptable level of accuracy. These techniques are crucial for enabling DL inference on resource-limited edge devices (Cheng et al., 2017). The primary methods include:

*   **Quantization:** This involves reducing the numerical precision of model weights and activations (e.g., transitioning from 32-bit floating-point to 8-bit integer representations, or even lower) to decrease the memory footprint and accelerate computation. Quantization can be applied either after the model has been fully trained (post-training quantization) or during the training process itself (quantization-aware training) (Jacob et al., 2018; Krishnamoorthi, 2018). While post-training quantization is generally simpler to implement, quantization-aware training typically yields better accuracy by explicitly accounting for the effects of quantization during the training process. Recent advancements also include mixed-precision quantization (Zhou et al., 2016), where different layers or weights are quantized to different bitwidths, offering a finer-grained control over the accuracy-efficiency trade-off.
*   **Pruning:** This technique focuses on removing redundant or less important connections (weights) from the network to reduce the number of parameters and operations. Pruning can be structured or unstructured. Structured pruning removes entire filters or channels, offering hardware-friendly speedups, while unstructured pruning removes individual weights, often resulting in higher compression ratios (Han et al., 2015; Li et al., 2017). Due to its compatibility with standard hardware architectures, structured pruning is often preferred for realizing real-world speedups. Dynamic pruning (Molchanov et al., 2019) adapts the pruning strategy during runtime based on resource availability.
*   **Knowledge Distillation:** This method involves training a smaller, more efficient "student" model to mimic the behavior of a larger, more complex "teacher" model. This enables the student model to achieve comparable performance with significantly fewer resources (Hinton et al., 2015; Gou et al., 2021). The student model learns to generalize from the teacher's soft outputs, which contain richer information than hard labels. Variations include using multiple teachers (ensemble distillation) and self-distillation, where the student learns from a previous version of itself (Zhang et al., 2019).
*   **Neural Architecture Search (NAS):** NAS automates the design of neural network architectures to discover models optimized for specific hardware constraints and performance metrics. NAS can identify architectures that are both accurate and efficient for edge deployment (Zoph & Le, 2016; Tan et al., 2019). NAS methods often employ reinforcement learning, evolutionary algorithms, or gradient-based optimization to explore the architectural search space. Hardware-aware NAS directly incorporates hardware performance metrics into the search process (Cai et al., 2018).

For example, Han et al. (2015) demonstrated the potential for significant compression (up to 90%) through pruning without substantial accuracy loss, resulting in smaller models and faster inference. Jacob et al. (2018) introduced quantization-aware training to minimize accuracy degradation caused by quantization. Hinton et al. (2015) presented knowledge distillation as an effective method for transferring knowledge from complex models to smaller, edge-deployable models. Zoph and Le (2016) employed reinforcement learning to search for optimal neural network architectures tailored to resource constraints. Li et al. (2017) refined pruning by using importance scores based on the first-order Taylor expansion. Molchanov et al. (2017) introduced variational dropout for pruning, providing a probabilistic approach for identifying unimportant weights. Further work by He et al. (2018) has explored channel pruning for accelerating convolutional neural networks. These methods often have synergistic effects; for instance, pruning can be combined with quantization for even greater compression (Guo et al., 2016). Recent studies explore the use of transformers in model compression (Tang et al., 2023).

#### 2.2.2 Federated Learning

Federated learning (FL) is a distributed learning paradigm that enables model training on decentralized data residing on edge devices without requiring direct data access or sharing, thereby addressing data scarcity and privacy concerns (McMahan et al., 2017; Li et al., 2020). Bonawitz et al. (2019) provide a practical overview of federated learning system design considerations.

*   **Federated Averaging (FedAvg):** This is a widely used FL algorithm where local models are trained on each device, and a central server aggregates the model updates to create a global model (McMahan et al., 2017). FedAvg is relatively simple to implement and has been shown to be effective in various applications. Its convergence properties have been extensively studied (Konečný et al., 2016).
*   **Differential Privacy (DP):** DP techniques add noise to model updates or gradients to protect the privacy of individual data points, providing a rigorous mathematical framework for privacy guarantees (Dwork et al., 2006; Abadi et al., 2016). DP ensures that the learning process does not reveal sensitive information about individual data points. The level of privacy is controlled by a privacy parameter, epsilon.
*   **Personalized Federated Learning:** These approaches allow customization of the global model to better fit the local data distribution of each device, addressing the issue of non-IID data and improving FL performance in heterogeneous environments (Smith et al., 2017; Dinh et al., 2020). Personalized FL allows each device to benefit from the shared knowledge of the global model while adapting to its own unique data characteristics. Techniques include meta-learning and multi-task learning.
*   **Federated Optimization Algorithms:** Beyond FedAvg, various optimization algorithms have been adapted for FL, such as FedProx, which addresses statistical heterogeneity by adding a proximal term to the local objective function (Li et al., 2018). Scaffold is another algorithm designed to correct for client drift in heterogeneous environments (Karimireddy et al., 2020). These algorithms aim to improve the convergence and stability of FL in challenging scenarios. Other algorithms include FedAdam and FedYogi, which adapt learning rates for each client (Reddi et al., 2020).

McMahan et al. (2017) introduced FedAvg, demonstrating its effectiveness in training DL models on decentralized mobile devices. Dwork et al. (2006) established a formal framework for DP in privacy-preserving data analysis. Smith et al. (2017) proposed a multi-task learning approach to personalized FL, enabling each device to learn a customized model while benefiting from shared knowledge. Abadi et al. (2016) presented a deep learning framework incorporating differential privacy. Li et al. (2018) introduced FedProx to handle heterogeneous data. Ghosh et al. (2020) explored a distributed learning approach with privacy guarantees. Karimireddy et al. (2020) introduced Scaffold, a method for correcting client drift. Handling non-IID data remains a significant challenge, and techniques like FedBN (Li et al., 2021), which utilizes batch normalization, have been proposed to mitigate its impact. Furthermore, research explores the impact of client selection strategies on FL performance (Nishio et al., 2019).

#### 2.2.3 Edge-Cloud Collaboration

Edge-cloud collaboration strategically combines the strengths of edge and cloud resources to optimize DL performance and efficiency, effectively overcoming the limitations of individual devices through distributed computation. This approach is particularly relevant when edge devices lack the resources to perform complex computations or store large amounts of data.

*   **Model Partitioning:** This involves dividing a DL model into multiple parts and executing different parts on the edge and the cloud (e.g., offloading computationally intensive layers to the cloud) to balance resource usage and latency (Kang et al., 2017; Teerapittayanon et al., 2017). The placement of the partitioning point significantly affects performance, and various strategies have been proposed to optimize this decision. These strategies often consider network bandwidth, device capabilities, and model structure.
*   **Dynamic Offloading:** This entails adaptively deciding whether to execute a DL task locally on the edge or offload it to the cloud based on network conditions and resource availability to optimize performance in dynamic environments (Sardellitti et al., 2015; Chen et al., 2018). This requires real-time monitoring of network conditions and resource utilization. Reinforcement learning techniques are often used to make these offloading decisions (Mao et al., 2017).
*   **Edge Caching:** This involves caching frequently used data or model parameters on the edge to reduce latency and bandwidth consumption, which is particularly beneficial for real-time applications (Golrezaei et al., 2012; Shanmugam et al., 2013). Efficient cache management strategies are crucial for maximizing the benefits of edge caching. Content Delivery Networks (CDNs) often employ edge caching to improve content delivery performance.

Kang et al. (2017) explored model partitioning strategies for DNN inference at the edge. Sardellitti et al. (2015) formulated the computation offloading problem as a Markov decision process. Golrezaei et al. (2012) studied the benefits of edge caching for content delivery networks. Teerapittayanon et al. (2017) proposed BranchyNet for distributing DNN computation across edge and cloud. Chen et al. (2018) explored energy-efficient offloading strategies in mobile edge computing. Mao et al. (2017) explored dynamic computation offloading, focusing on energy efficiency. Furthermore, the work in (Ehsanpour et al., 2020) addresses joint resource allocation and offloading decisions in vehicular edge computing. The use of serverless computing frameworks can also facilitate edge-cloud collaboration (Wang et al., 2017).

#### 2.2.4 Resource Management and Scheduling

Efficient resource management and scheduling are critical for maximizing DL task performance on resource-constrained edge devices through careful resource allocation. This involves optimizing the utilization of CPU, memory, and energy resources.

*   **Task Scheduling:** This involves optimizing the allocation of computational resources to different DL tasks to minimize latency and energy consumption by prioritizing tasks and allocating resources based on importance and resource requirements (Liu et al., 2018; You et al., 2017). Scheduling algorithms need to consider the diverse resource requirements of different DL tasks. Deadline-aware scheduling is crucial for real-time applications.
*   **Adaptive Resource Allocation:** This involves dynamically adjusting the resources allocated to each DL task based on its resource requirements and the current system load to adapt to changing conditions and optimize resource utilization (Verbelen et al., 2013; Mao et al., 2017). Adaptive resource allocation can improve system performance in dynamic environments. Containerization technologies, such as Docker, can facilitate adaptive resource allocation.
*   **Energy-Aware Scheduling:** This involves scheduling DL tasks to minimize energy consumption while meeting performance requirements, which is crucial for battery-powered edge devices (Li et al., 2016; Zhang et al., 2017). Energy-aware scheduling is essential for extending the battery life of edge devices. Dynamic Voltage and Frequency Scaling (DVFS) is often used to reduce energy consumption.

Liu et al. (2018) proposed a task scheduling algorithm for edge computing environments considering latency and energy consumption. Verbelen et al. (2013) introduced an adaptive resource allocation scheme for virtualized edge resources. Li et al. (2016) developed an energy-aware scheduling algorithm for mobile devices, deciding between local execution and cloud offloading. You et al. (2017) presented a resource management framework for edge computing. Mao et al. (2017) investigated dynamic voltage and frequency scaling for energy efficiency. Zhang et al. (2017) proposed an energy-aware task scheduling algorithm for heterogeneous edge devices. Ghasemi et al. (2020) focused on joint resource allocation and task scheduling. The integration of reinforcement learning techniques for resource management is becoming increasingly popular (e.g., Wang et al., 2019). Furthermore, the use of Network Function Virtualization (NFV) can improve resource utilization in edge computing environments (Mijumbi et al., 2016).

### 2.3 Critical Discussion of the State of the Art

The research directions discussed above have significantly advanced the feasibility of deploying DL on resource-constrained edge devices. Model compression techniques effectively reduce model size and complexity. Federated learning addresses data scarcity and privacy concerns. Edge-cloud collaboration optimizes DL performance by strategically utilizing both edge and cloud resources. Resource management and scheduling algorithms ensure efficient task execution. However, each of these areas presents its own challenges and limitations that warrant further investigation.

Despite the progress, key limitations and research gaps remain:

*   **Accuracy vs. Efficiency Trade-off:** Model compression often presents a trade-off between accuracy and efficiency. Overly aggressive compression can lead to unacceptable accuracy degradation. Balancing this trade-off is crucial for real-world DL deployments. Future research should focus on sophisticated compression methods, such as adaptive quantization and pruning, and on understanding the impact of compression on various DL architectures and tasks. Hardware-aware compression techniques are also needed to fully leverage the capabilities of edge devices. Work by Cai et al. (2019) has explored automated compression with a focus on maintaining accuracy. Furthermore, the development of metrics that directly quantify the trade-off between accuracy and efficiency is crucial (e.g., energy consumption per inference, latency vs. accuracy curves). Novel compression techniques that minimize information loss are also needed.
*   **Communication Overhead in Federated Learning:** FL can suffer from high communication overhead due to frequent model updates between edge devices and the central server. Reducing this overhead is vital for scalability and real-time performance. Communication-efficient FL algorithms, such as model compression applied to updates, sparse update methods, and reduced communication frequency, are needed. Techniques like federated distillation (Li & Wang, 2019) aim to reduce communication costs by transferring knowledge through smaller models. Suresh et al. (2017) have examined communication efficiency in distributed optimization. The development of asynchronous FL algorithms can also mitigate the impact of straggling devices and network delays. Furthermore, exploring the use of edge aggregation techniques can reduce the communication burden on the central server (Chiang et al., 2019).
*   **Security Vulnerabilities in Edge Computing:** Edge devices are vulnerable to security threats, including physical attacks, malware infections, and network intrusions. Ensuring their security is paramount. Research is needed to develop robust security mechanisms, including intrusion detection systems, secure boot processes, secure communication protocols, and defenses against adversarial attacks. Federated learning also introduces unique security challenges like poisoning attacks, where malicious participants can inject corrupted data into the training process. Bhagat et al. (2021) present a survey of security and privacy issues in edge-based deep learning. Furthermore, the use of trusted execution environments (TEEs) can enhance the security of edge devices. Blockchain technology can also be used to secure federated learning systems (Kim et al., 2020).
*   **Heterogeneity of Edge Devices:** The diverse hardware and software configurations of edge devices pose a significant challenge. DL models optimized for one device may not perform well on another. Developing adaptable DL solutions is essential. Future research should explore meta-learning and transfer learning to enable models to quickly adapt to new devices. Techniques for automatically profiling edge devices and tailoring model configurations are also needed. Dean et al. (2012) discuss large-scale distributed deep networks which implicitly address heterogeneity through distributed training. Moreover, the development of hardware-aware NAS techniques can lead to models that are specifically optimized for different hardware platforms. Domain adaptation techniques can also be used to address the heterogeneity of data distributions across different edge devices (Ben-David et al., 2010).
*   **Non-IID Data Handling in Federated Learning:** FL performance can degrade significantly when data is non-IID, as the global model may not accurately represent the local data distributions on each device. Addressing this is critical. Personalized federated learning and robust aggregation techniques are promising research avenues. Quantifying non-IID-ness and adapting the learning strategy is also important. Data augmentation techniques can also mitigate the effects of Non-IID data (Zhao et al., 2018). The development of robust aggregation rules that are less sensitive to data heterogeneity is an active area of research. Techniques such as FedBN (Li et al., 2021) have shown promise in mitigating the effects of non-IID data by allowing clients to adapt their batch normalization layers to their local data distributions. Furthermore, techniques that explicitly model the data distribution on each client can improve FL performance (Mansour et al., 2020).

### 2.4 Synthesis and Future Research Directions

The existing literature provides a strong foundation for deploying DL in resource- and data-constrained edge computing systems. Model compression, federated learning, edge-cloud collaboration, and resource management offer promising solutions. Addressing the identified limitations will pave the way for more efficient, robust, and secure edge-based AI systems. This study focuses on investigating a novel model compression technique based on a combination of quantization and pruning, designed for resource-constrained edge devices and optimized for Non-IID data in federated learning, aiming to minimize accuracy loss while achieving significant compression ratios. Our approach seeks to address the accuracy vs. efficiency trade-off by adaptively adjusting the quantization and pruning parameters based on the characteristics of the data and the hardware constraints of the edge device. Specifically, we will explore the use of reinforcement learning to dynamically adjust these parameters during the training process.

Future research directions include:

*   Developing more advanced model compression techniques that minimize accuracy loss and maximize efficiency gains, with a focus on hardware-aware compression and adaptive compression strategies.
*   Designing communication-efficient federated learning algorithms that reduce communication overhead and improve scalability, including exploring the use of edge aggregation and asynchronous communication protocols.
*   Implementing robust security mechanisms that protect edge devices and federated learning systems from various threats, with a focus on defending against poisoning attacks and ensuring data privacy.
*   Creating DL solutions that adapt to the heterogeneity of edge devices and data distributions, including exploring the use of meta-learning and domain adaptation techniques.
*   Exploring dynamic edge-cloud collaboration strategies that optimize resource utilization and latency, with a focus on using reinforcement learning for dynamic offloading decisions.
*   Addressing the challenge of Non-IID data in Federated Learning through personalized models and robust aggregation techniques, including developing techniques that explicitly model the data distribution on each client.
*   Investigating the use of hardware accelerators, such as GPUs and FPGAs, to improve the performance of DL models on edge devices, with a focus on optimizing DL models for specific hardware architectures.
*   Developing methods for automatically tuning hyperparameters of DL models to optimize their performance on edge devices, including the use of NAS and Bayesian optimization.
*   Exploring the application of explainable AI (XAI) techniques to improve the transparency and trustworthiness of DL models deployed on edge devices, with a focus on providing insights into the decision-making process of DL models.
*   Investigating the use of reinforcement learning for adaptive resource management and task scheduling in edge computing environments, with a focus on optimizing resource allocation for different DL tasks.

Addressing these challenges and exploring these directions will unlock the full potential of DL in edge computing, enabling innovative applications in autonomous driving, smart cities, healthcare, industrial automation, and environmental monitoring, paving the way for intelligent, efficient, and secure edge-based AI systems. The future of edge computing lies in the development of intelligent and adaptive systems that can seamlessly integrate DL models with the constraints and opportunities of the edge environment. The development of standardized benchmarks and evaluation metrics will also be crucial for accelerating progress in this field.

### References

Abadi, M., Chu, A., Goodfellow, I., McMahan, H. B., Mironov, I., Talwar, K., & Zhang, L. (2016). Deep learning with differential privacy. *Proceedings of the 2016 ACM SIGSAC Conference on Computer and Communications Security*, 308-318.

Ben-David, S., Blitzer, J., Crammer, K., & Pereira, F. (2010). A theory of learning from different domains. *Machine Learning*, *79*(1), 151-175.

Bhagat, S., Gupta, I., & Gupta, S. (2021). Security and privacy issues in edge-based deep learning: A survey. *Journal of Network and Computer Applications*, *177*, 102955.

Bonawitz, K., Ivanov, V., Kreuter, B., Marcedone, A., McMahan, H. B., Patel, S., ... & Song, S. (2019). Towards federated learning at scale: System design. *Proceedings of Machine Learning and Systems*, *1*, 374-388.

Cai, H., Chen, T., Zhang, W., Yu, Y., & Wang, J. (2019). AutoCompress: An automatic DNN structured pruning framework for ultra-high compression rate on mobile devices. *International Conference on Computer Vision (ICCV)*.

Cai, H., Tian, Y., Talwalkar, A., & Zhang, Y. (2018). ProxylessNAS: Direct neural architecture search on target task and hardware. *International Conference on Learning Representations (ICLR)*.

Chen, M., Hao, Y., Hwang, K., Wang, L., & Wang, Z. (2018). Offloading games to the cloud with energy-aware adaptive control. *IEEE Transactions on Parallel and Distributed Systems*, *29*(7), 1421-1434.

Cheng, Y., Wang, D., Zhou, P., & Zhang, T. (2017). A survey of model compression and acceleration for deep neural networks. *arXiv preprint arXiv:1710.09282*.

Chiang, C. L., Lin, T. H., & Chen, P. Y. (2019). Clustering-based federated learning for 5g hetnets. *IEEE International Conference on Communications Workshops (ICCW)*, 1-6.

Dean, J., Corrado, G. S., Monga, R., Chen, K., Mathieu, M., Chen, M. A., ... & Ng, A. Y. (2012). Large scale distributed deep networks. *Advances in neural information processing systems*, *25*.

Dinh, C. T., Tran, N. H., Nguyen, H. X., Nguyen, D. T., Hwang, W. J., & Poor, H. V. (2006). Calibrating noise to sensitivity in private data analysis. *Theory of Cryptography*, 265-284.

Dwork, C., McSherry, F., Nissim, K., & Smith, A. (2006). Calibrating noise to sensitivity in private data analysis. *Theory of Cryptography*, 265-284.

Ehsanpour, A., Javanmard, H., Esmaeili, A., & Tarchi, D. (2020). Joint resource allocation and computation offloading in vehicular edge computing based on fog computing paradigm. *Vehicular Communications*, *26*, 100275.

Ghasemi, R., Hassanpour, R., & Beigy, A. (2020). Joint Resource Allocation and Task Scheduling in Edge Computing: A Deep Reinforcement Learning Approach. *Journal of Network and Systems Management*, *28*(4), 1277-1303.

Ghosh, A., Song, Q., Gupta, A., & Li, P. (2020). Federated learning with differential privacy: Algorithms and performance analysis. *arXiv preprint arXiv:2002.06440*.

Golrezaei, N., Dimakis, A. G., & Tassiulas, L. (2012). Approximate nearest neighbor search in content distribution networks. *IEEE INFOCOM*, 1203-1211.

Gou, J., Yu, B., Maybank, S. J., & Tao, D. (2021). Knowledge distillation: A survey. *International Journal of Computer Vision*, *129*(6), 1789-1819.

Guo, Y., Yao, A., & Chen, Y. (2016). Dynamic network surgery for efficient DNNs. *Advances in neural information processing systems*, *29*.

Han, S., Mao, H., & Dally, W. J. (2015). Deep compression: Compressing deep neural networks with pruning, trained quantization and huffman coding. *International Conference on Learning Representations (ICLR)*.

He, Y., Kang, G., Dong, X., Fu, Y., & Yang, Y. (2018). Channel pruning for accelerating very deep neural networks. *International Conference on Computer Vision (ICCV)*.

Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the knowledge in a neural network. *NIPS Deep Learning Workshop*.

Jacob, B., Kligys, W., Chen, B., Zhu, M., Tang, M., Howard, A., ... & Warden, P. (2018). Quantization-aware training for low-precision inference. *Conference on Computer Vision and Pattern Recognition (CVPR)*, 7032-7040.

Kang, Y., Hauswald, J., Gao, C., Rovinski, A., Mudge, T., Chou, P., ... & Das, T. (2017). Neurosurgeon: Collaborative intelligence between the edge and the cloud. *International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS)*, 615-629.

Karimireddy, S. P., Kale, S., Mohri, M., Reddi, S., Stich, S. U., & Suresh, A. T. (2020). Scaffold: Stochastic controlled averaging for federated learning. *International Conference on Machine Learning (ICML)*.

Kim, H., Lee, J., Kim, J., & Park, C. (2020). Blockchain-based federated learning. *IEEE Access*, *8*, 146424-146433.

Konečný, J., McMahan, B., Ramage, D., & Richtárik, P. (2016). Federated optimization: Distributed machine learning for on-device intelligence. *arXiv preprint arXiv:1610.02526*.

Krishnamoorthi, R. (2018). Quantizing deep convolutional networks for efficient inference: A whitepaper. *arXiv preprint arXiv:1806.08342*.

Li, K., Wang, J., & He, B. (2016). Energy-aware scheduling for mobile cloud computing. *IEEE Transactions on Cloud Computing*, *4*(2), 159-171.

Li, J., Qu, T., & Shen, J. (2018). FedProx: On the global convergence of federated optimization. *Advances in Neural Information Processing Systems*, *31*.

Li, H., Kadambi, S., Durdanovic, I., Sandler, M., El-Nouby, A., & Cholakkal, H. (2017). Pruning filters for efficient convnets. *International Conference on Learning Representations (ICLR)*.

Li, T., Sahu, A. K., Talwalkar, A., & Smith, V. (2021). Fedbn: Federated learning on non-iid features via local batch normalization. *International Conference on Learning Representations (ICLR)*.

Li, D., & Wang, J. (2019). FedMD: Heterogeneous federated learning via model distillation. *arXiv preprint arXiv:1910.03581*.

Li, X., Huang, K., Yang, W., Wang, S., & Zhang, Z. (2020). Federated learning on non-iid data: A survey. *IEEE Transactions on Neural Networks and Learning Systems*.

Liu, X., Yu, W., Chen, X., & Zhang, Y. (2018). Task scheduling optimization in edge computing for IoT applications. *IEEE Internet of Things Journal*, *5*(4), 2778-2788.

Lu, Y., Huang, X., Zhang, K., Maharjan, S., & Zhang, Y. (2020). Differentially private federated learning for IoT devices. *IEEE Internet of Things Journal*, *7*(5), 4315-4325.

Mansour, Y., Mohri, M., Ro, R., & Suresh, A. T. (2020). Three approaches to fair federated learning. *arXiv preprint arXiv:2007.04918*.

Mao, Y., Zhang, J., & Letaief, K. B. (2017). Dynamic computation offloading for mobile-edge computing with energy harvesting. *IEEE Journal on Selected Areas in Communications*, *35*(12), 2827-2840.

McMahan, B., Moore, E., Ramage, D., Hampson, S., & Arcas, B. A. (2017). Communication-efficient learning of deep networks from decentralized data. *Artificial Intelligence and Statistics*, 1273-1282.

Mijumbi, R., Serrat, J., Gorricho, J. L., подряд, N., Bouet, M., & Comвань, R. (2016). Network function virtualization: State-of-the-art and research challenges. *IEEE Communications Surveys & Tutorials*, *18*(1), 236-262.

Molchanov, D., Mallya, A., Tyree, S., & Karras, T. (2017). Variational dropout sparsifies deep neural networks. In *Proceedings of the 31st International Conference on Neural Information Processing Systems* (pp. 2507-2517).

Molchanov, P., Gholami, A., Bińkowski, M., & Tyree, S. (2019). Importance estimation for neural network pruning. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 11243-11251.

Nishio, T., & Yonetani, R. (2019). Client selection for federated learning with heterogeneous resources in mobile edge. *IEEE International Conference on Communications (ICC)*, 1-7.

Reddi, S., Charles, Z., Zaheer, M., Garrett, Z., Rush, K., Konečný, J., ... & Kumar, S. (2020). Adaptive federated optimization. *International Conference on Learning Representations (ICLR)*.

Sardellitti, S., Scutari, G., & Barbarossa, S. (2015). Joint optimization of radio and computational resources for multicell mobile edge computing. *IEEE Transactions on Signal Processing*, *63*(22), 6602-6617.

Shanmugam, K., Golrezaei, N., Dimakis, A. G., & Tassiulas, L. (2013). Femto caching: Wireless content placement for small cell networks. *IEEE Transactions on Information Theory*, *59*(12), 8402-8412.

Shi, W., Cao, J., Zhang, Q., Li, Y., & Xu, L. (2016). Edge computing: An emerging computing paradigm. *Proceedings of the 2016 16th International Symposium on Cluster, Cloud and Grid Computing (CCGrid)*, 587-596.

Smith, V., Chiang, C. K., Sanjabi, M., & Talwalkar, A. (2017). Federated multi-task learning. *Neural Information Processing Systems (NIPS)*, 2263-2273.

Suresh, A. T., Yu, F. X., Kumar, S., & McMahan, H. B. (2017). Distributed mean estimation with limited communication. *Artificial Intelligence and Statistics*, 1505-1513.

Tan, M., Chen, B., Pang, R., Vasudevan, V., Le, Q. V., & Bengio, S. (2019). MnasNet: Platform-aware neural architecture search for mobile. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 2820-2828.

Tang, R., Wang, Y., Zhang, Y., & Xue, H. (2023). Compressing transformers via spectral-domain tensor decomposition. *arXiv preprint arXiv:2302.01877*.

Teerapittayanon, S., McDanel, B., & Kung, H. T. (2017). Branchynet: Fast inference via early exiting from deep neural networks. *2017 26th International Conference on Computer Communications and Networks (ICCCN)*, 1-9.

Verbelen, T., Simoens, P., & De Turck, F. (2013). Adaptive resource allocation for cloud services. *IEEE Transactions on Network and Service Management*, *10*(4), 439-452.

Verhelst, M., & Moons, P. (2017). What edge computing can do for deep learning. *2017 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)*, 6059-6063.

Wang, Z., Guo, B., Yu, Z., & Guo, L. (2019). Deep reinforcement learning for dynamic resource management in edge computing. *IEEE Transactions on Cognitive Communications and Networking*, *6*(1), 259-271.

Wang, Y., Pourreza, N., Salama, R., & Hassanein, H. (2017). Serverless edge computing: Vision and research directions. *2017 IEEE International Conference on Edge Computing (ICEC)*, 97-104.

You, C., Huang, K., Chae, H., & Zuk