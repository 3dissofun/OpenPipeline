from flask import Blueprint, request, jsonify
import subprocess
import os

import utils

publishBP = Blueprint('publish', __name__)

@publishBP.route('/publish', methods=['POST'])
def publishEndpoint():
    data = request.json
    path = data['path']

    print(f"--- NEW PUBLISH REQUEST ---")
    print(f"FileName: {data['name']}")
    print(f"Location: {path}")
    
    # Publish Path
    base, ext = os.path.splitext(path)
    pubPath = rf"{base}_PUB{ext}"
    pubPathBlender = pubPath.replace("\\", "/")
    blenderApp = utils.getBlenderExe()

    print(f"Publishing to: {pubPath}")

    bCommand = f"import bpy; bpy.ops.wm.save_as_mainfile(filepath='{pubPathBlender}', copy=True)"
    try:
        result = subprocess.run([
            blenderApp, 
            "-b", path,           # Open the file in background
            "--python-expr", bCommand # Run the save command
        ], check=True, capture_output=True, text=True)

        if "Error" in result.stdout or "Traceback" in result.stdout:
            return jsonify({"status": "error", "message": f"Blender process failed:{result.stdout}"}), 501
        
        if not os.path.exists(pubPath):
            return jsonify({"status": "error", "message": "Blender ran but output file was not created"}), 502

        print(f"Succesfully Published:{os.path.basename(pubPath)}")
        return jsonify({"status": "success", "message": f"Published: {os.path.basename(pubPath)}"}), 200
            
    except subprocess.CalledProcessError as e:
        # Blender itself crashed or exited with a non-zero code
        print(f"Blender process failed:\n{e.stdout}")
        return jsonify({"status": "error", "message": f"Blender process failed:\n{e.stdout}"}), 503

    except RuntimeError as e:
        # Blender ran but reported an internal error
        print(f"Runtime Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 504

    except Exception as e:
        # Unknown Error
        print(f"Unknown Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 505