FROM giulianocruz/rstudio:0.0.11

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openssh-client
ENV R_REMOTES_UPGRADE=never
ENV VIRTUAL_ENV_DISABLE_PROMPT=1
RUN echo "PS1='\[\e[1;38;2;231;41;138m\]${VIRTUAL_ENV:+[$(basename -- $VIRTUAL_ENV)] }\[\e[1;38;2;117;112;179m\][[\u]]\[\033[00m\]:\[\e[1;38;2;27;158;119m\]\w/\n\[\e[1;38;2;217;95;2m\]\\$\\$\[\033[00m\] '" >> ~/.bashrc

RUN pip install --upgrade pip

RUN pip install poetry cookiecutter
RUN pip install --upgrade git+https://github.com/cornellius-gp/linear_operator.git
RUN pip install --upgrade git+https://github.com/cornellius-gp/gpytorch.git
RUN export ALLOW_LATEST_GPYTORCH_LINOP=true
RUN pip install --upgrade git+https://github.com/pytorch/botorch.git