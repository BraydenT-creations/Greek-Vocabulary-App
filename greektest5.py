import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import json
import csv
import random
import os

VOCAB_FILE = 'vocab.json'

def load_vocab():
    if os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_vocab(vocab):
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

def export_vocab(data):
    filepath = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")],
        title="Export Vocabulary"
    )
    if filepath:
        try:
            if filepath.endswith(".csv"):
                with open(filepath, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['greek', 'english', 'type'])
                    writer.writeheader()
                    writer.writerows(data)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Export Successful", f"Vocabulary exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {e}")

def import_vocab():
    filepath = filedialog.askopenfilename(
        filetypes=[("JSON or CSV files", "*.json *.csv")],
        title="Import Vocabulary"
    )
    if not filepath:
        return

    imported = []
    try:
        if filepath.endswith(".json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
        elif filepath.endswith(".csv"):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if all(k in row for k in ['greek', 'english', 'type']):
                        imported.append({
                            'greek': row['greek'].strip(),
                            'english': row['english'].strip(),
                            'type': row['type'].strip().lower()
                        })
        else:
            raise ValueError("Unsupported file type.")

        if not isinstance(imported, list):
            raise ValueError("Data must be a list of vocabulary entries.")

        added = 0
        for entry in imported:
            if not all(k in entry for k in ['greek', 'english', 'type']):
                continue
            existing = next((v for v in vocab if v['greek'] == entry['greek']), None)
            if existing:
                continue
            vocab.append(entry)
            added += 1

        save_vocab(vocab)
        messagebox.showinfo("Import Complete", f"Imported {added} new vocabulary entries.")

    except Exception as e:
        messagebox.showerror("Import Failed", f"Error: {e}")

def add_word():
    greek = simpledialog.askstring("Add Vocabulary", "Enter the Greek word:")
    if greek is None:
        return
    for i, entry in enumerate(vocab):
        if entry['greek'] == greek:
            if not messagebox.askyesno("Duplicate Detected", f"The word '{greek}' already exists. Update it?"):
                return
            english = simpledialog.askstring("Update Vocab", "Enter the new English meaning:", initialvalue=entry['english'])
            if english is None:
                return
            new_type = simpledialog.askstring("Update Vocab", "Enter the new part of speech:", initialvalue=entry.get('type', ''))
            vocab[i] = {'greek': greek, 'english': english, 'type': new_type.lower()}
            save_vocab(vocab)
            messagebox.showinfo("Updated", f"Updated: {greek} — {english} [{new_type}]")
            return
    english = simpledialog.askstring("Add Vocab", "Enter the English meaning:")
    if english is None:
        return
    type_window = tk.Toplevel(root)
    type_window.title("Choose Part of Speech")
    type_window.geometry("300x150")
    tk.Label(type_window, text="Select the part of speech:", font=('Helvetica', 12)).pack(pady=10)
    pos_var = tk.StringVar(type_window)
    pos_var.set("noun")
    options = ["noun", "verb", "adjective", "preposition", "conjunction", "particle", "adverb", "pronoun"]
    dropdown = tk.OptionMenu(type_window, pos_var, *options)
    dropdown.pack(pady=5)
    def confirm_type():
        word_type = pos_var.get()
        vocab.append({'greek': greek, 'english': english, 'type': word_type})
        save_vocab(vocab)
        messagebox.showinfo("Success", f"Added: {greek} — {english} [{word_type}]")
        type_window.destroy()
    tk.Button(type_window, text="Confirm", command=confirm_type).pack(pady=10)

def add_vocab_menu():
    add_window = tk.Toplevel(root)
    add_window.title("Add Vocabulary")
    add_window.geometry("250x150")
    tk.Label(add_window, text="Choose a method:", font=('Helvetica', 12)).pack(pady=10)
    tk.Button(add_window, text="Import .csv", command=lambda: [import_vocab(), add_window.destroy()], width=20).pack(pady=5)
    tk.Button(add_window, text="Manual Add", command=lambda: [add_word(), add_window.destroy()], width=20).pack(pady=5)

def start_quiz_pool(word_list):
    correct = []
    incorrect = []
    total = len(word_list)
    index = 0
    for word in word_list:
        index += 1
        progress = f"({index} / {total})\nWhat does '{word['greek']}' mean?\n\n✅ {len(correct)}     ❌ {len(incorrect)}"
        answer = simpledialog.askstring("Quiz", progress)
        if answer is None:
            break
        answer = answer.strip().lower()
        accepted = [a.strip().lower() for a in word['english'].split(",")]
        if answer in accepted:
            correct.append(word)
            messagebox.showinfo("Correct", f"✅ Correct!\n\n{word['greek']} — {word['english']}\n\n✅ {len(correct)}     ❌ {len(incorrect)}")
        else:
            incorrect.append(word)
            messagebox.showinfo("Incorrect", f"❌ Incorrect.\n\n{word['greek']} — {word['english']}\n\n✅ {len(correct)}     ❌ {len(incorrect)}")
    if incorrect:
        percent = round(100 * len(correct) / total)
        if messagebox.askyesno("Round Complete", f"You got {len(correct)} / {total} correct ({percent}%).\n\nReview {len(incorrect)} incorrect terms?"):
            random.shuffle(incorrect)
            start_quiz_pool(incorrect)
        else:
            messagebox.showinfo("Done", "Quiz ended.")
    else:
        messagebox.showinfo("Congratulations!", "🎉 You got 100% — you're done!")

def quiz_menu():
    if not vocab:
        messagebox.showinfo("Quiz", "No vocabulary to quiz.")
        return
    quiz_window = tk.Toplevel(root)
    quiz_window.title("Quiz Options")
    quiz_window.geometry("300x300")
    tk.Label(quiz_window, text="Choose a quiz type:", font=('Helvetica', 12, 'bold')).pack(pady=10)
    def launch_quiz(pos=None):
        filtered = [v for v in vocab if v.get('type') == pos] if pos else vocab[:]
        if not filtered:
            messagebox.showinfo("Quiz", f"No {pos}s in your vocab list." if pos else "No words available.")
            return
        random.shuffle(filtered)
        start_quiz_pool(filtered)
    for pos in ["All", "noun", "verb", "adjective", "preposition"]:
        label = f"{pos.capitalize()}s Only" if pos != "All" else "All Vocabulary"
        value = None if pos == "All" else pos
        tk.Button(quiz_window, text=label, command=lambda v=value: launch_quiz(v), width=25).pack(pady=5)

def show_all(filter_type=None):
    if not vocab:
        messagebox.showinfo("Vocabulary List", "No words saved yet.")
        return
    top = tk.Toplevel(root)
    top.title("Vocabulary")
    top.geometry("700x450")
    filter_var = tk.StringVar()
    filter_var.set("All")
    filter_options = ["All"] + sorted(set(v.get('type', '') for v in vocab if v.get('type')))
    def update_display(*args):
        for i in tree.get_children():
            tree.delete(i)
        selected = filter_var.get()
        filtered_vocab = [v for v in vocab if v.get('type') == selected] if selected != "All" else vocab
        sorted_vocab = sorted(filtered_vocab, key=lambda x: x['greek'])
        for i, entry in enumerate(sorted_vocab):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            tree.insert("", tk.END, values=(entry['greek'], entry['english'], entry.get('type', '')), tags=tags)
    filter_frame = tk.Frame(top)
    filter_frame.pack(pady=5)
    tk.Label(filter_frame, text="Filter by part of speech:").pack(side=tk.LEFT, padx=5)
    filter_menu = tk.OptionMenu(filter_frame, filter_var, *filter_options, command=update_display)
    filter_menu.pack(side=tk.LEFT)
    columns = ("greek", "english", "type")
    tree = ttk.Treeview(top, columns=columns, show="headings", selectmode="extended")
    tree.tag_configure('oddrow', background="#ffffff")
    tree.tag_configure('evenrow', background="#f0f0f0")
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=200 if col == "english" else 140, anchor=tk.W)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def on_double_click(event):
        item = tree.identify_row(event.y)
        if not item:
            return
        selected = tree.item(item)['values']
        old_greek = selected[0]
        old_english = selected[1]
        old_type = selected[2]

        edit_win = tk.Toplevel(top)
        edit_win.title("Edit Word")
        tk.Label(edit_win, text="Greek:").grid(row=0, column=0, padx=5, pady=5)
        greek_entry = tk.Entry(edit_win)
        greek_entry.insert(0, old_greek)
        greek_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="English:").grid(row=1, column=0, padx=5, pady=5)
        english_entry = tk.Entry(edit_win)
        english_entry.insert(0, old_english)
        english_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_win, text="Type:").grid(row=2, column=0, padx=5, pady=5)
        type_entry = tk.Entry(edit_win)
        type_entry.insert(0, old_type)
        type_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_changes():
            new_greek = greek_entry.get().strip()
            new_english = english_entry.get().strip()
            new_type = type_entry.get().strip().lower()
            for entry in vocab:
                if entry['greek'] == old_greek:
                    entry['greek'] = new_greek
                    entry['english'] = new_english
                    entry['type'] = new_type
                    break
            save_vocab(vocab)
            update_display()
            edit_win.destroy()

        tk.Button(edit_win, text="Save", command=save_changes).grid(row=3, columnspan=2, pady=10)

    tree.bind("<Double-1>", on_double_click)

    def delete_selected():
        selected_items = tree.selection()
        if not selected_items:
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected_items)} selected word(s)?"):
            return
        selected_greek_words = [tree.item(item)['values'][0] for item in selected_items]
        global vocab
        vocab = [entry for entry in vocab if entry['greek'] not in selected_greek_words]
        save_vocab(vocab)
        messagebox.showinfo("Deleted", f"Deleted {len(selected_items)} word(s).")
        update_display()
    btn_frame = tk.Frame(top)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Export", command=lambda: export_vocab(vocab)).pack(side=tk.LEFT, padx=10)
    update_display()

