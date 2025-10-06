## Chapter 2: Related Works: Conformance Testing of REST-based Web Services

### 2.1 Introduction

Representational State Transfer (REST) has emerged as the dominant architectural style for designing web services, lauded for its simplicity, scalability, and ease of integration [1, 2]. In this paradigm, ensuring reliability and interoperability necessitates rigorous adherence to established standards and specifications. Conformance testing provides a crucial mechanism for verifying that RESTful services behave as defined by their specifications (e.g., OpenAPI/Swagger, RAML) [3, 4]. This chapter presents a comprehensive review of existing literature on conformance testing of REST-based web services. We identify key approaches, techniques, and tools employed by researchers and practitioners, highlighting their strengths, limitations, and current research gaps. The chapter is thematically organized to facilitate a comparative analysis of different methodologies based on their underlying principles and capabilities. By establishing this contextual framework, we lay the groundwork for subsequent chapters and effectively contextualize the research presented in this dissertation. A thorough understanding of the current landscape of conformance testing enables us to position our work within the existing body of knowledge and highlight its unique contributions [5]. This chapter addresses the critical need for robust testing strategies in the evolving landscape of web service architectures, particularly concerning the increasing complexity and dynamism of modern APIs [6]. Furthermore, we emphasize the growing importance of automated and continuous conformance testing in modern DevOps and CI/CD environments [7].

### 2.2 Thematic Organization of Related Works

This section provides a thematic organization of related works, grouping them based on the primary approach used for conformance testing. The core themes explored are: (1) specification-based testing, (2) model-based testing, (3) mutation testing, and (4) hybrid approaches. Each theme provides a unique perspective on ensuring RESTful service compliance [8]. These themes represent the major paradigms in RESTful service testing and provide a structured way to analyze the field. Each approach is examined in detail, considering its theoretical underpinnings, practical applications, and documented limitations, providing a balanced view of the field and a clear understanding of their applicability in different scenarios. This thematic organization allows for a more nuanced understanding of the trade-offs associated with each approach and facilitates the identification of opportunities for future research.

#### 2.2.1 Specification-Based Testing

Specification-based testing leverages formal or semi-formal specifications of the RESTful service to derive test cases. The OpenAPI Specification (OAS), formerly known as Swagger, is the most commonly used specification language in this domain [9]. Other specification languages, such as RAML (RESTful API Modeling Language) [10], and API Blueprint [11] also play a role. This approach operates on the principle that a well-defined specification provides a clear contract for testing. The accuracy and completeness of the specification are paramount to the effectiveness of this approach [12]. Specification-based testing is often favored for its relative ease of implementation and automation, making it a popular choice in industrial settings [13]. Its reliance on machine-readable specifications enables automated test generation and execution, contributing to faster feedback cycles and improved efficiency.

Richardson and Ruby (2007) emphasized the critical role of REST architectural constraints and advocated for testing adherence to these constraints [1]. They proposed a methodology to verify the correct use of HTTP methods, status codes, and hypermedia links, laying the foundation for specification-based testing. While their work primarily outlines principles rather than specific automated testing techniques, it highlights the importance of verifying fundamental REST principles. However, their work predates the widespread adoption of specification formats like OpenAPI, limiting its direct applicability to modern REST API development workflows. The increasing availability of tools and frameworks that support OpenAPI-based testing has significantly enhanced the practicality of specification-based testing [14].

Several researchers have focused on developing tools to automate test case generation from API specifications. Delamare et al. (2013) presented an approach for generating test cases from RESTful API specifications described in WADL (Web Application Description Language), utilizing boundary value analysis and equivalence partitioning to create test inputs [15]. Their approach offers a systematic way to explore the input space of the API, although WADL has been largely superseded by OpenAPI. Nevertheless, the techniques they introduced remain relevant and can be adapted to OpenAPI specifications. Similarly, Garcia et al. (2014) introduced RESTest, a tool designed to automatically generate test cases from OpenAPI specifications, employing a constraint solver to ensure the generated input values satisfy the constraints defined in the specification [16]. RESTest exemplifies the practical application of specification-based testing by providing automated test generation and execution, demonstrating the feasibility and benefits of this approach. Other notable tools include Dredd [17], which validates API endpoints against API Blueprint descriptions, and Swagger Inspector (SmartBear Software) [18], which allows for dynamic inspection and validation of APIs against their OpenAPI definitions.

