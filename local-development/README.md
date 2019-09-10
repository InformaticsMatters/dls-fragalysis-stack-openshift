# Developing the Fragalysis Stack (local)
Basic instructions for building and running the Fragalysis Stack locally.

## Background
The stack consists of three services, running as containers: -
-   a MySQL database
-   a neo4j graph database
-   the fraglaysis stack
-   a transient data loader container

The stack is formed from code resident in a number of repositories.
Begin by forking repositories you anticipate editing (although you really want
to consider forking all the repositories as this is a relatively low-cost
operation).

The repositories are: -

-   `xchem/fragalysis`
-   `xchem/fragalysis-frontend`
-   `xchem/fragalsysi-backend`
-   `xchem/fragalysis-stack`
-   `xchem/fragalysis-loader`

## Prerequisites
-   Docker
-   Git
-   Some target data

## Setup
Create a development directory, say `~/Code/FRAGALYSIS` and clone this repository
there. If you've forked the repositories to the `xyz` account you'd run
the following: -

    $ ACCOUNT=informaticsmatters
    $ mkdir -p ~/Code/FRAGALYSIS
    $ cd ~/Code/FRAGALYSIS
    $ git clone https://github.com/InformaticsMatters/dls-fragalysis-stack-openshift.git
    $ ./dls-fragalysis-stack-openshift/local-development/setup-local-dev.sh $ACCOUNT

You will now have all the repositories available in `~/Code/FRAGALYSIS`.

## Initial build
A build script exists to start your development. It will
build all the container images you'll need from the local clones
creating initial container images for you.

From your development directory (i.e. `~/Code/FRAGALYSIS`) run...

    $ ./dls-fragalysis-stack-openshift/local-development/build-local.sh

## Populating the input data
Before you can do anything sensible with the stack you will need
**target data**. This needs to be stored in a directory whose root
is `django_data` and whose name is (typically) a timestamp of the form
`YYYY-MM-DDTHH` i.e. `django_data/2019-09-09T12`. The files in this
directory are expected by the _loader_ which loads them into the
SQL and Graph databases while the stack is running. For development,
instead of a date directory we'll just use `EXAMPLE`.

-   Get some data and copy it to `../data/input/django_data/EXAMPLE`

>   If you change the directory you'll need to modify the
    loader's `DATA_ORIGIN` environment variable, defined in the
    `fragalysis-stack/docker-compose.yml` file.

## Launching the application
Done via `docker-compose` in the Fragalysis Stack project: -

    $ cd fragalysis-stack
    $ docker-compose up -d

Initial initialisation of the individual containers can take some time but
you should be able to navigate to the stack at
[http://localhost:8080](http://localhost:8080).

Much of the material should be ready when the **loader** exits. The loader's
role is load the SQL database from the input data and then stop.

## Deleting the application
You can then stop and remove containers from thew Fragalysis project with: -

    $ cd fragalysis-stack
    $ docker-compose down
