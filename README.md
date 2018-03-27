# An OpenShift deployment of Fragalysis Stack
An OpenShift deployment of Anthony Bradley's [Fragalysis], consisting of
object templates at the moment.

## Preliminary builds
Because the stack data and container images are not available in DockerHub
we must build some container images locally (using `evel $(minishift docker-env)`
for example).

Note: This is _work in progress_ and, at the moment, relies on changes
to the Fragalysis Stack's `web` service that have not been propagated back to
the original repository. Until then you will need the following images: -

-   `docker build . -t informaticsmatters/fragalysis-backend:1.0.0`
    from the working directory of the Informatics Matters fork of the
    `fragalysis-backend` repository
-   `docker build . -t informaticsmatters/fragalysis-stack:stable`
    from the working directory of the Informatics Matters fork of the
    `fragalysis-stack` repository

-   `docker build . -t informaticsmatters/fragalysis-stack-media-loader:stable`
    from the `images/web-media-loader` directory
-   `docker build . -t informaticsmatters/neo4j-data-loader:stable`
    from the `images/neo4j-data-loader` directory

## Deployment
The deployment creates a `fragalysis-stack` project and the following
OpenShift 3.7 deployments (services): -

-   cartridge
-   db
-   graph
-   web

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
    
This should create a `fragalysis-stack` project and deploy the services.

## Undeploy (Minishift)
From the `minishift` directory run: -

    $ ./undeploy.sh

>   Note: the `project` and `service account` created by `deploy`
    is not removed by `undeploy`. This is deliberate to simplify testing.
    
---

[Blog]: https://developers.redhat.com/blog/2017/04/05/adding-persistent-storage-to-minishift-cdk-3-in-minutes/
[Fragalysis]: https://github.com/xchem/fragalysis-stack