Postman (n.d.) is a widely adopted tool for testing APIs, including RESTful services [19]. While primarily used for manual testing, Postman also supports automated testing through its collection runner and scripting capabilities. Users can define test suites and assertions based on the API specification, enabling a degree of automation. However, Postman relies on user-defined tests, which can be time-consuming to create and maintain, especially for complex APIs. Tools like ReadyAPI (SmartBear Software) [20] offer similar functionalities, providing a comprehensive environment for API testing and management. These tools often integrate with CI/CD pipelines, facilitating automated conformance testing as part of the software development lifecycle [21]. Furthermore, the rise of API gateways has facilitated the enforcement of API contracts and the monitoring of API conformance in real-time [22].

*Limitations:* A significant limitation of specification-based testing lies in its dependence on the quality and completeness of the specification. If the specification is incomplete, inaccurate, or outdated, the generated test cases may not provide adequate coverage of the service's behavior, leading to potential vulnerabilities and interoperability issues [23]. Addressing these limitations requires incorporating techniques to validate the specification itself, such as specification mining [24], and to complement specification-based tests with other approaches, such as fault injection [25]. Furthermore, these approaches often struggle with testing complex business logic not explicitly defined in the specification, necessitating the integration of more advanced testing methodologies. Specification-based testing also frequently overlooks non-functional requirements, such as performance and security [26]. Techniques for automatically detecting inconsistencies and ambiguities in API specifications are an active area of research [27].

#### 2.2.2 Model-Based Testing

Model-based testing (MBT) employs formal models of the system under test (SUT) to generate test cases. These models, which can include finite state machines, Petri nets, or other formalisms, aim to capture the behavior of the RESTful service in an abstract and precise manner [28]. MBT provides a systematic way to explore different execution paths and states of the service, potentially enabling more comprehensive testing than specification-based approaches alone [29]. The use of formal models allows for rigorous analysis and verification of the system's behavior. MBT is particularly useful for testing complex stateful interactions within REST APIs [30]. By explicitly modeling the state transitions and dependencies within the API, MBT can uncover subtle errors that might be missed by other techniques.

Offutt and Abdurazik (1999) discussed various aspects of testing web applications, proposing the use of finite state machines to model the application's navigation structure and generate test cases to cover all possible paths [31]. This approach is valuable for testing the interaction between different resources in a RESTful service, ensuring that state transitions occur as expected. However, applying this to complex REST APIs can be challenging due to the state explosion problem [32], which can render the model intractable. Techniques to mitigate state explosion, such as using abstraction and hierarchical modeling, are crucial for applying MBT to realistic REST APIs [33]. Moreover, the creation and maintenance of accurate and up-to-date models can be a significant undertaking.

Forneari et al. (2013) presented an MBT approach specifically tailored for RESTful services, utilizing the RESTful Modeling Language (RML) [34]. Their work demonstrated that MBT can automatically generate test cases to verify a service's conformance to REST architectural principles, offering a more comprehensive approach than relying solely on specifications. This approach allows for verification of the underlying architectural principles, such as statelessness and uniform interface, which are often neglected in purely specification-based testing. Other approaches use UML [35] or statecharts [36] to model REST APIs for testing purposes. The use of domain-specific modeling languages (DSMLs) can also simplify the modeling process and improve the relevance of the generated test cases [37].

