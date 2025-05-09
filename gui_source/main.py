def main():
    try:
        import pyi_splash  # only available when packaged with pyinstaller # type: ignore

        im_ok = True
    except Exception:
        im_ok = False

    if im_ok:
        pyi_splash.update_text("Initializing UI...")

    ##### INITIALIZE #####
    from gui import show_app

    if im_ok:
        pyi_splash.close()
    show_app()


if __name__ == "__main__":
    main()
