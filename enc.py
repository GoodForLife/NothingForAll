import sys
import marshal
import zlib
import base64

def encode_python_file(file_path, output_path):
    with open(file_path, "r") as file:
        python_code = file.read()

    compiled_code = marshal.dumps(compile(python_code, "<string>", "exec"))
    compressed_code = zlib.compress(compiled_code)
    encoded_code = base64.b64encode(compressed_code).decode("utf-8")

    with open(output_path, "w") as output_file:
        output_file.write(f"import marshal\nimport zlib\nimport base64\nexec(marshal.loads(zlib.decompress(base64.b64decode({repr(encoded_code)}))));")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python enc.py <input_path> <output_path>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        encode_python_file(input_file, output_file)
        print(f"Encoded Python file created as {output_file}")
