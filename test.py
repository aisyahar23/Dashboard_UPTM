Microsoft Windows [Version 10.0.22631.5699]
(c) Microsoft Corporation. All rights reserved.

C:\Users\MNZEML5\idp-serv-external>az acr login -n azadpk8s1ikpyxi175ma --expose-token
Note: The token in both the accessToken and refreshToken fields is an ACR Refresh Token, not an ACR Access Token. This ACR Refresh Token cannot be used directly to authenticate with registry APIs such as pushing/pulling images and listing repositories/tags. This ACR Refresh Token must be subsequently exchanged for an ACR Access.Please see https://aka.ms/acr/auth/oauth
You can perform manual login using the provided refresh token below, for example: 'docker login loginServer -u 00000000-0000-0000-0000-000000000000 -p refreshToken'
{
  "accessToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkZYU1M6M1FNWTpZMjZWOkJQR0Y6Q0NORjpRQzNGOkVPUlE6SUJXRDpFUVBVOklUMzQ6RFU1NzpVRTIzIn0.eyJqdGkiOiJhYTU0MDM1Yi1jZWM5LTQyMGEtOTY2Ny1iZWNhYjg4NTYwYWIiLCJzdWIiOiJleHRlcm4uYWJkdWwtcmF6YWtfYWlzeWFoLWJpbnRpQGFsbGlhbnouY29tIiwibmJmIjoxNzU1MDc5ODEwLCJleHAiOjE3NTUwOTE1MTAsImlhdCI6MTc1NTA3OTgxMCwiaXNzIjoiQXp1cmUgQ29udGFpbmVyIFJlZ2lzdHJ5IiwiYXVkIjoiYXphZHBrOHMxaWtweXhpMTc1bWEuYXp1cmVjci5pbyIsInZlcnNpb24iOiIxLjAiLCJyaWQiOiI5YmQwZWQ2NTM3YzI0YmUwODg4NTA1ZDNlNzU2NGFiNSIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiYXBwaWQiOiIwNGIwNzc5NS04ZGRiLTQ2MWEtYmJlZS0wMmY5ZTFiZjdiNDYiLCJ0ZW5hbnQiOiI2ZTA2ZTQyZC02OTI1LTQ3YzYtYjllNy05NTgxYzdjYTMwMmEiLCJwZXJtaXNzaW9ucyI6eyJhY3Rpb25zIjpbInJlYWQiLCJ3cml0ZSIsImRlbGV0ZSIsInNpZ24iLCJxdWFyYW50aW5lL3JlYWQiLCJxdWFyYW50aW5lL3dyaXRlIiwibWV0YWRhdGEvcmVhZCIsIm1ldGFkYXRhL3dyaXRlIiwiZGVsZXRlZC9yZWFkIiwiZGVsZXRlZC9yZXN0b3JlL2FjdGlvbiJdfSwicm9sZXMiOlsiQWNySW1hZ2VTaWduZXIiLCJBY3JRdWFyYW50aW5lUmVhZGVyIiwiQWNyUXVhcmFudGluZVdyaXRlciJdfQ.nqh9IrEcFXLWq5pIxWV7BfuDeMzt5b5Mm-H3XFUrg_EHo2cNUtoAxlMwlwPJEZI9rFOSFhZ1uAabghFeFCfDaQbnAzcf8DN1k4HR0gzEE5HlJp7j_EUYvmOJXo2HjRz4wfh8A7K_Sh8-QGG365X8G7HTkF2kkjjmLQfVcod36lF8EfHAZuILMlCHLIlJ9-ehErrb-kQmKTu-BgnH8bJJibymPgCteD3sKNy3GXBEck6bGf7sqmZAvF5nvj-5jdg01Pj0nJFtKQc6r7bSZ2g7IMyLx93A_fcp3DX_c4h65Yc4j_2cgGuvY_XZXijmO9uTbkhukaM3sZS25_IvAE9q1w",
  "loginServer": "azadpk8s1ikpyxi175ma.azurecr.io",
  "refreshToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkZYU1M6M1FNWTpZMjZWOkJQR0Y6Q0NORjpRQzNGOkVPUlE6SUJXRDpFUVBVOklUMzQ6RFU1NzpVRTIzIn0.eyJqdGkiOiJhYTU0MDM1Yi1jZWM5LTQyMGEtOTY2Ny1iZWNhYjg4NTYwYWIiLCJzdWIiOiJleHRlcm4uYWJkdWwtcmF6YWtfYWlzeWFoLWJpbnRpQGFsbGlhbnouY29tIiwibmJmIjoxNzU1MDc5ODEwLCJleHAiOjE3NTUwOTE1MTAsImlhdCI6MTc1NTA3OTgxMCwiaXNzIjoiQXp1cmUgQ29udGFpbmVyIFJlZ2lzdHJ5IiwiYXVkIjoiYXphZHBrOHMxaWtweXhpMTc1bWEuYXp1cmVjci5pbyIsInZlcnNpb24iOiIxLjAiLCJyaWQiOiI5YmQwZWQ2NTM3YzI0YmUwODg4NTA1ZDNlNzU2NGFiNSIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiYXBwaWQiOiIwNGIwNzc5NS04ZGRiLTQ2MWEtYmJlZS0wMmY5ZTFiZjdiNDYiLCJ0ZW5hbnQiOiI2ZTA2ZTQyZC02OTI1LTQ3YzYtYjllNy05NTgxYzdjYTMwMmEiLCJwZXJtaXNzaW9ucyI6eyJhY3Rpb25zIjpbInJlYWQiLCJ3cml0ZSIsImRlbGV0ZSIsInNpZ24iLCJxdWFyYW50aW5lL3JlYWQiLCJxdWFyYW50aW5lL3dyaXRlIiwibWV0YWRhdGEvcmVhZCIsIm1ldGFkYXRhL3dyaXRlIiwiZGVsZXRlZC9yZWFkIiwiZGVsZXRlZC9yZXN0b3JlL2FjdGlvbiJdfSwicm9sZXMiOlsiQWNySW1hZ2VTaWduZXIiLCJBY3JRdWFyYW50aW5lUmVhZGVyIiwiQWNyUXVhcmFudGluZVdyaXRlciJdfQ.nqh9IrEcFXLWq5pIxWV7BfuDeMzt5b5Mm-H3XFUrg_EHo2cNUtoAxlMwlwPJEZI9rFOSFhZ1uAabghFeFCfDaQbnAzcf8DN1k4HR0gzEE5HlJp7j_EUYvmOJXo2HjRz4wfh8A7K_Sh8-QGG365X8G7HTkF2kkjjmLQfVcod36lF8EfHAZuILMlCHLIlJ9-ehErrb-kQmKTu-BgnH8bJJibymPgCteD3sKNy3GXBEck6bGf7sqmZAvF5nvj-5jdg01Pj0nJFtKQc6r7bSZ2g7IMyLx93A_fcp3DX_c4h65Yc4j_2cgGuvY_XZXijmO9uTbkhukaM3sZS25_IvAE9q1w",
  "username": "00000000-0000-0000-0000-000000000000"
}