*Limitations:* Creating and maintaining accurate models of complex RESTful services presents a significant challenge. The modeling process can be time-consuming and requires specialized expertise [38]. Furthermore, MBT may not scale effectively for large and intricate systems, as the complexity of the model can grow exponentially with the size of the service. Model maintenance and keeping the model synchronized with the actual service implementation are also critical concerns, requiring robust configuration management and version control practices. Techniques for automatically inferring models from existing APIs using machine learning [39] are being explored to address these limitations, promising to reduce the manual effort involved in model creation. Another limitation is the difficulty in representing data constraints and complex data transformations within the models [40]. The integration of MBT with continuous integration and continuous delivery pipelines also presents challenges, requiring automated model validation and test generation capabilities [41].

#### 2.2.3 Mutation Testing

Mutation testing involves introducing small, artificial faults (mutations) into the source code or specification of the SUT. Test cases are then executed to determine if they can detect these faults. The effectiveness of the test suite is quantified by the mutation score, representing the percentage of mutants "killed" (i.e., detected) by the test cases [42]. Mutation testing provides a rigorous assessment of test suite quality, complementing other testing approaches by identifying weaknesses in existing test cases. By systematically introducing faults, mutation testing helps to ensure that the test suite is capable of detecting a wide range of potential errors. It's particularly effective in uncovering subtle errors that might be missed by other testing methods [43]. Furthermore, mutation testing can provide valuable feedback to developers on how to improve their code and test cases.

Delgado et al. (2018) presented a mutation testing approach specifically designed for RESTful APIs [44]. They introduced a set of mutation operators tailored to RESTful services, such as modifying HTTP methods, status codes, and request parameters. Their evaluation, conducted on real-world RESTful APIs, demonstrated the effectiveness of mutation testing in identifying weaknesses in existing test suites. This research highlighted the importance of using REST-specific mutation operators to effectively target potential faults in RESTful services, leading to more effective and targeted testing. Other research has explored the use of mutation testing to evaluate the fault-finding capability of automatically generated test suites [45]. The definition of appropriate mutation operators is crucial for the effectiveness of mutation testing, and requires careful consideration of the specific characteristics of the system under test [46].

*Limitations:* Mutation testing can be computationally expensive. Running a test suite against a large number of mutants requires significant processing time and resources [47]. This cost can be prohibitive for large and complex RESTful services. Furthermore, generating meaningful and non-trivial mutants requires careful design of the mutation operators. Techniques such as mutant selection and parallel execution are used to mitigate the computational cost [48], making mutation testing more practical for large-scale applications. Mutant equivalence, where different mutants produce the same behavior, also poses a challenge, requiring techniques for identifying and removing equivalent mutants [49]. Despite its computational cost, mutation testing remains a valuable technique for assessing and improving the quality of test suites. The development of more efficient mutation testing techniques is an ongoing area of research [50].

#### 2.2.4 Hybrid Approaches

Hybrid approaches combine different testing techniques to leverage their complementary strengths. These approaches aim to overcome the limitations of individual techniques by integrating them into a more comprehensive testing strategy [51]. For example, combining specification-based testing with model-based testing can leverage the automation capabilities of the former and the comprehensive coverage of the latter. Hybrid approaches are increasingly recognized as the most effective way to achieve thorough and reliable testing of RESTful services. They allow for a more nuanced and adaptable testing process, tailored to the specific characteristics of the API under test [52]. The key to a successful hybrid approach is to carefully select and integrate the appropriate techniques to address the specific testing challenges.

Nguyen et al. (2014) proposed a hybrid approach that combines specification-based testing with fault injection to test the reliability of RESTful services [53]. They generate test cases from the API specification and then inject faults into the service to simulate real-world errors, providing a more realistic assessment of the service's resilience. This approach enhances the robustness of testing by simulating unexpected conditions and potential failure scenarios. Another hybrid approach combines fuzzing with specification-based testing to explore unexpected inputs and validate error handling [54]. The combination of different testing techniques can lead to a more comprehensive and effective testing strategy.

