# Dockerfile for tasks requiring IndigoRenderer

FROM golemfactory/indigo:0.1

RUN apt-get update && \
	apt-get install -y \
		curl \
		bzip2 \
		libglu1-mesa \
		libgomp1 \
		libpng12-0 && \
	apt-get -y autoremove && \
	rm -rf /var/lib/apt/lists/*

ENV INDIGO_URL http://downloads.indigorenderer.com/dist/beta/IndigoRenderer_x64_v3.8.37.tar.gz

RUN curl -SL ${INDIGO_URL} | tar -xzv -C /opt && \
    ln -s /opt/IndigoRenderer_x64_v3.8.37 /opt/indigo

ENV PATH=/opt/indigo:$PATH INDIGO_ROOT=/opt/indigo
