FROM debian:bullseye-slim
LABEL maintainer="Maxesisn" description="HoshinoBot UNOFFICIAL Edition"
EXPOSE 8080

COPY ./ /home/TachibanaBot

WORKDIR /home/TachibanaBot

VOLUME [ "hoshino/config", "hoshino/modules/yobot/yobot/src/client/yobot_data" ]

RUN apt-get -qq -o Dpkg::Use-Pty=0 update && apt-get -qq -o Dpkg::Use-Pty=0 install -y python3.8 python3-pip libgl1-mesa-glx wget libgtk2.0-dev

RUN wget -nv https://cn-pan.di.he.cn/res.tar.gz && tar xzf ./res.tar.gz && rm res.tar.gz

RUN pip3 install --quiet -r requirements.txt

CMD python3.8 run.py