# An OpenShift deployment of Fragalysis Stack
An OpenShift deployment of Anthony Bradley's [Fragalysis], consisting of
object templates at the moment.

>   Note: This is _work in progress_ and, at the moment, relies on changes
    to the Fragalysis Stack's `web` service that have not been published.
    Until this is resolved you will need `xchem/fragalysis-stack:1.0.0` image
    before the `web` service can be deployed.

>   The **web** services remains un-deployed for the time-being.

The deployment creates a `fragalysis-stack` project and the following
deployments (services): -

-   cartridge
-   db
-   graph
-   web

For the demo (minishift) we also create: -

-   A user ('diamond')
-   A service account ('diamond')

## Deploy (Minishift)
Assuming you ave a suitable minishift instance running,
from the `minishift` directory run: -

    $ ./deploy.sh
    
This should create a `fragalysis-stack` project and deploy the services.

## Undeploy (Minishift)
From the `minishift` directory run: -

    $ ./undeploy.sh

>   Note: the project created by `deploy` is not removed by `undeploy`.
    This is deliberate for now to simplify testing.
    
---

[Fragalysis]: https://github.com/xchem/fragalysis-stack