C:\Users\MNZEML5\idp-serv-external>podman login azadpk8s1ikpyxi175ma.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p   "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkZYU1M6M1FNWTpZMjZWOkJQR0Y6Q0NORjpRQzNGOkVPUlE6SUJXRDpFUVBVOklUMzQ6RFU1NzpVRTIzIn0.eyJqdGkiOiJhYTU0MDM1Yi1jZWM5LTQyMGEtOTY2Ny1iZWNhYjg4NTYwYWIiLCJzdWIiOiJleHRlcm4uYWJkdWwtcmF6YWtfYWlzeWFoLWJpbnRpQGFsbGlhbnouY29tIiwibmJmIjoxNzU1MDc5ODEwLCJleHAiOjE3NTUwOTE1MTAsImlhdCI6MTc1NTA3OTgxMCwiaXNzIjoiQXp1cmUgQ29udGFpbmVyIFJlZ2lzdHJ5IiwiYXVkIjoiYXphZHBrOHMxaWtweXhpMTc1bWEuYXp1cmVjci5pbyIsInZlcnNpb24iOiIxLjAiLCJyaWQiOiI5YmQwZWQ2NTM3YzI0YmUwODg4NTA1ZDNlNzU2NGFiNSIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiYXBwaWQiOiIwNGIwNzc5NS04ZGRiLTQ2MWEtYmJlZS0wMmY5ZTFiZjdiNDYiLCJ0ZW5hbnQiOiI2ZTA2ZTQyZC02OTI1LTQ3YzYtYjllNy05NTgxYzdjYTMwMmEiLCJwZXJtaXNzaW9ucyI6eyJhY3Rpb25zIjpbInJlYWQiLCJ3cml0ZSIsImRlbGV0ZSIsInNpZ24iLCJxdWFyYW50aW5lL3JlYWQiLCJxdWFyYW50aW5lL3dyaXRlIiwibWV0YWRhdGEvcmVhZCIsIm1ldGFkYXRhL3dyaXRlIiwiZGVsZXRlZC9yZWFkIiwiZGVsZXRlZC9yZXN0b3JlL2FjdGlvbiJdfSwicm9sZXMiOlsiQWNySW1hZ2VTaWduZXIiLCJBY3JRdWFyYW50aW5lUmVhZGVyIiwiQWNyUXVhcmFudGluZVdyaXRlciJdfQ.nqh9IrEcFXLWq5pIxWV7BfuDeMzt5b5Mm-H3XFUrg_EHo2cNUtoAxlMwlwPJEZI9rFOSFhZ1uAabghFeFCfDaQbnAzcf8DN1k4HR0gzEE5HlJp7j_EUYvmOJXo2HjRz4wfh8A7K_Sh8-QGG365X8G7HTkF2kkjjmLQfVcod36lF8EfHAZuILMlCHLIlJ9-ehErrb-kQmKTu-BgnH8bJJibymPgCteD3sKNy3GXBEck6bGf7sqmZAvF5nvj-5jdg01Pj0nJFtKQc6r7bSZ2g7IMyLx93A_fcp3DX_c4h65Yc4j_2cgGuvY_XZXijmO9uTbkhukaM3sZS25_IvAE9q1w"
Error: currently logged in, auth file contains an Identity token

C:\Users\MNZEML5\idp-serv-external>docker-compose build
time="2025-08-13T18:27:18+08:00" level=warning msg="C:\\Users\\MNZEML5\\idp-serv-external\\docker-compose.yml: the attribute version is obsolete, it will be ignored, please remove it to avoid potential confusion"
time="2025-08-13T18:27:18+08:00" level=warning msg="Docker Compose is configured to build using Bake, but buildx isn't installed"
error during connect: in the default daemon configuration on Windows, the docker client must be run with elevated privileges to connect: Head "http://%2F%2F.%2Fpipe%2Fdocker_engine/_ping": open //./pipe/docker_engine: Access is denied.

C:\Users\MNZEML5\idp-serv-external>docker ps
error during connect: in the default daemon configuration on Windows, the docker client must be run with elevated privileges to connect: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.51/containers/json": open //./pipe/docker_engine: Access is denied.

C:\Users\MNZEML5\idp-serv-external>podman ps
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES

C:\Users\MNZEML5\idp-serv-external>
C:\Users\MNZEML5\idp-serv-external>
C:\Users\MNZEML5\idp-serv-external>wsl -d podman-machine-default

You will be automatically entered into a nested process namespace where
systemd is running. If you need to access the parent namespace, hit ctrl-d
or type exit. This also means to log out you need to exit twice.

