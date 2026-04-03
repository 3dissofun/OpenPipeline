from flask import Blueprint, request, jsonify
import os

import utils

projectsBP = Blueprint('projects', __name__)

# MAKING METHODS

@projectsBP.route('/mkprj', methods=['POST'])
def makeProject():
    data = request.get_json()
    
    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()
    try:
        dbCursor.execute(
            "INSERT INTO projects (name,code,dir) VALUES (?, ?, ?)",
            (data["name"], data.get("code"), data.get("dir"))
        )
        dbConn.commit()
    except Exception as e:
        return jsonify({"status":"error","message":f"ERROR:{str(e)}"})
    
    if not os.path.exists(data.get("dir")):
        try:
            os.makedirs(data.get("dir"))
            return jsonify({"status":"success", "message": f"succesfully made project {data["name"]}"}),200
        except Exception as e:
            return jsonify({"status":"error","message":f"ERROR making directories:{str(e)}"})
    
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

    try:
        dbCursor.execute(
            "INSERT INTO episodes (project_id, name, code, dir) VALUES (?, ?, ?, ?)",
            (project["id"], data.get("name"), data["code"], epDir)
        )
        dbConn.commit()
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"ERROR: {str(e)}"})
    
    if not os.path.exists(epDir):
        try:
            os.makedirs(epDir)
            return jsonify({"status": "success", "message": f"succesfully made episode in project {data["project_code"]} at {epDir}"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"ERROR making directories: {str(e)}"})
    else:
        return jsonify({"status": "error", "message": f"Episode {data["code"]} already exists on project {data["project_code"]}"})

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

    sqDir = os.path.join(episode["dir"], "Sequences", data["code"])

    try:
        dbCursor.execute(
            "INSERT INTO sequences (project_id, episode_id, name, code, dir) VALUES (?, ?, ?, ?, ?)",
            (project["id"], episode["id"], data.get("name"), data["code"], sqDir)
        )
        dbConn.commit()
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"ERROR: {str(e)}"})
    
    if not os.path.exists(sqDir):
        try:
            os.makedirs(sqDir)
            return jsonify({"status": "success", "message": f"succesfully made sequence {sqDir} in project {data["project_code"]}"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"ERROR making directories: {str(e)}"})
    else:
        return jsonify({"status": "error", "message": f"Sequence {data["code"]} already exists in episode {data["ep_code"]} on project {data["project_code"]}"})

@projectsBP.route('/mksh', methods=['POST'])
def makeShot():
    # ARGS  = ProjectCode, code 'sh010', name 'shotName'
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
    # Verify the sequence exists
    dbCursor.execute("SELECT id, dir FROM sequences WHERE code = ?", (data["sq_code"],))
    sequence = dbCursor.fetchone()
    if not sequence:
        return jsonify({"status": "error", "message": f"Sequence '{data['sq_code']}' not found in episode {data['ep_code']} on project {data['project_code']}"}), 404
    
    shDir = os.path.join(sequence["dir"], data["code"])

    try:
        dbCursor.execute(
            "INSERT INTO shots (project_id, episode_id, sequence_id, name, code, dir) VALUES (?, ?, ?, ?, ?, ?)",
            (project["id"], episode["id"], sequence["id"], data.get("name"), data["code"], shDir)
        )
        dbConn.commit()
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"ERROR: {str(e)}"})
    
    if not os.path.exists(shDir):
        try:
            tasks = utils.getShotTasks()
            os.makedirs(shDir)
            for task in tasks:
                taskPath = os.path.join(shDir,task)
                os.mkdir(taskPath)
                wipPath = os.path.join(taskPath,"WIP")
                pubPath = os.path.join(taskPath,"PUB")
                os.mkdir(wipPath)
                os.mkdir(pubPath)
            return jsonify({"status": "success", "message": f"sucessfully made shot {data["code"]} in {str(shDir)}"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"ERROR making directories: {str(e)}"})
    else:
        return jsonify({"status": "error", "message": f"Shot {data["code"]} already exists in sequence {data["sq_code"]} in episode {data["ep_code"]} on project {data["project_code"]}"})

# REMOVAL METHODS

@projectsBP.route('/rmsh', methods=['POST'])
def removeShot():
    data = request.get_json()
    
    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()

    try:
        dbCursor.execute("SELECT id FROM projects WHERE code = ?",(data["project_code"],))
        project = dbCursor.fetchone()
        if not project:
            return jsonify({"status":"error","message":f"couldnt find project {data["project_code"]}"})
        dbCursor.execute("SELECT id FROM episodes WHERE code = ? AND project_id = ?",(data["ep_code"],project["id"]))
        episode = dbCursor.fetchone()
        if not episode:
            return jsonify({"status":"error","message":f"couldnt find episode {data["ep_code"]}"})
        dbCursor.execute("SELECT id FROM sequences WHERE code = ? AND project_id = ?",(data["sq_code"],project["id"]))
        sequence = dbCursor.fetchone()
        if not sequence:
            return jsonify({"status":"error","message":f"couldnt find sequence {data["sq_code"]}"})
        
        dbCursor.execute("DELETE FROM shots WHERE code = ? AND project_id = ? AND episode_id = ? AND sequence_id = ?",
                        (data["sh_code"], project["id"], episode["id"], sequence["id"]))
        dbConn.commit()
        
        if dbCursor.rowcount:
            return jsonify({"status":"success","message":f"Shot {data["sh_code"]} deleted succesfully"})
        else:
            return jsonify({"status":"error","message":f"Couldnt find shot {data["sh_code"]}"})

    except Exception as e:
        dbConn.rollback()
        return jsonify({"status":"error","message":f"Error deleting shot {data["sh_code"]}"})
    
# RETRIVAL METHODS

@projectsBP.route('/lsprjs', methods=['GET'])
def getProjects():
    dbConn = utils.getDB()
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT id, name FROM projects ORDER BY name")
    rows = [dict(row) for row in dbCursor.fetchall()]
    dbConn.close()
    return jsonify(rows)