# An OpenShift deployment of Fragalysis Stack
An OpenShift deployment of Anthony Bradley's [Fragalysis], that automatically
restarts the Graph (Neo4J) and Web (Django) application containers based
on scheduled CI/CD jobs running in Jenkins.

## Deployment
The deployment creates a `fragalysis-cicd` project and the following
OpenShift 3.7 deployments (services): -

-   db (MySQL 5.7)
-   graph (driven by an ImageStream)
-   web (driven by an ImageStream)

For the demo (minishift) we also create: -

-   A user ('diamond')
-   A service account ('diamond')

## Creating PVs (Minishift)
You can create your own PVs in Minishift.
Follow the instructions in `minishift/mkpvs.sh`.

Tested with Minishift using:

-   `--openshift-version 3.6.1`
-   `--openshift-version 3.7.1`
    
## Deploy (Minishift)
Assuming you ave a suitable minishift instance running,
from the `minishift` directory run: -

    $ eval $(minishift oc-env)
    
    $ ./deploy.sh
    
This should create a `fragalysis-cicd` project and deploy the services.

## Undeploy (Minishift)
From the `minishift` directory run: -

    $ ./undeploy.sh

>   Note: the `project` and `service account` created by `deploy`
    is not removed by `undeploy`. This is deliberate because
    the Jenkins CI/CD platform is currently installed (separately)
    into the same project.
    
---

[Blog]: https://developers.redhat.com/blog/2017/04/05/adding-persistent-storage-to-minishift-cdk-3-in-minutes/
[Fragalysis]: https://github.com/xchem/fragalysis-stack
