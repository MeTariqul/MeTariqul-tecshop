with open(r'd:\Project\Git Hub\Ecommerse\techshop\templates\orders\order_confirmation.html', 'rb') as f:
    lines = f.readlines()
    # Line 27 (0-indexed is 26)
    line_26 = lines[26]
    print(f"Line 26 content: {line_26}")
    print(f"Line 26 hex: {line_26.hex()}")

    # Line 27
    line_27 = lines[27]
    print(f"Line 27 content: {line_27}")
    print(f"Line 27 hex: {line_27.hex()}")

    for i, line in enumerate(lines):
        if b"Total:" in line:
            print(f"Line {i+1} content: {line}")
            print(f"Line {i+1} hex: {line.hex()}")

