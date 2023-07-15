FROM gitpod/workspace-full
USER gitpod
ENV PIP_USER=no
RUN pip3 install pipx; \
    pipx install pdm; \
    pipx ensurepath
