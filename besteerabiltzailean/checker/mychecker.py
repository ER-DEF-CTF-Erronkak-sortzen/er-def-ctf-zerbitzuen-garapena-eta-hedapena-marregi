#!/usr/bin/env python3

from ctf_gameserver import checkerlib
import logging
import http.client
import socket
import paramiko
import hashlib
import requests



FILE_CHECKSUM_PATHS = {
"./main.py" : "82340b16c7062bd8e496921ef8c687ec",
"./app/model/user_model.py" : "46c962705e39dd1c6a4916884e04cc79",
#"./app/schema/user_schema.py" : "af696b3d3ad148d633aa575514efdeac",
"./app/schema/token_schema.py" : "de9354500504ca87959bb73d20a64a0b",
"./app/scripts/create_tables.py" : "a2ccc09ad5859cb8a20dfffb1efe47c2",
"./app/router/health_router.py" : "38bb8f10bc34eb68aaf67c4fc9c88fa6",
"./app/router/user_router.py" : "8c5a120bd4226b46b8c867df4f92d0e0",
"./app/utils/db.py" : "d39f29e7c67f70ce910fbcbf0bd0dffc",
"./app/utils/settings.py" : "a4161d7b7c08a2fdb70113c03c911cdd",
"./app/service/auth_service.py" : "9e6fa74d58610d57281c382c525a14f1",
"./app/service/user_service.py" : "e8fdc8847028446e0519c8d4b1cb3883",
}
PORT_API = 8008
def ssh_connect():
    def decorator(func):
        def wrapper(*args, **kwargs):
            # SSH connection setup
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            rsa_key = paramiko.RSAKey.from_private_key_file(f'/keys/team{args[0].team}-sshkey')
            client.connect(args[0].ip, username = 'root', pkey=rsa_key)

            # Call the decorated function with the client parameter
            args[0].client = client
            result = func(*args, **kwargs)

            # SSH connection cleanup
            client.close()
            return result
        return wrapper
    return decorator

class MyChecker(checkerlib.BaseChecker):

    def __init__(self, ip, team):
        checkerlib.BaseChecker.__init__(self, ip, team)
        self._baseurl = f'http://[{self.ip}]:{PORT_API}'
        logging.info(f"URL: {self._baseurl}")

    @ssh_connect()
    def place_flag(self, tick):
        flag = checkerlib.get_flag(tick)
        logging.info("yyyyyyyyyyy: " + flag)
        creds = self._add_new_flag(self.client, flag)
        if not creds:
            return checkerlib.CheckResult.FAULTY
        logging.info('created')
        checkerlib.store_state(str(tick), creds)
        checkerlib.set_flagid(str(tick))
        return checkerlib.CheckResult.OK

    def check_service(self):
        # check if ports are open
        if not self._check_port_api(self.ip, PORT_API):
            logging.info(f"xxx1")
            return checkerlib.CheckResult.DOWN
        if not self._get_api_normal_response(self.ip, PORT_API):
            logging.info(f"xxx2")
            return checkerlib.CheckResult.FAULTY 
        # check if files from besterabiltzailean has been changed by comparing its hash with the hash of the original file
        if not self._check_api_integrity(FILE_CHECKSUM_PATHS):
            logging.info(f"xxx3")
            return checkerlib.CheckResult.FAULTY
                  
        return checkerlib.CheckResult.OK
    
    def check_flag(self, tick):
        if not self.check_service():
            return checkerlib.CheckResult.DOWN
        flag = checkerlib.get_flag(tick)
        #creds = checkerlib.load_state("flag_" + str(tick))
        # if not creds:
        #     logging.error(f"Cannot find creds for tick {tick}")
        #     return checkerlib.CheckResult.FLAG_NOT_FOUND
        flag_present = self._check_flag_present(flag)
        if not flag_present:
            return checkerlib.CheckResult.FLAG_NOT_FOUND
        return checkerlib.CheckResult.OK
        

    

  
    # Private Funcs - Return False if error
  
    def _add_new_flag(self, ssh_session, flag):
        # Execute the file creation command in the container
        db_command = f"psql -qtXA postgres://ctf:ctf@localhost/ctf -c \\\"UPDATE public.user SET flag=concat(flag,'{flag}') WHERE username='admin';\\\""
        logging.info(db_command)
        command = f"docker exec besteerabiltzailean_db_1 sh -c \"{db_command}\""
        stdin, stdout, stderr = ssh_session.exec_command(command)

        # Check if the command executed successfully
        if stderr.channel.recv_exit_status() != 0:
            logging.info(stderr)
            return False
        
        # Return the result
        return {'flag': flag}

    @ssh_connect()
    def _check_flag_present(self, flag):
        ssh_session = self.client
        db_command = f"psql -qtAX postgres://ctf:ctf@localhost/ctf -c \\\"SELECT flag FROM public.user WHERE username='admin'\\\""
        command = f"docker exec besteerabiltzailean_db_1 sh -c \"{db_command}\""
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        logging.info(flag)
        logging.info(output)
        return flag in output

    def _check_port_api(self, ip, port):
        try:
            conn = http.client.HTTPConnection(ip, port, timeout=5)
            conn.request("GET", "/api/v1/health")
            response = conn.getresponse()
            return response.status == 200
        except (http.client.HTTPException, socket.error) as e:
            print(f"Exception: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def _get_api_normal_response(self, ip, port):
        url = f"http://{ip}:{port}/api/v1"
        res = requests.post(f'{url}/login', data={'username': 'user', 'password': 'pasahitz_sekretua'})
        if res.status_code != 200:
            return False
        headers={'Authorization': f'Bearer {res.json()["access_token"]}'}
        user = requests.get(f'{url}/user/user', headers=headers)
        user_json = user.json()
        return user_json['username'] == 'user'
    
    @ssh_connect()  
    def _check_api_integrity(self, paths):
        ssh_session = self.client
        for path, file_sum in paths.items():
            command = f"docker exec besteerabiltzailean_web_1 sh -c 'cat {path}'"
            stdin, stdout, stderr = ssh_session.exec_command(command)
            if stderr.channel.recv_exit_status() != 0:
                return False
            output = stdout.read().decode()
            if hashlib.md5(output.encode()).hexdigest() != file_sum:
                return False
        return True

  
if __name__ == '__main__':
    checkerlib.run_check(MyChecker)
