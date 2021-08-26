FROM robertf99/tfx-tfdf

WORKDIR /models
COPY ./models ./

WORKDIR /pipeline
COPY ./pipeline ./
ENV PYTHONPATH="/pipeline:${PYTHONPATH}"