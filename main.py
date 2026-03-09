
if __name__ == '__main__':
    # 1. Boot up the backend.
    from BackendCode.manage import main as backend_main
    backend_main()

    # 2. Boot up the frontend.
    from FrontendCode.gui_main import main as frontend_main
    frontend_main()
    