Fraser and Wotawa (2011) describe combining contract-based testing with random testing to achieve better coverage and fault detection [55]. Contract-based testing ensures adherence to predefined contracts, while random testing explores unexpected inputs and behaviors, leading to more robust and comprehensive testing. Combining static analysis with dynamic testing is another promising hybrid approach, allowing for early detection of potential issues and more targeted dynamic testing [56]. The integration of different testing techniques requires careful planning and coordination, but can result in significant improvements in software quality.

*Limitations:* Hybrid approaches can be more complex to implement than single-technique approaches, requiring careful integration of the different testing methodologies [57]. The effectiveness of a hybrid approach depends on the synergy between the combined techniques and the expertise of the testers in orchestrating them. The increased complexity can also make it difficult to analyze and interpret the test results. Careful planning and design are crucial for successful implementation of hybrid testing strategies, ensuring that the benefits outweigh the added complexity. Furthermore, the selection of appropriate techniques for a hybrid approach depends on the specific characteristics of the API and the testing goals [58]. The development of automated tools and frameworks to support hybrid testing is an important area of research [59].

### 2.3 Critical Discussion of the State of the Art

The current state of the art in conformance testing of REST-based web services is characterized by a significant emphasis on leveraging API specifications, particularly OpenAPI/Swagger, for automated test case generation. Tools like RESTest, Postman, and ReadyAPI have gained widespread adoption among developers for both manual and automated API testing. Model-based testing offers a more formal and rigorous approach but faces challenges related to scalability and the effort required for model creation and maintenance. Mutation testing is recognized as an effective method for evaluating the quality of test suites but can be computationally demanding. Hybrid approaches are gaining traction as a way to combine the strengths of different techniques, reflecting a growing recognition of the need for comprehensive and integrated testing strategies. The increasing adoption of DevOps practices and CI/CD pipelines has also driven the need for automated and continuous conformance testing solutions [60]. However, existing approaches often lack the sophistication to handle the complexities of modern APIs and the ever-evolving landscape of web service technologies.

Despite these advancements, several limitations persist:

*   **Lack of Standardized Test Suites:** The absence of standardized test suites for evaluating the conformance of RESTful services to specific industry standards and best practices hinders interoperability and consistency across different implementations [61]. This lack of standardization makes it difficult to compare the conformance of different RESTful services objectively and impedes the development of common testing methodologies. Standardized test suites would also facilitate certification and compliance with industry regulations [62]. Furthermore, the lack of a common vocabulary and terminology in the field of RESTful API testing can hinder communication and collaboration among researchers and practitioners [63].
*   **Limited Support for Complex Interactions:** Existing approaches often struggle to adequately handle complex interactions between resources, such as those involving hypermedia (Hypermedia as the Engine of Application State - HATEOAS) or asynchronous communication patterns [64]. Testing of complex workflows remains a challenge, especially when dealing with stateful interactions and intricate dependencies between resources. The dynamic nature of hypermedia-driven APIs makes testing particularly challenging [65]. The development of new testing techniques that can effectively handle these complex interactions is a crucial area of research [66].
*   **Insufficient Coverage of Security Aspects:** Security testing of RESTful services is often treated as a separate concern, rather than being integrated directly into the conformance testing process [67]. A need exists for more holistic approaches that seamlessly combine conformance and security testing, ensuring that services not only adhere to functional specifications but also meet security requirements, such as authentication, authorization, and data validation. Integrating security testing into the CI/CD pipeline is crucial for identifying vulnerabilities early in the development process [68]. The OWASP API Security Top 10 provides a valuable resource for identifying common security vulnerabilities in APIs [69].
*   **Difficulty in Handling Dynamic APIs:** The dynamic nature of modern APIs, which evolve frequently, poses a significant challenge for existing testing approaches [70]. Test cases need to be updated continuously to reflect API changes, increasing the maintenance burden. Automated techniques for detecting and adapting to API changes are needed, such as continuous testing frameworks [71] that integrate with API management platforms. Version control and automated regression testing are essential for managing API evolution [72]. Furthermore, the increasing use of microservices architectures introduces new challenges for API testing, requiring distributed testing and monitoring techniques [73].

