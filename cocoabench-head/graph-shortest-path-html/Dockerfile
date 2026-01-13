FROM ghcr.io/agent-infra/sandbox:latest

RUN mkdir -p /home/gem/assets
COPY assets/graph_diagram.png /home/gem/assets/
COPY assets/graph_task_spec.html /home/gem/assets/
RUN chown -R 1000:1000 /home/gem/

