FROM python:3.8.6-buster
LABEL maintainer="Maxesisn" description="HoshinoBot UNOFFICIAL Edition"

COPY ./ /home/TachibanaBot

RUN pip3 install -r requirements.txt && pip3 install -r hoshino/modules/yobot/yobot/src/client/requirements.txt

RUN cd /home/TachibanaBot && python3 run.py