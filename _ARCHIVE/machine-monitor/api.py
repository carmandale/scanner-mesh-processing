from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import socket
import subprocess
import os
from flask import after_this_request

app = Flask(__name__)
CORS(app)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def check_scan_db_process():
    command = "ps -ef | grep -iE '([bB]lender.*(--scan|-b)|[bB]lender)|[s]can_db.py|[g]roove-mesher' | grep -v grep | awk '/scan_db/ {print \"PYTHON - scan_db\"} /([bB]lender.*--scan|-b)|[bB]lender/ {match($0, /--scan[[:space:]]+([[:alnum:]-]+)/); printf \"BLENDER - %s\\n\", substr($0, RSTART+8, RLENGTH-8)} /groove-mesher/ {match($0, /takes\\/([[:alnum:]-]+)/); printf \"GROOVE-MESHER - %s\\n\", substr($0, RSTART+6, RLENGTH-6)}'"
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)

    lines = output.split('\n')
    running_processes = {
        'scan_db': False,
        'blender': False,
        'scan_id': None,
        'groove_mesher': False
    }

    for line in lines:
        if 'PYTHON - scan_db' in line:
            running_processes['scan_db'] = True
        elif 'BLENDER' in line:
            running_processes['blender'] = True
            running_processes['scan_id'] = line.split(' - ')[1].strip()
        elif 'GROOVE-MESHER' in line:
            running_processes['groove_mesher'] = True
            running_processes['scan_id'] = line.split(' - ')[1].strip()


    print("Running processes:", running_processes)  # Add this line
    return running_processes

def get_scan_db_output():
    log_file = "scan_db_output.log"
    try:
        with open(log_file, "r") as f:
            output = f.read()
        return output
    except Exception as e:
        return f"Error fetching scan_db output: {str(e)}"


@app.route('/api/scan_db_output', methods=['GET'])
def scan_db_output():
    output = get_scan_db_output()
    return jsonify({'output': output})



@app.route('/api/check_machines', methods=['GET'])
def check_machines():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    running_processes = check_scan_db_process()
    return jsonify({'hostname': hostname, 'ip_address': ip_address, 'running_processes': running_processes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)