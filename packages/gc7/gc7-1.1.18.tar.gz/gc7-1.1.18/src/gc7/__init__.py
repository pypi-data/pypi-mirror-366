try:
    # Essayer d'abord d'importer depuis le fichier généré par setuptools_scm
    from ._version import __version__
except ImportError:
    try:
        # Sinon, essayer d'utiliser setuptools_scm directement
        from setuptools_scm import get_version

        __version__ = get_version(root="../..", relative_to=__file__)
    except (ImportError, LookupError):
        try:
            # Sinon, essayer d'obtenir la version depuis le package installé
            from importlib.metadata import version

            __version__ = version("gc7")
        except:
            # Valeur par défaut si tout échoue
            __version__ = "0.0.0"
