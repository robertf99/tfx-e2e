FROM apache/airflow:latest-python3.8

USER root
RUN apt-get update \
    && apt-get install -y gcc g++

# RUN echo "${GREEN}Installing TFX workshop${NORMAL}\n\n"

# RUN echo "${GREEN}Refreshing setuptools to avoid _NamespacePath issues${NORMAL}\n"
# RUN pip uninstall setuptools -y && RUN pip install setuptools

# RUN echo "${GREEN}Installing httplib2 for Beam compatibility${NORMAL}\n"
# RUN pip install httplib2==0.12.0

# RUN echo "${GREEN}Installing pendulum to avoid problem with tzlocal${NORMAL}\n"
# RUN pip install pendulum==1.4.4

# RUN echo "${GREEN}Installing TFX${NORMAL}\n"
# RUN pip install pyarrow==0.15.0
# RUN pip install apache_beam==2.17.0

USER airflow

RUN pip install --no-cache-dir tfx==1.0.0
RUN pip install --no-cache-dir tensorflow_decision_forests --upgrade

# RUN echo "${GREEN}Installing Google API Client${NORMAL}\n"
# RUN pip install google-api-python-client