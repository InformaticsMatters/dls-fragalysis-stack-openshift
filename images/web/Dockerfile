FROM xchem/fragalysis-stack:latest

# The image build number.
# This should be different and ideally incrementing for each build.
# It's probably just the Jenkins BUILD_ID.
ARG BUILD_NUMBER
LABEL build.number=${BUILD_NUMBER}

# Upstream Git commits
BE_COMMIT=$(git log --pretty=format:'%h' -n 1)
WORKDIR ${APP_ROOT}/frontend
FE_COMMIT=$(git log --pretty=format:'%h' -n 1)
WORKDIR ${APP_ROOT}
LABEL build.be.commit=${BE_COMMIT}
LABEL build.fe.commit=${FE_COMMIT}
