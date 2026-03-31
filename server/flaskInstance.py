from flask import Flask

from routes.publish import publishBP
from routes.projects import projectsBP

app = Flask(__name__)
app.register_blueprint(publishBP)
app.register_blueprint(projectsBP)