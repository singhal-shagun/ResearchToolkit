
def main():
    from nicegui import app, ui
    from .Infrastructure.Constants import SiteConstants
    from .Routes import router
    
    app.include_router(router)

    ui.run(title= SiteConstants.SITE_TITLE,
        favicon='.\\FrontendCode\\Infrastructure\\static\\icons8-brain-100 (1).png',
        reload=False,
        show=False)

if __name__ == '__main__':
    main()