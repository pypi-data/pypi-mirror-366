import argparse

def count_words(filename):
    try:
        with open(filename, 'r') as f:
            text = f.read()
        words = text.split()
        print(f"{len(words)} words in {filename}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

def main():
    parser = argparse.ArgumentParser(description="Counts words in a text file.")
    parser.add_argument("filename", help="The name of the file to analyze.")
    args = parser.parse_args()
    count_words(args.filename)

if __name__ == "__main__":
    main()
