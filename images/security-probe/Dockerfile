FROM python:3.7.0

# Get the OpenShift Origin OC CLI tools ---------------------------------------

ENV OC_TOOL_PATH /oc-tool
ENV OC_VERSION 3.9.0
ENV OC_SRC openshift-origin-client-tools-v${OC_VERSION}-191fece-linux-64bit
WORKDIR ${OC_TOOL_PATH}
RUN wget https://github.com/openshift/origin/releases/download/v${OC_VERSION}/${OC_SRC}.tar.gz && \
    tar -xvzf ${OC_SRC}.tar.gz && \
    mv ${OC_SRC}/* . && \
    rm ${OC_SRC}.tar.gz && \
    rmdir ${OC_SRC}
ENV PATH = ${PATH}:${OC_TOOL_PATH}

# Probe code ------------------------------------------------------------------

ENV APP_ROOT /probe
ENV HOME ${APP_ROOT}
WORKDIR ${APP_ROOT}

COPY requirements.txt ${APP_ROOT}/
COPY probe.py ${APP_ROOT}/
RUN pip install -r requirements.txt && \
    chmod 755 ${APP_ROOT}/probe.py && \
    chmod 777 ${APP_ROOT}

# Force the binary layer of the stdout and stderr streams
# to be unbuffered
ENV PYTHONUNBUFFERED 1

CMD [ "./probe.py" ]
