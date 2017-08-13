FROM python:alpine


WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com

COPY . .

EXPOSE '5000:5555'

CMD [ "python", "./main.py" ]