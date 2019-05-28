# OpenShift, CI/CD and Graph processing support for Fragalysis Stack
A collection of software and files to support the CI/CD deployment of the
[Fragalysis] Stack. This essentially contains the tools to manage the
[Jenkins] CI/CD deployment to [OpenShift] using [ansible] and the material
used to assist the generation of a [neo4j] graph representation of the
underlying molecule data using [nextflow].

Distributed amongst a number of sub-directories: -
 
-   **ansible**:
    A directory of roles and playbooks used to deploy
    (and un-deploy) the stack and related software into an OpenShift cluster
    as paired projects used for development/test and production.

-   **cluster-config**:
    Ansible plays to configure the OKD cluster nodes (prior to orchestration)
    
-   **images**:
    Dockerfiles and Jenkinsfiles for additional container images.
    This includes a data loader, specialised graph and jobs to automate
    the promotion of development project images to the production project.
    
-   **jenkins**:
    Utilities to support the configuration and backup of the
    cluster's Jenkins deployment. Based on a simple set of Python-based
    utilities, this code uses the Jenkins API to write and read job
    configurations and write job-related secrets.
    
-   **minishift**:
    A simple and early deployment of the stack to a local
    [Minishift] installation allowing experimentation on the desktop.
    
-   **okd-orchestrator**:
    OKD-Orchestrator deployment file for the Verne cluster.

-   **openshift**:
    All the OpenShift templates required to deploy the
    developer/test and production application, used in conjunction with the
    Ansible roles & playbooks.
    
-   **s2g-processor**:
    Material used to support the generation of the graph
    representation of molecule data using Fragalysis utilities and Nextflow.

---

Alan Christie  
Informatics Matters Ltd.  

[ansible]: https://www.ansible.com
[fragalysis]: https://github.com/xchem/fragalysis-stack
[jenkins]: https://jenkins.io
[minishift]: https://github.com/minishift/minishift
[neo4j]: https://neo4j.com
[nextflow]: https://www.nextflow.io
[openshift]: https://www.openshift.com
