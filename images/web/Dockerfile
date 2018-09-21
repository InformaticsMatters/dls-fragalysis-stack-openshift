FROM xchem/fragalysis-stack:latest

RUN ls /code/frontend
RUN ls /code/frontend/bundles

# The image build number.
# This should be different and ideally incrementing for each build.
# It's probably just the Jenkins BUILD_ID.
ARG BUILD_NUMBER
LABEL build.number=${BUILD_NUMBER}