[user@AMC-D-PF5GTEYP ~]$ cat ~/.config/containers/auth.json
cat: /home/user/.config/containers/auth.json: No such file or directory
[user@AMC-D-PF5GTEYP ~]$ exit
logout
[user@AMC-D-PF5GTEYP idp-serv-external]$
[user@AMC-D-PF5GTEYP idp-serv-external]$
[user@AMC-D-PF5GTEYP idp-serv-external]$
[user@AMC-D-PF5GTEYP idp-serv-external]$ >podman login azadpk8s1ikpyxi175ma.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p   "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkZYU1M6M1FNWTpZMjZWOkJQR0Y6Q0NORjpRQzNGOkVPUlE6SUJXRDpFUVBVOklUMzQ6RFU1NzpVRTIzIn0.eyJqdGkiOiJhYTU0MDM1Yi1jZWM5LTQyMGEtOTY2Ny1iZWNhYjg4NTYwYWIiLCJzdWIiOiJleHRlcm4uYWJkdWwtcmF6YWtfYWlzeWFoLWJpbnRpQGFsbGlhbnouY29tIiwibmJmIjoxNzU1MDc5ODEwLCJleHAiOjE3NTUwOTE1MTAsImlhdCI6MTc1NTA3OTgxMCwiaXNzIjoiQXp1cmUgQ29udGFpbmVyIFJlZ2lzdHJ5IiwiYXVkIjoiYXphZHBrOHMxaWtweXhpMTc1bWEuYXp1cmVjci5pbyIsInZlcnNpb24iOiIxLjAiLCJyaWQiOiI5YmQwZWQ2NTM3YzI0YmUwODg4NTA1ZDNlNzU2NGFiNSIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiYXBwaWQiOiIwNGIwNzc5NS04ZGRiLTQ2MWEtYmJlZS0wMmY5ZTFiZjdiNDYiLCJ0ZW5hbnQiOiI2ZTA2ZTQyZC02OTI1LTQ3YzYtYjllNy05NTgxYzdjYTMwMmEiLCJwZXJtaXNzaW9ucyI6eyJhY3Rpb25zIjpbInJlYWQiLCJ3cml0ZSIsImRlbGV0ZSIsInNpZ24iLCJxdWFyYW50aW5lL3JlYWQiLCJxdWFyYW50aW5lL3dyaXRlIiwibWV0YWRhdGEvcmVhZCIsIm1ldGFkYXRhL3dyaXRlIiwiZGVsZXRlZC9yZWFkIiwiZGVsZXRlZC9yZXN0b3JlL2FjdGlvbiJdfSwicm9sZXMiOlsiQWNySW1hZ2VTaWduZXIiLCJBY3JRdWFyYW50aW5lUmVhZGVyIiwiQWNyUXVhcmFudGluZVdyaXRlciJdfQ.nqh9IrEcFXLWq5pIxWV7BfuDeMzt5b5Mm-H3XFUrg_EHo2cNUtoAxlMwlwPJEZI9rFOSFhZ1uAabghFeFCfDaQbnAzcf8DN1k4HR0gzEE5HlJp7j_EUYvmOJXo2HjRz4wfh8A7K_Sh8-QGG365X8G7HTkF2kkjjmLQfVcod36lF8EfHAZuILMlCHLIlJ9-ehErrb-kQmKTu-BgnH8bJJibymPgCteD3sKNy3GXBEck6bGf7sqmZAvF5nvj-5jdg01Pj0nJFtKQc6r7bSZ2g7IMyLx93A_fcp3DX_c4h65Yc4j_2cgGuvY_XZXijmO9uTbkhukaM3sZS25_IvAE9q1w" --authfile ./auth.json
login: invalid option -- 'u'
Try 'login --help' for more information.
[user@AMC-D-PF5GTEYP idp-serv-external]$ >podman login azadpk8s1ikpyxi175ma.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p   "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkZYU1M6M1FNWTpZMjZWOkJQR0Y6Q0NORjpRQzNGOkVPUlE6SUJXRDpFUVBVOklUMzQ6RFU1NzpVRTIzIn0.eyJqdGkiOiJhYTU0MDM1Yi1jZWM5LTQyMGEtOTY2Ny1iZWNhYjg4NTYwYWIiLCJzdWIiOiJleHRlcm4uYWJkdWwtcmF6YWtfYWlzeWFoLWJpbnRpQGFsbGlhbnouY29tIiwibmJmIjoxNzU1MDc5ODEwLCJleHAiOjE3NTUwOTE1MTAsImlhdCI6MTc1NTA3OTgxMCwiaXNzIjoiQXp1cmUgQ29udGFpbmVyIFJlZ2lzdHJ5IiwiYXVkIjoiYXphZHBrOHMxaWtweXhpMTc1bWEuYXp1cmVjci5pbyIsInZlcnNpb24iOiIxLjAiLCJyaWQiOiI5YmQwZWQ2NTM3YzI0YmUwODg4NTA1ZDNlNzU2NGFiNSIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiYXBwaWQiOiIwNGIwNzc5NS04ZGRiLTQ2MWEtYmJlZS0wMmY5ZTFiZjdiNDYiLCJ0ZW5hbnQiOiI2ZTA2ZTQyZC02OTI1LTQ3YzYtYjllNy05NTgxYzdjYTMwMmEiLCJwZXJtaXNzaW9ucyI6eyJhY3Rpb25zIjpbInJlYWQiLCJ3cml0ZSIsImRlbGV0ZSIsInNpZ24iLCJxdWFyYW50aW5lL3JlYWQiLCJxdWFyYW50aW5lL3dyaXRlIiwibWV0YWRhdGEvcmVhZCIsIm1ldGFkYXRhL3dyaXRlIiwiZGVsZXRlZC9yZWFkIiwiZGVsZXRlZC9yZXN0b3JlL2FjdGlvbiJdfSwicm9sZXMiOlsiQWNySW1hZ2VTaWduZXIiLCJBY3JRdWFyYW50aW5lUmVhZGVyIiwiQWNyUXVhcmFudGluZVdyaXRlciJdfQ.nqh9IrEcFXLWq5pIxWV7BfuDeMzt5b5Mm-H3XFUrg_EHo2cNUtoAxlMwlwPJEZI9rFOSFhZ1uAabghFeFCfDaQbnAzcf8DN1k4HR0gzEE5HlJp7j_EUYvmOJXo2HjRz4wfh8A7K_Sh8-QGG365X8G7HTkF2kkjjmLQfVcod36lF8EfHAZuILMlCHLIlJ9-ehErrb-kQmKTu-BgnH8bJJibymPgCteD3sKNy3GXBEck6bGf7sqmZAvF5nvj-5jdg01Pj0nJFtKQc6r7bSZ2g7IMyLx93A_fcp3DX_c4h65Yc4j_2cgGuvY_XZXijmO9uTbkhukaM3sZS25_IvAE9q1w" --authfile ./auth.json
login: invalid option -- 'u'
Try 'login --help' for more information.
[user@AMC-D-PF5GTEYP idp-serv-external]$ podman login azadpk8s1ikpyxi175ma.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p   "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkZYU1M6M1FNWTpZMjZWOkJQR0Y6Q0NORjpRQzNGOkVPUlE6SUJXRDpFUVBVOklUMzQ6RFU1NzpVRTIzIn0.eyJqdGkiOiJhYTU0MDM1Yi1jZWM5LTQyMGEtOTY2Ny1iZWNhYjg4NTYwYWIiLCJzdWIiOiJleHRlcm4uYWJkdWwtcmF6YWtfYWlzeWFoLWJpbnRpQGFsbGlhbnouY29tIiwibmJmIjoxNzU1MDc5ODEwLCJleHAiOjE3NTUwOTE1MTAsImlhdCI6MTc1NTA3OTgxMCwiaXNzIjoiQXp1cmUgQ29udGFpbmVyIFJlZ2lzdHJ5IiwiYXVkIjoiYXphZHBrOHMxaWtweXhpMTc1bWEuYXp1cmVjci5pbyIsInZlcnNpb24iOiIxLjAiLCJyaWQiOiI5YmQwZWQ2NTM3YzI0YmUwODg4NTA1ZDNlNzU2NGFiNSIsImdyYW50X3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiYXBwaWQiOiIwNGIwNzc5NS04ZGRiLTQ2MWEtYmJlZS0wMmY5ZTFiZjdiNDYiLCJ0ZW5hbnQiOiI2ZTA2ZTQyZC02OTI1LTQ3YzYtYjllNy05NTgxYzdjYTMwMmEiLCJwZXJtaXNzaW9ucyI6eyJhY3Rpb25zIjpbInJlYWQiLCJ3cml0ZSIsImRlbGV0ZSIsInNpZ24iLCJxdWFyYW50aW5lL3JlYWQiLCJxdWFyYW50aW5lL3dyaXRlIiwibWV0YWRhdGEvcmVhZCIsIm1ldGFkYXRhL3dyaXRlIiwiZGVsZXRlZC9yZWFkIiwiZGVsZXRlZC9yZXN0b3JlL2FjdGlvbiJdfSwicm9sZXMiOlsiQWNySW1hZ2VTaWduZXIiLCJBY3JRdWFyYW50aW5lUmVhZGVyIiwiQWNyUXVhcmFudGluZVdyaXRlciJdfQ.nqh9IrEcFXLWq5pIxWV7BfuDeMzt5b5Mm-H3XFUrg_EHo2cNUtoAxlMwlwPJEZI9rFOSFhZ1uAabghFeFCfDaQbnAzcf8DN1k4HR0gzEE5HlJp7j_EUYvmOJXo2HjRz4wfh8A7K_Sh8-QGG365X8G7HTkF2kkjjmLQfVcod36lF8EfHAZuILMlCHLIlJ9-ehErrb-kQmKTu-BgnH8bJJibymPgCteD3sKNy3GXBEck6bGf7sqmZAvF5nvj-5jdg01Pj0nJFtKQc6r7bSZ2g7IMyLx93A_fcp3DX_c4h65Yc4j_2cgGuvY_XZXijmO9uTbkhukaM3sZS25_IvAE9q1w" --authfile ./auth.json
WARN[0001] "/" is not a shared mount, this could cause issues or missing mounts with rootless containers
Login Succeeded!
[user@AMC-D-PF5GTEYP idp-serv-external]$ py -m  podman-compose
-bash: py: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ py -m  podman-compose build
-bash: py: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ py -m  podman_compose build
-bash: py: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ podman_compose build
-bash: podman_compose: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ podman-compose build
-bash: podman-compose: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$
[user@AMC-D-PF5GTEYP idp-serv-external]$
[user@AMC-D-PF5GTEYP idp-serv-external]$
[user@AMC-D-PF5GTEYP idp-serv-external]$ podman-compose -verision
-bash: podman-compose: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ podman-compose -version
-bash: podman-compose: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ set PYTHONPATH=C:\Users\MNZEML5\AppData\Roaming\Python\Python313\site-packages
[user@AMC-D-PF5GTEYP idp-serv-external]$ py -m podman_compose build
-bash: py: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ py -m podman_compose build
-bash: py: command not found
[user@AMC-D-PF5GTEYP idp-serv-external]$ exit
logout

