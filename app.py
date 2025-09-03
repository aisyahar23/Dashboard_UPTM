from flask import Flask, render_template
from config.settings import Config
from blueprints.sosioekonomi import sosioekonomi_bp
from blueprints.demografi import demografi_bp
from blueprints.analytics import analytics_bp
from blueprints.industri_gaji import sektor_gaji_bp
from blueprints.graduanluar import graduanluar_bp
from blueprints.intern import intern_bp
from blueprints.gig_economy import gig_economy_bp
from blueprints.faktor_graduan import faktor_graduan_bp
from blueprints.statuspekerjaan import status_pekerjaan_bp
from blueprints.graduanbidang import graduan_bidang_bp
from blueprints.dashboard import dashboard_bp
from blueprints.alldata import alldata_bp

def create_app():
    app = Flask(__name__, template_folder='Website/templates', static_folder='Website/static')
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(sosioekonomi_bp, url_prefix='/sosioekonomi')
    app.register_blueprint(demografi_bp, url_prefix='/demografi')
    app.register_blueprint(sektor_gaji_bp, url_prefix='/sektor-gaji')
    app.register_blueprint(graduanluar_bp, url_prefix='/graduan-luar')
    app.register_blueprint(intern_bp, url_prefix='/intern')
    app.register_blueprint(gig_economy_bp, url_prefix='/gig-economy')
    app.register_blueprint(faktor_graduan_bp, url_prefix='/faktor-graduan')
    app.register_blueprint(status_pekerjaan_bp, url_prefix='/status-pekerjaan')
    app.register_blueprint(graduan_bidang_bp, url_prefix='/graduan-bidang')  
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(alldata_bp, url_prefix='/alldata')

    
    @app.route('/')
    def dashboard():
        return render_template('login.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)