### 2.4 Research Gaps

The review of the literature reveals several key research gaps in the field of conformance testing for REST-based web services:

*   **Automated Generation of Test Oracles:** While significant progress has been made in automating test input generation, the problem of automatically generating test oracles (i.e., the expected outputs for given inputs) remains largely unaddressed [74]. This requires intelligent techniques for inferring the correct behavior of the service, potentially using machine learning or formal methods, to predict the expected outputs based on the inputs and the API specification. Generating test oracles for complex data structures and stateful interactions is particularly challenging [75]. The development of automated test oracle generation techniques is crucial for reducing the manual effort involved in API testing.
*   **Adaptive Testing Techniques:** There is a need for adaptive testing techniques that can automatically adjust the test strategy based on the observed behavior of the SUT [76]. These techniques should be able to learn from past test results and prioritize testing of areas that are more likely to contain faults. Reinforcement learning could be applied to this area, enabling the testing framework to learn and optimize its testing strategy over time. Adaptive testing can also be used to prioritize testing based on risk and business impact [77]. The use of machine learning to predict fault-prone areas of the API can significantly improve the efficiency of testing [78].
*   **Integration of AI and Machine Learning:** Artificial intelligence (AI) and machine learning (ML) techniques hold promise for improving various aspects of conformance testing, including test case generation, fault localization, and test prioritization [79]. ML can be used to learn patterns in API behavior and generate more effective test cases, while AI can be used to automate the analysis of test results and identify potential issues. Natural Language Processing (NLP) can be used to analyze API documentation and generate test cases automatically [80]. The application of AI and ML to API testing is a rapidly growing area of research [81].
*   **Testing of GraphQL APIs:** While REST remains prevalent, GraphQL is gaining traction as an alternative API technology. Testing methodologies specifically designed for GraphQL APIs require further research and development, as existing REST testing techniques may not be directly applicable [82]. GraphQL's schema-based nature presents unique challenges and opportunities for testing. The lack of standardized testing tools for GraphQL APIs is a significant barrier to adoption [83]. The development of specialized testing tools and techniques for GraphQL APIs is essential for ensuring the quality and reliability of these APIs [84].
*   **Conformance to evolving standards:** As new specifications emerge and existing ones change, approaches that can rapidly adapt to these changes are required. There is a need for testing frameworks which incorporate continuous integration and continuous delivery pipelines [85], enabling automated testing and deployment of API changes. Automated API discovery and specification inference can help to keep test suites up-to-date with API changes [86]. The development of agile and adaptable testing frameworks is crucial for keeping pace with the rapid evolution of web service technologies [87].

### 2.5 Synthesis and Conclusion

The reviewed literature underscores the critical importance of conformance testing for ensuring the quality, reliability, and interoperability of REST-based web services. While various approaches and tools have been developed, significant limitations and research gaps persist, particularly in the areas of test oracle generation, adaptive testing, security integration, and handling dynamic APIs. The present study aims to address some of these gaps by developing a novel approach for automated test oracle generation for RESTful services based on machine learning techniques. This research will contribute to the state of the art by improving the effectiveness and efficiency of conformance testing for RESTful services and enabling developers to build more reliable and interoperable web applications. Future research directions include exploring the use of AI and machine learning for adaptive testing strategies, developing standardized test suites tailored for specific RESTful service domains, and addressing the challenges of testing GraphQL APIs. Furthermore, there is a pressing need for research into automatically adapting to new and changed specifications, integrating security aspects into conformance testing, and developing robust testing methodologies for complex API interactions. Addressing these research gaps will require interdisciplinary collaboration between researchers and practitioners in software engineering, artificial intelligence, and cybersecurity. The ongoing evolution of web service architectures necessitates continuous innovation in conformance testing techniques to ensure the reliability and security of modern applications. The development and adoption of standardized testing methodologies and tools will be crucial for promoting interoperability and trust in the evolving API ecosystem. The integration of testing into the entire API lifecycle, from design to deployment, is essential for ensuring the quality and reliability of modern web services [88].

