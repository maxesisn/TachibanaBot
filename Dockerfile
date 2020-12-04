FROM debian:bullseye-slim
LABEL maintainer="Maxesisn" description="HoshinoBot UNOFFICIAL Edition"

COPY ./ /home/TachibanaBot

RUN cd /home/TachibanaBot

RUN apt install python3.8 python3-pip

RUN pip3 install -r requirements.txt && pip3 install -r hoshino/modules/yobot/yobot/src/client/requirements.txt

CMD cd cd /home/TachibanaBot && python3.8 run.py