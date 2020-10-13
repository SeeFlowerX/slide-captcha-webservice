# build
```
  docker build -t crack-captcha .
```
# run
```
  docker run  -d --name crack-container  -p 8008:5000 crack-captcha
```
# log 
```
  docker logs crack-container -f
```
