def tokens():
    from setuptools_scm import get_version

    print("\nDernière version pymox_tools1: " + get_version() + "\n" + ("-" * 71))
    from dotenv import load_dotenv
    import os

    load_dotenv()  # Charge les variables depuis .env
    # load_dotenv(override=True)

    gh_token = os.getenv("GH_TOKEN")
    pypi_token = os.getenv("PYPI_TOKEN")

    print(f"GH_TOKEN: {gh_token}\n\nPYPI_TOKEN: {pypi_token}\n")

    return f"Salut les gens !"


if __name__ == "__main__":

    tokens()

    # import greetings as gt
    from pymox_tools1 import greetings as gt

    print(gt.hello(), "\n" + gt.bye())
