FROM python:3.12.3-bookworm

RUN apt-get update && apt-get install -y \
    graphviz \
    cmake \
    texlive texlive-latex-extra texlive-fonts-extra texlive-science texlive-lang-cyrillic \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /project
WORKDIR /project

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./scripts/ ./scripts/

RUN ./scripts/install_refal.sh
ENV PATH="$PATH:/project/refal"

COPY ./Chipollino/ ./Chipollino/
RUN ./scripts/build_chipollino.sh

COPY . .

ENTRYPOINT ./scripts/start.sh