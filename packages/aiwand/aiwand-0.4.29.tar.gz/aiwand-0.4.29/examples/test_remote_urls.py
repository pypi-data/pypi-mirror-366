import aiwand

def main():

    # Test cases
    test_paths = [
        "amankumar.ai",
        "bella.amankumar.ai/images/1",
        "man.txt",
        "cat.png",
        "https://bella.amankumar.ai/images/2",
        "www.amankumar.ai/projects/",
        "localhost:3000",
        "127.0.0.1/file",
        "/usr/local/data.csv",
        "./notes.md",
        "README.md"
    ]

    for path in test_paths:
        print(f"{path:<45} -> {'REMOTE' if aiwand.is_remote_url(path) else 'LOCAL'}")

if __name__ == 'main':
    main()
