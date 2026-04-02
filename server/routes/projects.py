from flask import Blueprint, request, jsonify
import os

import utils

projectsBP = Blueprint('projects', __name__)

@projectsBP.route('/mkprj', methods=['POST'])
def makeProject():
    data = request.get_json()
    if not os.path.exists(data.get("dir")):
        try:
            os.makedirs(data.get("dir"))
        except Exception as e:
            return jsonify({"status":"error","message":f"ERROR making directories:{str(e)}"})
        
    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()
    try:
        dbCursor.execute(
            "INSERT INTO projects (name,code,dir) VALUES (?, ?, ?)",
            (data["name"], data.get("code"), data.get("dir"))
        )
        dbConn.commit()
        return jsonify({"status":"success","id":dbCursor.lastrowid}),200
    except Exception as e:
        return jsonify({"status":"error","message":f"ERROR:{str(e)}"})
    
@projectsBP.route('/mkep', methods=['POST'])
def makeEpisode():
    # ARGS = ProjectCode, Code 'ep101'eg ,name 'episodeLabel' Optional
    data = request.get_json()

    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()
    # Verify the project exists
    dbCursor.execute("SELECT id, dir FROM projects WHERE code = ?", (data["project_code"],))
    project = dbCursor.fetchone()
    if not project:
        return jsonify({"status": "error", "message": f"Project '{data['project_code']}' not found"}), 404

    epDir = os.path.join(project["dir"], "Episodes", data["code"])
    if not os.path.exists(epDir):
        try:
            os.makedirs(epDir)
        except Exception as e:
            return jsonify({"status": "error", "message": f"ERROR making directories: {str(e)}"})
    else:
        return jsonify({"status": "error", "message": f"Episode {data["code"]} already exists on project {data["project_code"]}"})

    try:
        dbCursor.execute(
            "INSERT INTO episodes (project_id, name, code, dir) VALUES (?, ?, ?, ?)",
            (project["id"], data.get("name"), data["code"], epDir)
        )
        dbConn.commit()
        return jsonify({"status": "success", "id": dbCursor.lastrowid}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"ERROR: {str(e)}"})

@projectsBP.route('/mksq', methods=['POST'])
def makeSequence():
    # ARGS = ProjectCode, epcode, code 'sp101'eg ,name 'sequenceLabel' Optional
    data = request.get_json()

    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()
    # Verify the project exists
    dbCursor.execute("SELECT id, dir FROM projects WHERE code = ?", (data["project_code"],))
    project = dbCursor.fetchone()
    if not project:
        return jsonify({"status": "error", "message": f"Project '{data['project_code']}' not found"}), 404
    
    # Verify the episode exists
    dbCursor.execute("SELECT id, dir FROM episodes WHERE code = ?", (data["ep_code"],))
    episode = dbCursor.fetchone()
    if not episode:
        return jsonify({"status": "error", "message": f"Episode '{data['ep_code']}' not found in project {data['project_code']}"}), 404

    epDir = os.path.join(project["dir"], "Episodes", data["ep_code"])
    sqDir = os.path.join(epDir, "Sequences", data["code"])

    if not os.path.exists(sqDir):
        try:
            os.makedirs(sqDir)
        except Exception as e:
            return jsonify({"status": "error", "message": f"ERROR making directories: {str(e)}"})
    else:
        return jsonify({"status": "error", "message": f"Sequence {data["code"]} already exists in episode {data["ep_code"]} on project {data["project_code"]}"})
    
    try:
        dbCursor.execute(
            "INSERT INTO sequences (project_id, episode_id, name, code, dir) VALUES (?, ?, ?, ?, ?)",
            (project["id"], episode["id"], data.get("name"), data["code"], sqDir)
        )
        dbConn.commit()
        return jsonify({"status": "success", "id": dbCursor.lastrowid}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"ERROR: {str(e)}"})



@projectsBP.route('/mksh', methods=['POST'])
def makeShot():
    # ARGS  = ProjectCode, code 'sh010', name 'shotName'
    pass

@projectsBP.route('/projects', methods=['GET'])
def getProjects():
    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT id, name FROM projects ORDER BY name")
    rows = [dict(row) for row in dbCursor.fetchall()]
    dbConn.close()
    return jsonify(rows)