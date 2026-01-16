FROM ghcr.io/agent-infra/sandbox:latest

RUN mkdir -p /home/gem/assets
COPY assets/event_rules.txt /home/gem/assets/
COPY assets/people_prefs.txt /home/gem/assets/
COPY assets/room_constraints.txt /home/gem/assets/
RUN chown -R 1000:1000 /home/gem/