C:\Users\MNZEML5\idp-serv-external>python -version
Unknown option: -e
usage: python [option] ... [-c cmd | -m mod | file | -] [arg] ...
Try `python -h' for more information.

C:\Users\MNZEML5\idp-serv-external>python --version
Python 3.13.1

C:\Users\MNZEML5\idp-serv-external>pip --version
pip 25.2 from C:\Users\MNZEML5\AppData\Roaming\Python\Python313\site-packages\pip (python 3.13)

C:\Users\MNZEML5\idp-serv-external>pip install podman-compose
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: podman-compose in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (1.5.0)
Requirement already satisfied: python-dotenv in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (from podman-compose) (1.1.1)
Requirement already satisfied: pyyaml in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (from podman-compose) (6.0.2)

C:\Users\MNZEML5\idp-serv-external>podman-compose --version
'podman-compose' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\MNZEML5\idp-serv-external>podman_compose --version
'podman_compose' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\MNZEML5\idp-serv-external>pip install --user podman-compose
Requirement already satisfied: podman-compose in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (1.5.0)
Requirement already satisfied: python-dotenv in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (from podman-compose) (1.1.1)
Requirement already satisfied: pyyaml in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (from podman-compose) (6.0.2)

C:\Users\MNZEML5\idp-serv-external>podman_compose --version
'podman_compose' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\MNZEML5\idp-serv-external>podman-compose --version
'podman-compose' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\MNZEML5\idp-serv-external>wsl -d podman-machine-default

You will be automatically entered into a nested process namespace where
systemd is running. If you need to access the parent namespace, hit ctrl-d
or type exit. This also means to log out you need to exit twice.

[user@AMC-D-PF5GTEYP ~]$ pip3 install --user podman-compose
export PATH=$PATH:~/.local/bin
-bash: pip3: command not found
[user@AMC-D-PF5GTEYP ~]$ sudo apt update
sudo apt upgrade -y
sudo: apt: command not found
sudo: apt: command not found
[user@AMC-D-PF5GTEYP ~]$
[user@AMC-D-PF5GTEYP ~]$
[user@AMC-D-PF5GTEYP ~]$ py -m pip install --user podman-compose
set PATH=%PATH%;C:\Users\MNZEML5\AppData\Roaming\Python\Python313\Scripts
podman-compose -f docker-compose.yml build
-bash: py: command not found
-bash: C:UsersMNZEML5AppDataRoamingPythonPython313Scripts: command not found
-bash: podman-compose: command not found
[user@AMC-D-PF5GTEYP ~]$ py -m pip install --user podman-compose
-bash: py: command not found
[user@AMC-D-PF5GTEYP ~]$
[user@AMC-D-PF5GTEYP ~]$
[user@AMC-D-PF5GTEYP ~]$
[user@AMC-D-PF5GTEYP ~]$ exit
logout
[user@AMC-D-PF5GTEYP idp-serv-external]$ exit
logout

C:\Users\MNZEML5\idp-serv-external>py -m pip install --user podman-compose
Requirement already satisfied: podman-compose in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (1.5.0)
Requirement already satisfied: python-dotenv in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (from podman-compose) (1.1.1)
Requirement already satisfied: pyyaml in c:\users\mnzeml5\appdata\roaming\python\python313\site-packages (from podman-compose) (6.0.2)

C:\Users\MNZEML5\idp-serv-external>podman-compose build
'podman-compose' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\MNZEML5\idp-serv-external>set PATH=%PATH%;C:\Users\MNZEML5\AppData\Roaming\Python\Python313\Scripts

C:\Users\MNZEML5\idp-serv-external>podman-compose --version
podman-compose version 1.5.0
podman version 5.4.0

C:\Users\MNZEML5\idp-serv-external>
C:\Users\MNZEML5\idp-serv-external>
C:\Users\MNZEML5\idp-serv-external>podman-compose build
STEP 1/12: FROM azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2
Trying to pull azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2...
Error: creating build container: internal error: unable to copy from source docker://azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2: initializing source docker://azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2: unable to retrieve auth token: invalid username/password: unauthorized: authentication required, visit https://aka.ms/acr/authorization for more information. CorrelationId: fda91afc-a927-4cf7-8bdf-f8dec01d99b1


C:\Users\MNZEML5\idp-serv-external>podman-compose --authfile C:\Users\MNZEML5\idp-serv-external\auth.json build
usage: podman-compose [-h] [-v] [--in-pod in_pod] [--pod-args pod_args] [--env-file env_file] [-f file]
                      [--profile profile] [-p PROJECT_NAME] [--podman-path PODMAN_PATH] [--podman-args args]
                      [--podman-pull-args args] [--podman-push-args args] [--podman-build-args args]
                      [--podman-inspect-args args] [--podman-run-args args] [--podman-start-args args]
                      [--podman-stop-args args] [--podman-rm-args args] [--podman-volume-args args] [--no-ansi]
                      [--no-cleanup] [--dry-run] [--parallel PARALLEL] [--verbose]
                      {help,version,wait,systemd,pull,push,build,up,down,ps,run,exec,start,stop,restart,logs,config,port,pause,unpause,kill,stats,images} ...
podman-compose: error: argument command: invalid choice: 'C:\\Users\\MNZEML5\\idp-serv-external\\auth.json' (choose from help, version, wait, systemd, pull, push, build, up, down, ps, run, exec, start, stop, restart, logs, config, port, pause, unpause, kill, stats, images)

C:\Users\MNZEML5\idp-serv-external>podman-compose --authfile C:\Users\MNZEML5\.config\containers\auth.json build
usage: podman-compose [-h] [-v] [--in-pod in_pod] [--pod-args pod_args] [--env-file env_file] [-f file]
                      [--profile profile] [-p PROJECT_NAME] [--podman-path PODMAN_PATH] [--podman-args args]
                      [--podman-pull-args args] [--podman-push-args args] [--podman-build-args args]
                      [--podman-inspect-args args] [--podman-run-args args] [--podman-start-args args]
                      [--podman-stop-args args] [--podman-rm-args args] [--podman-volume-args args] [--no-ansi]
                      [--no-cleanup] [--dry-run] [--parallel PARALLEL] [--verbose]
                      {help,version,wait,systemd,pull,push,build,up,down,ps,run,exec,start,stop,restart,logs,config,port,pause,unpause,kill,stats,images} ...
podman-compose: error: argument command: invalid choice: 'C:\\Users\\MNZEML5\\.config\\containers\\auth.json' (choose from help, version, wait, systemd, pull, push, build, up, down, ps, run, exec, start, stop, restart, logs, config, port, pause, unpause, kill, stats, images)

C:\Users\MNZEML5\idp-serv-external>podman-compose --authfile C:\Users\MNZEML5\idp-serv-external\auth.json build
usage: podman-compose [-h] [-v] [--in-pod in_pod] [--pod-args pod_args] [--env-file env_file] [-f file]
                      [--profile profile] [-p PROJECT_NAME] [--podman-path PODMAN_PATH] [--podman-args args]
                      [--podman-pull-args args] [--podman-push-args args] [--podman-build-args args]
                      [--podman-inspect-args args] [--podman-run-args args] [--podman-start-args args]
                      [--podman-stop-args args] [--podman-rm-args args] [--podman-volume-args args] [--no-ansi]
                      [--no-cleanup] [--dry-run] [--parallel PARALLEL] [--verbose]
                      {help,version,wait,systemd,pull,push,build,up,down,ps,run,exec,start,stop,restart,logs,config,port,pause,unpause,kill,stats,images} ...
podman-compose: error: argument command: invalid choice: 'C:\\Users\\MNZEML5\\idp-serv-external\\auth.json' (choose from help, version, wait, systemd, pull, push, build, up, down, ps, run, exec, start, stop, restart, logs, config, port, pause, unpause, kill, stats, images)

C:\Users\MNZEML5\idp-serv-external>podman pull --authfile C:\Users\MNZEML5\idp-serv-external\auth.json azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2
Trying to pull azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2...
Error: internal error: unable to copy from source docker://azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2: initializing source docker://azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2: unable to retrieve auth token: invalid username/password: unauthorized: authentication required, visit https://aka.ms/acr/authorization for more information. CorrelationId: f46b9ec6-0247-4f63-a922-ca587cf78080

C:\Users\MNZEML5\idp-serv-external>wsl -d podman-machine-default

You will be automatically entered into a nested process namespace where
systemd is running. If you need to access the parent namespace, hit ctrl-d
or type exit. This also means to log out you need to exit twice.

[user@AMC-D-PF5GTEYP ~]$ mkdir -p ~/.config/containers/
[user@AMC-D-PF5GTEYP ~]$ cp /mnt/c/Users/MNZEML5/idp-serv-external/auth.json ~/.config/containers/auth.json
[user@AMC-D-PF5GTEYP ~]$ exit
logout
[user@AMC-D-PF5GTEYP idp-serv-external]$ exit
logout

C:\Users\MNZEML5\idp-serv-external>podman-compose build
STEP 1/12: FROM azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2
Trying to pull azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2...
Error: creating build container: internal error: unable to copy from source docker://azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2: initializing source docker://azadpk8s1ikpyxi175ma.azurecr.io/keycloak/keycloak:18.0.2: unable to retrieve auth token: invalid username/password: unauthorized: authentication required, visit https://aka.ms/acr/authorization for more information. CorrelationId: 1dd45bc7-92c2-4c06-9944-04ca285dec6b


C:\Users\MNZEML5\idp-serv-external>podman-compose build
STEP 1/12: FROM docker.io/keycloak/keycloak:18.0.2
Trying to pull docker.io/keycloak/keycloak:18.0.2...
Error: creating build container: internal error: unable to copy from source docker://keycloak/keycloak:18.0.2: initializing source docker://keycloak/keycloak:18.0.2: reading manifest 18.0.2 in docker.io/keycloak/keycloak: manifest unknown


C:\Users\MNZEML5\idp-serv-external>podman-compose build
STEP 1/12: FROM quay.io/keycloak/keycloak:18.0.2
Trying to pull quay.io/keycloak/keycloak:18.0.2...
Error: creating build container: internal error: unable to copy from source docker://quay.io/keycloak/keycloak:18.0.2: initializing source docker://quay.io/keycloak/keycloak:18.0.2: pinging container registry quay.io: Get "https://quay.io/v2/": tls: failed to verify certificate: x509: certificate signed by unknown authority


C:\Users\MNZEML5\idp-serv-external>podman pull --tls-verify=false docker.io/keycloak/keycloak:18.0.2
Trying to pull docker.io/keycloak/keycloak:18.0.2...
Error: internal error: unable to copy from source docker://keycloak/keycloak:18.0.2: initializing source docker://keycloak/keycloak:18.0.2: reading manifest 18.0.2 in docker.io/keycloak/keycloak: manifest unknown

C:\Users\MNZEML5\idp-serv-external>podman pull --tls-verify=false quay.io/keycloak/keycloak:18.0.2
Trying to pull quay.io/keycloak/keycloak:18.0.2...
Getting image source signatures
Copying blob sha256:6963f872abface896838f7f855db3c316f6d9ded4aa57deae35c0600c8ecb61d
Copying blob sha256:59d7767644241c8c86c96730e52e738619df3edf46586828e0093532dbfdc3e3
Copying blob sha256:3dbfdcfb8c042ca6f0e551c23a9fc7bc9083fafcdbe8edec3e142ece1b916a1d
Copying blob sha256:8ad940a6151ae0c6e82a51d9ccb495e2fc42c50de0ae4d78947c007887ebd190
^C
C:\Users\MNZEML5\idp-serv-external>podman pull --tls-verify=false quay.io/keycloak/keycloak:18.0.2
Trying to pull quay.io/keycloak/keycloak:18.0.2...
Getting image source signatures
Copying blob sha256:59d7767644241c8c86c96730e52e738619df3edf46586828e0093532dbfdc3e3
Copying blob sha256:6963f872abface896838f7f855db3c316f6d9ded4aa57deae35c0600c8ecb61d
Copying blob sha256:3dbfdcfb8c042ca6f0e551c23a9fc7bc9083fafcdbe8edec3e142ece1b916a1d
Copying blob sha256:8ad940a6151ae0c6e82a51d9ccb495e2fc42c50de0ae4d78947c007887ebd190
Copying config sha256:ce57c5afb395c260491094271ed468559ae964163cbfa1d94b3faadf01e985df
Writing manifest to image destination
ce57c5afb395c260491094271ed468559ae964163cbfa1d94b3faadf01e985df

C:\Users\MNZEML5\idp-serv-external>podman-compose build
STEP 1/12: FROM quay.io/keycloak/keycloak:18.0.2
STEP 2/12: ENV TZ Asia/Bangkok
--> 8363194ef1a8
STEP 3/12: ENV KC_HEALTH_ENABLED=true
--> 90a83112d9e7
STEP 4/12: ENV KC_METRICS_ENABLED=false
--> efd351d1c5a7
STEP 5/12: ENV KC_SPI_THEME_WELCOME_THEME=aagi-welcome
--> ce8725949ef9
STEP 6/12: COPY "themes/aagi-welcome" "/opt/keycloak/themes/aagi-welcome"
--> 6acb8a9129e3
STEP 7/12: COPY "themes/cust-portal" "/opt/keycloak/themes/cust-portal"
--> 017ca6431178
STEP 8/12: COPY "themes/keycloak-fix" "/opt/keycloak/themes/keycloak-fix"
--> 2cf0f55b478c
STEP 9/12: COPY "providers" "/opt/keycloak/providers"
--> dd5ab53ef2d9
STEP 10/12: WORKDIR /opt/keycloak
--> 3190fe294e52
STEP 11/12: RUN /opt/keycloak/bin/kc.sh build --cache-stack=kubernetes --db=postgres
Updating the configuration and installing your custom providers, if any. Please wait.
2025-08-13 19:19:15,369 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-card-id-username-form (com.allianzth.keycloak.authenticator.CardIdUsernameFormFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
2025-08-13 19:19:15,371 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-forgot-password-redirect (com.allianzth.keycloak.authenticator.authenticator.AAGIForgotPasswordRedirect) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
2025-08-13 19:19:15,372 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-sms-otp-authenticator (com.allianzth.keycloak.authenticator.SMSOTPAuthenticatorFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
2025-08-13 19:19:15,374 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-user-session-removal-provider (com.allianzth.keycloak.authenticator.UserSessionRemovalAuthenticatorFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
2025-08-13 19:19:15,374 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-config (com.allianzth.keycloak.authenticator.ConfigAuthenticationFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
2025-08-13 19:19:15,375 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-consent-page-authenticator (com.allianzth.keycloak.authenticator.AAGIConsentPageAuthenticatorFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
2025-08-13 19:19:15,546 WARN  [io.quarkus.arc.deployment.SplitPackageProcessor] (build-73) Detected a split package usage which is considered a bad practice and should be avoided. Following packages were detected in multiple archives:
- "com.allianzth.keycloak.model" found in [/opt/keycloak/lib/../providers/aagi-common.jar, /opt/keycloak/lib/../providers/aagi-consent-page-provider.jar]
- "com.allianzth.keycloak.authenticator" found in [/opt/keycloak/lib/../providers/aagi-card-id-username-provider.jar, /opt/keycloak/lib/../providers/aagi-common.jar, /opt/keycloak/lib/../providers/aagi-consent-page-provider.jar, /opt/keycloak/lib/../providers/aagi-sms-otp-authenticator.jar, /opt/keycloak/lib/../providers/aagi-user-session-removal-provider.jar]
2025-08-13 19:19:15,857 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-password-expiration-page (com.allianzth.keycloak.action.AAGIPasswordExpirationActionFactory) is implementing the internal SPI required-action. This SPI is internal and may change without notice
2025-08-13 19:19:15,858 WARN  [org.keycloak.services] (build-36) KC-SERVICES0047: aagi-consent-page (com.allianzth.keycloak.authenticator.AAGIConsentPageRequiredActionFactory) is implementing the internal SPI required-action. This SPI is internal and may change without notice
2025-08-13 19:19:21,426 INFO  [io.quarkus.deployment.QuarkusAugmentor] (main) Quarkus augmentation completed in 11508ms
Server configuration updated and persisted. Run the following command to review the configuration:

        kc.sh show-config

--> 2ce2118615d8
STEP 12/12: ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
COMMIT idp-serv-external:latest
--> b5d7aba04cf7
Successfully tagged localhost/idp-serv-external:latest
b5d7aba04cf7d730d348e7dd6d2afd646240b892e7015f787d7a225b7783e15d

C:\Users\MNZEML5\idp-serv-external>podman-compose up
c0d89ef6f671f0687d20974d7d07ac9ed2c420cfc7f4db9cb1e132e89ceb1424
50e56c8a4ff16fc9f78dc61fa1578528ab4e2574670237b44700dff96268f6ef
68a68845d14d27c6ac654e9f3840aad5ab7ccc1ec1a0b8aa9cef738e83ea33f2
[postgres]          | The files belonging to this database system will be owned by user "postgres".
[postgres]          | This user must also own the server process.
[postgres]          |
[postgres]          | The database cluster will be initialized with locale "en_US.utf8".
[postgres]          | The default database encoding has accordingly been set to "UTF8".
[postgres]          | The default text search configuration will be set to "english".
[postgres]          |
[postgres]          | Data page checksums are disabled.
[postgres]          |
[postgres]          | fixing permissions on existing directory /var/lib/postgresql/data ... ok
[postgres]          | creating subdirectories ... ok
[postgres]          | selecting dynamic shared memory implementation ... posix
[postgres]          | selecting default "max_connections" ... 100
[postgres]          | selecting default "shared_buffers" ... 128MB
[postgres]          | selecting default time zone ... Etc/UTC
[postgres]          | creating configuration files ... ok
[postgres]          | running bootstrap script ... ok
[postgres]          | performing post-bootstrap initialization ... ok
[idp-serv-external] | Listening for transport dt_socket at address: 8787
[postgres]          | syncing data to disk ... ok
[postgres]          |
[postgres]          |
[postgres]          | Success. You can now start the database server using:
[postgres]          |
[postgres]          |     pg_ctl -D /var/lib/postgresql/data -l logfile start
[postgres]          |
[postgres]          | initdb: warning: enabling "trust" authentication for local connections
[postgres]          | initdb: hint: You can change this by editing pg_hba.conf or using the option -A, or --auth-local and --auth-host, the next time you run initdb.
[idp-serv-external] | Updating the configuration and installing your custom providers, if any. Please wait.
[postgres]          | waiting for server to start....2025-08-13 12:35:19.119 UTC [43] LOG:  starting PostgreSQL 17.5 (Debian 17.5-1.pgdg130+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
[postgres]          | 2025-08-13 12:35:19.125 UTC [43] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
[postgres]          | 2025-08-13 12:35:19.136 UTC [46] LOG:  database system was shut down at 2025-08-13 12:35:18 UTC
[postgres]          | 2025-08-13 12:35:19.146 UTC [43] LOG:  database system is ready to accept connections
[postgres]          |  done
[postgres]          | server started
[postgres]          | CREATE DATABASE
[postgres]          |
[postgres]          |
[postgres]          | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
[postgres]          |
[postgres]          | waiting for server to shut down....2025-08-13 12:35:19.526 UTC [43] LOG:  received fast shutdown request
[postgres]          | 2025-08-13 12:35:19.530 UTC [43] LOG:  aborting any active transactions
[postgres]          | 2025-08-13 12:35:19.532 UTC [43] LOG:  background worker "logical replication launcher" (PID 49) exited with exit code 1
[postgres]          | 2025-08-13 12:35:19.532 UTC [44] LOG:  shutting down
[postgres]          | 2025-08-13 12:35:19.536 UTC [44] LOG:  checkpoint starting: shutdown immediate
[postgres]          | 2025-08-13 12:35:19.731 UTC [44] LOG:  checkpoint complete: wrote 925 buffers (5.6%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.043 s, sync=0.138 s, total=0.199 s; sync files=301, longest=0.004 s, average=0.001 s; distance=4256 kB, estimate=4256 kB; lsn=0/1915968, redo lsn=0/1915968
[postgres]          | 2025-08-13 12:35:19.738 UTC [43] LOG:  database system is shut down
[postgres]          |  done
[postgres]          | server stopped
[postgres]          |
[postgres]          | PostgreSQL init process complete; ready for start up.
[postgres]          |
[postgres]          | 2025-08-13 12:35:19.886 UTC [1] LOG:  starting PostgreSQL 17.5 (Debian 17.5-1.pgdg130+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
[postgres]          | 2025-08-13 12:35:19.887 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
[postgres]          | 2025-08-13 12:35:19.887 UTC [1] LOG:  listening on IPv6 address "::", port 5432
[postgres]          | 2025-08-13 12:35:19.897 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
[postgres]          | 2025-08-13 12:35:19.910 UTC [59] LOG:  database system was shut down at 2025-08-13 12:35:19 UTC
[postgres]          | 2025-08-13 12:35:19.919 UTC [1] LOG:  database system is ready to accept connections
[idp-serv-external] | 2025-08-13 19:35:21,985 INFO  [org.keycloak.common.Profile] (build-30) Preview feature enabled: declarative_user_profile
[idp-serv-external] | 2025-08-13 19:35:22,684 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-card-id-username-form (com.allianzth.keycloak.authenticator.CardIdUsernameFormFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,685 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-config (com.allianzth.keycloak.authenticator.ConfigAuthenticationFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,686 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-consent-page-authenticator (com.allianzth.keycloak.authenticator.AAGIConsentPageAuthenticatorFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,687 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-forgot-password-redirect (com.allianzth.keycloak.authenticator.authenticator.AAGIForgotPasswordRedirect) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,688 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-sms-otp-authenticator (com.allianzth.keycloak.authenticator.SMSOTPAuthenticatorFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,689 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-user-session-removal-provider (com.allianzth.keycloak.authenticator.UserSessionRemovalAuthenticatorFactory) is implementing the internal SPI authenticator. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,891 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-consent-page (com.allianzth.keycloak.authenticator.AAGIConsentPageRequiredActionFactory) is implementing the internal SPI required-action. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:22,892 WARN  [org.keycloak.services] (build-30) KC-SERVICES0047: aagi-password-expiration-page (com.allianzth.keycloak.action.AAGIPasswordExpirationActionFactory) is implementing the internal SPI required-action. This SPI is internal and may change without notice
[idp-serv-external] | 2025-08-13 19:35:23,037 WARN  [io.quarkus.arc.deployment.SplitPackageProcessor] (build-18) Detected a split package usage which is considered a bad practice and should be avoided. Following packages were detected in multiple archives:
[idp-serv-external] | - "com.allianzth.keycloak.model" found in [/opt/keycloak/lib/../providers/aagi-common.jar, /opt/keycloak/lib/../providers/aagi-consent-page-provider.jar]
[idp-serv-external] | - "com.allianzth.keycloak.authenticator" found in [/opt/keycloak/lib/../providers/aagi-card-id-username-provider.jar, /opt/keycloak/lib/../providers/aagi-common.jar, /opt/keycloak/lib/../providers/aagi-consent-page-provider.jar, /opt/keycloak/lib/../providers/aagi-sms-otp-authenticator.jar, /opt/keycloak/lib/../providers/aagi-user-session-removal-provider.jar]
[idp-serv-external] | 2025-08-13 19:35:27,593 INFO  [io.quarkus.deployment.QuarkusAugmentor] (main) Quarkus augmentation completed in 7211ms
[idp-serv-external] | Listening for transport dt_socket at address: 8787
[idp-serv-external] | 2025-08-13 19:35:30,822 INFO  [org.keycloak.common.Profile] (main) Preview feature enabled: declarative_user_profile
[idp-serv-external] | 2025-08-13 19:35:30,843 INFO  [org.keycloak.quarkus.runtime.hostname.DefaultHostnameProvider] (main) Hostname settings: FrontEnd: <request>, Strict HTTPS: false, Path: <request>, Strict BackChannel: false, Admin: <request>, Port: -1, Proxied: false
[idp-serv-external] | 2025-08-13 19:35:31,676 WARN  [org.infinispan.PERSISTENCE] (keycloak-cache-init) ISPN000554: jboss-marshalling is deprecated and planned for removal
[idp-serv-external] | 2025-08-13 19:35:31,790 WARN  [org.infinispan.CONFIG] (keycloak-cache-init) ISPN000569: Unable to persist Infinispan internal caches as no global state enabled
[idp-serv-external] | 2025-08-13 19:35:31,823 INFO  [org.infinispan.CONTAINER] (keycloak-cache-init) ISPN000556: Starting user marshaller 'org.infinispan.jboss.marshalling.core.JBossUserMarshaller'
[idp-serv-external] | 2025-08-13 19:35:32,060 INFO  [org.infinispan.CONTAINER] (keycloak-cache-init) ISPN000128: Infinispan version: Infinispan 'Triskaidekaphobia' 13.0.9.Final
[idp-serv-external] | 2025-08-13 19:35:32,481 INFO  [org.keycloak.connections.infinispan.DefaultInfinispanConnectionProviderFactory] (main) Node name: node_934324, Site name: null
[postgres]          | 2025-08-13 12:35:32.512 UTC [63] ERROR:  relation "public.migration_model" does not exist at character 25
[postgres]          | 2025-08-13 12:35:32.512 UTC [63] STATEMENT:  SELECT ID, VERSION FROM public.MIGRATION_MODEL ORDER BY UPDATE_TIME DESC
[postgres]          | 2025-08-13 12:35:33.395 UTC [63] ERROR:  relation "public.databasechangelog" does not exist at character 22
[postgres]          | 2025-08-13 12:35:33.395 UTC [63] STATEMENT:  SELECT COUNT(*) FROM public.databasechangelog
[postgres]          | 2025-08-13 12:35:33.809 UTC [64] ERROR:  relation "public.databasechangeloglock" does not exist at character 22
[postgres]          | 2025-08-13 12:35:33.809 UTC [64] STATEMENT:  SELECT COUNT(*) FROM public.databasechangeloglock
[postgres]          | 2025-08-13 12:35:33.850 UTC [63] ERROR:  relation "public.databasechangelog" does not exist at character 22
[postgres]          | 2025-08-13 12:35:33.850 UTC [63] STATEMENT:  SELECT COUNT(*) FROM public.databasechangelog
[idp-serv-external] | 2025-08-13 19:35:33,851 INFO  [org.keycloak.quarkus.runtime.storage.database.liquibase.QuarkusJpaUpdaterProvider] (main) Initializing database schema. Using changelog META-INF/jpa-changelog-master.xml
[idp-serv-external] | 2025-08-13 19:35:36,013 INFO  [org.keycloak.services] (main) KC-SERVICES0050: Initializing master realm
[idp-serv-external] | 2025-08-13 19:35:38,138 INFO  [org.keycloak.services] (main) KC-SERVICES0009: Added user 'admin' to realm 'master'
[idp-serv-external] | 2025-08-13 19:35:38,391 INFO  [io.quarkus] (main) Keycloak 18.0.2 on JVM (powered by Quarkus 2.7.5.Final) started in 10.224s. Listening on: http://0.0.0.0:9080
[idp-serv-external] | 2025-08-13 19:35:38,394 INFO  [io.quarkus] (main) Profile dev activated.
[idp-serv-external] | 2025-08-13 19:35:38,394 INFO  [io.quarkus] (main) Installed features: [agroal, cdi, hibernate-orm, jdbc-h2, jdbc-mariadb, jdbc-mssql, jdbc-mysql, jdbc-oracle, jdbc-postgresql, keycloak, narayana-jta, reactive-routes, resteasy, resteasy-jackson, smallrye-context-propagation, smallrye-health, smallrye-metrics, vault, vertx]
[idp-serv-external] | 2025-08-13 19:35:38,400 WARN  [org.keycloak.quarkus.runtime.KeycloakMain] (main) Running the server in development mode. DO NOT use this configuration in production.
[postgres]          | 2025-08-13 12:40:19.921 UTC [57] LOG:  checkpoint starting: time
[postgres]          | 2025-08-13 12:41:15.136 UTC [57] LOG:  checkpoint complete: wrote 545 buffers (3.3%); 1 WAL file(s) added, 0 removed, 0 recycled; write=54.582 s, sync=0.526 s, total=55.215 s; sync files=534, longest=0.036 s, average=0.001 s; distance=3737 kB, estimate=3737 kB; lsn=0/1CBC0F0, redo lsn=0/1CBC060
[postgres]          | 2025-08-14 01:38:22.576 UTC [57] LOG:  checkpoint starting: time
[postgres]          | 2025-08-14 01:38:37.031 UTC [57] LOG:  checkpoint complete: wrote 142 buffers (0.9%); 0 WAL file(s) added, 0 removed, 0 recycled; write=14.301 s, sync=0.117 s, total=14.455 s; sync files=103, longest=0.034 s, average=0.002 s; distance=521 kB, estimate=3416 kB; lsn=0/1D3E560, redo lsn=0/1D3E4D0
[postgres]          | 2025-08-14 01:43:22.133 UTC [57] LOG:  checkpoint starting: time
[postgres]          | 2025-08-14 01:43:26.098 UTC [57] LOG:  checkpoint complete: wrote 39 buffers (0.2%); 0 WAL file(s) added, 0 removed, 0 recycled; write=3.869 s, sync=0.038 s, total=3.965 s; sync files=32, longest=0.007 s, average=0.002 s; distance=60 kB, estimate=3080 kB; lsn=0/1D4D720, redo lsn=0/1D4D6C8
[postgres]          | 2025-08-14 01:48:22.198 UTC [57] LOG:  checkpoint starting: time
[postgres]          | 2025-08-14 01:48:23.723 UTC [57] LOG:  checkpoint complete: wrote 15 buffers (0.1%); 0 WAL file(s) added, 0 removed, 0 recycled; write=1.449 s, sync=0.019 s, total=1.525 s; sync files=14, longest=0.008 s, average=0.002 s; distance=17 kB, estimate=2774 kB; lsn=0/1D51D60, redo lsn=0/1D51D08
[postgres]          | 2025-08-14 01:58:22.923 UTC [57] LOG:  checkpoint starting: time
[postgres]          | 2025-08-14 01:58:23.734 UTC [57] LOG:  checkpoint complete: wrote 8 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.744 s, sync=0.011 s, total=0.811 s; sync files=8, longest=0.006 s, average=0.002 s; distance=7 kB, estimate=2497 kB; lsn=0/1D53D20, redo lsn=0/1D53CC8
[postgres]          | 2025-08-14 02:03:22.834 UTC [57] LOG:  checkpoint starting: time
[postgres]          | 2025-08-14 02:03:23.655 UTC [57] LOG:  checkpoint complete: wrote 8 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.746 s, sync=0.016 s, total=0.821 s; sync files=8, longest=0.009 s, average=0.002 s; distance=8 kB, estimate=2248 kB; lsn=0/1D55E88, redo lsn=0/1D55DF8