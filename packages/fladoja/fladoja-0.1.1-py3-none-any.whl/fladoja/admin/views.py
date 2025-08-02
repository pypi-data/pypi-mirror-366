def setup_admin_routes(app):
    @app.site('/admin/')
    def admin_panel(params):
        # Логика админ-панели
        pass

    @app.site('/admin/edit')
    def admin_edit(params):
        # Логика редактора
        pass