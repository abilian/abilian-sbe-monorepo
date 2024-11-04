from flask import Flask


def setup_blueprints(app: Flask) -> None:
    from abilian.services.preferences import preferences
    from abilian.web.coreviews import users
    from abilian.web.preferences.user import UserPreferencesPanel
    from abilian.web.views.images import images_bp

    app.register_blueprint(images_bp)
    app.register_blueprint(users.blueprint)
    preferences.register_panel(UserPreferencesPanel(), app)