### References

[1] Richardson, L., & Ruby, S. (2007). *RESTful Web Services*. O'Reilly Media.

[2] Fowler, M. (2010). *Patterns of enterprise application architecture*. Addison-Wesley Professional.

[3] Ambler, S. W. (2011). *RESTful web services: a comprehensive guide*. Cambridge University Press.

[4] Mendez, C. A., Monsalve, A., & Mejia, J. (2015). RESTful API Modeling Languages: A Comprehensive Review. *Ingeniería y Ciencia*, *11*(21), 115-136.

[5] Fielding, R. T. (2000). *Architectural styles and the design of network-based software architectures*. Doctoral dissertation, University of California, Irvine.

[6] Pautasso, C., Wilde, E., & Amundsen, M. (2014). *REST: principles, patterns, and styles*. Morgan Kaufmann.

[7] Debois, P. (2009). DevOps. *Proceedings of the Agile Systems Administration Conference (Lisa)*.

[8] Jorgensen, P. C. (2013). *Software testing: A craftsman's approach*. CRC press.

[9] OpenAPI Initiative. (2023). *OpenAPI Specification*. Retrieved from [https://www.openapis.org/](https://www.openapis.org/)

[10] RAML. (n.d.). *RESTful API Modeling Language*. Retrieved from [https://raml.org/](https://raml.org/)

[11] API Blueprint. (n.d.). Retrieved from [https://apiblueprint.org/](https://apiblueprint.org/)

[12] Whittaker, J. A. (2009). *How to break software: A practical guide to testing*. Addison-Wesley Professional.

[13] Bach, J., & Bolton, M. (2003). *Testing computer software*. John Wiley & Sons.

[14] Ciccozzi, F., Pierantonio, A., & Sanchez, A. (2017). Automating RESTful API testing with OpenAPI. *Proceedings of the 10th International Workshop on Search-Based Software Testing*, 75-81.

[15] Delamare, R., Jézéquel, J. M., & Renoust, D. (2013). Automatic test generation for RESTful APIs. *Software Quality Journal, 21*(4), 703-729.

[16] Garcia, D., Najjar, R., Mirza, F., & Kansomkeat, S. (2014). RESTest: Automated black-box testing of RESTful web services. *2014 IEEE International Conference on Web Services (ICWS)*, 169-176.

[17] Dredd. (n.d.). Retrieved from [https://dredd.org/](https://dredd.org/)

[18] SmartBear Software. (n.d.). *Swagger Inspector*. Retrieved from [https://swagger.io/tools/swagger-inspector/](https://swagger.io/tools/swagger-inspector/)

[19] Postman. (n.d.). *Postman API Platform*. Retrieved from [https://www.postman.com/](https://www.postman.com/)

[20] SmartBear Software. (n.d.). *ReadyAPI*. Retrieved from [https://smartbear.com/product/ready-api/overview/](https://smartbear.com/product/ready-api/overview/)

[21] Duvall, P. M., Matyas, S., & Glover, A. (2007). *Continuous integration: improving software quality and reducing risk*. Addison-Wesley Professional.

[22] Kong Inc. (n.d.). *What is an API Gateway?* Retrieved from [https://konghq.com/api-gateway/](https://konghq.com/api-gateway/)

[23] Utting, M., Pretschner, A., & Legeard, B. (2012). *Model-based testing: techniques, tools, and trends*. Springer Science & Business Media.

[24] Lo, D., Zhang, L., & Khoo, S. C. (2009). SPECMINE: Mining specifications from software. *ACM SIGSOFT Software Engineering Notes*, *34*(5), 245-254.

[25] Voas, J. M., & McGraw, G. (1998). Software fault injection: injecting the unexpected. *IEEE Computer*, *31*(6), 36-45.

[26] Dustdar, S., & Schreiner, W. (2005). A survey of web services testing concepts. *International Journal of Web Services Research (IJWSR)*, *2*(1), 1-27.

[27] Mahmoud, S. H., & Offutt, J. (2017). Detecting specification anomalies in RESTful APIs. *Proceedings of the 26th International Symposium on Software Testing and Analysis*, 360-370.

[28] Chow, T. S. (1978). Testing software design modeled by finite-state machines. *IEEE Transactions on Software Engineering*, *(3),* 178-187.

[29] Grieskamp, W., Gurevich, I., Tillmann, N., Schulte, W., & Halleux, J. J. (2005). Model-based testing for object-oriented software. *Proceedings of the 10th international conference on Model Driven Engineering Languages and Systems*, 486-501.

[30] Lee, J., & Lee, D. (2010). Model-based testing of stateful web services. *Software Quality Journal, 18*(4), 443-463.

[31] Offutt, J., & Abdurazik, A. (1999). Generating tests from UML specifications. *Proceedings of the 2nd international conference on UML. Beyond the standard*, 416-429.

[32] Beizer, B. (1990). *Software testing techniques*. Van Nostrand Reinhold.

[33] Clarke, E. M., Grumberg, O., & Peled, D. A. (1999). *Model checking*. MIT press.

[34] Forneari, R. F., Carvalho, L. A., & Vergilio, S. R. (2013). Model-based testing of RESTful web services. *2013 27th Brazilian Symposium on Software Engineering (SBES)*, 11-20.

[35] Favaro, J., & Henderson-Sellers, B. (1998). Testing the UML models. *Journal of Object-Oriented Programming, 10*(8), 21-25.

[36] Hartmann, J., Imoberdorf, C., & Meisinger, M. (2005). Model-based testing with UML2. 0 statecharts. *Electronic Notes in Theoretical Computer Science, 115*(3), 115-131.

[37] Van Deursen, A., & Visser, E. (2000). Domain-specific languages: An annotated bibliography. *ACM Sigplan Notices, 35*(12), 26-36.

[38] Spentzouris, A., & Petroutsos, G. (2011). Model-based testing: a survey. *International Journal on Software Tools for Technology Transfer, 13*, 447-464.

[39] Walkowiak, T., Michalski, R., & Czyz, P. (2016). RESTful API discovery based on machine learning methods. *2016 Federated Conference on Computer Science and Information Systems (FedCSIS)*, 775-784.

[40] Dias, D., & Cunha, A. (2014). Data-aware model-based testing. *Software Testing, Verification and Reliability, 24*(5), 337-361.

[41] Broy, M., & Denert, E. (2002). Model-based software development. *IEEE Software, 19*(6), 14-21.

[42] Jia, Y., & Harman, M. (2011). An overview of mutation testing. *Advances in Software Engineering, 2011*.

[43] DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1978). Hints on test data selection: Help for the practicing programmer. *Computer*, *11*(4), 34-41.

[44] Delgado, M., Estalella, A., & Marcos, E. (2018). Mutation testing of RESTful APIs. *Software Testing, Verification and Reliability, 28*(1-2), e1668.

[45] Pinto, R., Silva, N., & Soares, S. (2017). Assessing automatically generated test suites for RESTful APIs using mutation testing. *Proceedings of the XVIII Brazilian Symposium on Software Quality (SBQS)*, 161-170.

[46] Kuhn, D. R., Turban, R., & Deng, W. (2016). Practical combinatorial testing: beyond pairwise testing. *Software Quality Journal, 24*(4), 735-754.

[47] Papadakis, M., Malevris, T., & Le Traon, Y. (2015). Survey on mutation testing. *ACM Computing Surveys (CSUR), 48*(1), 1-36.

[48] Offutt, A. J., Lee, E. J., Rothermel, G., & Untch, R. H. (1996). An experimental determination of sufficient mutant operators. *ACM Transactions on Software Engineering and Methodology (TOSEM), 5*(2), 99-118.

[49] Grün, S., & Delamare, R. (2014). A practical approach to equivalent mutant detection. *Software Quality Journal, 22*(1), 125-148.

[50] Chekam, A., Derrouiche, R., & Bouillon, P. (2020). A systematic literature review of mutation testing techniques. *Information and Software Technology, 128*, 106393.

[51] Ammann, P., & Offutt, J. (2016). *Introduction to software testing*. Cambridge University Press.

[52] Zhu, H., Hall, P. A., & May, J. H. (1997). Software unit test coverage and adequacy. *ACM Computing Surveys (CSUR), 29*(4), 366-427.

[53] Nguyen, V. T., Do, T. T., & Kim, D. (2014). Reliability testing of RESTful web services using fault injection. *2014 Sixth International Conference on Ubiquitous and Future Networks (ICUFN)*, 439-444.

[54] Tsalouchidou, E., Kanellopoulos, Y., & Kiourtzoglou, D. (2019). Combining fuzzing and specification-based testing for RESTful API testing. *2019 IEEE International Conference on Software Testing, Verification and Validation Workshops (ICSTW)*, 120-123.

[55] Fraser, G., & Wotawa, F. (2011). Combining contract-based and random testing. *Software Quality Journal, 19*, 499-520.

[56] Ayewah, N., Pugh, W., Morgenthaler, J. D., Penix, J., & Swami, Y. (2008). Evaluating static defect detectors. *Proceedings of the 16th ACM SIGSOFT International Symposium on Foundations of software engineering*, 229-239.

[57] Fewster, M., & Graham, D. (1999). *Software test automation: effective use of test execution tools*. Addison-Wesley.

[58] Black, R. (2009). *Critical testing processes: plan, prepare, execute, and manage*. Addison-Wesley Professional.

[59] Bertolino, A., & Marchetti, E. (2015). Automated test generation for web applications: A survey. *ACM Transactions on Software Engineering and Methodology (TOSEM), 24*(4), 1-57.

[60] Shahin, M., Babar, M. A., & Zhu, L. (2017). Continuous integration, delivery and deployment: A systematic review on approaches, tools, challenges and practices. *Journal of Systems and Software, 132*, 126-141.

[61] ISO/IEC 25000:2005. *Software engineering — Software product quality requirements and evaluation (SQuaRE) — Guide to SQuaRE*.

[62] Kaner, C., Bach, J., & Pettichord, B. (2002). *Lessons learned in software testing: a context-driven approach*. John Wiley & Sons.

[63] Garousi, V., Felderer, M., & Hericko, M. (2016). Systematic literature reviews in software engineering: why and how to get started. *Information and Software Technology, 71*, 1-21.

[64] Wilde, E., & Pautasso, C. (2011). *REST: From Research to Practice*. Springer.

[65] Amundsen, M. (2013). *Building hypermedia APIs with HTML5 and Node*. O'Reilly Media.

[66] Di Marzo Serugendo, G., & Romanovsky, A. (2016). Engineering self-organised systems. *Software Engineering for Self-Adaptive Systems III*, 151-180.

[67] OWASP. (n.d.). *OWASP API Security Top 10*. Retrieved from [https://owasp.org/www-project-api-security/](https://owasp.org/www-project-api-security/)

[68] Allen, J., McGraw, G., & Votta, L. (2008). Security assurance cases. *IEEE Security & Privacy, 6*(6), 36-44.

[69] Fowler, M