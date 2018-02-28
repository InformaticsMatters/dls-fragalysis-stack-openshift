# An OpenShift deployment of Fragalysis Stack
An OpenShift deployment of Anthony Bradley's [Fragalysis], consisting of
object templates at the moment.

>   Note: This is _work in progress_ and, at the moment, relies on changes
    to the Fragalysis Stack's `web` service that have not been published.
    Until this is resolved you will need`xchem/fragalysis-stack:1.0.0`
    and `xzchem/fragalysis-stack-media-loader:1.0.0` images
    before the `web` service and its `loader` can be deployed.

>   The **web** services remains un-deployed for the time-being.

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