root = tk.Tk()
root.title("Greek Vocabulary Trainer")
root.geometry("320x550")

style = ttk.Style()
style.configure("Treeview", rowheight=24)
style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'))
style.map('Treeview', background=[('selected', '#d1e7dd')])
if 'clam' in style.theme_names():
    style.theme_use('clam')
    style.configure("Treeview", background="#f9f9f9", fieldbackground="#f9f9f9")
    style.map("Treeview", background=[('selected', '#b0d4c1')])
    style.configure("Treeview", rowheight=26)
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

vocab = load_vocab()

container = tk.Frame(root)
container.pack(expand=True, fill='both')
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

main_frame = tk.Frame(container)
main_frame.place(relx=0.5, rely=0.5, anchor='center')

widgets = []
widgets.append(tk.Label(main_frame, text="Greek Vocabulary Trainer", font=('Helvetica', 14, 'bold')))

search_frame = tk.Frame(main_frame)
search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, font=('Helvetica', 11), width=30)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind("<Return>", lambda event: perform_search())
widgets.append(search_frame)

widgets.append(tk.Button(main_frame, text="Add Vocabulary", command=add_vocab_menu, width=25))
widgets.append(tk.Button(main_frame, text="Vocabulary List", command=lambda: show_all(None), width=25))
widgets.append(tk.Button(main_frame, text="Quiz Me", command=quiz_menu, width=25))
widgets.append(tk.Button(main_frame, text="Exit", command=root.destroy, width=25))

for widget in widgets:
    widget.pack(pady=10)

def perform_search():
    query = search_var.get().strip().lower()
    if not query:
        return
    matches = []
    for v in vocab:
        greek = v['greek'].strip().lower()
        english_list = [e.strip().lower() for e in v['english'].split(",")]
        if query == greek:
            matches.append(f"{v['greek']} — {v['english']} [{v.get('type', '')}]")
        elif query in english_list:
            matches.append(f"{v['english']} — {v['greek']} [{v.get('type', '')}]")
    if matches:
        messagebox.showinfo("Definition", "\n".join(matches))
    else:
        messagebox.showinfo("Definition", "No match found.")
    root.after(100, lambda: search_entry.focus_set())

root.mainloop()
