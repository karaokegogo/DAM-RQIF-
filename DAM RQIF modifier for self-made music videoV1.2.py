import tkinter as tk
from tkinter import filedialog
import struct

def open_and_modify_files():
    file_paths = filedialog.askopenfilenames(title="【STEP 1】Choose files to add 1999 information", filetypes=[("Binary Files", "*")])

    if file_paths:
        for file_path in file_paths:
            modify_file(file_path)

def modify_file(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()

    # Find the position of the first occurrence of 03 FD
    first_position = content.find(b'\x03\xFD')

    if first_position != -1:
        # Replace the first occurrence of 03 FD with 07 CF
        content = content[:first_position] + b'\x07\xCF' + content[first_position + 2:]

        # Get the file name suffix and convert it to binary code
        file_suffix_binary = file_suffix_to_binary(file_path)

        # Get the original content after the first 03 FD
        original_content = content[first_position + 2: first_position + 8]

        # Build new content, including the binary code of the file name suffix
        new_content = file_suffix_binary + b'\x00\x00'

        # Concatenate the new content with the original content after the first 03 FD
        content = content[:first_position + 2] + new_content + content[first_position + 8:]

        # Find the position of the second occurrence of 03 FD
        second_position = content.find(b'\x03\xFD', first_position + 2)

        if second_position != -1:
            # Build new content, maintaining the original length
            new_content = b'\x07\xCF\x00\x00\x00\x01\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

            # Replace the content after the second 03 FD with the new content
            content = content[:second_position] + new_content + content[second_position + len(new_content):]

            # Find the position of the third occurrence of 03 FD
            third_position = content.find(b'\x03\xFD', second_position + len(new_content))

            if third_position != -1:
                # Replace the content after the third 03 FD with the new content, maintaining the original length
                content = content[:third_position] + new_content + content[third_position + len(new_content):]

                # Write back to the file
                with open(file_path, 'wb') as file:
                    file.write(content)

                result_text.insert(tk.END, f"{get_file_name(file_path)}: Successfully added 1999 information!\n")
            else:
                result_text.insert(tk.END, f"{get_file_name(file_path)}: Third occurrence of 03 FD not found, unable to perform the first modification.\n", "red_text")
        else:
            result_text.insert(tk.END, f"{get_file_name(file_path)}: Second occurrence of 03 FD not found, unable to perform the first modification.\n", "red_text")
    else:
        result_text.insert(tk.END, f"{get_file_name(file_path)}: First occurrence of 03 FD not found, unable to perform the first modification.\n", "red_text")

def file_suffix_to_binary(file_path):
    # Extract the file name suffix and convert it to a 6-digit binary code
    file_name = file_path.split('/')[-1]  # Get the file name
    suffix = file_name.split('.')[-1]  # Get the suffix part
    suffix_binary = format(int(suffix), '06b')  # Convert to a 6-digit binary code
    return struct.pack('!I', int(suffix_binary, 2))

def choose_files():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename(title="【STEP 2】Adjust video time to align music", filetypes=[("Binary Files", "*")])

    if selected_file_path:
        selected_file_label.config(text=f"Selected file: {selected_file_path}")
    else:
        selected_file_label.config(text="No file selected")

def confirm_modification():
    # Get the selected file path
    file_path = selected_file_path if 'selected_file_path' in globals() else None

    if file_path:
        # Perform the second modification
        modify_second_time(file_path)
    else:
        result_text_second.insert(tk.END, "Please choose a file first and then click the confirm modification button.\n", "red_text")

def modify_second_time(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()

    # Find the position of content starting with 07 CF
    start_position = content.find(b'\x07\xCF')

    if start_position != -1:
        # Get the milliseconds to advance and delay
        milliseconds_before = int(entry_before.get())
        milliseconds_after = int(entry_after.get())

        # Keep the original content from the first modification
        original_content = content[start_position:start_position + 8]

        # Build new content
        new_content = original_content + struct.pack('>I', milliseconds_before)[2:] + b'\xFF\xFF\xFF\xFF' + struct.pack('>I', milliseconds_after)[2:].rjust(4, b'\x00')

        # Replace the content
        content = content[:start_position] + new_content + content[start_position + len(new_content):]

        # Write back to the file
        with open(file_path, 'wb') as file:
            file.write(content)

        # Update the result text box to display success message and advance/delay time
        success_message = f"{get_file_name(file_path)}: Time offset modification successful! [Advance {milliseconds_before} ms] [Delay {milliseconds_after} ms]\n"
        result_text_second.insert("1.0", success_message)
            
    else:
        result_text_second.insert(tk.END, f"{get_file_name(file_path)}: Content starting with 07 CF not found, unable to perform the second modification.\n", "red_text")

def get_file_name(file_path):
    return file_path.split('/')[-1]

# Create the main window
window = tk.Tk()
window.title("karaokegogo")
window.geometry("600x800")  # Set window size

# Add title
title_label = tk.Label(window, text="DAM本人映像RQIFファイル全自動モディファイヤ V1.2", font=("TkDefaultFont", 16, "bold"))
title_label.pack(pady=12)

# Add the first line of introductory text
intro_label1 = tk.Label(window, text="【STEP 1】Choose files to add 1999 information", font=("TkDefaultFont", 10, "bold"), foreground="blue")
intro_label1.pack(pady=5)

# Add the "Choose files" button and result text box
btn_open_files = tk.Button(window, text="Choose files to add 1999 information", command=open_and_modify_files)
btn_open_files.pack(pady=10)

result_text = tk.Text(window, height=15, width=70)
result_text.pack()

result_text.tag_configure("red_text", foreground="red")

# Add the second line of introductory text
intro_label2 = tk.Label(window, text="【STEP 2】Adjust video time to align music", font=("TkDefaultFont", 10, "bold"), foreground="blue")
intro_label2.pack(pady=5)

# Add the "Choose a file" button and file path display box
btn_choose_files = tk.Button(window, text="Choose a file", command=choose_files)
btn_choose_files.pack(pady=5)

label_before = tk.Label(window, text="Advance milliseconds:")
label_before.pack()
entry_before = tk.Entry(window, width=8)
entry_before.insert(0, "0")
entry_before.pack()

label_after = tk.Label(window, text="Delay milliseconds:")
label_after.pack()
entry_after = tk.Entry(window, width=8)
entry_after.insert(0, "0")
entry_after.pack()

selected_file_label = tk.Label(window, text="No file selected")
selected_file_label.pack()

# Add the "Confirm modification" button
btn_confirm_modification = tk.Button(window, text="Confirm modification", command=confirm_modification)
btn_confirm_modification.pack()

# Add the result text box for the second modification
result_text_second = tk.Text(window, height=3, width=30)

# Add a scrollbar
scrollbar = tk.Scrollbar(window, command=result_text_second.yview)
result_text_second.config(yscrollcommand=scrollbar.set)

# Update the pack method of result_text_second
result_text_second.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure tags to set text color
result_text_second.tag_configure("red_text", foreground="red")

# Run the main loop
window.mainloop()
