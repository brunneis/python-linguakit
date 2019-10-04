FROM brunneis/python:3.7

RUN \
	apt-get update \
	&& dpkg-query -Wf '${Package}\n' | sort > /tmp/init_pkgs \
	&& apt-get -y install git build-essential zlib1g-dev \
	&& dpkg-query -Wf '${Package}\n' | sort > /tmp/new_pkgs \
	&& cpan PerlIO::gzip \
	&& cpan LWP::UserAgent \
	&& apt-get -y purge $(diff -u /tmp/init_pkgs /tmp/new_pkgs | grep -E "^\+" | cut -d + -f2- | sed -n '1!p' | grep -v perl) \
	&& apt-get -y install $(diff -u /tmp/init_pkgs /tmp/new_pkgs | grep -E "^\+" | cut -d + -f2- | sed -n '1!p' | grep perl)

RUN \
	pip install --upgrade pip \
	&& pip install linguakit \
	&& python -c "import linguakit"