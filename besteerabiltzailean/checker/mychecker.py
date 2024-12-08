#!/usr/bin/env python3

from ctf_gameserver import checkerlib
import logging
import http.client
import socket
import paramiko
import hashlib
import requests



FILE_CHECKSUM_PATHS = {
    "/app/app/v1/router/health_router.py" : "6ea812b475199025ba978d68d4881440",
    "/app/app/v1/router/user_router.py" : "00ceb52767a796b6129a9c34ea2016ff",
    # "/app/app/v1/service/user_service.py" : "2a41fe7736f800631a297e8d5a684c94", # Must be change to defense
    "/app/app/v1/service/auth_service.py" : "7a75d92cf1e7ad1bf7d5dfab32405079",
    "/app/app/v1/utils/db.py" : "b87765c77377a471aa81f4d7a76ff383",
    "/app/app/v1/utils/settings.py" : "36e06f1dc771c70482a0b4a0f79e27d4",
    "/app/app/v1/scripts/create_tables.py" : "9bc7c3d28d86ca5599052d7a9480a14d",
    "/app/app/v1/schema/token_schema.py" : "de9354500504ca87959bb73d20a64a0b",
    "/app/app/v1/schema/user_schema.py" : "864d8e38e7f59bdb709aba3e96e2d119",
    "/app/app/v1/model/user_model.py" : "61aae88dfe8f89d1994adf699f49d7b4",
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
            return checkerlib.CheckResult.DOWN
        if not self._get_api_normal_response():
            return checkerlib.CheckResult.FAULTY 
        # check if files from besterabiltzailean has been changed by comparing its hash with the hash of the original file
        if not self._check_api_integrity(FILE_CHECKSUM_PATHS):
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
        db_command = f"psql 'postgres://ctf:ctf@localhost/ctf' -c \"UPDATE public.user SET flag='{flag}' WHERE username='admin'\""
        command = f"docker exec besteerabiltzailean-db-1 sh -c '{db_command}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)

        # Check if the command executed successfully
        if stderr.channel.recv_exit_status() != 0:
            return False
        
        # Return the result
        return {'flag': flag}

    @ssh_connect()
    def _check_flag_present(self, flag):
        ssh_session = self.client
        db_command = f"psql -qtAX 'postgres://ctf:ctf@localhost/ctf' -c \"SELECT flag FROM public.user WHERE username='admin'\""
        command = f"docker exec besteerabiltzailean-db-1 sh -c '{db_command}'"
        stdin, stdout, stderr = ssh_session.exec_command(command)
        if stderr.channel.recv_exit_status() != 0:
            return False
        output = stdout.read().decode().strip()
        return flag == output

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
        headers={'Authorization': f'Bearer {res.json['access_token']}'}
        user = requests.get(f'{url}/user/user', headers=headers)
        user_json = user.json()
        return user_json['username'] == 'user'
    
    @ssh_connect()
    def _check_api_integrity(self, paths):
        ssh_session = self.client
        for path, file_sum in paths.items():
            command = f"docker exec besteerabiltzailean-web-1 sh -c 'cat {path}'"
            stdin, stdout, stderr = ssh_session.exec_command(command)
            if stderr.channel.recv_exit_status() != 0:
                return False
            
            output = stdout.read().decode().strip()
            if hashlib.md5(output.encode()).hexdigest() != file_sum:
                return False
        return True

  
if __name__ == '__main__':
    checkerlib.run_check(MyChecker)
