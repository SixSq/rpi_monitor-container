FROM  raspbian/stretch
LABEL maintainer="SixSq"

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN	apt-get -y update \
	&& apt-get -y --no-install-recommends install \
		libraspberrypi-bin \
		python \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

COPY ./files/rpi_monitor.py /

CMD ["python", "/rpi_monitor.py"]
