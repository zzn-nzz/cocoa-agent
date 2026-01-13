FROM ghcr.io/agent-infra/sandbox:latest

RUN mkdir -p /home/gem/assets
COPY ["assets/Public Speaking 101.pptx", "/home/gem/assets/"]
COPY assets/public_speaking_notes.docx /home/gem/assets/
RUN chown -R 1000:1000 /home/gem/

